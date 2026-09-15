#!/usr/bin/env python3
"""Paired real-renderer crops. Only equal crops/resampling and editorial labels."""
from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1];O=R/'qa/v012';DEST=Path('/mnt/data')
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
font=lambda s:ImageFont.truetype(FONT,s)
records=[]
def plate(file,title,sub,items,box):
 w,h=box[2]-box[0],box[3]-box[1];pad=20;header=100;label=39;foot=48
 out=Image.new('RGB',(pad+(w+pad)*len(items),header+label+h+foot),(16,23,25));d=ImageDraw.Draw(out)
 d.text((pad,20),title,font=font(27),fill=(227,237,225));d.text((pad,59),sub,font=font(16),fill=(162,183,182))
 for i,(name,caption)in enumerate(items):
  x=pad+i*(w+pad);p=O/name;im=Image.open(p).convert('RGB');assert im.width==966 and im.height==912
  d.text((x,header),caption,font=font(19),fill=(213,232,156));out.paste(im.crop(box),(x,header+label))
 d.text((pad,out.height-29),'Capturas del juego · mismo encuadre y luz · sin retoque de los personajes',font=font(14),fill=(168,184,183));out.save(DEST/file,quality=95,subsampling=0)
 records.append({'file':file,'source_files':[name for name,_ in items],'equal_crop':box,'alteration':'Identical crop with labels only. No image-generation or character retouch.','sha256':hashlib.sha256((DEST/file).read_bytes()).hexdigest()})
plate('distrito-cero-v0.12-comparacion.jpg','DISTRITO CERO · CONTINUIDAD ANATÓMICA','Cuello, inserción torácica y transición de hombros', [('review-before-neck.png','v0.11 · Antes'),('review-neck.png','v0.12 · Actual')],(220,180,760,770))
plate('distrito-cero-v0.12-manos.jpg','DISTRITO CERO · MANOS','Muñeca, volumen palmar, uñas y deformación', [('review-before-hand.png','v0.11 · Abierta'),('review-hand.png','v0.12 · Abierta'),('review-grip.png','v0.12 · Flexión máxima')],(255,225,680,660))
(O/'comparison-composition.json').write_text(json.dumps(records,indent=2,ensure_ascii=False));print(records)
