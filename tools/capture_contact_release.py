from pathlib import Path
import subprocess,os,json
R=Path(__file__).resolve().parents[1];Q=R/'qa/v019';env={**os.environ,'DISPLAY':':99'};results=[]
for args in [['rifle','--before'],['pistol','--before'],['rifle'],['gauss'],['reload'],['pistol'],['binoculars']]:
 print('START',args,flush=True)
 with (Q/('capture-'+args[0]+('-before' if '--before' in args else '')+'.log')).open('w') as f:
  c=subprocess.run(['python','tests/contact_capture.py',*args],env=env,cwd=R,stdout=f,stderr=subprocess.STDOUT,timeout=120).returncode
 results.append({'args':args,'code':c});print('FINISH',args,c,flush=True)
 if c:raise RuntimeError(str(args))
(Q/'capture-execution.json').write_text(json.dumps(results,indent=2))
