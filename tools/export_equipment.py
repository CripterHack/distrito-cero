#!/usr/bin/env python3
"""Export original native fictional props to portable GLB. No runtime dependency.
Local origin is the equipment mount, Y up and +Z forward. Gallery root translations
are for inspection, not physical weapon dimensions for fabrication.
"""
from pathlib import Path
import json,struct,subprocess
R=Path(__file__).resolve().parents[1]
code="""const fs=require('fs'),vm=require('vm');for(const n of ['core','equipment','equipment-geometry'])vm.runInThisContext(fs.readFileSync('src/'+n+'.js','utf8'));console.log(JSON.stringify(DC.Equipment.catalog.filter(w=>w.kind!=='none').map(w=>({id:w.id,name:w.name,parts:DC.EquipmentGeometry.build(w.id).map(p=>({...p,data:Array.from(p.data)}))}))));"""
objects=json.loads(subprocess.check_output(['node','-e',code],cwd=R));g={'asset':{'version':'2.0','generator':'Distrito Cero original offline equipment exporter v0.17','copyright':'Original fictional game geometry. No engineering or fabrication specification.'},'scene':0,'scenes':[{'name':'Arsenal gallery','nodes':[]}],'nodes':[],'meshes':[],'materials':[],'accessors':[],'bufferViews':[],'buffers':[]};buf=bytearray();material_cache={}
for i,obj in enumerate(objects):
 root=len(g['nodes']);g['scenes'][0]['nodes'].append(root);g['nodes'].append({'name':obj['id'],'translation':[(i%4)*1.35,0,(i//4)*1.45],'children':[],'extras':{'label':obj['name'],'mountConvention':'Y-up, +Z-forward, mount local origin'}})
 for part in obj['parts']:
  values=part['data'];key=(part['material'],tuple(part['color']))
  if key not in material_cache:
   mat={'name':str(part['material'])+'_'+str(len(g['materials'])),'pbrMetallicRoughness':{'baseColorFactor':part['color']+[1],'metallicFactor':.7 if part['material']==3 else .05,'roughnessFactor':.34 if part['material']==3 else .68},'doubleSided':True}
   if part['material']==0:mat['emissiveFactor']=part['color']
   material_cache[key]=len(g['materials']);g['materials'].append(mat)
  v=len(g['bufferViews']);offset=len(buf);packed=struct.pack('<'+'f'*len(values),*values);buf.extend(packed);g['bufferViews'].append({'buffer':0,'byteOffset':offset,'byteLength':len(packed),'byteStride':32,'target':34962});count=len(values)//8;accessors={}
  for name,start,typ in [('POSITION',0,'VEC3'),('NORMAL',12,'VEC3'),('TEXCOORD_0',24,'VEC2')]:
   a={'bufferView':v,'byteOffset':start,'componentType':5126,'count':count,'type':typ}
   if name=='POSITION':a.update({'min':[min(values[j::8])for j in range(3)],'max':[max(values[j::8])for j in range(3)]})
   accessors[name]=len(g['accessors']);g['accessors'].append(a)
  mesh=len(g['meshes']);g['meshes'].append({'name':obj['id']+'_'+part['name'],'primitives':[{'attributes':accessors,'material':material_cache[key],'mode':4}]});g['nodes'][root]['children'].append(len(g['nodes']));g['nodes'].append({'name':obj['id']+'_'+part['name'],'mesh':mesh})
g['buffers']=[{'byteLength':len(buf)}];header=json.dumps(g,separators=(',',':'),ensure_ascii=True).encode();header+=b' '*((-len(header))%4);buf+=b'\x00'*((-len(buf))%4);out=struct.pack('<4sII',b'glTF',2,28+len(header)+len(buf))+struct.pack('<I4s',len(header),b'JSON')+header+struct.pack('<I4s',len(buf),b'BIN\0')+buf;(R/'assets/dc017-equipment.glb').write_bytes(out);print(json.dumps({'bytes':len(out),'equipment':len(objects),'meshes':len(g['meshes']),'triangles':sum(len(p['data'])//24 for o in objects for p in o['parts'])}))
