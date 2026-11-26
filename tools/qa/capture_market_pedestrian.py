"""Trace the seeded Mercado resident from the simulation into street-view WebGL pixels.

Usage: DC_QA_BROWSER=/usr/bin/chromium python3 tools/qa/capture_market_pedestrian.py \
         --html index.html --output artifacts/market-pedestrian
"""
import argparse
import base64
from hashlib import sha256
from io import BytesIO
import json
import struct
from pathlib import Path
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tests'))
from character_benchmark import FIX
from qa_support import launch_options

SETUP = """async () => {
 const app=DC_APP;app.stopFrame();qaStopFrames();window.requestAnimationFrame=()=>0;
 const r=app.renderer,sim=new DC.Simulation(new DC.World(1337));
 sim.free=true;
 const marked=sim.peds.filter(p=>p.visualModel==='mercado-higgsfield');
 if(marked.length!==1)throw Error('Expected one seeded Mercado resident; got '+marked.length);
 const ped=marked[0],live=JSON.stringify(app.sim.serialize()),storage=JSON.stringify([...qaCharacterStorage]);
 await r.humanReady;
 if(!(await r.mercadoReady)||!(await r.marketPedReady))throw Error('Embedded maps are not ready');
 // Enter the parked starter car so that a real horn can later provoke the fallback.
 sim.interact('car');
 for(let i=0;sim.access&&i<720;i++)sim.step(1/60,{});
 if(sim.player.car!==0)throw Error('Starter vehicle access failed');
 const shop=sim.world.pois.find(p=>p.name==='Taller del Mercado');
 if(!shop||!sim.travel(shop.x,shop.z))throw Error('Travel to the workshop failed');
 if(ped.hidden||DC.distance(ped,sim.player)>=90)throw Error('Resident is not in the normal pedestrian drawing radius');
 r.world=sim.world;r.previewStudio=false;r.daylight=.83;r.rain=r.bloom=0;r.quality='balanced';
 r.resize();r.resetSectors();r.syncSectors(100);
 const settle=seconds=>{for(let i=0;i<Math.round(seconds*60);i++)sim.step(1/60,{});};
 window.marketQA={r,sim,ped,settle,live,storage};
 const gl=r.gl,ext=gl.getExtension('WEBGL_debug_renderer_info');
 return {seed:sim.world.seed,actor:ped.personId||ped.id,actorOrigin:[ped.x,ped.z],workshop:[shop.x,shop.z],
   webgl:gl.getParameter(gl.VERSION),renderer:ext?gl.getParameter(ext.UNMASKED_RENDERER_WEBGL):gl.getParameter(gl.RENDERER),
   canvas:[r.canvas.width,r.canvas.height]};
}"""

WALK = """() => {
 const {sim,ped}=marketQA,initial=[ped.x,ped.z];
 for(let i=0;i<480;i++){
   sim.step(1/60,{});
   if(ped.moveSpeed>.5 && Math.hypot(ped.x-initial[0],ped.z-initial[1])>.40)return;
 }
 throw Error('Resident never began walking from the stop');
}"""

HORN = """() => {
 const {sim,ped}=marketQA;
 for(let i=0;i<900 && DC.distance(ped,sim.player)>20;i++)sim.step(1/60,{throttle:.54});
 const range=DC.distance(ped,sim.player);
 if(range>22||ped.panic>.01)throw Error('Failed to reach a calm resident by car at '+range+' m');
 sim.interact('horn');sim.step(1/60,{});
 if(ped.panic<=0||sim.actor().horn<=0)throw Error('Vehicle horn did not startle the resident');
 return {range,horn:sim.actor().horn,panic:ped.panic};
}"""

