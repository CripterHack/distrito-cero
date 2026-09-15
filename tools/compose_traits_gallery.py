"""Lay out actual captures with identical crop/scale. Never retouch character pixels."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1]; O=R/'qa/v016'
f=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
labels=['Corto clásico','Rapado','Hacia atrás','Sin cabello','Corto texturizado','Degradado alto','Media melena','Flequillo lateral','Undercut asimétrico','Recogido corto','Melena recta']
W,H=1512,1500; canvas=Image.new('RGB',(W,H),(12,19,24));d=ImageDraw.Draw(canvas)
d.text((32,22),'DISTRITO CERO  /  RASGOS  v0.16',font=f(26),fill=(226,235,240))
d.text((32,64),'11 estilos de cabello · mismo modelo, cámara e iluminación',font=f(18),fill=(171,195,205))
for i,label in enumerate(labels):
 x=24+(i%4)*372;y=113+(i//4)*443
 im=Image.open(O/f'hair-{i:02d}.png').convert('RGB').crop((218,213,760,795)).resize((350,376),Image.Resampling.LANCZOS)
 canvas.paste(im,(x,y));d.text((x,y+386),f'{i+1:02d}  {label}',font=f(16),fill=(218,231,235))
x=24+3*372;y=113+2*443
d.text((x+20,y+72),'VISTA DEL MOTOR',font=f(22),fill=(218,231,235))
for j,t in enumerate(['Geometría 3D compartida','Tres niveles de detalle','Color y volumen editables','Sin pelo físico','Sin retoque del personaje']):d.text((x+20,y+123+j*31),t,font=f(17),fill=(171,195,205))
d.text((32,H-53),'Capturas WebGL reales · posiciones de estudio · no representan un benchmark',font=f(17),fill=(171,195,205))
canvas.save(O/'galeria-peinados.jpg',quality=93)
