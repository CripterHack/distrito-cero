from pathlib import Path
import subprocess,os,json,hashlib,time
R=Path(__file__).resolve().parents[1];Q=R/'qa/v019';env={**os.environ,'DISPLAY':':99'};result=[];initial_hash=hashlib.sha256((R/"index.html").read_bytes()).hexdigest()
for name in ['contact_browser','contact_arsenal','contact_library','contact_legacy','contact_continuous']:
 assert hashlib.sha256((R/'index.html').read_bytes()).hexdigest()==initial_hash,'HTML changed during verification'
 print('START',name,flush=True)
 with (Q/(name+'-final.log')).open('w') as f:
  try: p=subprocess.run(['python','tests/'+name+'.py'],cwd=R,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=300);code=p.returncode
  except subprocess.TimeoutExpired: code=124
 assert hashlib.sha256((R/'index.html').read_bytes()).hexdigest()==initial_hash,'HTML changed during verification'
 result.append({'suite':name,'code':code});(Q/'browser-execution.json').write_text(json.dumps({'html':hashlib.sha256((R/'index.html').read_bytes()).hexdigest(),'suites':result},indent=2));print('FINISH',name,code,flush=True)
 if code:break
