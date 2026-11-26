"""Measure the street sole/curb and both car-access boundaries from released HTML."""
import argparse
import hashlib
import json
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw
from capture_market_pedestrian import PLAYER_VIEW, SETUP, draw, launch_options, load_page
from playwright.sync_api import sync_playwright


STREET = """() => {
 const {r,sim}=marketQA,p=sim.player,g=r.gl;
 const cell=r.world.activeChunks.find(c=>p.x>=c.x&&p.x<c.x+336&&p.z>=c.z&&p.z<c.z+336);
 const batch=r.sectorGPU.get(cell.key).box,slots=new Float32Array(batch.count*16);
 const old=g.getParameter(g.ARRAY_BUFFER_BINDING);
 g.bindBuffer(g.ARRAY_BUFFER,batch.buffer);g.getBufferSubData(g.ARRAY_BUFFER,0,slots);g.bindBuffer(g.ARRAY_BUFFER,old);
 let street=-Infinity;
 for(let i=0;i<slots.length;i+=16){
  const [x,y,z,yaw,w,h,d]=slots.subarray(i,i+7),top=y+h/2;
  if(!yaw&&!slots[i+12]&&!slots[i+13]&&top<.30&&Math.abs(p.x-cell.x-x)<=w/2&&Math.abs(p.z-cell.z-z)<=d/2)
   street=Math.max(street,top);
 }
 const part=DC.HeroAsset.parts.find(v=>v.name==='sole'),v=DC.Realism.decode(part),instances=r.dynamic.hero_sole;
 const slot=instances.findIndex((val,i)=>i%16===15&&val===200)-15;
 if(slot<0||!Number.isFinite(street))throw Error('Missing player or pavement batch');
 let sole=Infinity;
 for(let i=0;i<v.length;i+=16){
  const pos=DC.DualQuaternion.transform(r.dualPixels,v.subarray(i,i+3),v.subarray(i+8,i+12),v.subarray(i+12,i+16));
  sole=Math.min(sole,instances[slot+1]+pos[1]*instances[slot+5]);
 }
 let shadow=null;
 const s=r.dynamic.smoke;for(let i=0;i<s.length;i+=16)if(s[i]===p.x&&s[i+2]===p.z&&s[i+7]===37)shadow=s[i+1];
 if(shadow===null||g.getError()!==g.NO_ERROR)throw Error('Invalid shadow or WebGL readback');
 return {pavementY:street,soleY:sole,clearance:sole-street,shadowY:shadow,phase:p.walk,rigRoot:r.motionDebug.rootY};
}"""

ACCESS = """() => {
 const {r}=marketQA,sim=new DC.Simulation(new DC.World(1337)),c=sim.cars[1],p=sim.player;
 sim.free=true;r.world=sim.world;r.lastAccessSurface=null;
 sim.cars.forEach((v,i)=>Object.assign(v,{x:300+i*6,z:0,speed:0,parked:true}));
 Object.assign(c,{x:158.7,z:141.45,yaw:0,speed:0,driver:null,owned:true});
 Object.assign(p,{x:156.4,z:141.60,yaw:Math.PI/2,car:null});
 let lift=0,pose;
 const original=r.renderPerson;
 // Measure the same instance translation applied to a zero-height landmark.
 r.renderPerson=function(actor){
  pose=actor;const batch={probe:[]};this.add(batch,'probe',actor.x,0,actor.z,1,1,1,[1,1,1]);lift=batch.probe[1];
 };
 const sample=()=>{r.renderPlayer(sim);return lift;};
 const entry={start:sample(),maxStep:0,maxPalmError:0,palmFrames:0},exit={maxStep:0};
 sim.interact('car');if(sim.access?.kind!=='enter')throw Error('Cannot start boarding');
 entry.first=sample();let previous=entry.start;
 for(let i=0;sim.access&&i<600;i++){
  const value=sample();entry.maxStep=Math.max(entry.maxStep,Math.abs(value-previous));previous=value;
  if(pose.handTargets?.R?.weight===1){
   const frame=DC.vehicleBodyFrame(c,sim.time),door=frame.door(-1,c.doorOpen),outside=frame.direction(-1,0,0,door.yaw);
   const target=door.handle.map((v,j)=>v+.015*outside[j]),hand=DC.SkinRig.palmPoint(DC.SkinRig.pose(pose,sim.time),pose,'R');
   entry.maxPalmError=Math.max(entry.maxPalmError,Math.hypot(hand.x-target[0],hand.y+value-target[1],hand.z-target[2]));
   entry.palmFrames++;
  }
  sim.step(1/60,{});
 }
 if(p.car!==1||!entry.palmFrames)throw Error('Incomplete boarding or unmeasured palm');
 entry.seatLift=sample();entry.seatY=pose.y;sim.interact('car');previous=sample();
 for(let i=0;sim.access&&i<600;i++){const value=sample();exit.maxStep=Math.max(exit.maxStep,Math.abs(value-previous));previous=value;sim.step(1/60,{});}
 if(p.car!==null)throw Error('Incomplete exit');
 exit.last=previous;exit.free=sample();exit.maxStep=Math.max(exit.maxStep,Math.abs(exit.free-exit.last));
 r.renderPerson=original;
 return {hz:60,door:[c.x-1.85,c.z+.15],entry,exit};
}"""


