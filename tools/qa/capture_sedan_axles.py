"""Compare both sedan wheel frames across the production LOD change at 66 m."""
import argparse
from hashlib import sha256
from io import BytesIO
import json
from math import dist
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

from capture_vehicle_door import FIX, SETUP, compare, launch_options


FRAME = """({distance, street, tilted}) => {
 const {r, sim, car, live, storage}=doorScene;
 Object.assign(sim.player,{x:-distance*Math.cos(.52),z:distance*Math.sin(.52)});
 Object.assign(car,{wheel:1.35, steerAngle:.44, yaw:0, boarding:false,
                    suspension:{pitch:tilted?.09:0,roll:tilted?-.065:0,kick:0}});
 r.camera.eye=street?[sim.player.x,2.4,sim.player.z]:[-2.66,.86,2.28];
 r.camera.target=street?[0,.78,0]:[-.92,.38,1.36];
 r.fovOverride=street?.66:.64;
 const draw=r.renderCar,add=r.add, wheels=[];
 r.renderCar=function(c){
  this.add=function(list,key,x,y,z,w,h,d,col,mat,em,yaw,seed,detail,pitch,roll){
   if(key==='tire'||(key==='wheel'&&mat===4)){
    wheels.push({center:[x,y,z],diameter:h,width:w,axle:[Math.cos(yaw)*Math.cos(roll||0),Math.sin(roll||0),-Math.sin(yaw)*Math.cos(roll||0)]});
   }
   return add.apply(this,arguments);
  };
  try{return draw.call(this,c);}finally{delete this.add;}
 };
 try{r.frame=0;r.lightTime=-1;r.lightVP=null;r.render(sim);r.gl.finish();}
 finally{delete r.renderCar;}
 if(wheels.length!==4||r.gl.getError()||JSON.stringify(DC_APP.sim.serialize())!==live||
   JSON.stringify([...qaCharacterStorage])!==storage)throw Error('Unexpected wheel count or state change');
 return wheels;
}"""


def capture(browser, html):
    raw=html.read_bytes()
    page=browser.new_page(viewport={'width':800,'height':500},device_scale_factor=1)
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.on('request',lambda r:errors.append(r.url) if r.url.startswith(('http:','https:')) else None)
    try:
        page.set_content(raw.decode().replace('<script>','<script>'+FIX,1),timeout=120000)
        page.wait_for_function('!!window.DC_APP',timeout=120000)
        page.evaluate(SETUP)
        report={'htmlSha256':sha256(raw).hexdigest(),'cases':{}}
        shots={}
        for pose,tilted in [('llano',False),('inclinado',True)]:
            for view,street in [('detalle',False),('distancia',True)]:
                for lod,distance in [('cerca',65.99),('lejos',66.01)]:
                    key=f'{pose}-{view}-{lod}'
                    report['cases'][key]=page.evaluate(FRAME,dict(distance=distance,street=street,tilted=tilted))
                    shots[key]=page.screenshot(timeout=60000)
        if errors: raise ValueError(errors)
        return report,shots
    finally:
        page.close()


def board(before,after,path):
    board=Image.new('RGB',(1162,875),'#101918')
    label=ImageDraw.Draw(board)
    large=ImageFont.truetype('DejaVuSans-Bold.ttf',30)
    small=ImageFont.truetype('DejaVuSans.ttf',19)
    label.text((22,15),'Sedán   /   Eje delantero al cambiar de distancia',font=large,fill='#f2f5ee')
    for j,(name,shots) in enumerate([('v0.20.30',before),('v0.20.31',after)]):
        left=22+j*573
        for i,(key,caption) in enumerate([('inclinado-detalle-lejos', 'Rueda delantera · inspección de la malla lejana'),
                                        ('inclinado-distancia-lejos','Cámara a 66 m · recorte ampliado 4×')]):
            im=Image.open(BytesIO(shots[key])).convert('RGB')
            if i: im=im.crop((330,207,470,296))
            im=im.resize((548,348),Image.Resampling.LANCZOS if not i else Image.Resampling.NEAREST)
            top=67+392*i
            label.text((left,top),f'{name}   {caption}',font=small,fill='#d7e5d9')
            board.paste(im,(left,top+31))
    board.save(path,quality=90)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for arg in ['before','after','output']:parser.add_argument('--'+arg,type=Path,required=True)
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    with sync_playwright() as pw,pw.chromium.launch(**launch_options()) as browser:
        a,old=capture(browser,args.before)
        b,new=capture(browser,args.after)
        report={'browser':browser.version,'before':a,'after':b,'maximumHubShiftMm':{},'pixels':{}}
    for pose in ['llano','inclinado']:
        for stage,data in [('before',a),('after',b)]:
            near,far=(data['cases'][f'{pose}-detalle-{lod}'] for lod in ['cerca','lejos'])
            shift=max(dist(i['center'],j['center']) for i,j in zip(near,far,strict=True))*1000
            report['maximumHubShiftMm'][f'{stage}-{pose}']=shift
            if stage=='after':
                assert shift<.001 and all(dist(i['axle'],j['axle'])<1e-7 and
                    i['diameter']==j['diameter'] for i,j in zip(near,far,strict=True))
            else: assert shift>50
        for key in (k for k in old if k.startswith(pose)):
            delta=compare(old[key],new[key])
            report['pixels'][key]=delta
            assert bool(delta['pixels'])==key.endswith('lejos'),(key,delta)
    board(old,new,args.output/'sedan.jpg')
    (args.output/'medidas.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['maximumHubShiftMm'])


if __name__=='__main__':
    main()
