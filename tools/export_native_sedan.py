"""Export the unoccupied production sedan in its closed, undamaged near or distant pose."""
import argparse
import json
import math
from pathlib import Path
import subprocess
import tempfile
import sys

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools/qa'))
from capture_vehicle_door import FIX, SETUP, launch_options

# Read only the buffers the renderer actually submits for this car.
CAPTURE = """distance => {
 const {r,sim,car}=doorScene, parts=[], geometry={};
 Object.assign(sim.player,{x:distance,z:0,car:null});Object.assign(car,{doorOpen:0,steerAngle:0,wheel:0,speed:0});
 r.currentSim=sim;r.currentTime=sim.time;
 r.add=function(list,key,x,y,z,w,h,d,color,mat=0,em=0,yaw=0,seed=0,detail=0,pitch=0,roll=0){
  parts.push({key,translation:[x,y,z],scale:[w,h,d],color,mat,em,yaw,pitch,roll});
 };
 try{r.renderCar(car);}finally{delete r.add;}
 const gl=r.gl, previous=gl.getParameter(gl.ARRAY_BUFFER_BINDING);
 try{
  for(const key of new Set(parts.map(p=>p.key))){
   const m=r.meshes[key], raw=new Uint8Array(m.count*32);
   gl.bindBuffer(gl.ARRAY_BUFFER,m.vbo);gl.getBufferSubData(gl.ARRAY_BUFFER,0,raw);
   let str='';for(let i=0;i<raw.length;i+=4096)str+=String.fromCharCode(...raw.subarray(i,i+4096));
   geometry[key]=btoa(str);
  }
 }finally{gl.bindBuffer(gl.ARRAY_BUFFER,previous);}
 if(gl.getError()||gl.isContextLost())throw Error('Could not read native wheel/car buffers');
 return {parts,geometry,source:distance>=66?'Distrito Cero / procedural distant sedan':DC.VehicleAsset.sourceProject,
         revision:distance>=66?DC.BuildInfo.version:DC.VehicleAsset.revision};
}"""


def capture(html, lod='near'):
    with sync_playwright() as pw, pw.chromium.launch(**launch_options()) as browser:
        page = browser.new_page(viewport={'width': 800, 'height': 500})
        raw = html.read_text()
        page.set_content(raw.replace('<script>', '<script>'+FIX, 1), timeout=180000)
        page.wait_for_function('!!window.DC_APP', timeout=180000)
        page.evaluate('DC_APP.renderer.humanReady')
        page.evaluate(SETUP)
        return page.evaluate(CAPTURE, 68 if lod=='far' else 2)


def shader_rotation(yaw, roll, pitch):
    """Quaternion for Ry(yaw) * Rz(roll) * Rx(pitch)."""
    sy, cy = math.sin(yaw/2), math.cos(yaw/2)
    sz, cz = math.sin(roll/2), math.cos(roll/2)
    sx, cx = math.sin(pitch/2), math.cos(pitch/2)
    return [cy*cz*sx+sy*sz*cx, sy*cz*cx+cy*sz*sx,
            cy*sz*cx-sy*cz*sx, cy*cz*cx-sy*sz*sx]


def assemble(native):
    nodes = [{'name': 'Distrito Cero | Sedan', 'children': [1],
              'extras': {'sourceProject': native['source'], 'sourceRevision': native['revision'],
                         'units': 'm', 'forward': '+Z', 'up': '+Y'}},
             {'name': 'Chassis', 'children': []}]
    parts = []
    corners = set()
    i = 0
    while i < len(native['parts']):
        part = native['parts'][i]
        distant_wheel = part['key'] == 'wheel' and part['mat'] == 4
        if part['key'] != 'tire' and not distant_wheel:
            part = dict(part, parent=1, rotation=shader_rotation(part['yaw'], part['roll'], part['pitch']),
                        material=part['mat'])
            parts.append(part)
            i += 1
            continue
        names = ['tire','rim','hub'] if distant_wheel else ['tire','rim','wheelBrake','wheelCaliper','wheelAlloy']
        assembly = native['parts'][i:i+len(names)]
        keys = ['wheel']*3 if distant_wheel else names
        if [p['key'] for p in assembly] != keys:
            raise ValueError('Unexpected native wheel components')
        pivot = part['translation']
        corner = ('Front' if pivot[2]>0 else 'Rear') + ('Left' if pivot[0]<0 else 'Right')
        if corner in corners:
            raise ValueError('Duplicate wheel pivot '+corner)
        corners.add(corner)
        upright, axle = len(nodes), len(nodes)+1
        nodes[0]['children'].append(upright)
        nodes.extend([{'name':'Steering_'+corner,'translation':pivot,'children':[axle]},
                      {'name':'Rolling_'+corner,'children':[]}])
        for p, name in zip(assembly, names, strict=True):
            parts.append(dict(p, material=p['mat'], name=corner+'_'+name,
                              parent=upright if p['key']=='wheelCaliper' else axle,
                              translation=[v-origin for v,origin in zip(p['translation'],pivot,strict=True)],
                              rotation=shader_rotation(p['yaw'],p['roll'],p['pitch'])))
        i += len(assembly)
    if len(corners)!=4 or len(parts)!=len(native['parts']):
        raise ValueError('Incomplete sedan assembly')
    return {'geometry':native['geometry'], 'nodes':nodes, 'parts':parts}


def export(native, output):
    with tempfile.TemporaryDirectory() as temporary:
        source = Path(temporary)/'sedan.json'
        source.write_text(json.dumps(assemble(native)))
        subprocess.run(['node', ROOT/'tools/vehicle_glb.cjs', source, output], check=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--html', type=Path, default=ROOT/'index.html')
    parser.add_argument('--lod', choices=['near','far'], default='near')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    export(capture(args.html, args.lod), args.output)
