"""SPEC-002 coverage: real renderer, prepared clock/poses, isolated storage fixture.
Run through tools.qa.run --suite characters, or directly with --matrix full.
No artwork is automatically approved and no FPS claim is derived from capture time.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, os, struct, subprocess, sys, time, uuid
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.qa.character_matrix import load_matrix, make_cases, render_gallery
from qa_support import launch_options
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1]
FIX="""(()=>{const frames=new Set(),raf=requestAnimationFrame.bind(window);window.requestAnimationFrame=fn=>{let id=raf(t=>{frames.delete(id);fn(t)});frames.add(id);return id;};window.qaStopFrames=()=>{for(const id of frames)cancelAnimationFrame(id);frames.clear();};window.qaCharacterStorage=new Map([['distrito-cero:settings:v1',JSON.stringify({quality:'balanced',sound:false,rain:false,bloom:false})]]);Object.defineProperty(window,'localStorage',{value:{getItem:k=>qaCharacterStorage.get(k)||null,setItem:(k,v)=>qaCharacterStorage.set(k,String(v)),removeItem:k=>qaCharacterStorage.delete(k)}});})();"""
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--matrix',choices=['smoke','full'],default='smoke')
    parser.add_argument('--output',type=Path)
    a=parser.parse_args()
    if os.environ.get('DC_QA_RUN_ID'):
        if a.output or a.matrix!='smoke':parser.error('The portable suite has the fixed smoke contract.')
        out=R/'qa/v019/characters';report=R/'qa/v019/character-benchmark.json'
    else:
        out=(a.output or R/'artifacts'/('characters-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:6])).resolve()
        if not out.is_relative_to(R/'artifacts') or out==R/'artifacts' or (R/'artifacts').resolve()!=R/'artifacts':parser.error('Output must be a fresh child of <repo>/artifacts/.')
        report=out/'character-benchmark.json'
    out.mkdir(parents=True,exist_ok=False);(out/'images').mkdir()
    checks=[];errors=[];requests=[];captures=[];sha=digest(R/'index.html')
    commit=subprocess.run(['git','rev-parse','HEAD'],cwd=R,capture_output=True,text=True)
    data={'schema':1,'sha256':sha,'htmlSha256':sha,'commit':commit.stdout.strip() if commit.returncode==0 else None,
        'matrix':a.matrix,'checks':checks,'errors':errors,'requests':requests,'captures':captures,
        'nativeStorage':False,'physicalGpu':False,'artisticAcceptance':'pending','status':'running',
        'startedUtc':datetime.now(timezone.utc).isoformat(),'matrixSha256':digest(R/'tests/benchmarks/characters.json'),
        'stageSha256':digest(R/'tools/qa/character_stage.js'),'environments':[]}
    def ck(name,ok):
        checks.append({'name':name,'pass':bool(ok)});print(('PASS ' if ok else 'FAIL ')+name,flush=True)
        if not ok:raise AssertionError(name)
    def save():report.parent.mkdir(parents=True,exist_ok=True);report.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    save()
    try:
        matrix=load_matrix(R/'tests/benchmarks/characters.json');cases=make_cases(matrix,a.matrix)
        data['plannedCases']=len(cases);ck('Versioned coverage contract and cases validated',len(cases)==(30 if a.matrix=='smoke' else 586))
        raw=(R/'index.html').read_text(encoding='utf-8');script=(R/'tools/qa/character_stage.js').read_text(encoding='utf-8')
        ck_external_seed=os.environ.get('DC_QA_HTML_SHA',sha)
        if ck_external_seed!=sha:raise ValueError('Harness HTML differs before capture.')
        pristine=True
        with sync_playwright() as pw:
            browser=pw.chromium.launch(**launch_options(['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage']))
            try:
                for offset in range(0,len(cases),10):
                    page=browser.new_page(viewport={'width':720,'height':720},device_scale_factor=1)
                    page.set_default_timeout(60000)
                    page.on('pageerror',lambda e:errors.append(str(e)))
                    page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
                    page.on('request',lambda req:requests.append(req.url) if req.url.startswith(('http:','https:')) else None)
                    page.set_content(raw.replace('<script>','<script>'+FIX,1),timeout=120000)
                    page.wait_for_function("!!window.DC_APP || (document.getElementById('error') && !document.getElementById('error').hidden)",timeout=120000,polling=50)
                    if not page.evaluate('!!window.DC_APP'):raise RuntimeError('Game boot failed: '+page.locator('#errorText').inner_text())
                    page.evaluate('DC_APP.renderer.humanReady')
                    page.evaluate('()=>{DC_APP.stopFrame?.();window.qaStopFrames();window.requestAnimationFrame=()=>0;}');page.wait_for_timeout(100)
                    page.add_script_tag(content=script)
                    data['environments'].append({'browser':browser.version,**page.evaluate('DCCharacterBenchmark.init()')})
                    for case in cases[offset:offset+10]:
                        started=time.monotonic();metrics=page.evaluate('c=>DCCharacterBenchmark.applyCase(c)',case)
                        file=out/'images'/(case['id']+'.png');page.screenshot(path=str(file),timeout=120000)
                        image=file.read_bytes();width,height=struct.unpack('>II',image[16:24])
                        entry={**case,'label':case['sample']['label'],'image':'images/'+file.name,'imageSha256':hashlib.sha256(image).hexdigest(),'metrics':metrics,'captureWallSeconds':round(time.monotonic()-started,3)}
                        captures.append(entry)
                        pristine=pristine and metrics['storageUntouched'] and metrics['liveSimulationUntouched']
                        contact=metrics.get('equipment')
                        ok=(image[:8]==b'\x89PNG\r\n\x1a\n' and (width,height)==(720,720) and len(image)>4000 and metrics['glError']==0 and metrics['finitePalette'] and metrics['actors']>=1 and metrics['hairStyle']==case['look']['hairStyle'])
                        if case['sample'].get('weapon'):
                            ok=ok and contact is not None and contact['selected']==case['sample']['weapon'] and bool(contact['contacts']) and all(v['reachError']<.012 for v in contact['contacts'].values())
                        if case['pose']=='entry':ok=ok and metrics['accessPhase']=='enter'
                        ck('Production frame '+case['id'],ok);save()
                    page.close()
            finally:browser.close()
        ck('Benchmark never writes the live simulation or saved-game fixture',pristine)
        ck('Captured all declared axes and eleven hair styles',len(captures)==len(cases) and {c['look']['hairStyle'] for c in captures}==set(range(11)))
        ck('HTML remained unchanged during this run',digest(R/'index.html')==sha)
        ck('Browser recorded no JavaScript or console errors',not errors)
        ck('Runtime and benchmark made no external requests',not requests)
        data['status']='passed'
    except Exception as error:
        data['status']='failed';data['failure']=str(error);print('BENCHMARK FAILED:',error,flush=True)
    finally:
        data['finishedUtc']=datetime.now(timezone.utc).isoformat();save()
        (out/'report.html').write_text(render_gallery(data,captures),encoding='utf-8')
        review={'status':'pending','reviewer':'','htmlSha256':sha,'evidence':'report.html','decision':'','criteria':['cervical integration','shoulders and garment seams','hands and contacts','hairline and long hair','animation continuity'],'note':'Do not mark accepted because numeric checks passed.'}
        (out/'art-review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('REPORT:',report,flush=True)
    return 0 if data['status']=='passed' else 1
if __name__=='__main__':sys.exit(main())
