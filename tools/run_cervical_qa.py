"""Sequential browser QA with per-suite logs and exit codes. Do not sum historical reports."""
from pathlib import Path
import subprocess,os,json,time
R=Path(__file__).resolve().parents[1];O=R/'qa/v014';env=dict(os.environ,DISPLAY=':99');results=[]
for name in ['cervical_browser','cervical_library','cervical_legacy','cervical_continuous']:
 print('START',name,flush=True);t=time.monotonic()
 with (O/(name+'-final.log')).open('w') as log:
  try:r=subprocess.run(['python','tests/'+name+'.py'],cwd=R,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=220);rc=r.returncode
  except subprocess.TimeoutExpired:rc=124
 results.append({'suite':name,'exit_code':rc,'elapsed_s':round(time.monotonic()-t,2)});(O/'suites-execution.json').write_text(json.dumps(results,indent=2));print('END',results[-1],flush=True)
 if rc:raise SystemExit(rc)
