"""Run explicit suites in a fresh copy, validate results, retain logs on failure.
Usage: python3 -m tools.qa.run --suite handling --browser /path/to/chromium
No network or browser installation is performed by this program.
"""
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, os, shutil, signal, subprocess, sys, tempfile, time, uuid
from .config import Config
from .workspace import stage_workspace
from .reporting import failure_summary

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def write_json(path, data):
    tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');tmp.replace(path)

@dataclass(frozen=True)
class Suite:
    name: str
    command: tuple[str, ...]
    report: str
    expected_checks: int
    origin: str = 'fixture'

SUITES={
 'sidearms': Suite('sidearms',('tests/sidearm_support_browser.py',),'qa/v019/sidearm-support.json',20),
 'thumbs': Suite('thumbs',('tests/thumb_contact_browser.py',),'qa/v019/thumb-contact.json',15),
 'fingers': Suite('fingers',('tests/finger_contact_browser.py',),'qa/v019/finger-contact.json',15),
 'optical': Suite('optical',('tests/optical_shoulder.py',),'qa/v019/optical-shoulder.json',14),
 'characters': Suite('characters',('tests/character_benchmark.py',),'qa/v019/character-benchmark.json',36),
 'recovery': Suite('recovery',('tests/graphics_recovery.py',),'qa/v019/graphics-recovery.json',25),
 'native': Suite('native',('tests/native_saves.py',),'qa/v019/native-saves.json',35,'http'),
 'handling': Suite('handling',('tests/contact_browser.py',),'qa/v019/handling-browser.json',51),
 'arsenal': Suite('arsenal',('tests/contact_arsenal.py',),'qa/v019/arsenal-browser.json',78),
 'library': Suite('library',('tests/contact_library.py',),'qa/v019/library-regression.json',64),
 'campaign': Suite('campaign',('tests/contact_legacy.py',),'qa/v019/legacy/browser-report.json',52),
 'continuous': Suite('continuous',('tests/contact_continuous.py',),'qa/v019/arsenal-continuous.json',26),
}

def select_suites(names, origin):
    selected = [s for s in SUITES.values() if s.origin == origin] if 'all' in names else [SUITES[n] for n in dict.fromkeys(names)]
    if not selected or any(s.origin != origin for s in selected):
        raise ValueError('Choose suites with the requested storage/origin contract.')
    return selected

def execute_suite(config, suite, stage, html_sha, run_id):
    """A report is accepted only after its producer completed successfully THIS run."""
    report=stage/suite.report
    if not report.resolve().is_relative_to(stage.resolve()):
        raise ValueError('Report path escapes isolated workspace.')
    report.parent.mkdir(parents=True,exist_ok=True)
    if report.is_symlink(): raise ValueError('Report must not be a symlink.')
    report.unlink(missing_ok=True)
    env=os.environ.copy();env.update(DC_QA_HEADLESS='0' if config.headed else '1',DC_QA_RUN_ID=run_id,DC_QA_ORIGIN=config.origin,DC_QA_HTML_SHA=html_sha,PYTHONUNBUFFERED='1')
    if config.browser: env['DC_QA_BROWSER']=str(Path(config.browser).resolve())
    else: env.pop('DC_QA_BROWSER',None)
    if config.display: env['DISPLAY']=config.display
    started=time.time();entry={'suite':suite.name,'runId':run_id,'command':[sys.executable,*suite.command], 'origin':suite.origin,'expectedChecks':suite.expected_checks,'status':'failed'}
    logfile=config.output/(suite.name+'.log')
    with logfile.open('w',encoding='utf-8') as log:
        try:
            process=subprocess.Popen(entry['command'],cwd=stage,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=os.name=='posix')
            try: entry['exitCode']=process.wait(timeout=config.timeout)
            except subprocess.TimeoutExpired:
                # Kill children too, including the browser. Never leave a stale suite running.
                if os.name=='posix': os.killpg(process.pid,signal.SIGKILL)
                else: process.kill()
                process.wait();entry['exitCode']=124
        except OSError as error:
            entry['exitCode']=127;entry['error']=str(error)
    entry['durationSeconds']=round(time.time()-started,3)
    try:
        if entry['exitCode']!=0: raise ValueError('Producer failed or timed out. See its log.')
        if not report.is_file() or report.is_symlink(): raise ValueError('Fresh report missing.')
        if report.stat().st_mtime < started-1: raise ValueError('Stale report timestamp.')
        result=json.loads(report.read_text(encoding='utf-8'))
        if not isinstance(result,dict): raise ValueError('Report must be an object.')
        checks=result.get('checks')
        if not isinstance(checks,list) or len(checks)!=suite.expected_checks: raise ValueError('Unexpected number of checks; update the contract explicitly.')
        if any(not isinstance(c,dict) or c.get('pass',c.get('passed')) is not True for c in checks): raise ValueError('A check did not pass.')
        if result.get('errors') or result.get('requests'): raise ValueError('Runtime errors or external requests recorded.')
        if result.get('sha256')!=html_sha: raise ValueError('Report belongs to different HTML.')
        if digest(stage/'index.html')!=html_sha or digest(config.root/'index.html')!=html_sha: raise ValueError('HTML changed during execution.')
        if suite.origin=='http' and result.get('nativeStorage') is not True: raise ValueError('Native mode cannot be satisfied with a storage fixture.')
        entry.update(status='passed',checks=len(checks),nativeStorage=result.get('nativeStorage',False))
    except (ValueError,OSError,TypeError) as error:
        entry['error']=str(error)
    if report.is_file() and not report.is_symlink(): shutil.copy2(report,config.output/(suite.name+'.json'))
    return entry

