"""Capture the Mercado at walking height, an approach, and a distant LOD in production WebGL2."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

from PIL import Image, ImageChops
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tests'))
from character_benchmark import FIX
from qa_support import launch_options

VIEWS = {
    'taller': ('taller', [-13,3.35,-6.2], [0,3.12,0], .68),
    'taller-puerta': ('taller', [-9.9,1.72,1.1], [0,2.25,0], .84),
    'marquesina': ('marquesina', [4.7,1.76,2.8], [0,1.29,0], .59),
    'marquesina-lateral': ('marquesina', [3.5,1.64,-3.3], [0,1.25,0], .68),
    'marquesina-lejos': ('marquesina', [1.8,1.65,-46], [0,1.32,0], .72),
}
SETUP = """async () => {
 const app=DC_APP;app.stopFrame();qaStopFrames();window.requestAnimationFrame=()=>0;
 const r=app.renderer, world=new DC.World(1337), sim=new DC.Simulation(world);
 await r.humanReady;if(r.mercadoReady&&!(await r.mercadoReady))throw Error('atlas');
 window.mercadoQA={r,sim,world};
 world.focus(0,0,1);r.world=world;r.previewStudio=false;r.daylight=.87;r.rain=0;r.bloom=0;r.quality='balanced';
 r.resize();r.resetSectors();r.syncSectors(25);
 sim.free=true;sim.time=1.25;sim.wanted=0;sim.player.car=null;sim.peds.forEach(p=>p.hidden=true);
 document.querySelectorAll('body > :not(canvas):not(script)').forEach(e=>e.style.display='none');
 const b=world.cell(2,1).buildings[0], shop=world.workshop||{x:b.x-b.w/2+8.5286/2,z:b.z-b.d/2+6.5325/2};
 return {taller:[shop.x,shop.z],marquesina:[-13.5,58]};
}"""
RENDER = """({site,eye,target,fov})=>{
 const {r,sim,world}=mercadoQA,at=q=>[q[0]+site[0],q[1],q[2]+site[1]];
 Object.assign(sim.player,{x:site[0]+16,z:site[1]+15});
 Object.assign(r.camera,{eye:at(eye),target:at(target),initialized:true});
 r.fovOverride=fov;r.frame=0;r.lightTime=-1;r.lightVP=null;r.render(sim);r.gl.finish();
 if(r.gl.isContextLost()||r.gl.getError())throw Error('WebGL');
 return Object.fromEntries(Object.keys(r.dynamic).filter(k=>/^(taller|marquesina)/.test(k)).map(k=>[k,r.dynamic[k].length/16]));
}"""


def capture(browser, html, out):
    page=browser.new_page(viewport={'width':900,'height':600},device_scale_factor=1)
    errors=[]
    page.on('pageerror',lambda e: errors.append(str(e)))
    page.on('request',lambda r: errors.append(r.url) if r.url.startswith(('http:', 'https:')) else None)
    try:
        raw=html.read_bytes()
        page.set_content(raw.decode().replace('<script>','<script>'+FIX,1),timeout=120000)
        page.wait_for_function('!!window.DC_APP',timeout=120000)
        sites=page.evaluate(SETUP)
        frames={}
        for name,(site,eye,target,fov) in VIEWS.items():
            lod=page.evaluate(RENDER,dict(site=sites[site],eye=eye,target=target,fov=fov))
            page.screenshot(path=str(out/(name+'.png')),timeout=30000)
            frames[name]={'site':sites[site],'eyeOffset':eye,'instances':lod}
        if errors:
            raise RuntimeError(str(errors))
        return {'htmlSha256':hashlib.sha256(raw).hexdigest(),'frames':frames}
    finally:
        page.close()


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for flag in ('before','after','output'):
        parser.add_argument('--'+flag,required=True,type=Path)
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    report={}
    with sync_playwright() as pw,pw.chromium.launch(**launch_options()) as browser:
        report['chromium']=browser.version
        for label,html in [('before',args.before),('after',args.after)]:
            out=args.output/label
            out.mkdir()
            report[label]=capture(browser,html,out)
    for name in VIEWS:
        a,b=[Image.open(args.output/l/(name+'.png')).convert('RGB') for l in ['before','after']]
        if not ImageChops.difference(a,b).getbbox():raise RuntimeError('No visual change in '+name)
    frames=report['after']['frames']
    assert frames['taller']['instances']['taller0']==1
    assert frames['marquesina']['instances']['marquesina0']>=1
    assert frames['marquesina-lejos']['instances']['marquesina0']==0
    (args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
