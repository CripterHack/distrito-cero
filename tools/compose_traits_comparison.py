"""Compare actual before/after screenshots with matched per-pair cropping."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1];r=R/'qa/v016'
f=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
im=Image.new('RGB',(1200,1360),(12,19,24));d=ImageDraw.Draw(im)
d.text((28,20),'DISTRITO CERO  /  PROPORCIÓN CERVICAL',font=f(27),fill=(230,237,239))
d.text((28,62),'Mismo modelo facial, cámara, pose e iluminación de inspección',font=f(18),fill=(174,197,207))
for i,n in enumerate(['neck','profile']):
 for j,tag in enumerate(['before-','']):
  s=Image.open(r/f'review-{tag}{n}.png').convert('RGB');crop=(230,175,770,730) if n=='neck' else (270,170,770,690)
  s=s.crop(crop);s.thumbnail((546,520),Image.Resampling.LANCZOS);x=24+j*590;y=112+i*602
  im.paste(s,(x+(546-s.width)//2,y+40));d.text((x+5,y),('v0.15  /  Antes' if j==0 else 'v0.16  /  Rasgos'),font=f(21),fill=(220,232,236))
d.text((28,1320),'Capturas WebGL reales · recortes/escalado iguales por par · sin retoque',font=f(17),fill=(174,197,207))
im.save(r/'comparacion-rasgos.jpg',quality=94)
