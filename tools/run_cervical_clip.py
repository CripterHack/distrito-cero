from pathlib import Path
import subprocess,os,json,time
R=Path(__file__).resolve().parents[1];O=R/'qa/v014'
# Avoid competing render jobs. Wait only for the capture runner started in this task.
for i in range(300):
 if (O/'capture-execution.json').exists() and len(json.loads((O/'capture-execution.json').read_text()))==16:break
 time.sleep(2)
else:raise RuntimeError('Capture batch did not finish; no duplicate render job started')
with (O/'clip-execution.log').open('w') as f:
 p=subprocess.run(['python','tests/cervical_clip.py'],cwd=R,env={**os.environ,'DISPLAY':':99'},stdout=f,stderr=subprocess.STDOUT,timeout=420)
if p.returncode:raise SystemExit(p.returncode)
p=subprocess.run(['ffmpeg','-y','-framerate','20','-i','qa/v014/clip-frames/%04d.jpg','-c:v','libx264','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart','qa/v014/movilidad-cervical.mp4'],cwd=R,stdout=subprocess.DEVNULL,stderr=(O/'ffmpeg.log').open('w'))
raise SystemExit(p.returncode)
