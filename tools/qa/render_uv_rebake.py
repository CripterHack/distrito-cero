#!/usr/bin/env python3
"""Compare local portable GLBs; never evidence of the native DQ renderer/FPS."""
import argparse, functools, hashlib, http.server, json, pathlib, threading
from playwright.sync_api import sync_playwright
ROOT=pathlib.Path(__file__).resolve().parents[2]

def run():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('before',type=pathlib.Path)
    parser.add_argument('after',type=pathlib.Path)
    parser.add_argument('--output',required=True,type=pathlib.Path)
    parser.add_argument('--browser',default='/usr/bin/chromium')
    args=parser.parse_args()
    paths=[p.resolve() for p in [args.before,args.after]]
    if any(not p.is_relative_to(ROOT/'artifacts') for p in paths):
        parser.error('Inputs must be under artifacts/')
    output=args.output.resolve()
    if not output.is_relative_to(ROOT/'artifacts'):
        parser.error('Output must be a fresh directory under artifacts/')
    output.mkdir(parents=True,exist_ok=False)
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self,*_):pass
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    origin='http://127.0.0.1:'+str(server.server_port)
    report={'type':'portable-authoring-comparison','status':'failed','nativeRuntime':False,'physicalPerformance':False,'cases':[],'inputs':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},'errors':[],'externalRequests':[]}
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path=args.browser,headless=True,args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage'])
            report['browserVersion']=browser.version
            for label,path in zip(['before','after'],paths):
                page=browser.new_page(viewport={'width':800,'height':800},device_scale_factor=1)
                page.on('pageerror',lambda e:report['errors'].append(str(e)))
                page.on('console',lambda m:report['errors'].append(m.text) if m.type=='error' else None)
                page.on('response',lambda r:report['errors'].append(f'HTTP {r.status}: {r.url}') if r.status>=400 else None)
                page.on('request',lambda r:report['externalRequests'].append(r.url) if not r.url.startswith(origin) and not r.url.startswith(('data:','blob:')) else None)
                page.goto(origin+'/tools/qa/uv_rebake_viewer.html?asset=/'+str(path.relative_to(ROOT)))
                page.wait_for_function('window.ready === true',timeout=120000)
                for pose,clip,time in [('rest',None,0),('turn','NeckTurn procedural',1.5)]:
                    for view in ['front','side','back']:
                        for mode in ['color','normal']:
                            info=page.evaluate('opts => window.capture(opts)',{'view':view,'mode':mode,'clip':clip,'time':time})
                            filename=f'{label}-{pose}-{view}-{mode}.png'
                            page.screenshot(path=str(output/filename))
                            report['cases'].append({'file':filename,**info})
                page.close()
            browser.close()
    except Exception as error:
        report['errors'].append(str(error))
        raise
    finally:
        server.shutdown()
        server.server_close()
        # The browser loaded live local files after the initial provenance was
        # recorded. Never accept captures against an obsolete input identity.
        report['finalInputs']={}
        for path in paths:
            key=str(path.relative_to(ROOT))
            try:
                digest=hashlib.sha256(path.read_bytes()).hexdigest()
                report['finalInputs'][key]=digest
                if digest!=report['inputs'][key]:
                    report['errors'].append('Input changed during capture: '+key)
            except OSError as error:
                report['errors'].append('Input unavailable after capture: '+key+': '+str(error))
        if not report['errors'] and not report['externalRequests'] and len(report['cases'])==24:
            report['status']='passed'
        (output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    if report['status']!='passed':
        raise RuntimeError('Portable viewer errors; inspect report')
    print(json.dumps({'captures':len(report['cases']),'output':str(output),'errors':len(report['errors'])}))

if __name__=='__main__':run()