def survey(browser, file, take_photo):
    html = file.read_bytes()
    errors = []
    page = load_page(browser, html.decode(), errors)
    page.evaluate(SETUP)
    report = {'htmlSha256': hashlib.sha256(html).hexdigest()}
    photo = None
    if take_photo:
        page.set_viewport_size({'width': 1280, 'height': 800})
        report['camera'] = page.evaluate(PLAYER_VIEW, dict(approach=[1.4, 3.2], turnToResident=False))
        draw(page, 'player')
        report['street'] = page.evaluate(STREET)
        photo = Image.open(BytesIO(page.screenshot())).convert('RGB').crop((493, 353, 786, 581))
    report['access'] = page.evaluate(ACCESS)
    page.close()
    if errors:
        raise RuntimeError(errors)
    return report, photo


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['before', 'intermediate', 'after', 'output']:
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    reports, images = {}, {}
    with sync_playwright() as pw, pw.chromium.launch(**launch_options()) as browser:
        for key in ['before', 'intermediate', 'after']:
            reports[key], images[key] = survey(browser, getattr(args, key), key!='intermediate')
        reports['chromium'] = browser.version
    before, intermediate, after = (reports[k] for k in ['before', 'intermediate', 'after'])
    assert before['camera']==after['camera']
    assert before['street']['phase']==after['street']['phase'] and before['street']['rigRoot']==after['street']['rigRoot']
    assert before['street']['clearance']<-.13 and abs(after['street']['clearance'])<.001
    assert .002<after['street']['shadowY']-after['street']['pavementY']<.004
    assert intermediate['access']['entry']['maxStep']>.13 and intermediate['access']['exit']['maxStep']>.13
    entry, exit = after['access']['entry'], after['access']['exit']
    assert entry['maxStep']<.024 and exit['maxStep']<.024
    assert abs(entry['start']-entry['first'])<1e-8 and abs(exit['last']-exit['free'])<1e-8
    assert entry['seatLift']==0 and entry['seatY']==-.29 and entry['maxPalmError']<.005
    (args.output/'mediciones.json').write_text(json.dumps(reports, indent=2)+'\n')
    plate = Image.new('RGB', (612, 266), '#14191C')
    labels = ImageDraw.Draw(plate)
    for i, (key, caption) in enumerate([('before', 'Antes'), ('after', 'Después')]):
        x=8+i*303
        labels.text((x+2, 8), caption, fill='#F2F2ED')
        plate.paste(images[key], (x, 29))
    plate.save(args.output/'apoyo-en-la-acera.png', optimize=True)


if __name__=='__main__':
    main()
