"""Run current acceptance suites sequentially without an outer tool-call timeout."""
from pathlib import Path
import os,subprocess,json,hashlib,time
R=Path(__file__).resolve().parents[1];Q=R/'qa/v017';reports=[]
for name in ['arsenal_browser.py','arsenal_library.py','arsenal_legacy.py','arsenal_continuous.py']:
 print('START',name,time.strftime('%H:%M:%S'),flush=True)
 with (Q/(name[:-3]+'.log')).open('w') as log:
  r=subprocess.run(['python',str(R/'tests'/name)],cwd=R,env={**os.environ,'DISPLAY':':99'},stdout=log,stderr=subprocess.STDOUT,timeout=750)
 reports.append({'suite':name,'exit':r.returncode,'sha256':hashlib.sha256((R/'index.html').read_bytes()).hexdigest()})
 (Q/'browser-execution.json').write_text(json.dumps(reports,indent=2))
 print('END',name,r.returncode,time.strftime('%H:%M:%S'),flush=True)
 if r.returncode:break
