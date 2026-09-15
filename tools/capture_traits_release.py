from pathlib import Path
import subprocess,os,time,json
R=Path(__file__).resolve().parents[1]; O=R/'qa/v016';res=[]
items=[('neck',False),('profile',False),('lookleft',False),('noddown',False),('nodup',False),('thin',False),('thick',False),('full',False),('run',False),('neck',True),('profile',True)]
for name,before in items:
 env=dict(os.environ,DISPLAY=':99',DC_REVIEW_DPR='1.5',DC_REVIEW_QUALITY='balanced')
 if before:env.update(DC_REVIEW_HTML='/mnt/data/distrito-cero-v0.15-integracion.html',DC_REVIEW_TAG='before-')
 tag=('before-' if before else '')+name;t=time.time();print('START',tag,flush=True)
 with (O/('capture-'+tag+'.log')).open('w') as log:r=subprocess.run(['python','tests/traits_capture.py',name],cwd=R,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=120)
 res.append({'name':tag,'exit_code':r.returncode,'seconds':round(time.time()-t,2)});(O/'capture-execution.json').write_text(json.dumps(res,indent=2));print('END',res[-1],flush=True)
 if r.returncode:raise SystemExit(r.returncode)
for name in ['driver','pull','cast','police']:
 print('START scene',name,flush=True)
 with (O/('capture-'+name+'.log')).open('w') as log:r=subprocess.run(['python','tests/traits_scene_capture.py',name],cwd=R,env=dict(os.environ,DISPLAY=':99'),stdout=log,stderr=subprocess.STDOUT,timeout=120)
 res.append({'name':name,'exit_code':r.returncode});(O/'capture-execution.json').write_text(json.dumps(res,indent=2))
 if r.returncode:raise SystemExit(r.returncode)
print('START film',flush=True)
with (O/'film.log').open('w') as log:r=subprocess.run(['python','tests/traits_clip.py'],cwd=R,env=dict(os.environ,DISPLAY=':99'),stdout=log,stderr=subprocess.STDOUT,timeout=280)
res.append({'name':'film','exit_code':r.returncode});(O/'capture-execution.json').write_text(json.dumps(res,indent=2))
print('END film',r.returncode,flush=True)
