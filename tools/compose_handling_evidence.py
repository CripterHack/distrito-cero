"""Compose unretouched, equally cropped game screenshots with labels."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json,hashlib
R=Path(__file__).resolve().parents[1];Q=R/'qa/v018'
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',22)
small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14)
a=Image.open(Q/'before-rifle.png').convert('RGB');b=Image.open(Q/'review-rifle.png').convert('RGB');box=(225,170,850,580)
canvas=Image.new('RGB',(1286,498),(17,27,30));d=ImageDraw.Draw(canvas)
for i,(im,title) in enumerate([(a,'v0.17 · Agarre anterior'),(b,'v0.18 · Contactos orientados')]):
 x=12+i*637;canvas.paste(im.crop(box),(x,48));d.text((x+10,12),title,font=font,fill=(230,238,233))
d.text((22,473),'Misma cámara, luz y pose de referencia. Recortes iguales, sin retocar los modelos.',font=small,fill=(183,203,196))
canvas.save(Q/'comparacion-manejo.jpg',quality=93)
(Q/'comparison.json').write_text(json.dumps({'before':str(Q/'before-rifle.png'),'after':str(Q/'review-rifle.png'),'crop':box,'retouch':False,'beforeHtml':json.loads((Q/'before-rifle.json').read_text())['html'],'afterHtml':json.loads((Q/'review-rifle.json').read_text())['html']},indent=2))
print('Created',Q/'comparacion-manejo.jpg')
