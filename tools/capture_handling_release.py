from pathlib import Path
import subprocess,os,json
R=Path(__file__).resolve().parents[1];Q=R/'qa/v018';env={**os.environ,'DISPLAY':':99'};results=[]
for args in [['rifle'],['gauss'],['reload'],['pistol'],['binoculars']]:
 print('START',args,flush=True)
 with (Q/('capture-'+args[0]+'.log')).open('w') as f:
  c=subprocess.run(['python','tests/handling_capture.py',*args],env=env,cwd=R,stdout=f,stderr=subprocess.STDOUT,timeout=120).returncode
 results.append({'args':args,'code':c});print('FINISH',args,c,flush=True)
 if c:break
(Q/'capture-execution.json').write_text(json.dumps(results,indent=2))
