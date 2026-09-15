from pathlib import Path
import subprocess,os,json,hashlib,time
R=Path(__file__).resolve().parents[1];Q=R/'qa/v018';env={**os.environ,'DISPLAY':':99'};result=[]
for name in ['handling_browser','handling_arsenal','handling_library','handling_legacy','handling_continuous']:
 print('START',name,flush=True)
 with (Q/(name+'-final.log')).open('w') as f:
  try: p=subprocess.run(['python','tests/'+name+'.py'],cwd=R,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=240);code=p.returncode
  except subprocess.TimeoutExpired: code=124
 result.append({'suite':name,'code':code});(Q/'browser-execution.json').write_text(json.dumps({'html':hashlib.sha256((R/'index.html').read_bytes()).hexdigest(),'suites':result},indent=2));print('FINISH',name,code,flush=True)
 if code:break
