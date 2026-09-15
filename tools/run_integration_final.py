"""Final verification/render pipeline. Same source bytes for every current report."""
from pathlib import Path
import subprocess,os,json,time
R=Path(__file__).resolve().parents[1];O=R/'qa/v015';env={**os.environ,'DISPLAY':':99'};steps=[]
commands=[('browser',['python','tools/run_integration_browser.py'],500),('captures',['python','tools/run_integration_captures.py'],700),('film',['python','tests/integration_clip.py'],450),('encode',['ffmpeg','-y','-framerate','20','-i','qa/v015/clip-frames/%04d.jpg','-c:v','libx264','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart','qa/v015/movilidad-integrada.mp4'],60)]
for name,cmd,timeout in commands:
 print('START',name,flush=True);t=time.monotonic()
 with (O/('final-'+name+'.log')).open('w') as log:
  try:p=subprocess.run(cmd,cwd=R,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=timeout);code=p.returncode
  except subprocess.TimeoutExpired:code=124
 steps.append({'step':name,'exit_code':code,'seconds':round(time.monotonic()-t,2)});(O/'final-execution.json').write_text(json.dumps(steps,indent=2));print('END',steps[-1],flush=True)
 if code:raise SystemExit(code)
