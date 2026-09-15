from pathlib import Path
import os,subprocess,json,time
R=Path(__file__).resolve().parents[1];O=R/'qa/v014';env={**os.environ,'DISPLAY':':99','DC_REVIEW_DPR':'1.5','DC_REVIEW_QUALITY':'high'}
results=[]
jobs=[('neck',False),('profile',False),('back',False),('lookleft',False),('lookright',False),('nodup',False),('noddown',False),('thin',False),('thick',False),('neck',True),('profile',True)]
for pose,before in jobs:
 e=env.copy();label=('before-' if before else '')+pose
 if before:e.update(DC_REVIEW_HTML=str(O/'baseline-v013.html'),DC_REVIEW_TAG='before-')
 print('START',label,flush=True)
 with (O/('capture-'+label+'.log')).open('w') as f:
  p=subprocess.run(['python','tests/cervical_capture.py',pose],cwd=R,env=e,stdout=f,stderr=subprocess.STDOUT,timeout=150)
 results.append({'capture':label,'exit_code':p.returncode});print('END',results[-1],flush=True)
 (O/'capture-execution.json').write_text(json.dumps(results,indent=2))
 if p.returncode:raise SystemExit(p.returncode)
for pose in ['driver','pull','cast','run','hand']:
 print('START scene',pose,flush=True)
 with (O/('capture-'+pose+'.log')).open('w') as f:
  p=subprocess.run(['python','tests/cervical_scene_capture.py',pose],cwd=R,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=150)
 results.append({'capture':pose,'exit_code':p.returncode});print('END',results[-1],flush=True)
 (O/'capture-execution.json').write_text(json.dumps(results,indent=2))
 if p.returncode:raise SystemExit(p.returncode)
