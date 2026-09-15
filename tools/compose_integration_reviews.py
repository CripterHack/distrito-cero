from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
R=Path(__file__).resolve().parents[1]/'qa/v015'
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
canvas=Image.new('RGB',(1160,1118),(13,22,27));d=ImageDraw.Draw(canvas)
d.text((34,22),'DISTRITO CERO · INTEGRACIÓN CERVICAL',font=ImageFont.truetype(bold,26),fill=(225,235,232))
d.text((35,60),'Misma cámara, iluminación y pose · capturas del motor',font=ImageFont.truetype(font,17),fill=(172,193,195))
box=(255,200,740,650);cell=(540,448)
for row,name in enumerate(['neck','profile']):
 for col,tag in enumerate(['before-','']):
  source=Image.open(R/f'review-{tag}{name}.png').convert('RGB');assert source.size==(966,912),source.size
  frame=ImageOps.contain(source.crop(box),cell,Image.Resampling.LANCZOS)
  x=34+col*552;y=133+row*476;canvas.paste(frame,(x+(cell[0]-frame.width)//2,y))
  d.text((x,y-30),('v0.14 · anterior'if col==0 else 'v0.15 · cuello integrado')+(' · perfil'if row else ''),font=ImageFont.truetype(bold,18),fill=(209,221,221))
d.text((34,1083),'Recorte y ampliación idénticos. Sin retoques ni imágenes generadas.',font=ImageFont.truetype(font,17),fill=(172,193,195))
canvas.save(R/'comparacion-integracion.jpg',quality=94)
# All source versions/settings are checked by the release audit.