DRAW = """({view,control}) => {
 const {r,sim,ped,live,storage}=marketQA,gl=r.gl;
 const delta=view==='far'?[5.6,1.65,23.7]:[2.55,1.36,2.20];
 const eye=[ped.x+delta[0],delta[1],ped.z+delta[2]],target=[ped.x,.95,ped.z];
 if(sim.world.blocked(eye[0],eye[2],.18)||!sim.world.visible(eye[0],eye[2],ped.x,ped.z))
   throw Error('Blocked pedestrian camera');
 Object.assign(r.camera,{eye,target,initialized:true});r.fovOverride=.63;
 const keyOf=new Map([0,1].map(i=>[r.meshes['marketPed'+i].vao,'marketPed'+i]));
 const state=()=>JSON.stringify({ped,save:sim.serialize()});
 const before=state(),parts=new Set(),otherCrowd=new Set(),calls=[];
 const bind=gl.bindVertexArray,draw=gl.drawArraysInstanced,indexed=gl.drawElementsInstanced;
 const person=r.renderPerson,add=r.add;
 let vao=null,inside=false,actorVisits=0;
 gl.bindVertexArray=function(v){vao=v;return bind.call(this,v);};
 function omit(vertices,instances){
   const key=keyOf.get(vao);
   if(!key)return false;
   const main=gl.getParameter(gl.DRAW_FRAMEBUFFER_BINDING)===r.scene.fb;
   calls.push({key,main,vertices,instances});
   return main && control==='without-model';
 }
 gl.drawArraysInstanced=function(mode,first,count,instances){
   if(!omit(count,instances))return draw.call(gl,mode,first,count,instances);
 };
 gl.drawElementsInstanced=function(mode,count,type,offset,instances){
   if(!omit(count,instances))return indexed.call(gl,mode,count,type,offset,instances);
 };
 r.renderPerson=function(p,...a){
   const previous=inside;inside=p===ped;if(inside)actorVisits++;
   try{return person.call(this,p,...a);}finally{inside=previous;}
 };
 r.add=function(list,mesh,...a){
   if(inside)parts.add(mesh);
   else if(r.meshes[mesh]?.crowd)otherCrowd.add(mesh);
   if((mesh==='marketPed0'||mesh==='marketPed1')&&!inside)throw Error('Special mesh assigned to another actor');
   return add.call(this,list,mesh,...a);
 };
 try {r.frame=0;r.lightTime=-1;r.lightVP=null;r.render(sim);gl.finish();}
 finally{gl.bindVertexArray=bind;gl.drawArraysInstanced=draw;gl.drawElementsInstanced=indexed;r.renderPerson=person;r.add=add;}
 if(gl.getError()||gl.isContextLost()||r.streamStats.pending)throw Error('Incomplete native WebGL frame');
 if(before!==state()||live!==JSON.stringify(DC_APP.sim.serialize())||storage!==JSON.stringify([...qaCharacterStorage]))
   throw Error('Rendering changed the resident, game state, or persistent storage');
 if(actorVisits!==1)throw Error('Expected one production renderPerson visit for the seeded resident; got '+actorVisits);
 const batch=Object.keys(r.dynamic).find(k=>keyOf.get(r.meshes[k]?.vao) && r.dynamic[k].length);
 if(!batch||r.dynamic[batch].length!==16)throw Error('Expected one native Mercado instance');
 const slot=r.dynamic[batch][15]-200,stride=DC.SkinRig.paletteStride;
 if(!Number.isInteger(slot)||slot<1||slot>=r.castCursor)throw Error('Invalid pose palette row');
 const pose=Array.from(r.posePixels.subarray(slot*stride,(slot+1)*stride));
 if(!pose.every(Number.isFinite))throw Error('Non-finite skin palette');
 if([...parts].some(k=>r.meshes[k]?.crowd&&!keyOf.has(r.meshes[k].vao))||!otherCrowd.size)
   throw Error('Duplicate cast body or missing unmarked crowd');
 const corners=[];
 for(const dx of [-.53,.53])for(const dy of [-.03,1.88])for(const dz of [-.42,.42]){
   const [x,y,z,w]=r.project(ped.x+dx,dy+(ped.groundY||0),ped.z+dz);
   if(w<=0||Math.abs(z)>=1)throw Error('Resident out of view');
   corners.push([(1+x)*r.canvas.width/2,(1-y)*r.canvas.height/2]);
 }
 return {png:r.canvas.toDataURL('image/png').split(',')[1],pose,calls,slot,otherCrowdMeshes:otherCrowd.size,parts:[...parts].sort(),actorVisits,
   time:sim.time,pos:[ped.x,ped.z],speed:ped.moveSpeed||0,phase:ped.phase,panic:ped.panic,yaw:ped.yaw,
   camera:eye,playerRange:DC.distance(ped,sim.player),roi:[Math.floor(Math.min(...corners.map(p=>p[0]))),
   Math.floor(Math.min(...corners.map(p=>p[1]))),Math.ceil(Math.max(...corners.map(p=>p[0]))),Math.ceil(Math.max(...corners.map(p=>p[1])))]};
}"""


def draw(page, view, control=None):
    frame=page.evaluate(DRAW, dict(view=view,control=control))
    pixels=base64.b64decode(frame.pop('png'))
    frame['sha256']=sha256(pixels).hexdigest()
    palette=frame.pop('pose')
    frame['poseSha256']=sha256(struct.pack('<'+'f'*len(palette),*palette)).hexdigest()
    return frame, Image.open(BytesIO(pixels)).convert('RGB')


def actor_mask(frame, present, absent):
    # Intersect a world-space body envelope with the actual raster. Very small
    # (<=4/255) color differences on antialiased edges are discarded.
    bounds=frame['roi']
    diff=ImageChops.difference(present.crop(bounds),absent.crop(bounds))
    red,green,blue=diff.split()
    mask=ImageChops.lighter(ImageChops.lighter(red,green),blue).point(lambda p:255 if p>4 else 0)
    area=mask.histogram()[255]
    if area < max(12,.025*mask.width*mask.height):
        raise RuntimeError(f'No substantial shaded silhouette at projected actor: {area} / {mask.size}')
    return mask, area


