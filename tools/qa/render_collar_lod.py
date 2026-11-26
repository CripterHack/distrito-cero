#!/usr/bin/env python3
"""Prepared native collar LOD QA. Source-region probes are directional coverage,
not exact exposed area, full collision volumes, continuous motion, or FPS.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse,copy,gzip,hashlib,json,math,struct,subprocess,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from tools.qa import render_lod_seam as seam
from playwright.sync_api import sync_playwright
base=seam.base
CONTRACT='native-collar-lod-v1'
SOURCE_REST_SHA256='86ba0aeb8a98df0aabe84a98cb5d90abdeeb34977b205e253c9e8a765b15daed'
SOURCE_VERTICES=29016
EXPECTED_ANCHORS=611
FULLBODY_CAMERA={'targetY':.93,'distance':3.3,'eyeOffsetY':.10,'fov':.62}
PROFILES=('neutral','light','robust','extreme')
POSES=('idle','neck-left','neck-right')

def selections(matrix):
    reference=base.cases(matrix);cases=[]
    for profile in PROFILES:
        for pose in POSES:
            for lod in (0,1,2):
                c=copy.deepcopy(next(c for c in reference if c['pose']=='idle' and c['camera']=='back' and c['light']=='neutral' and c['bodyGeometryLOD']==lod))
                c.update(id=f'{profile}--{pose}--back--lod{lod}',profile=profile,pose=pose,
                    look={**copy.deepcopy(matrix['profiles'][profile]),'hairStyle':0},conditionId=profile+'/'+pose,cohortFrame=True,framing='closeup')
                if pose!='idle':
                    c['sample']=copy.deepcopy(matrix['poses']['neck']);sign=1 if pose=='neck-left' else -1
                    c['sample']['actor'].update(lookYaw=.62*sign,lookPitch=.14,lookRoll=.03*sign)
                cases.append(c)
    for camera,light,framing in [('profile','neutral','closeup'),('profile','side','closeup'),
                                 ('front','neutral','fullbody'),('back','neutral','fullbody'),
                                 ('front','side','fullbody'),('profile','side','fullbody')]:
        c=copy.deepcopy(next(c for c in reference if c['pose']=='idle' and c['camera']==camera and c['light']==light and c['bodyGeometryLOD']==2))
        c.update(id=f'visual--{framing}--{light}--{camera}',conditionId='neutral/idle',cohortFrame=False,framing=framing)
        if framing=='fullbody':c['closeup']=dict(FULLBODY_CAMERA)
        cases.append(c)
    return cases

def make_cohort(rest):
    p=np.asarray(rest,dtype=np.float64)
    if not p.size or p.size%9 or not np.isfinite(p).all():raise ValueError('Invalid source triangle stream')
    t=p.reshape(-1,3,3);centers=t.mean(1);cross=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);area=np.linalg.norm(cross,axis=1)/2
    normals=cross/np.maximum(area[:,None]*2,1e-30);radial=centers.copy();radial[:,1]=0;radial[:,2]+=.01
    radius=np.linalg.norm(radial,axis=1);alignment=np.einsum('ij,ij->i',normals,radial)/np.maximum(radius,1e-30)
    ids=np.flatnonzero((centers[:,1]>=1.445)&(centers[:,1]<=1.49)&(radius<.16)&(alignment>.25)&(area>1e-14))
    if not len(ids):raise ValueError('Empty source-region cohort')
    return [{'sourceTriangle':int(i),'barycentric':[1/3]*3,'restCenter':centers[i].tolist(),
        'restNormal':normals[i].tolist(),'restAreaM2':float(area[i])} for i in ids]

def place_anchors(cohort,world):
    p=np.asarray(world,dtype=np.float64)
    if not cohort or not p.size or p.size%9 or not np.isfinite(p).all():raise ValueError('Invalid posed triangle stream')
    tri=p.reshape(-1,3,3);out=[]
    for a in cohort:
        i=a['sourceTriangle']
        if type(i) is not int or not 0<=i<len(tri):raise ValueError('Source anchor triangle out of range')
        t=tri[i];n=np.cross(t[1]-t[0],t[2]-t[0]);length=np.linalg.norm(n)
        if not np.isfinite(length) or length<1e-14:raise ValueError('Degenerate posed source anchor')
        out.append({**a,'worldCenter':(np.asarray(a['barycentric'])@t).tolist(),'worldNormal':(n/length).tolist()})
    return out

def coverage_summary(cohort,probes,reference_ids):
    byid={a['sourceTriangle']:i for i,a in enumerate(cohort)}
    if not reference_ids or len(set(reference_ids))!=len(reference_ids) or len(probes)!=len(cohort) or any(i not in byid for i in reference_ids):
        raise ValueError('Invalid or empty fixed coverage reference')
    lost=[i for i in reference_ids if probes[byid[i]]['outwardM'] is None]
    return {'anchors':len(reference_ids),'lostAnchors':len(lost),'lostSourceTriangleIDs':lost,
        'referenceAreaM2':sum(cohort[byid[i]]['restAreaM2'] for i in reference_ids),
        'lostAreaM2':sum(cohort[byid[i]]['restAreaM2'] for i in lost)}

def fixed_core_failures(core_ids,covered_ids):
    if not core_ids or len(set(core_ids))!=len(core_ids):raise ValueError('Empty or duplicate fixed core')
    return sorted(set(core_ids)-set(covered_ids))

def digest_data(data):
    return hashlib.sha256(json.dumps(data,separators=(',',':'),allow_nan=False).encode()).hexdigest()

def validate_face_invariance(capture,reference_capture):
    def face_sha(c):
        value=c.get('partGeometrySha256',{}).get('face')
        if not isinstance(value,str) or len(value)!=64 or any(x not in '0123456789abcdef' for x in value):
            raise ValueError('Invalid face geometry SHA256')
        return value
    if capture.get('id')!=reference_capture.get('id') or face_sha(capture)!=face_sha(reference_capture):
        raise ValueError('Face count/rest/world geometry changed outside jacket-only scope')

def rest_digest(rest):
    return hashlib.sha256(np.asarray(rest,dtype='<f4').tobytes()).hexdigest()

def validate_reference(reference,inputs,planned):
    def require(ok,message):
        if not ok:raise ValueError('Invalid reference: '+message)
    def sha(x):return isinstance(x,str) and len(x)==64 and all(c in '0123456789abcdef' for c in x)
    require(isinstance(reference,dict),'expected object')
    require(reference.get('schema')==1 and type(reference.get('schema')) is int and reference.get('contract')==CONTRACT,'schema/contract')
    require(reference.get('captureStatus')=='passed','completed capture')
    require(reference.get('geometricStatus') in ('passed','failed'),'recorded geometric result')
    require(reference.get('cameraContract')=={'closeup':base.CAMERA,'fullbody':FULLBODY_CAMERA} and reference.get('viewport')==base.VIEWPORT,'camera/viewport')
    require(sha(reference.get('vertexShaderSha256')),'native vertex shader hash')
    require(reference.get('errors')==[] and reference.get('requests')==[],'runtime errors/requests')
    hashes=reference.get('inputHashes')
    require(isinstance(hashes,dict) and all(sha(hashes.get(k)) for k in inputs),'input hashes')
    require(all(hashes[k]==inputs[k] for k in inputs if k!='html'),'helper/fixture mismatch')
    require(reference.get('sourceRestSha256')==SOURCE_REST_SHA256,'canonical source geometry')
    cohort=reference.get('cohort')
    require(isinstance(cohort,list) and len(cohort)==EXPECTED_ANCHORS,'complete source cohort')
    ids=[]
    for a in cohort:
        require(isinstance(a,dict) and type(a.get('sourceTriangle')) is int and 0<=a['sourceTriangle']<SOURCE_VERTICES//3,'anchor triangle')
        require(a.get('barycentric')==[1/3]*3,'canonical barycentrics')
        require(type(a.get('restAreaM2')) in (int,float) and math.isfinite(a['restAreaM2']) and a['restAreaM2']>0,'anchor area')
        require(all(isinstance(a.get(k),list) and len(a[k])==3 and all(type(v) in (int,float) and math.isfinite(v) for v in a[k]) for k in ('restCenter','restNormal')),'anchor rest attributes')
        ids.append(a['sourceTriangle'])
    require(len(set(ids))==len(ids) and reference.get('cohortSha256')==digest_data(cohort),'cohort identity')
    captures=reference.get('captures')
    require(isinstance(captures,list) and len(captures)==len(planned),'complete captures')
    for c,case in zip(captures,planned):
        require(isinstance(c,dict) and c.get('id')==case['id'] and c.get('case')==case,'capture scenario')
        require(all(sha(c.get(k)) for k in ('imageSha256','nativeGeometrySha256','geometryDataSha256')),'capture data hashes')
        parts=c.get('partGeometrySha256');require(isinstance(parts,dict) and set(parts)=={'face','jacket'} and all(sha(x) for x in parts.values()),'separate native part hashes')
        metrics=c.get('metrics');require(isinstance(metrics,dict),'capture metrics')
        require(all(metrics.get(k) is True for k in ('storageUntouched','liveSimulationUntouched','bodyGeometryRestored','drawMethodRestored')),'fixture guard')
        require(metrics.get('glError')==0 and type(metrics.get('glError')) is int and isinstance(metrics.get('cullAtDraw'),list) and metrics['cullAtDraw'] and all(x is False for x in metrics['cullAtDraw']),'native GL guard')
    checks=reference.get('captureChecks');require(isinstance(checks,list) and checks and all(isinstance(c,dict) and c.get('pass') is True for c in checks),'capture guards')
    conditions=reference.get('conditions');expected={p+'/'+s for p in PROFILES for s in POSES}
    require(isinstance(conditions,dict) and set(conditions)==expected,'condition coverage')
    for condition in conditions.values():
        require(isinstance(condition,dict),'condition')
        for field in ('sourceCoveredIDs','lod1CoveredIDs','coreIDs'):
            values=condition.get(field);require(isinstance(values,list) and values and all(type(i) is int and i in ids for i in values) and len(values)==len(set(values)),'nonempty source/core IDs')
        require(set(condition['coreIDs'])==set(condition['sourceCoveredIDs'])&set(condition['lod1CoveredIDs']),'core from source LOD0+1 only')
    return reference

def snapshot_reference(path,inputs,planned):
    raw=Path(path).read_bytes();reference=json.loads(raw)
    validate_reference(reference,inputs,planned)
    return reference,hashlib.sha256(raw).hexdigest()

def require_reference_unchanged(path,sha):
    if hashlib.sha256(Path(path).read_bytes()).hexdigest()!=sha:raise ValueError('Reference changed during capture')
def normal_probe(origin,direction,triangles,limit=.12):
 """Both directions along the source skin normal, within explicit local radius."""
 tri=triangles;e1=tri[:,1]-tri[:,0];e2=tri[:,2]-tri[:,0];h=np.cross(direction,e2);det=np.einsum('ij,ij->i',e1,h);s=origin-tri[:,0]
 with np.errstate(divide='ignore',invalid='ignore'):
  u=np.einsum('ij,ij->i',s,h)/det;q=np.cross(s,e1);v=q@direction/det;t=np.einsum('ij,ij->i',e2,q)/det
  valid=(abs(det)>1e-12)&(u>=-1e-9)&(v>=-1e-9)&(u+v<=1+1e-9)&(abs(t)<=limit)
  positive=np.where(valid&(t>=0),t,np.inf);negative=np.where(valid&(t<0),-t,np.inf)
 pi=int(np.argmin(positive));ni=int(np.argmin(negative))
 return {'outwardM':float(positive[pi]) if np.isfinite(positive[pi]) else None,'outwardTriangle':pi if np.isfinite(positive[pi]) else None,
  'inwardM':float(negative[ni]) if np.isfinite(negative[ni]) else None,'inwardTriangle':ni if np.isfinite(negative[ni]) else None}

CAPTURE=seam.CAPTURE.replace("p.name==='face'","['face','jacket'].includes(p.name)")
CAPTURE=r'''c=>{
 const result=('''+CAPTURE+r''')(c),r=DC_APP.renderer;
 const p1=r.lodParts[1].find(p=>p.name==='jacket'),p2=r.lodParts[2].find(p=>p.name==='jacket');
 return {...result,jacketPolicy:{lod1Key:p1.key,lod2Key:p2.key,sharedKey:p1.key===p2.key,
  sharedMesh:r.meshes[p1.key]===r.meshes[p2.key],sharedVBO:r.meshes[p1.key].vbo===r.meshes[p2.key].vbo}};
}'''

def analyze(report,native,reference):
    captures=report['captures'];conditions={};checks=[]
    def check(name,ok):checks.append({'name':name,'pass':bool(ok)})
    first=next(c for c in captures if c['case'].get('cohortFrame') and c['case']['bodyGeometryLOD']==0)
    source=native[first['id']]['face'];cohort=make_cohort(source['rest'])
    if len(cohort)!=EXPECTED_ANCHORS or source['count']!=SOURCE_VERTICES or rest_digest(source['rest'])!=SOURCE_REST_SHA256:
        raise ValueError('Canonical source/cohort contract changed')
    report.update(sourceRestSha256=SOURCE_REST_SHA256,cohort=cohort,cohortSha256=digest_data(cohort))
    if reference and reference['cohortSha256']!=report['cohortSha256']:raise ValueError('Reference cohort does not match canonical source geometry')
    for profile in PROFILES:
        for pose in POSES:
            key=profile+'/'+pose
            group={c['case']['bodyGeometryLOD']:c for c in captures if c['case'].get('cohortFrame') and c['case']['conditionId']==key}
            if set(group)!={0,1,2}:raise ValueError('Incomplete LOD cohort condition')
            source=native[group[0]['id']]['face']
            if rest_digest(source['rest'])!=SOURCE_REST_SHA256:raise ValueError('Source rest geometry varies across conditions')
            anchors=place_anchors(cohort,source['world']);probes={};covered={}
            for lod in (0,1,2):
                jacket=np.asarray(native[group[lod]['id']]['jacket']['world'],dtype=np.float64).reshape(-1,3,3)
                if not np.isfinite(jacket).all():raise ValueError('Nonfinite jacket geometry')
                probes[lod]=[normal_probe(a['worldCenter'],a['worldNormal'],jacket) for a in anchors]
                covered[lod]=[a['sourceTriangle'] for a,p in zip(cohort,probes[lod]) if p['outwardM'] is not None]
            core=sorted(set(covered[0])&set(covered[1]))
            if not covered[0] or not core:raise ValueError('Empty source-covered cohort/core')
            if reference:
                fixed=reference['conditions'][key]
                if covered[0]!=fixed['sourceCoveredIDs'] or covered[1]!=fixed['lod1CoveredIDs'] or core!=fixed['coreIDs']:
                    raise ValueError('Source LOD0/1 reference coverage changed for '+key)
                core=fixed['coreIDs']
            lost=fixed_core_failures(core,covered[2])
            check('Preserve every source LOD0+1 covered anchor: '+key,not lost)
            jacket1=native[group[1]['id']]['jacket'];jacket2=native[group[2]['id']]['jacket']
            check('Jacket LOD2 has exact native LOD1 rest/world geometry: '+key,digest_data(jacket1)==digest_data(jacket2))
            # Separate actual reduced-skin clearance diagnostic. A normal probe can
            # intersect another fold; it is not a complete collision/silhouette test.
            skin2=np.asarray(native[group[2]['id']]['face']['world'],dtype=np.float64).reshape(-1,3,3)
            skin_clearance=[];byid={a['sourceTriangle']:i for i,a in enumerate(cohort)}
            for source_id in core:
                i=byid[source_id];a=anchors[i];hit=normal_probe(a['worldCenter'],a['worldNormal'],skin2)
                candidates=[x for x in (hit['outwardM'],-hit['inwardM'] if hit['inwardM'] is not None else None) if x is not None]
                skin_t=min(candidates,key=abs) if candidates else None;garment_t=probes[2][i]['outwardM']
                skin_clearance.append({'sourceTriangle':source_id,'skinOffsetM':skin_t,
                    'outwardGarmentM':garment_t,'garmentMinusSkinM':garment_t-skin_t if garment_t is not None and skin_t is not None else None})
            conditions[key]={'sourceCoveredIDs':covered[0],'lod1CoveredIDs':covered[1],'coreIDs':core,'candidateCoveredIDs':covered[2],
                'coreLostIDs':lost,'sourceCoverage':{str(lod):coverage_summary(cohort,probes[lod],covered[0]) for lod in (0,1,2)},
                'coreCoverage':coverage_summary(cohort,probes[2],core),'probes':{str(k):v for k,v in probes.items()},
                'posedAnchors':anchors,'actualLOD2SkinClearanceDiagnostic':skin_clearance}
    for c in captures:
        if c['case']['bodyGeometryLOD']==2:
            check('Shared native jacket key/mesh/VBO: '+c['id'],all(c['metrics']['jacketPolicy'][k] for k in ('sharedKey','sharedMesh','sharedVBO')))
    report['conditions']=conditions
    report['pixelRays']=[]
    for case_id,pixel in [('neutral--idle--back--lod2',(267,547)),('visual--closeup--neutral--profile',(447,548))]:
        c=next(c for c in captures if c['id']==case_id)
        with np.errstate(invalid='ignore'):
            rays={name:seam.ray_hit(part['world'],c['metrics']['camera'],pixel) for name,part in native[case_id].items()}
        check('Neutral collar ray has jacket before skin: '+case_id,bool(rays['face'] and rays['jacket'] and rays['jacket']['depthM']<rays['face']['depthM']))
        report['pixelRays'].append({'case':case_id,'pixel':list(pixel),'hits':rays})
    if reference:
        for c in captures:
            previous=next(p for p in reference['captures'] if p['id']==c['id'])
            if c['metrics']['camera']!=previous['metrics']['camera']:raise ValueError('Reference camera differs')
            validate_face_invariance(c,previous)
            check('Face count/rest/world geometry unchanged: '+c['id'],True)
            if c['case'].get('cohortFrame') and c['case']['bodyGeometryLOD']<2:
                check('Source LOD0/1 image and geometry unchanged: '+c['id'],c['imageSha256']==previous['imageSha256'] and c['geometryDataSha256']==previous['geometryDataSha256'])
    report['geometricChecks']=checks
    report['geometricStatus']='passed' if all(c['pass'] for c in checks) else 'failed'

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--html',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--label',required=True);parser.add_argument('--browser',type=Path);parser.add_argument('--reference',type=Path)
    args=parser.parse_args();html=args.html.resolve();out=args.output.resolve();artifacts=ROOT/'artifacts'
    if not html.is_file():parser.error('HTML input does not exist')
    if not out.is_relative_to(artifacts) or out==artifacts or artifacts.resolve()!=artifacts or out.exists():parser.error('Output must be a fresh repository artifacts child')
    stage=ROOT/'tools/qa/character_stage.js';matrix_path=ROOT/'tests/benchmarks/characters.json'
    paths={'html':html,'stage':stage,'matrix':matrix_path,'nativeNeckHelper':Path(base.__file__),
        'nativeSeamHelper':Path(seam.__file__),'fixture':ROOT/'tests/character_benchmark.py','tool':Path(__file__)}
    raw=html.read_bytes();inputs={name:base.digest(path) for name,path in paths.items()}
    if inputs['html']!=hashlib.sha256(raw).hexdigest():parser.error('HTML changed while reading')
    cases=selections(base.load_matrix(matrix_path));reference=None;reference_sha=None
    if args.reference is not None:reference,reference_sha=snapshot_reference(args.reference,inputs,cases)
    out.mkdir(parents=True);(out/'images').mkdir();(out/'geometry').mkdir()
    report={'schema':1,'contract':CONTRACT,'label':args.label,'captureStatus':'running','geometricStatus':'pending',
        'startedUtc':datetime.now(timezone.utc).isoformat(),'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'inputHashes':inputs,'referenceReportSha256':reference_sha,'referenceSource':'preserved report' if reference else 'LOD0/1 in this same frozen HTML',
        'cameraContract':{'closeup':base.CAMERA,'fullbody':FULLBODY_CAMERA},'viewport':base.VIEWPORT,
        'captureChecks':[],'geometricChecks':[],'captures':[],'errors':[],'requests':[],
        'scenario':'Four canonical appearances × idle/left/right prepared neck poses × native body LOD0/1/2, plus six neutral/side-lit closeup/full-body views. Native DQ/shaders unchanged.',
        'coverageContract':'611 canonical rest-face centroids. For each profile/pose preserve all IDs with outward jacket coverage in BOTH source LOD0 and LOD1. Full LOD0 coverage loss remains reported separately; reference never selected from candidate.',
        'limitations':['Directional finite probes, not full collision volume or all-view silhouette proof. A hit may belong to another garment fold.',
            'LostAreaM2 weights whole source triangles by centroid classification; not exact visibly exposed skin area.',
            'Existing authored/LOD1 intersections and facial geometry defects remain outside this per-part LOD policy. Global face before/after invariance is checked only with an external reference; same-build CI checks source geometry and relies on separate native source/LOD regressions.',
            'Prepared independent poses, software WebGL, forced body LOD and LOD0 groom; no continuous animation, distance behavior, hardware FPS, native storage or AAA approval.']}
    def save():(out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    def check(name,ok):
        report['captureChecks'].append({'name':name,'pass':bool(ok)})
        if not ok:raise AssertionError(name)
    native={};save()
    try:
        with sync_playwright() as pw:
            options=base.launch_options(['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage'])
            if args.browser:options['executable_path']=str(args.browser.resolve())
            browser=pw.chromium.launch(**options)
            try:
                page=browser.new_page(viewport=base.VIEWPORT,device_scale_factor=1);page.set_default_timeout(120000)
                page.on('pageerror',lambda e:report['errors'].append(str(e)))
                page.on('console',lambda m:report['errors'].append(m.text) if m.type=='error' else None)
                page.on('request',lambda r:report['requests'].append(r.url) if r.url.startswith(('http:','https:')) else None)
                page.set_content(raw.decode().replace('<script>','<script>'+base.FIX,1),timeout=120000)
                page.wait_for_function("!!window.DC_APP || (document.getElementById('error') && !document.getElementById('error').hidden)")
                if not page.evaluate('!!window.DC_APP'):raise RuntimeError('Native game failed to boot')
                page.evaluate('DC_APP.renderer.humanReady');page.evaluate('()=>{DC_APP.stopFrame?.();qaStopFrames();window.requestAnimationFrame=()=>0;}');page.wait_for_timeout(100)
                page.add_script_tag(content=stage.read_text());report['environment']={'browser':browser.version,'headless':options['headless'],**page.evaluate('DCCharacterBenchmark.init()')}
                page.evaluate(seam.EXTRACT_SETUP)
                for c in cases:
                    metrics=page.evaluate(CAPTURE,c);geometry=metrics.pop('geometry');shader=metrics.pop('vertexShader')
                    check('Both native surfaces present: '+c['id'],set(geometry)=={'face','jacket'})
                    shader_sha=hashlib.sha256(shader.encode()).hexdigest();check('Canonical vertex shader stable: '+c['id'],shader_sha==report.setdefault('vertexShaderSha256',shader_sha))
                    if reference:check('Vertex shader matches reference: '+c['id'],shader_sha==reference['vertexShaderSha256'])
                    image=out/'images'/(c['id']+'.png');page.screenshot(path=str(image),timeout=120000);png=image.read_bytes()
                    geometry_path=out/'geometry'/(c['id']+'.json.gz')
                    with gzip.open(geometry_path,'wt') as f:json.dump(geometry,f,separators=(',',':'),allow_nan=False)
                    check('Native frame and fixture invariants: '+c['id'],png[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',png[16:24])==(720,720)
                        and all(metrics[k] for k in ('storageUntouched','liveSimulationUntouched','bodyGeometryRestored','drawMethodRestored'))
                        and metrics['glError']==0 and metrics['cullAtDraw'] and all(x is False for x in metrics['cullAtDraw']))
                    native[c['id']]=geometry
                    report['captures'].append({'id':c['id'],'case':c,'metrics':metrics,'image':str(image.relative_to(out)),'imageSha256':base.digest(image),
                        'nativeGeometry':str(geometry_path.relative_to(out)),'nativeGeometrySha256':base.digest(geometry_path),'geometryDataSha256':digest_data(geometry),
                        'partGeometrySha256':{name:digest_data(part) for name,part in geometry.items()}})
                    save();print('CAPTURE '+c['id'],flush=True)
                page.close()
            finally:browser.close()
        check('All forty-two declared frames captured',len(report['captures'])==42)
        check('No JavaScript/console errors or external requests',not report['errors'] and not report['requests'])
        check('Frozen inputs unchanged',all(inputs[name]==base.digest(path) for name,path in paths.items()))
        if args.reference is not None:
            require_reference_unchanged(args.reference,reference_sha);check('Reference bytes unchanged during capture',True)
        analyze(report,native,reference)
        # Validation/analysis is part of the producer, so mutation here also fails.
        if args.reference is not None:require_reference_unchanged(args.reference,reference_sha)
        check('Frozen inputs unchanged after analysis',all(inputs[name]==base.digest(path) for name,path in paths.items()))
        report['captureStatus']='passed'
    except Exception as e:
        report['captureStatus']='failed';report['geometricStatus']='invalid';report['failure']=str(e);raise
    finally:
        report['finishedUtc']=datetime.now(timezone.utc).isoformat();save()
    print('Capture '+report['captureStatus']+'; collar geometric acceptance '+report['geometricStatus'],flush=True)
    return 0 if report['captureStatus']=='passed' and report['geometricStatus']=='passed' else 1

if __name__=='__main__':raise SystemExit(main())
