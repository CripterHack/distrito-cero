"""Export the street-facing Mercado shopfront from the standalone game's WebGL buffers."""
import argparse
import base64
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/qa'))
from capture_street_architecture import DRAW, FIX, SETUP, launch_options

# Observe which contiguous static instances were appended by this storefront.
CALL = "buildCornerShop(shop,add,(...args)=>this.add(detail,'box',...args),color);"
OBSERVE = """
const shopStart = {box: lists.box.length, smoke: lists.smoke.length};
""" + CALL + """
if(c.ix===1 && c.iz===2)window.shopTrace={shop,chunk:chunk.key,near:detail.box,
 spans:Object.fromEntries(['box','smoke'].map(k=>[k,[shopStart[k],lists[k].length-shopStart[k]]]))};
"""
READ = """() => {
 const {r,sim}=archScene, gl=r.gl, tr=window.shopTrace;
 if(!tr || sim.world.seed!==1337 || gl.isContextLost())throw Error('Missing the seed-1337 Mercado storefront');
 const sector=r.sectorGPU.get(tr.chunk), meshes={}, parts={};
 const bytes=b=>{let s='';for(let i=0;i<b.length;i+=4096)s+=String.fromCharCode(...b.subarray(i,i+4096));return btoa(s)};
 function read(buffer,floatOffset,length){
   gl.bindBuffer(gl.ARRAY_BUFFER,buffer);
   const data=new Float32Array(length);gl.getBufferSubData(gl.ARRAY_BUFFER,floatOffset*4,data);return data;
 }
 function rows(data,x,z) {
   const out=[];
   for(let i=0;i<data.length;i+=16){const v=Array.from(data.slice(i,i+16));v[0]+=x;v[2]+=z;out.push(v)}
   return out;
 }
 const previous=gl.getParameter(gl.ARRAY_BUFFER_BINDING), previousFbo=gl.getParameter(gl.READ_FRAMEBUFFER_BINDING);
 const fb=gl.createFramebuffer();
 try{
   for(const [key,[start,length]] of Object.entries(tr.spans)){
    const b=sector[key],m=r.meshes[key];parts[key]=rows(read(b.buffer,start,length),b.baseX,b.baseZ);
    gl.bindBuffer(gl.ARRAY_BUFFER,m.vbo);const data=new Uint8Array(m.count*32);
    gl.getBufferSubData(gl.ARRAY_BUFFER,0,data);meshes[key]=bytes(data);
   }
   const m=r.meshes.box, origin=r.renderOrigin;
   const dynamic=rows(read(m.dynamicBuffer,0,m.dynamicCount*16),origin[0],origin[1]);
   parts.near=rows(tr.near,0,0).map(expected=>{
    const matches=dynamic.filter(v=>v.every((x,i)=>Math.abs(x-expected[i])<.00005));
    if(matches.length!==1)throw Error('Missing or ambiguous GPU storefront detail');return matches[0];
   });
   const signs=parts.box.filter(v=>v[7]>=10 && v[7]<26);
   if(signs.length!==1)throw Error('Expected one shop sign');
   const idx=signs[0][7]-10,pixels=new Uint8Array(512*256*4);
   gl.bindFramebuffer(gl.READ_FRAMEBUFFER,fb);
   gl.framebufferTexture2D(gl.READ_FRAMEBUFFER,gl.COLOR_ATTACHMENT0,gl.TEXTURE_2D,r.signs,0);
   if(gl.checkFramebufferStatus(gl.READ_FRAMEBUFFER)!==gl.FRAMEBUFFER_COMPLETE)throw Error('Unreadable sign atlas');
   gl.readPixels((idx%4)*512,(3-Math.floor(idx/4))*256,512,256,gl.RGBA,gl.UNSIGNED_BYTE,pixels);
   if(gl.getError()!==gl.NO_ERROR)throw Error('Could not read Mercado shop GPU resources');
   return {parts,meshes,sign:bytes(pixels),shop:tr.shop,version:DC.BuildInfo.version};
 }finally{gl.bindFramebuffer(gl.READ_FRAMEBUFFER,previousFbo);gl.deleteFramebuffer(fb);gl.bindBuffer(gl.ARRAY_BUFFER,previous)}
}"""


def capture(html):
    data = html.read_bytes()
    source = data.decode()
    if source.count(CALL) != 1:
        raise ValueError('Expected one buildCornerShop call in the standalone game')
    with sync_playwright() as pw, pw.chromium.launch(**launch_options()) as browser:
        page = browser.new_page(viewport={'width': 768, 'height': 480})
        page.set_content(source.replace(CALL, OBSERVE).replace('<script>', '<script>' + FIX, 1), timeout=180000)
        page.wait_for_function('!!window.DC_APP', timeout=180000)
        page.evaluate(SETUP)
        page.evaluate(DRAW, [[148.5, 1.8, 176.7], [146.5, 1.55, 185.8]])
        result = page.evaluate(READ)
    image = Image.frombytes('RGBA', (512, 256), base64.b64decode(result['sign']))
    encoded = io.BytesIO()
    image.transpose(Image.Transpose.FLIP_TOP_BOTTOM).convert('RGB').save(encoded, format='PNG')
    result.update(sign=base64.b64encode(encoded.getvalue()).decode(), sha256=hashlib.sha256(data).hexdigest())
    return result


def export(html, output):
    output.parent.mkdir(exist_ok=True, parents=True)
    with tempfile.TemporaryDirectory() as temp:
        payload = Path(temp) / 'native.json'
        payload.write_text(json.dumps(capture(html)))
        subprocess.run(['node', ROOT / 'tools/shop_glb.cjs', payload, output], check=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--html', type=Path, default=ROOT / 'index.html')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    export(args.html, args.output)