def sample(page, out, name, view='near', lod=0):
    frame,present=draw(page,view)
    control,absent=draw(page,view,'without-model')
    if any(frame[k]!=control[k] for k in ['time','roi','camera','pos','phase']):
        raise RuntimeError('The actor or camera moved between the test and control exposures')
    draws=[d for d in frame['calls'] if d['main']]
    if (len(draws)!=1 or draws[0]['key']!='marketPed'+str(lod) or draws[0]['instances']!=1
            or draws[0]['vertices']<=0):
        raise RuntimeError('Unexpected Mercado main-pass draw: '+str(draws))
    mask,pixels=actor_mask(frame,present,absent)
    present.save(out/(name+'.png'))
    if name=='idle':absent.save(out/'idle-control.png')
    frame['visibleActorPixels']=pixels
    frame['visibilityControlSha256']=control['sha256']
    return frame,present,mask


def motion(page, out, name):
    frames=[];trajectory=[]
    for _ in range(14):
        frame,image=draw(page,'near')
        trajectory.append({k:frame[k] for k in ['pos','phase','time','speed','poseSha256']})
        frames.append(image.resize((576,393),Image.Resampling.LANCZOS))
        page.evaluate('marketQA.settle(1/12)')
    if len({p['poseSha256'] for p in trajectory})!=len(frames):
        raise RuntimeError('A repeated pose interrupted '+name)
    frames[0].save(out/(name+'.webp'),save_all=True,append_images=frames[1:],duration=83,loop=0,quality=81,method=4)
    return trajectory


def capture(html, out):
    raw=html.read_bytes()
    report={'htmlSha256':sha256(raw).hexdigest(),'frames':{}}
    images={}
    with sync_playwright() as pw,pw.chromium.launch(**launch_options()) as browser:
        page=browser.new_page(viewport={'width':880,'height':600},device_scale_factor=1)
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
        page.on('request',lambda r:errors.append(r.url) if r.url.startswith(('https:','http:')) else None)
        page.set_content(raw.decode().replace('<script>','<script>'+FIX,1),timeout=120000)
        page.wait_for_function('!!window.DC_APP',timeout=120000)
        report['environment']=page.evaluate(SETUP)
        report['chromium']=browser.version
        # Warm shaders, static chunks, and the first crowd palette transfer.
        draw(page,'near')
        idle,images['idle'],_=sample(page,out,'idle')
        if idle['speed']>.01 or idle['panic']>0:raise RuntimeError('Expected a calm resident at rest')
        report['frames']['idle']=idle
        page.evaluate('marketQA.settle(.75)')
        rest,_=draw(page,'near')
        if rest['pos']!=idle['pos'] or rest['poseSha256']==idle['poseSha256']:
            raise RuntimeError('Idle breathing must update the skin palette without moving the resident')
        report['frames']['rest']=rest
        page.evaluate(WALK)
        walking,images['walk'],first=sample(page,out,'walk')
        report['frames']['walk']=walking
        page.evaluate('marketQA.settle(0.35)')
        stride,_,second=sample(page,out,'stride')
        if (walking['speed']<=.5 or stride['phase']==walking['phase'] or stride['pos']==walking['pos']
                or first.size!=second.size):
            raise RuntimeError('Walking must advance the resident and its game phase')
        changed=ImageChops.difference(first,second).histogram()[255]
        if changed<max(12,walking['visibleActorPixels']*.01):
            raise RuntimeError(f'Walking moves the transform but barely changes its silhouette ({changed} pixels)')
        report['strideMaskChangedPixels']=changed
        report['frames']['stride']=stride
        far,images['far'],_=sample(page,out,'far','far',1)
        far_draw=next(d for d in far['calls'] if d['main'])
        near_draw=next(d for d in stride['calls'] if d['main'])
        if far_draw['vertices']>=near_draw['vertices']:
            raise RuntimeError('Distant model should draw fewer vertices')
        report['frames']['far']=far
        walk_frames=motion(page,out,'marcha')
        report['horn']=page.evaluate(HORN)
        page.evaluate('marketQA.settle(.25)')
        alert,images['alert'],_=sample(page,out,'alert')
        if alert['speed']<=walking['speed'] or alert['panic']<=0:
            raise RuntimeError('Startled resident did not run')
        report['frames']['alert']=alert
        report['motion']={'marcha':walk_frames,'carrera':motion(page,out,'carrera')}
        if errors:raise RuntimeError(str(errors))
        report['errors']=errors
        page.close()
    return report,images


def gallery(out, images):
    w,h=576,393
    board=Image.new('RGB',(2*w,2*(h+39)), '#1a262a')
    canvas=ImageDraw.Draw(board)
    font=ImageFont.load_default(size=20)
    for i,(key,label) in enumerate([('idle','En la parada'),('walk','En marcha'),
                                    ('far','Desde la calle · LOD lejano'),('alert','Carrera tras el claxon')]):
        x,y=i%2*w,i//2*(h+39)
        board.paste(images[key].resize((w,h),Image.Resampling.LANCZOS),(x,y))
        canvas.text((x+12,y+h+8),label,fill='#f5eee2',font=font)
    board.save(out/'calle.jpg',quality=90,optimize=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--html',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    result,shots=capture(args.html,args.output)
    gallery(args.output,shots)
    (args.output/'report.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print('Verified real Mercado pedestrian, motion, both LODs and horn reaction.')
