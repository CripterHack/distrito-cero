"""Compare the distant jacket in an on-foot street camera at native NPC LODs."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import sys

from PIL import Image, ImageChops
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests"))
from character_benchmark import FIX
from qa_support import launch_options


# A frozen street with one pedestrian. The game computes camera collision,
# perspective, crowd appearance and the LOD selected on each side of the switch.
SETUP = """() => {
  const app = DC_APP;
  app.stopFrame?.();
  qaStopFrames();
  window.requestAnimationFrame = () => 0;
  const sim = new DC.Simulation(new DC.World(1337));
  sim.free = true;
  sim.time = 1.25;
  sim.peds.forEach(p => p.hidden = true);
  sim.cars.forEach((car,i) => Object.assign(car, {x:5000+i*6,z:5000,driver:null}));
  const x = 4, z = 36;
  if (sim.world.blocked(x,z,.5) || !sim.world.visible(x,z-5,x+3.5,z+52))
    throw Error("Reference street is obstructed");
  Object.assign(sim.player, {x,z,y:0,yaw:0,car:null,moveSpeed:0});
  const ped = sim.peds[0];
  Object.assign(ped, {x:x+3.5,y:0,yaw:0,variant:0,speed:0,panic:0,hidden:false});
  const r = app.renderer;
  r.world = sim.world;
  r.previewStudio = false;
  r.rain = r.bloom = 0;
  r.resetSectors();
  r.syncSectors(1000);
  const css = document.createElement('style');
  css.textContent = 'body>*:not(#world){visibility:hidden!important}#world{visibility:visible!important;position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important}';
  document.head.append(css);
  window.streetFixture = {r,sim,ped,live:JSON.stringify(app.sim.serialize()),storage:JSON.stringify([...qaCharacterStorage.entries()])};
  const gl = r.gl, ext = gl.getExtension("WEBGL_debug_renderer_info");
  return {playerXZ:[x,z], webgl:gl.getParameter(gl.VERSION),
    renderer:ext ? gl.getParameter(ext.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER)};
}"""
DRAW = """({quality,distance,hidden}) => {
  const {r,sim,ped,live,storage} = streetFixture;
  r.quality = quality;
  r.resize();
  ped.z = sim.player.z + distance;
  ped.hidden = hidden;
  if (sim.world.blocked(ped.x,ped.z,.5)) throw Error("Pedestrian position is obstructed");
  Object.assign(r.camera,{mode:0,yaw:0,pitch:.22,initialized:false});
  r.updateCamera(sim,1/60);
  r.frame = 0;
  r.lightTime = -1;
  r.render(sim);
  r.gl.finish();
  const points = [0,1.47,1.8].map(y => {
    const [x,ny,z,w] = r.project(ped.x,y,ped.z);
    if (w<=0 || Math.abs(x)>=1 || Math.abs(ny)>=1 || Math.abs(z)>=1) throw Error("Pedestrian outside view");
    return [(1+x)*innerWidth/2,(1-ny)*innerHeight/2];
  });
  if (r.gl.isContextLost() || r.gl.getError() || live!==JSON.stringify(DC_APP.sim.serialize()) ||
      storage!==JSON.stringify([...qaCharacterStorage.entries()])) throw Error("Invalid native frame");
  return {points, eye:r.camera.eye,target:r.camera.target, nativeBuffer:[r.canvas.width,r.canvas.height],
    lod:r.lodHistory.get(ped.personId||ped.id),actors:r.castStats.actors, pedestrian:[ped.x,ped.z],
    actorDistance:DC.distance(ped,sim.player)};
}"""


def digest(data):
    return hashlib.sha256(data).hexdigest()


def capture(browser, html, out):
    page = browser.new_page(viewport={"width":1280,"height":720}, device_scale_factor=1)
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.on("request", lambda req: errors.append(req.url) if req.url.startswith(("https:", "http:")) else None)
    page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
    try:
        data = html.read_bytes()
        page.set_content(data.decode().replace("<script>", "<script>"+FIX, 1), timeout=120000)
        page.wait_for_function("!!window.DC_APP", timeout=120000)
        page.evaluate("DC_APP.renderer.humanReady")
        environment = page.evaluate(SETUP)
        frames = {}
        for quality, near, far in [("balanced",42,50),("eco",24,31)]:
            page.evaluate("streetFixture.r.lodHistory.clear()")
            for distance, expected in [(near,1),(far,2)]:
                key = f"{quality}-{distance}m"
                options = dict(quality=quality, distance=distance)
                metrics = page.evaluate(DRAW, {**options,"hidden":False})
                if metrics["actors"] != 2 or metrics["lod"] != expected:
                    raise RuntimeError(f"Unexpected cast or LOD in {key}: {metrics}")
                image = page.screenshot()
                (out/f"{key}.png").write_bytes(image)
                blank = page.evaluate(DRAW, {**options,"hidden":True})
                if blank["actors"] != 1 or metrics["points"] != blank["points"]:
                    raise RuntimeError("Visibility control changed camera or kept the pedestrian")
                without = page.screenshot()
                difference = ImageChops.difference(rgb(image), rgb(without))
                x,y = metrics["points"][1]
                if difference.crop((int(x)-4,int(y)-3,int(x)+5,int(y)+4)).getbbox() is None:
                    raise RuntimeError(f"No pedestrian pixels around projected neckline in {key}")
                frames[key] = {**metrics, "imageSha256":digest(image),
                               "visibilityControlBounds":difference.getbbox()}
        if errors:
            raise RuntimeError(str(errors))
        return {"htmlSha256":digest(data), "environment":environment, "frames":frames}
    finally:
        page.close()


def rgb(data):
    return Image.open(io.BytesIO(data)).convert("RGB")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before", required=True, type=Path)
    parser.add_argument("--after", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    out = args.output.resolve()
    if not out.is_relative_to(ROOT / "artifacts") or out == ROOT / "artifacts":
        parser.error("Choose a fresh directory under artifacts/")
    out.mkdir(parents=True, exist_ok=False)
    report = {"viewport":[1280,720], "seed":1337, "fixtureTime":1.25,
              "producerSha256":digest(Path(__file__).read_bytes())}
    with sync_playwright() as pw, pw.chromium.launch(**launch_options()) as browser:
        report["browser"] = browser.version
        for label, html in [("before",args.before),("after",args.after)]:
            (out/label).mkdir()
            report[label] = capture(browser, html, out/label)
    comparison = {}
    for key, a in report["after"]["frames"].items():
        b = report["before"]["frames"][key]
        if any(a[k] != b[k] for k in a if k not in ("imageSha256", "visibilityControlBounds")):
            raise RuntimeError("Camera, actor or sampling mismatch: "+key)
        delta = ImageChops.difference(*(Image.open(out/l/f"{key}.png").convert("RGB") for l in ("before","after")))
        if a["lod"] == 1 and delta.getbbox():
            raise RuntimeError("LOD1 image differs: "+key)
        comparison[key] = {"changedRGBPixels":sum(1 for value in delta.convert("RGB").get_flattened_data() if any(value)), "changeBounds":delta.getbbox()}
    if report["before"]["environment"] != report["after"]["environment"]:
        raise RuntimeError("World or WebGL environment changed during comparison")
    report["comparison"] = comparison
    (out/"report.json").write_text(json.dumps(report,indent=2)+"\n")


if __name__ == "__main__":
    main()
