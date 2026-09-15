"""Identical before/after crops, labels only. Does not alter model pixels."""
from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1];O=R/'qa/v014'
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
large=ImageFont.truetype(font,28);medium=ImageFont.truetype(font,20);small=ImageFont.truetype(font,16)
width=1228;height=1174;out=Image.new('RGB',(width,height),(12,19,24));d=ImageDraw.Draw(out)
d.text((26,22),'DISTRITO CERO · EQUILIBRIO CERVICAL',fill=(230,239,233),font=large)
d.text((26,65),'v0.13 · ANTES',fill=(188,202,209),font=medium)
d.text((634,65),'v0.14 · ACTUALIZADO',fill=(202,227,188),font=medium)
records=[]
for row,(pose,crop,cap) in enumerate([
 ('neck',(265,285,715,655),'Tres cuartos · unión con mandíbula y prenda'),
 ('profile',(275,285,725,655),'Perfil · contorno cervical y nuca')]):
 y=104+row*514
 for col,tag in enumerate(['before-','']):
  path=O/f'review-{tag}{pose}.png';im=Image.open(path).convert('RGB').crop(crop).resize((582,479),Image.Resampling.LANCZOS);out.paste(im,(26+608*col,y));records.append({'source':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'crop':crop,'output_size':[582,479]})
 d.text((26,y+485),cap,fill=(195,210,213),font=small)
d.text((26,1138),'Capturas del motor · mismos encuadres, luz y entradas de pose · recortes iguales, sin retocar los modelos',fill=(171,191,200),font=small)
out.save(O/'comparacion-cervical.jpg',quality=95)
(O/'comparison-manifest.json').write_text(json.dumps({'operation':'Identical crop and resize per pair; added labels only','records':records},indent=2))
# Six stills from the actual recorded sequence to inspect motion separately.
if (O/'clip-frames/0159.jpg').exists():
 tile=(322,304);sheet=Image.new('RGB',(tile[0]*3,tile[1]*2))
 for i,frame in enumerate([0,20,60,80,100,140]):
  im=Image.open(O/f'clip-frames/{frame:04d}.jpg').convert('RGB');im.thumbnail(tile,Image.Resampling.LANCZOS);sheet.paste(im,((i%3)*tile[0],(i//3)*tile[1]))
 sheet.save(O/'film-contact-sheet.jpg',quality=95)
print('Composed matched review photographs, no character retouching')
