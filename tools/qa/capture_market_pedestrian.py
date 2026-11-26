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

BROKEN_ATLAS = """(()=>{
 const src=Object.getOwnPropertyDescriptor(HTMLImageElement.prototype,'src');
 window.qaMarketAtlasFaults=0;
 Object.defineProperty(HTMLImageElement.prototype,'src',{...src,set(value){
   if(value===window.DC?.MarketPedAsset?.atlas){
     window.qaMarketAtlasFaults++;return src.set.call(this,'data:image/webp;base64,AA==');
   }
   return src.set.call(this,value);
 }});
})();"""

SETUP = """async (missingAtlas=false) => {
 const app=DC_APP;app.stopFrame();qaStopFrames();window.requestAnimationFrame=()=>0;
 const r=app.renderer,sim=new DC.Simulation(new DC.World(1337));
 sim.free=true;
 const marked=sim.peds.filter(p=>p.visualModel==='mercado-higgsfield');
 if(marked.length!==1)throw Error('Expected one seeded Mercado resident; got '+marked.length);
 const ped=marked[0],live=JSON.stringify(app.sim.serialize()),storage=JSON.stringify([...qaCharacterStorage]);
 await r.humanReady;
 if(!(await r.mercadoReady)||Boolean(await r.marketPedReady)===Boolean(missingAtlas))throw Error('Unexpected embedded atlas state');
 if(!DC.MarketPedAsset.clips.Carrera)throw Error('Missing authored Carrera clip');
 // Reach the resident with the starter car and sound its horn during the test.
 sim.interact('car');
 for(let i=0;sim.access&&i<720;i++)sim.step(1/60,{});
 if(sim.player.car!==0)throw Error('Starter vehicle access failed');
 const shop=sim.world.pois.find(p=>p.name==='Taller del Mercado');
 if(!shop||!sim.travel(shop.x,shop.z))throw Error('Travel to the workshop failed');
 if(ped.hidden||DC.distance(ped,sim.player)>=90)throw Error('Resident is not in the normal pedestrian drawing radius');
 r.world=sim.world;r.previewStudio=false;r.daylight=.83;r.rain=r.bloom=0;r.quality='balanced';
 r.resize();r.resetSectors();r.syncSectors(100);
 const settle=seconds=>{for(let i=0;i<Math.round(seconds*60);i++)sim.step(1/60,{});};
 window.marketQA={r,sim,ped,settle,live,storage,vertexBuffers:new Map()};
 const gl=r.gl,ext=gl.getExtension('WEBGL_debug_renderer_info');
 return {seed:sim.world.seed,actor:ped.personId||ped.id,actorOrigin:[ped.x,ped.z],workshop:[shop.x,shop.z],
   webgl:gl.getParameter(gl.VERSION),renderer:ext?gl.getParameter(ext.UNMASKED_RENDERER_WEBGL):gl.getParameter(gl.RENDERER),
   clips:DC.MarketPedAsset.clips,canvas:[r.canvas.width,r.canvas.height]};
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

DRAW = """({view,control,measure,fallback}) => {
 const {r,sim,ped,live,storage}=marketQA,gl=r.gl;
 const delta=view==='far'?[5.6,1.65,23.7]:[2.55,1.36,2.20];
 const eye=view==='player'?r.camera.eye:[ped.x+delta[0],delta[1],ped.z+delta[2]],target=[ped.x,.95,ped.z];
 if(sim.world.blocked(eye[0],eye[2],.18)||!sim.world.visible(eye[0],eye[2],ped.x,ped.z))
   throw Error('Blocked pedestrian camera');
 if(view!=='player'){Object.assign(r.camera,{eye,target,initialized:true});r.fovOverride=.63;}
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
 if(fallback){
   const generic=[...parts].filter(k=>r.meshes[k]?.crowd&&!keyOf.has(r.meshes[k].vao));
   if(!generic.length||!otherCrowd.size||calls.length||window.qaMarketAtlasFaults!==1)
     throw Error('Unusable embedded atlas did not select the standard cast');
   return {actor:ped.personId,atlasDecodeFailures:window.qaMarketAtlasFaults,nativeDraws:calls.length,
           genericCrowdMeshes:generic.sort(),actorVisits,glError:gl.getError()};
 }
 const batch=Object.keys(r.dynamic).find(k=>keyOf.get(r.meshes[k]?.vao) && r.dynamic[k].length);
 if(!batch||r.dynamic[batch].length!==16)throw Error('Expected one native Mercado instance');
 const slot=r.dynamic[batch][15]-200,stride=DC.SkinRig.paletteStride;
 if(!Number.isInteger(slot)||slot<1||slot>=r.castCursor)throw Error('Invalid pose palette row');
 const pose=Array.from(r.posePixels.subarray(slot*stride,(slot+1)*stride));
 if(!pose.every(Number.isFinite))throw Error('Non-finite skin palette');
 if([...parts].some(k=>r.meshes[k]?.crowd&&!keyOf.has(r.meshes[k].vao))||!otherCrowd.size)
   throw Error('Duplicate cast body or missing unmarked crowd');
 let metrics;
 if(measure){
   const mesh=r.meshes[batch],vertices=marketQA.vertexBuffers;
   if(!vertices.has(batch)){
     const previous=gl.getParameter(gl.ARRAY_BUFFER_BINDING),data=new Float32Array(mesh.count*16);
     gl.bindBuffer(gl.ARRAY_BUFFER,mesh.vbo);gl.getBufferSubData(gl.ARRAY_BUFFER,0,data);
     gl.bindBuffer(gl.ARRAY_BUFFER,previous);vertices.set(batch,data);
     if(gl.getError())throw Error('Cannot read production vertex buffer');
   }
   const data=vertices.get(batch),inst=r.dynamic[batch];
   if(inst[12]||inst[13]||inst[14])throw Error('Expected an upright resident for the pavement measurement');
   let low=Infinity,high=-Infinity;
   for(let i=0;i<data.length;i+=16){
     let height=0;
     for(let k=0;k<4;k++){
       const j=16*data[i+8+k],weight=data[i+12+k];
       height+=weight*(pose[j+1]*data[i]+pose[j+5]*data[i+1]+pose[j+9]*data[i+2]+pose[j+13]);
     }
     height=inst[1]+height*inst[5]-(ped.groundY||0);
     low=Math.min(low,height);high=Math.max(high,height);
   }
   const work=new Float32Array(stride),phase=ped.phase/(Math.PI*2),idle=r.currentTime/DC.MarketPedAsset.clips.Reposo.duration;
   const clipError=(walk,run)=>{
     DC.MarketPedAsset.writePalette(work,phase,idle,walk,run);
     return Math.sqrt(work.reduce((sum,v,i)=>sum+(v-pose[i])**2,0)/stride);
   };
   metrics={heightAboveCurb:[low,high],paletteRms:{Reposo:clipError(0,0),Marcha:clipError(1,0),Carrera:clipError(1,1)}};
 }
 const corners=[];
 for(const dx of [-.53,.53])for(const dy of [-.03,1.88])for(const dz of [-.42,.42]){
   const [x,y,z,w]=r.project(ped.x+dx,dy+(ped.groundY||0),ped.z+dz);
   if(w<=0||Math.abs(z)>=1)throw Error('Resident out of view');
   corners.push([(1+x)*r.canvas.width/2,(1-y)*r.canvas.height/2]);
 }
 return {metrics,png:r.canvas.toDataURL('image/png').split(',')[1],pose,calls,slot,otherCrowdMeshes:otherCrowd.size,parts:[...parts].sort(),actorVisits,
   time:sim.time,pos:[ped.x,ped.z],speed:ped.moveSpeed||0,phase:ped.phase,panic:ped.panic,yaw:ped.yaw,
   camera:eye,playerRange:DC.distance(ped,sim.player),roi:[Math.max(0,Math.floor(Math.min(...corners.map(p=>p[0])))),
   Math.max(0,Math.floor(Math.min(...corners.map(p=>p[1])))),Math.min(r.canvas.width,Math.ceil(Math.max(...corners.map(p=>p[0])))),
   Math.min(r.canvas.height,Math.ceil(Math.max(...corners.map(p=>p[1]))))]};
}"""


def draw(page, view, control=None, measure=False):
    frame=page.evaluate(DRAW, dict(view=view,control=control,measure=measure))
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
    frame,present=draw(page,view,measure=True)
    control,absent=draw(page,view,'without-model')
    if any(frame[k]!=control[k] for k in ['time','roi','camera','pos','phase']):
        raise RuntimeError('The actor or camera moved between the test and control exposures')
    draws=[d for d in frame['calls'] if d['main']]
    if (len(draws)!=1 or draws[0]['key']!='marketPed'+str(lod) or draws[0]['instances']!=1
            or draws[0]['vertices']<=0):
        raise RuntimeError('Unexpected Mercado main-pass draw: '+str(draws))
    errors=frame['metrics']['paletteRms']
    nearest=min(errors,key=errors.get)
    expected={'idle':'Reposo','alert':'Carrera'}.get(name,'Marcha')
    if nearest!=expected or errors[expected]>=.04:
        raise RuntimeError(f'{name} skin matrices do not match {expected}: {errors}')
    sole,crown=frame['metrics']['heightAboveCurb']
    if not 1.60<crown<2.0 or (name!='alert' and abs(sole)>.02):
        raise RuntimeError(f'{name} mesh lies outside its expected curb contact or adult scale: {sole}, {crown}')
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


PLAYER_VIEW = """({approach,turnToResident}) => {
 const app=DC_APP,{r,storage}=marketQA;
 const original=JSON.stringify(app.sim.serialize()),sim=new DC.Simulation(new DC.World(1337));
 sim.free=true;
 const workshop=sim.world.pois.find(p=>p.name==='Taller del Mercado');
 if(!sim.travel(workshop.x,workshop.z))throw Error('Cannot travel to the Mercado on foot');
 const ped=sim.peds.find(p=>p.visualModel==='mercado-higgsfield'),p=sim.player;
 const start=[p.x,p.z];
 let steps=0;
 for(;steps<900;steps++){
   const dx=ped.x+approach[0]-p.x,dz=ped.z+approach[1]-p.z;
   if(Math.hypot(dx,dz)<.25)break;
   sim.step(1/60,{throttle:1,sprint:true,lookYaw:Math.atan2(dx,dz)});
 }
 if(steps>=900||p.car!==null)throw Error('The default on-foot approach did not reach the resident: '+[p.x,p.z,ped.x,ped.z]);
 if(turnToResident){
   for(let i=0;i<24;i++)sim.step(1/60,{throttle:.38,lookYaw:Math.atan2(ped.x-p.x,ped.z-p.z)});
 }
 for(let i=0;i<(turnToResident?16:24);i++)sim.step(1/60,{});
 r.world=sim.world;r.resize();r.resetSectors();r.syncSectors(100);
 const yaw=Math.atan2(ped.x-p.x,ped.z-p.z)-.39;
 Object.assign(r.camera,{yaw,pitch:.22,mode:0,initialized:false});
 r.updateCamera(sim,1/60,{});
 if(r.fovOverride!=null)throw Error('Gameplay camera must use the default FOV');
 if(JSON.stringify(app.sim.serialize())!==original)throw Error('Starting the street view changed the existing game');
 marketQA.contextOriginal={sim:app.sim,world:app.world,mode:app.mode,started:app.started,save:original};
 app.world=sim.world;app.sim=sim;app.started=true;app.setMode('play');app.updateUI(performance.now());
 Object.assign(marketQA,{sim,ped,live:JSON.stringify(sim.serialize())});
 if(document.getElementById('hud').hidden||JSON.stringify([...qaCharacterStorage])!==storage)throw Error('Unavailable HUD or changed storage');
 return {player:[p.x,p.z],resident:[ped.x,ped.z],start,approachSeconds:steps/60,yaw,
         camera:r.camera.eye,target:r.camera.target,fov:Math.PI*.36,mode:r.camera.mode};
}"""


def player_view(page, out, *, approach, turn_to_resident):
    page.set_viewport_size({'width':1280,'height':800})
    data=page.evaluate(PLAYER_VIEW,dict(approach=approach,turnToResident=turn_to_resident))
    frame,present=draw(page,'player')
    _,absent=draw(page,'player','without-model')
    _,area=actor_mask(frame,present,absent)
    draw(page,'player')
    page.screenshot(path=out,quality=89,type='jpeg',timeout=60000)
    page.evaluate('''() => {
      const app=DC_APP,{contextOriginal:old,storage}=marketQA;
      app.sim=old.sim;app.world=old.world;app.renderer.world=old.world;app.started=old.started;app.setMode(old.mode);
      if(JSON.stringify(app.sim.serialize())!==old.save||JSON.stringify([...qaCharacterStorage])!==storage)
        throw Error('The gameplay capture changed the original game or persistent storage');
    }''')
    data.update(visibleActorPixels=area,mainDraws=[d for d in frame['calls'] if d['main']])
    return data


def load_page(browser, document, errors, *, fault=''):
    page=browser.new_page(viewport={'width':880,'height':600},device_scale_factor=1)
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
    page.on('request',lambda r:errors.append(r.url) if r.url.startswith(('https:','http:')) else None)
    page.set_content(document.replace('<script>','<script>'+FIX+fault,1),timeout=120000)
    page.wait_for_function('!!window.DC_APP',timeout=120000)
    return page


def capture(html, out):
    raw=html.read_bytes()
    report={'htmlSha256':sha256(raw).hexdigest(),'frames':{}}
    images={}
    with sync_playwright() as pw,pw.chromium.launch(**launch_options()) as browser:
        errors=[]
        page=load_page(browser,raw.decode(),errors)
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
        report['gameplayViews']={
            'street':player_view(page,out/'jugando.jpg',approach=[5.8,7],turn_to_resident=True),
            'sidewalk':player_view(page,out/'acera-avatar.jpg',approach=[1.4,3.2],turn_to_resident=False),
        }
        page.close()
        # Exercise the actual image decoder's error path with only the resident atlas damaged.
        fallback_page=load_page(browser,raw.decode(),errors,fault=BROKEN_ATLAS)
        fallback_page.evaluate(SETUP,True)
        report['fallback']=fallback_page.evaluate(DRAW,dict(view='near',fallback=True))
        fallback_page.close()
        if errors:raise RuntimeError(str(errors))
        report['errors']=errors
    return report,images


def visibility_plate(out, bounds):
    # The two source images differ only in the main-pass draw of the resident.
    present=Image.open(out/'idle.png').convert('RGB')
    absent=Image.open(out/'idle-control.png').convert('RGB')
    mask,_=actor_mask({'roi':bounds},present,absent)
    panels=[('Dibujo normal',present.crop(bounds)),('Control',absent.crop(bounds)),
            ('Píxeles del residente',mask.convert('RGB'))]
    w,h=panels[0][1].size
    board=Image.new('RGB',(3*w,h+40),'#1a262a')
    canvas=ImageDraw.Draw(board)
    font=ImageFont.load_default(size=19)
    for i,(label,panel) in enumerate(panels):
        board.paste(panel,(i*w,0))
        canvas.text((i*w+10,h+9),label,fill='#f5eee2',font=font)
    board.save(out/'control.jpg',quality=90,optimize=True)


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
    visibility_plate(args.output,result['frames']['idle']['roi'])
    (args.output/'report.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print('Verified real Mercado pedestrian, motion, both LODs and horn reaction.')