def run_suites(config,suites):
    config.validate()
    if not suites: raise ValueError('Select at least one suite.')
    if len({s.name for s in suites})!=len(suites): raise ValueError('Duplicate suite names.')
    if any(s.origin!=config.origin for s in suites): raise ValueError('Select suites with the configured origin, do not mislabel fixtures.')
    config.output.mkdir(parents=True,exist_ok=False)
    run_id=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:12]
    sha=digest(config.root/'index.html')
    commit=subprocess.run(['git','rev-parse','HEAD'],cwd=config.root,capture_output=True,text=True)
    manifest={'runId':run_id,'commit':commit.stdout.strip() if commit.returncode==0 else None,'htmlSha256':sha,'startedUtc':datetime.now(timezone.utc).isoformat(),'status':'running','browser':config.browser or 'playwright-bundled-chromium','headed':config.headed,'origin':config.origin,'physicalGpu':False,'suites':[]}
    write_json(config.output/'run.json',manifest)
    try:
        with tempfile.TemporaryDirectory(prefix='dc-qa-') as temp:
            stage=Path(temp)/'workspace'
            # Historical root qa is excluded; tools/qa remains executable test code.
            stage_workspace(config.root,stage)
            (stage/'qa/v019/legacy').mkdir(parents=True)
            for suite in suites:
                entry=execute_suite(config,suite,stage,sha,run_id);manifest['suites'].append(entry)
                print(json.dumps(entry,ensure_ascii=False),flush=True)
                write_json(config.output/'run.json',manifest)
                if entry['status']!='passed':
                    print(failure_summary(entry,config.output/(suite.name+'.log')),flush=True)
                    break
            if (stage/'qa').exists(): shutil.copytree(stage/'qa',config.output/'evidence')
        manifest['status']='passed' if len(manifest['suites'])==len(suites) and all(s['status']=='passed' for s in manifest['suites']) else 'failed'
    except Exception as error:
        manifest.update(status='failed',error=str(error))
    finally:
        manifest['finishedUtc']=datetime.now(timezone.utc).isoformat()
        write_json(config.output/'run.json',manifest)
    return manifest

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2]);p.add_argument('--output',type=Path)
    p.add_argument('--suite',action='append',choices=[*SUITES,'all'],required=True)
    p.add_argument('--browser');p.add_argument('--headed',action='store_true');p.add_argument('--display');p.add_argument('--timeout',type=float,default=600)
    p.add_argument('--origin',choices=['fixture','http'],default='fixture');a=p.parse_args()
    root=a.root.resolve();out=a.output or root/'artifacts'/('qa-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:8])
    try:
        result=run_suites(Config(root,out.resolve(),a.browser,a.timeout,a.origin,a.headed,a.display),select_suites(a.suite,a.origin))
        print('ARTIFACTS:',out);return 0 if result['status']=='passed' else 1
    except (ValueError,OSError) as error: p.error(str(error))

if __name__=='__main__': sys.exit(main())
