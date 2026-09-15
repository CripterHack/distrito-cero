"""Equal crops and labels on actual browser captures. No model retouching."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
R=Path(__file__).resolve().parents[1];Q=R/'qa/v019'
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',22)
small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14)
box=(225,110,910,640);width,height=box[2]-box[0],box[3]-box[1]
canvas=Image.new('RGB',(width*2+36,2*(height+65)+36),(17,27,30));d=ImageDraw.Draw(canvas);pairs=[]
for row,mode in enumerate(['rifle','pistol']):
 for column,(prefix,title) in enumerate([('before-','v0.18 · Anterior'),('review-','v0.19 · Contacto articulado')]):
  im=Image.open(Q/(prefix+mode+'.png')).convert('RGB');x=12+column*(width+12);y=12+row*(height+65)
  d.text((x+10,y),title+' · '+('Fusil' if mode=='rifle' else 'Pistola'),font=font,fill=(230,238,233));canvas.paste(im.crop(box),(x,y+36))
 pairs.append({'mode':mode,'beforeHtml':json.loads((Q/('before-'+mode+'.json')).read_text())['html'],'afterHtml':json.loads((Q/('review-'+mode+'.json')).read_text())['html'],'crop':box})
d.text((22,canvas.height-28),'Mismos encuadres, luz e inputs. Recortes iguales. Sin retoque de personajes ni armas.',font=small,fill=(183,203,196))
canvas.save(Q/'comparacion-contacto.jpg',quality=93)
principal=canvas.crop((0,0,canvas.width,height+70));pd=ImageDraw.Draw(principal);pd.text((22,height+52),'Misma cámara, luz e inputs. Recorte idéntico, sin retoque de modelos.',font=small,fill=(183,203,196));principal.save(Q/'comparacion-principal.jpg',quality=93)
(Q/'comparison.json').write_text(json.dumps({'pairs':pairs,'retouch':False},indent=2))
# Representative frames for manual animation inspection. Not part of the frame count.
frames=Q/'contact-frames';sheet=Image.new('RGB',(1200,3*298),(17,27,30));sd=ImageDraw.Draw(sheet)
for i,n in enumerate([0,20,32,40,54,66,78,94,116]):
 im=Image.open(frames/f'{n:04d}.png').convert('RGB');im.thumbnail((396,273));x=(i%3)*400;y=(i//3)*298;sheet.paste(im,(x,y+23));sd.text((x+8,y+3),'Fotograma '+str(n),font=small,fill=(230,238,233))
sheet.save(Q/'clip-contact-sheet.jpg',quality=89)
print('Comparison and film contact sheet saved')
