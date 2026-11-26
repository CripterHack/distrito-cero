#!/usr/bin/env python3
"""Native cervical seam QA: six neutral LOD views plus ten controlled neck poses.

Shares the canonical character fixture, cameras and capture implementation. Geometry
is read back from the actual face VBO and native vertex shader transform feedback.
Prepared software-rendered samples do not measure FPS or certify artistic quality.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import copy
import gzip
import hashlib
import json
import math
import struct
import subprocess
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from tools.qa import render_native_neck as base
from playwright.sync_api import sync_playwright

PIXEL=(362,470)
ENVELOPE_PIXELS=[(x,y) for y in (460,470,480) for x in (352,362,372)]
CONTRACT='native-lod-posterior-seam-v1'

def selections(matrix):
    reference=base.cases(matrix)
    cases=[copy.deepcopy(next(c for c in reference if c['pose']=='idle' and c['light']=='neutral'
        and c['camera']==view and c['bodyGeometryLOD']==lod)) for view in ('back','profile') for lod in (0,1,2)]
    for i in range(10):
        c=copy.deepcopy(next(c for c in reference if c['pose']=='neck' and c['light']=='neutral' and c['camera']=='back'))
        phase=i/9;wave=math.sin(phase*math.pi*2)
        c.update(id='neck-sequence-'+str(i).zfill(2),bodyGeometryLOD=2,time=matrix['time']+phase*.9)
        c['sample']['actor'].update(lookYaw=.62*wave,lookPitch=.14*math.sin(phase*math.pi),lookRoll=.03*wave)
        c['sample']['label']='Controlled neck pose '+str(i+1)+'/10'
        c['sequence']={'index':i,'phase':phase,'controlledPose':True,'continuousSimulation':False}
        cases.append(c)
    return cases

def posterior(point):
    x,y,z=point
    return abs(x)<.035 and 1.455<y<1.635 and z<-.02

def boundary_metrics(rest,world):
    """Weld by exact rest position, then select region; no alternate reducer."""
    rest=np.asarray(rest,dtype=np.float64).reshape(-1,3)
    world=np.asarray(world,dtype=np.float64).reshape(-1,3)
    if rest.shape!=world.shape or len(rest)%3 or not np.isfinite(rest).all() or not np.isfinite(world).all():
        raise ValueError('Invalid native triangle stream')
    edges={}
    welded={}
    for i,p in enumerate(rest):
        key=tuple(p);welded.setdefault(key,[]).append(i)
    for i in range(0,len(rest),3):
        for a,b in ((i,i+1),(i+1,i+2),(i+2,i)):
            key=tuple(sorted((tuple(rest[a]),tuple(rest[b]))))
            edges.setdefault(key,[]).append((a,b))
    boundaries=[]
    for key,uses in edges.items():
        if len(uses)==1 and all(posterior(p) for p in key):
            a,b=uses[0];boundaries.append({'rest':[rest[a].tolist(),rest[b].tolist()],
                'world':[world[a].tolist(),world[b].tolist()]})
    # Shared rest vertices in this band must stay coincident after real GPU DQ.
    spread=0.;groups=0
    for p,indices in welded.items():
        if len(indices)>1 and posterior(p):
            groups+=1;points=world[indices];spread=max(spread,float(np.linalg.norm(points-points[0],axis=1).max()))
    return {'posteriorBoundaryEdges':len(boundaries),'boundaries':boundaries,
        'sharedPosteriorRestPositions':groups,'maxSharedWorldSpreadM':spread,'triangles':len(rest)//3}

def ray_hit(world,camera,pixel):
    """Double-sided Möller–Trumbore; return camera-space depth and facing."""
    tri=np.asarray(world,dtype=np.float64).reshape(-1,3,3)
    if not np.isfinite(tri).all():raise ValueError('Nonfinite world geometry')
    eye=np.asarray(camera['eye'],dtype=np.float64);forward=np.asarray(camera['target'],dtype=np.float64)-eye;forward/=np.linalg.norm(forward)
    right=np.cross(forward,[0,1,0]);right/=np.linalg.norm(right);up=np.cross(right,forward)
    scale=720/(2*math.tan(camera['fov']/2));x,y=pixel
    direction=forward+right*((x+.5-360)/scale)-up*((y+.5-360)/scale)
    e1=tri[:,1]-tri[:,0];e2=tri[:,2]-tri[:,0];h=np.cross(direction,e2);det=np.einsum('ij,ij->i',e1,h)
    s=eye-tri[:,0]
    with np.errstate(divide='ignore',invalid='ignore'):
        u=np.einsum('ij,ij->i',s,h)/det;q=np.cross(s,e1);v=q@direction/det;t=np.einsum('ij,ij->i',e2,q)/det
    valid=(abs(det)>1e-12)&(u>=0)&(v>=0)&(u+v<=1)&(t>.15)
    candidates=np.where(valid,t,np.inf);i=int(np.argmin(candidates)) if len(tri) else 0
    if not len(tri) or not np.isfinite(candidates[i]):return None
    return {'pixel':list(pixel),'triangle':i,'depthM':float(t[i]),'frontFacing':bool(det[i]>0)}

def geometric_acceptance(captures,envelope):
    checks=[{'name':'No posterior seam boundary edges: '+c['id'],
             'pass':c['geometry']['posteriorBoundaryEdges']==0} for c in captures]
    checks.extend({'name':'Shared native vertices remain coincident: '+c['id'],
                   'pass':c['geometry']['maxSharedWorldSpreadM']==0} for c in captures)
    sample=next(c for c in captures if c['case']['pose']=='idle' and c['case']['camera']=='back' and c['case']['bodyGeometryLOD']==2)
    ray=sample['exteriorRay'];checks.append({'name':'LOD2 posterior ray hits exterior within fixed LOD0 envelope',
        'pass':bool(ray and ray['frontFacing'] and envelope['minDepthM']<=ray['depthM']<=envelope['maxDepthM'])})
    return checks

def validate_reference(reference,inputs,planned):
    """Require the preserved capture contract, including a failed geometric RED."""
    def require(ok,message):
        if not ok:raise ValueError('Invalid reference: '+message)
    def number(value):
        return type(value) in (int,float) and math.isfinite(value)
    def sha(value):
        return isinstance(value,str) and len(value)==64 and all(c in '0123456789abcdef' for c in value)
    require(isinstance(reference,dict),'expected an object')
    require(type(reference.get('schema')) is int and reference['schema']==1,'schema')
    require(reference.get('contract')==CONTRACT and reference.get('captureStatus')=='passed','completed capture contract')
    require(reference.get('cameraContract')==base.CAMERA and reference.get('viewport')==base.VIEWPORT,'camera/viewport contract')
    hashes=reference.get('inputHashes')
    require(isinstance(hashes,dict) and all(sha(hashes.get(k)) for k in inputs),'input SHA256 hashes')
    require(all(hashes[k]==inputs[k] for k in ('stage','matrix','sharedHelper','fixture','tool')),'fixture/helper hashes differ')
    require(reference.get('errors')==[] and reference.get('requests')==[],'capture errors or external requests')
    checks=reference.get('captureChecks')
    require(isinstance(checks,list) and bool(checks) and all(isinstance(c,dict) and
        isinstance(c.get('name'),str) and bool(c['name']) and c.get('pass') is True for c in checks),'capture checks')
    captures=reference.get('captures')
    require(isinstance(captures,list) and len(captures)==len(planned),'capture count')
    for capture,case in zip(captures,planned):
        require(isinstance(capture,dict) and capture.get('id')==case['id'] and capture.get('case')==case,'capture IDs/scenarios')
        require(sha(capture.get('imageSha256')),'image SHA256')
        metrics=capture.get('metrics');camera=metrics.get('camera') if isinstance(metrics,dict) else None
        require(isinstance(camera,dict) and all(isinstance(camera.get(k),list) and len(camera[k])==3
            and all(number(v) for v in camera[k]) for k in ('eye','target'))
            and number(camera.get('fov')) and 0<camera['fov']<math.pi,'capture camera')
    envelope=reference.get('exteriorEnvelope')
    require(isinstance(envelope,dict) and all(number(envelope.get(k)) for k in ('minDepthM','maxDepthM'))
        and .15<envelope['minDepthM']<=envelope['maxDepthM'],'exterior envelope bounds')
    rays=envelope.get('rays')
    require(isinstance(rays,list) and len(rays)==len(ENVELOPE_PIXELS),'exterior envelope ray count')
    for ray,pixel in zip(rays,ENVELOPE_PIXELS):
        require(isinstance(ray,dict) and ray.get('pixel')==list(pixel) and ray.get('frontFacing') is True
            and type(ray.get('triangle')) is int and ray['triangle']>=0 and number(ray.get('depthM'))
            and envelope['minDepthM']<=ray['depthM']<=envelope['maxDepthM'],'exterior envelope ray')
    require(envelope['minDepthM']==min(r['depthM'] for r in rays)
        and envelope['maxDepthM']==max(r['depthM'] for r in rays),'exterior envelope does not match rays')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--html',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--label',required=True);parser.add_argument('--browser',type=Path)
    parser.add_argument('--reference',type=Path,help='Preserved baseline report; fixes the LOD0 depth envelope and compares neutral LOD0/1 pixel hashes.')
    args=parser.parse_args();html=args.html.resolve();out=args.output.resolve()
    artifacts=ROOT/'artifacts'
    if not html.is_file():parser.error('HTML input does not exist.')
    if not out.is_relative_to(artifacts) or out==artifacts or artifacts.resolve()!=artifacts:parser.error('Output must be a fresh repository artifacts child.')
    if out.exists():parser.error('Output exists; preserve previous evidence and select a fresh directory.')
    matrix_path=ROOT/'tests/benchmarks/characters.json';stage=ROOT/'tools/qa/character_stage.js'
    inputs={name:base.digest(path) for name,path in {'html':html,'stage':stage,'matrix':matrix_path,
        'sharedHelper':Path(base.__file__),'fixture':ROOT/'tests/character_benchmark.py','tool':Path(__file__)}.items()}
    matrix=base.load_matrix(matrix_path);cases=selections(matrix)
    reference=None;reference_sha=None;reference_path=args.reference.resolve() if args.reference is not None else None
    if reference_path is not None:
        try:
            reference_bytes=reference_path.read_bytes()
            reference=json.loads(reference_bytes)
            reference_sha=hashlib.sha256(reference_bytes).hexdigest()
            validate_reference(reference,inputs,cases)
        except (OSError,UnicodeError,ValueError) as error:parser.error(str(error))
    out.mkdir(parents=True);(out/'images').mkdir();(out/'geometry').mkdir()
    report={'schema':1,'contract':CONTRACT,'label':args.label,'captureStatus':'running','geometricStatus':'pending',
        'startedUtc':datetime.now(timezone.utc).isoformat(),'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'inputHashes':inputs,'cameraContract':base.CAMERA,'viewport':base.VIEWPORT,'captures':[],
        'errors':[],'requests':[],'captureChecks':[],'geometricChecks':[],
        'referenceReportSha256':reference_sha,
        'posteriorRestRegion':'abs(x)<.035 && y>1.455 && y<1.635 && z<-.02, both endpoints; edge incidence1 after exact position weld; UV ignored',
        'scenario':'Six neutral body LOD0/1/2 back/profile views plus ten independently prepared controlled neck poses in LOD2/back. Canonical native renderer, DQ and material shaders unchanged.',
        'limitations':['Forced body geometry with LOD0 groom; not chooseLOD/distance behavior.','Ten controlled poses reset fixture between samples; not continuous simulation or a playthrough.',
            'Software WebGL/in-memory storage; no FPS, physical GPU, persistence or AAA approval.','Cervical seam criterion only; existing collar intersection and facial LOD artifacts remain separate.']}
    def save(): (out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    def check(name,ok):
        report['captureChecks'].append({'name':name,'pass':bool(ok)})
        if not ok:raise AssertionError(name)
    save()
    try:
        raw=html.read_text()
        if '<script>' not in raw:raise ValueError('Expected standalone script injection point')
        with sync_playwright() as pw:
            options=base.launch_options(['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage'])
            if args.browser:options['executable_path']=str(args.browser.resolve())
            browser=pw.chromium.launch(**options)
            try:
                page=browser.new_page(viewport=base.VIEWPORT,device_scale_factor=1);page.set_default_timeout(120000)
                page.on('pageerror',lambda e:report['errors'].append(str(e)))
                page.on('console',lambda m:report['errors'].append(m.text) if m.type=='error' else None)
                page.on('request',lambda r:report['requests'].append(r.url) if r.url.startswith(('http:','https:')) else None)
                page.set_content(raw.replace('<script>','<script>'+base.FIX,1),timeout=120000)
                page.wait_for_function("!!window.DC_APP || (document.getElementById('error') && !document.getElementById('error').hidden)")
                if not page.evaluate('!!window.DC_APP'):raise RuntimeError('Game boot failed: '+page.locator('#errorText').inner_text())
                page.evaluate('DC_APP.renderer.humanReady');page.evaluate('()=>{DC_APP.stopFrame?.();qaStopFrames();window.requestAnimationFrame=()=>0;}')
                page.wait_for_timeout(100);page.add_script_tag(content=stage.read_text())
                report['environment']={'browser':browser.version,'headless':options['headless'],**page.evaluate('DCCharacterBenchmark.init()')}
                page.evaluate(EXTRACT_SETUP)
                for c in cases:
                    result=page.evaluate(CAPTURE,c);geometry=result.pop('geometry');shader=result.pop('vertexShader')
                    shader_sha=hashlib.sha256(shader.encode()).hexdigest()
                    check('Native vertex shader stable: '+c['id'],shader_sha==report.setdefault('vertexShaderSha256',shader_sha))
                    native=geometry['face'];metrics=boundary_metrics(native['rest'],native['world'])
                    ray=ray_hit(native['world'],result['camera'],PIXEL) if c['pose']=='idle' and c['camera']=='back' else None
                    image=out/'images'/(c['id']+'.png');page.screenshot(path=str(image),timeout=120000);png=image.read_bytes()
                    geometry_path=out/'geometry'/(c['id']+'.json.gz')
                    with gzip.open(geometry_path,'wt',encoding='utf-8') as f:json.dump(native,f,separators=(',',':'))
                    check('Native frame and fixture invariants: '+c['id'],png[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',png[16:24])==(720,720)
                        and result['storageUntouched'] and result['liveSimulationUntouched'] and result['bodyGeometryRestored'] and result['drawMethodRestored']
                        and result['glError']==0 and not any(result['cullAtDraw']))
                    entry={'id':c['id'],'case':c,'metrics':result,'geometry':metrics,'exteriorRay':ray,
                        'image':str(image.relative_to(out)),'imageSha256':base.digest(image),'nativeGeometry':str(geometry_path.relative_to(out)),
                        'nativeGeometrySha256':base.digest(geometry_path)}
                    if c['pose']=='idle' and c['camera']=='back' and c['bodyGeometryLOD']==0:
                        rays=[ray_hit(native['world'],result['camera'],p) for p in ENVELOPE_PIXELS]
                        check('Reference LOD0 envelope rays all exterior',all(r and r['frontFacing'] for r in rays))
                        report['localLOD0Envelope']={'rays':rays,'minDepthM':min(r['depthM'] for r in rays),'maxDepthM':max(r['depthM'] for r in rays)}
                    report['captures'].append(entry);save();print('CAPTURE '+c['id'],flush=True)
                page.close()
            finally:browser.close()
        check('All sixteen declared views captured',len(report['captures'])==16)
        check('No JS/console errors or external requests',not report['errors'] and not report['requests'])
        check('All inputs unchanged',all(inputs[name]==base.digest(path) for name,path in {'html':html,'stage':stage,'matrix':matrix_path,
            'sharedHelper':Path(base.__file__),'fixture':ROOT/'tests/character_benchmark.py','tool':Path(__file__)}.items()))
        if reference_path is not None:check('Reference input unchanged',reference_sha==base.digest(reference_path))
        report['captureStatus']='passed';report['exteriorEnvelope']=reference['exteriorEnvelope'] if reference_path is not None else report['localLOD0Envelope']
        report['geometricChecks']=geometric_acceptance(report['captures'],report['exteriorEnvelope'])
        if reference_path is not None:
            for c in report['captures']:
                prev=next(p for p in reference['captures'] if p['id']==c['id'])
                check('Identical reference scenario: '+c['id'],c['case']==prev['case'] and c['metrics']['camera']==prev['metrics']['camera'])
                if c['case']['pose']=='idle' and c['case']['bodyGeometryLOD']<2:
                    report['geometricChecks'].append({'name':'LOD0/1 pixels unchanged: '+c['id'],'pass':c['imageSha256']==prev['imageSha256']})
        report['geometricStatus']='passed' if all(c['pass'] for c in report['geometricChecks']) else 'failed'
    except Exception as e:
        report['captureStatus']='failed';report['failure']=str(e);raise
    finally:
        report['finishedUtc']=datetime.now(timezone.utc).isoformat();save()
    print('Capture '+report['captureStatus']+'; cervical geometric acceptance '+report['geometricStatus'],flush=True)
    return 0 if report['captureStatus']=='passed' and report['geometricStatus']=='passed' else 1

EXTRACT_SETUP = r'''()=>{
 window.qaNeckBaseline={storage:JSON.stringify([...qaCharacterStorage.entries()]),live:JSON.stringify(DC_APP.sim.serialize())};
 window.qaExtractWorld=(r,parts)=>{
  const g=r.gl,src=g.getShaderSource(g.getAttachedShaders(r.sceneProgram).find(s=>g.getShaderParameter(s,g.SHADER_TYPE)===g.VERTEX_SHADER));
  const p=g.createProgram(),shaders=[];
  for(const [type,source] of [[g.VERTEX_SHADER,src],[g.FRAGMENT_SHADER,'#version 300 es\nprecision highp float;out vec4 color;void main(){color=vec4(1.);}']]){
   const s=g.createShader(type);g.shaderSource(s,source);g.compileShader(s);if(!g.getShaderParameter(s,g.COMPILE_STATUS))throw Error(g.getShaderInfoLog(s));g.attachShader(p,s);shaders.push(s);
  }
  g.transformFeedbackVaryings(p,['vWorld'],g.INTERLEAVED_ATTRIBS);g.linkProgram(p);if(!g.getProgramParameter(p,g.LINK_STATUS))throw Error(g.getProgramInfoLog(p));
  const oldProgram=g.getParameter(g.CURRENT_PROGRAM),oldVao=g.getParameter(g.VERTEX_ARRAY_BINDING),result={};g.useProgram(p);
  for(let i=0;i<g.getProgramParameter(p,g.ACTIVE_UNIFORMS);i++){
   const u=g.getActiveUniform(p,i),loc=g.getUniformLocation(p,u.name),v=g.getUniform(r.sceneProgram,g.getUniformLocation(r.sceneProgram,u.name));
   if(u.type===g.FLOAT)g.uniform1fv(loc,typeof v==='number'?[v]:v);
   else if(u.type===g.FLOAT_VEC2)g.uniform2fv(loc,v);else if(u.type===g.FLOAT_VEC3)g.uniform3fv(loc,v);else if(u.type===g.FLOAT_VEC4)g.uniform4fv(loc,v);
   else if(u.type===g.FLOAT_MAT4)g.uniformMatrix4fv(loc,false,v);
   else if(u.type===g.INT||u.type===g.SAMPLER_2D)g.uniform1iv(loc,typeof v==='number'?[v]:v);else throw Error('Unknown uniform '+u.name);
  }
  g.uniform1i(g.getUniformLocation(p,'uSkinned'),2);g.uniform3fv(g.getUniformLocation(p,'uChunkOffset'),[0,0,0]);
  const tf=g.createTransformFeedback();g.bindTransformFeedback(g.TRANSFORM_FEEDBACK,tf);g.enable(g.RASTERIZER_DISCARD);
  for(const part of parts){
   const m=r.meshes[part.key];if(m.dynamicCount!==1)throw Error('Expected one native instance');
   const b=g.createBuffer(),a=new Float32Array(m.count*3);g.bindBuffer(g.TRANSFORM_FEEDBACK_BUFFER,b);g.bufferData(g.TRANSFORM_FEEDBACK_BUFFER,a.byteLength,g.STREAM_READ);g.bindBufferBase(g.TRANSFORM_FEEDBACK_BUFFER,0,b);g.bindVertexArray(m.vao);
   g.beginTransformFeedback(g.TRIANGLES);g.drawArraysInstanced(g.TRIANGLES,0,m.count,1);g.endTransformFeedback();g.getBufferSubData(g.TRANSFORM_FEEDBACK_BUFFER,0,a);
   g.bindBuffer(g.ARRAY_BUFFER,m.vbo);const raw=new Float32Array(m.count*16);g.getBufferSubData(g.ARRAY_BUFFER,0,raw);const rest=[];for(let i=0;i<raw.length;i+=16)rest.push(raw[i],raw[i+1],raw[i+2]);result[part.name]={count:m.count,rest,world:Array.from(a)};g.deleteBuffer(b);
  }
  g.disable(g.RASTERIZER_DISCARD);g.bindTransformFeedback(g.TRANSFORM_FEEDBACK,null);g.deleteTransformFeedback(tf);g.bindVertexArray(oldVao);g.useProgram(oldProgram);g.deleteProgram(p);for(const s of shaders)g.deleteShader(s);
  if(g.getError()!==g.NO_ERROR)throw Error('Transform feedback GL error');return result;
 };
}'''

CAPTURE = r'''c=>{
 const r=DC_APP.renderer,originalDraw=r.drawMeshes,cullAtDraw=[];let result,geometry,vertexShader;
 r.drawMeshes=function(...args){cullAtDraw.push(this.gl.isEnabled(this.gl.CULL_FACE));return originalDraw.apply(this,args);};
 try{
  result=('''+base.CAPTURE+r''')(c);
  geometry=qaExtractWorld(r,r.lodParts[c.bodyGeometryLOD].filter(p=>p.name==='face'));
  vertexShader=r.gl.getShaderSource(r.gl.getAttachedShaders(r.sceneProgram).find(s=>r.gl.getShaderParameter(s,r.gl.SHADER_TYPE)===r.gl.VERTEX_SHADER));
 }finally{r.drawMeshes=originalDraw;}
 return {...result,geometry,vertexShader,cullAtDraw,drawMethodRestored:r.drawMeshes===originalDraw};
}'''

if __name__=='__main__':
    raise SystemExit(main())
