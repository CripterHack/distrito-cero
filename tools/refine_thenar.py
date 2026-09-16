#!/usr/bin/env python3
"""Bounded authoring corrective for the volar thenar pad of the native avatar.
Source rows are preserved in a sparse canonical seed. Skin weights, rig, UV and
connectivity are unchanged. Normals use the inverse-transpose of the same smooth
map as positions; no per-frame corrective, collider inflation or new library.
"""
from pathlib import Path
import argparse,base64,hashlib,json,math,struct,zlib
ROOT=Path(__file__).resolve().parents[1]
ROW=struct.Struct('<3h3h2H4B4B')
AMOUNT=.004

def smooth(a,b,x):
    t=max(0.,min(1.,(x-a)/(b-a)))
    return t*t*(3-2*t),6*t*(1-t)/(b-a) if a<x<b else 0.

def field(point):
    x,y,z=point;side=1 if x>0 else -1;depth=(side*.2637-x)*side
    if abs(x-side*.2637)>=.055:return 0.,(0.,0.,0.),side
    ya,da=smooth(.817,.832,y);yb,db=smooth(.857,.883,y)
    za,dc=smooth(-.012,.003,z);zb,dd=smooth(.028,.054,z)
    volar,dv=smooth(.003,.016,depth)
    yy=ya*(1-yb);zz=za*(1-zb)
    f=AMOUNT*yy*zz*volar
    # Preserve the measured palmar contact patch, not only its abstract target.
    # The first contour candidate moved it and was rejected by palm-surface tests.
    radial=math.hypot(y-.836,z);pin,dp=smooth(.0025,.006,radial)
    py=dp*(y-.836)/radial if radial else 0.;pz=dp*z/radial if radial else 0.
    return f*pin,(-side*AMOUNT*yy*zz*dv*pin,AMOUNT*(da*(1-yb)-ya*db)*zz*volar*pin+f*py,AMOUNT*yy*(dc*(1-zb)-za*dd)*volar*pin+f*pz),side

def deform(point,normal):
    f,(dx,dy,dz),side=field(point)
    if not f:return list(point),list(normal)
    # J = [A B C; 0 1 0; 0 0 1]. A >= 1 - .004*1.5/.013 > .538.
    # Thus the corrective cannot invert the bind-space surface.
    A=1+side*dx;B=side*dy;C=side*dz
    if A<=.53:raise ValueError('Corrective is not orientation preserving')
    nx=normal[0]/A;n=[nx,normal[1]-B*nx,normal[2]-C*nx];length=math.sqrt(sum(v*v for v in n))
    if not math.isfinite(length) or length<1e-12:raise ValueError('Invalid canonical normal')
    return [point[0]+side*f,point[1],point[2]],[v/length for v in n]

def rounded(value):
    return int(math.floor(value+.5)) if value>=0 else -int(math.floor(-value+.5))

def corrected(row):
    p=[v/10000 for v in row[:3]];n=[v/32767 for v in row[3:6]];point,normal=deform(p,n)
    if point==p:return row
    return tuple(rounded(v*10000)for v in point)+tuple(max(-32767,min(32767,rounded(v*32767)))for v in normal)+row[6:]

def refine(source,seed=None):
    text=source.decode('utf-8');header,payload=text.split('DC.HeroAsset=',1);data=json.loads(payload.strip().rstrip(';'))
    seed=seed or json.loads((ROOT/'assets/thenar-contour-source.json').read_text())
    if seed.get('schema')!=1 or seed.get('recordStride')!=28 or seed.get('part')!='skin':raise ValueError('Unsupported contour seed')
    if data['bones']!=seed['bones'] or len(data['bones'])!=49 or data['stride']!=24:raise ValueError('Rig contract changed')
    part=next(p for p in data['parts']if p['name']=='skin');raw=bytearray(base64.b64decode(part['data'],validate=True))
    if len(raw)!=seed['vertices']*24 or part['vertices']!=seed['vertices']:raise ValueError('Canonical skin vertex count changed')
    expected=seed['recordCount']*28
    if not 0<expected<=len(raw)*28//24:raise ValueError('Invalid seed size')
    decoder=zlib.decompressobj();rows=decoder.decompress(base64.b64decode(seed['recordsZlibBase64'],validate=True),expected+1)
    if len(rows)!=expected or not decoder.eof or decoder.unused_data:raise ValueError('Invalid bounded seed payload')
    original=bytearray(raw);changes=[];seen=set()
    for start in range(0,len(rows),28):
        index=struct.unpack_from('<I',rows,start)[0];old=rows[start+4:start+28]
        if index in seen or index>=part['vertices']:raise ValueError('Invalid or repeated seed index')
        seen.add(index);row=ROW.unpack(old);result=ROW.pack(*corrected(row));current=bytes(raw[index*24:(index+1)*24])
        if current not in(old,result):raise ValueError('Conflicting contour authoring at corner '+str(index))
        original[index*24:(index+1)*24]=old;changes.append((index,old,result))
    if hashlib.sha256(original).hexdigest()!=seed['partSha256']:raise ValueError('Canonical skin changed outside the corrective; review seed')
    changed=0;positions=set();maximum=0
    for index,old,result in changes:
        raw[index*24:(index+1)*24]=result
        if old!=result:
            changed+=1;positions.add(old[:6]);maximum=max(maximum,abs(ROW.unpack(old)[0]-ROW.unpack(result)[0])/10000)
    part['data']=base64.b64encode(raw).decode();data['thenarContour']={'version':1,'maxBindDisplacementMetres':AMOUNT,'source':'assets/thenar-contour-source.json'}
    output=(header+'DC.HeroAsset='+json.dumps(data,separators=(',',':'))+';\n').encode()
    return output,{'changedCorners':changed,'affectedBindPositions':len(positions),'maxPositionDeltaMetres':maximum,'preserved':'UVs, weights, topology, rig, nails, other material parts'}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');p.add_argument('--source',type=Path,default=ROOT/'src/hero-asset.js');a=p.parse_args()
    original=a.source.read_bytes();out,report=refine(original);report.update(inputSha256=hashlib.sha256(original).hexdigest(),outputSha256=hashlib.sha256(out).hexdigest());print(json.dumps(report,indent=2))
    if a.check:
        if original!=out:raise SystemExit('Thenar contour must be regenerated')
    else:a.source.write_bytes(out)
if __name__=='__main__':main()
