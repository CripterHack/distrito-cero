"""CONTACT-03 measurement integrity, NOT acceptance of the current long-arm pose.
Uses a prepared world/time/camera and Storage fixture. Never bundles QA helpers.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import math
import os
import struct
import sys
from playwright.sync_api import sync_playwright
from qa_support import launch_options

R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R))
from tools.qa.longarm_gallery import render_gallery

O=R/'qa/v020/longarms'
checks,errors,requests,cases,cycles,matrix=[],[],[],[],[],[]
sha=hashlib.sha256((R/'index.html').read_bytes()).hexdigest()
info={}
FIX="""(()=>{window.qaLongarmStore=new Map([['distrito-cero:settings:v1',JSON.stringify({quality:'balanced',sound:false,rain:false,bloom:false})]]);Object.defineProperty(window,'localStorage',{value:{getItem:k=>qaLongarmStore.get(k)||null,setItem:(k,v)=>qaLongarmStore.set(k,String(v)),removeItem:k=>qaLongarmStore.delete(k)}});})();"""


def ck(name,condition):
    checks.append({'name':name,'pass':bool(condition)})
    print(('PASS ' if condition else 'FAIL ')+name,flush=True)
    assert condition,name


def capture(page,name,record):
    path=O/'images'/(name+'.png')
    page.screenshot(path=str(path),timeout=120000)
    raw=path.read_bytes()
    assert raw[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',raw[16:24])==(820,680) and len(raw)>4000,'Invalid capture'
    record.update(name=name,image='images/'+path.name,imageSha256=hashlib.sha256(raw).hexdigest())
    cases.append(record)


def valid(record):
    m=record['measurement']
    return (m['source']=='renderer' and m['reference']['geometryVerified'] and record['actors']>=1
            and all(math.isfinite(m[k]) for k in ('eyeError','stockError','behind'))
            and set(m['palmErrors'])=={'L','R'} and len(m['segmentErrors'])==4
            and all(math.isfinite(v) for v in [*m['palmErrors'].values(),*m['segmentErrors'].values()])
            and 'invalid' not in record['screening']['failures']
            and record['screening']['artisticAcceptance'] is False
            and (m['item']!='rifle' or valid_clearance(record)))


def valid_clearance(record):
    value=record.get('stockClearance') or {}
    decision=record.get('stockScreen') or {}
    return (value.get('source')=='supplied-palette' and value.get('geometryVerified') is True
            and all(isinstance(value.get('samples',{}).get(part),int) and value['samples'][part]>100
                    and math.isfinite(value.get('minimum',{}).get(part,{}).get('distance',float('nan')))
                    for part in ('face','jacket'))
            and decision.get('artisticAcceptance') is False and decision.get('contactAcceptance') is False
            and 'invalid' not in decision.get('failures',['invalid']))


status='failed'
try:
    assert os.environ.get('DC_QA_ORIGIN','fixture')=='fixture','This diagnostic suite is not native HTTP'
    O.mkdir(parents=True,exist_ok=False);(O/'images').mkdir()
    with sync_playwright() as pw:
        browser=pw.chromium.launch(**launch_options())
        try:
            page=browser.new_page(viewport={'width':820,'height':680});page.set_default_timeout(45000)
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
            page.on('request',lambda r:requests.append(r.url) if r.url.startswith(('http:','https:')) else None)
            page.set_content((R/'index.html').read_text().replace('<script>','<script>'+FIX,1),timeout=120000)
            page.wait_for_function('!!window.DC_APP',timeout=120000);page.evaluate('DC_APP.renderer.humanReady')
            ck('Production renderer decodes all embedded skin maps',page.evaluate('DC_APP.renderer.humanTextureStatus.loaded===3'))
            page.add_style_tag(content='body>*:not(#world){visibility:hidden!important}#world{visibility:visible!important;position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important}')
            for helper in ('manual_frames.js','sidearm_sight.js','stock_clearance.js','longarm_contact.js','longarm_stage.js'):
                page.add_script_tag(content=(R/'tools/qa'/helper).read_text())
            info={'browser':browser.version,**page.evaluate('DC_LONGARM_STAGE.init()')}
            matrix=page.evaluate('DC_LONGARM_STAGE.matrix()')
            ck('Independent 72-pose matrix has every required family and numeric observation',
               len(matrix)==72 and {r['item'] for r in matrix}=={'smg','rifle','shotgun','sniper'}
               and all(math.isfinite(r['measurement']['eyeError']) and r['measurement']['source']=='simulation' for r in matrix))
            poses={'neutral':{},'crouch':{'crouch':1},'up':{'pitch':.3,'neck':1},'down':{'pitch':-.3,'neck':-1}}
            for item in ('smg','rifle','shotgun','sniper'):
                for name,config in poses.items():
                    record=page.evaluate('c=>DC_LONGARM_STAGE.sample(c)',{'item':item,**config})
                    capture(page,item+'-'+name,record)
                    ck(item+' '+name+' measures the actual rendered frame (not pose approval)',valid(record))
                    if name=='neutral':
                        front=page.evaluate('c=>DC_LONGARM_STAGE.sample(c)',{'item':item,'front':True})
                        capture(page,item+'-front',front)
                first=page.evaluate('c=>DC_LONGARM_STAGE.sample(c)',{'item':item,'aim':0})
                capture(page,item+'-cycle-00',first)
                sequence=[]
                for start in range(0,60,10):
                    result=page.evaluate('i=>DC_LONGARM_STAGE.stepCycle(i)',start)
                    sequence.extend(result['points']);capture(page,f'{item}-cycle-{start+10:02}',result['rendered'])
                cycles.append({'item':item,'simulationStep':1/60,'renderedEverySteps':10,'samples':sequence})
                ck(item+' raise/lower cycle retains all 60 numeric and seven rendered observations',
                   len(sequence)==60 and all(math.isfinite(p['eyeError']) and math.isfinite(p['stockError']) for p in sequence)
                   and all(valid(c) for c in cases if c['name'].startswith(item+'-cycle-')))
            ck('Diagnostic scene leaves the live game and storage fixture untouched',page.evaluate('DC_LONGARM_STAGE.pristine()'))
            ck('No graphics errors, browser exceptions, external requests or modified HTML',
               not errors and not requests and page.evaluate('DC_APP.renderer.gl.getError()')==0
               and hashlib.sha256((R/'index.html').read_bytes()).hexdigest()==sha)
            status='passed'
        finally:
            browser.close()
except Exception as error:
    errors.append(str(error))
    raise
finally:
    report={'schema':1,'status':status,'sha256':sha,'runId':os.environ.get('DC_QA_RUN_ID'),
            'checks':checks,'errors':errors,'requests':requests,'cases':cases,'cycles':cycles,'matrix':matrix,
            'nativeStorage':False,'physicalGpu':False,'preparedWorld':True,'preparedTimers':True,
            'artisticAcceptance':False,'gateKind':'measurement integrity only',
            'finishedUtc':datetime.now(timezone.utc).isoformat(),**info}
    O.mkdir(parents=True,exist_ok=True)
    (O/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    (O/'report.html').write_text(render_gallery(report),encoding='utf-8')
    (O.parent/'longarm-contact.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
