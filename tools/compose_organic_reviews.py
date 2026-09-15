from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1];Q=R/'qa/v013';OUT=Path('/mnt/data')
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
F=lambda n:ImageFont.truetype(font,n)
def pair(names,labels,out,crop,title,sub):
 ims=[Image.open(Q/name).convert('RGB').crop(crop)for name in names]
 assert ims[0].size==ims[1].size
 w,h=ims[0].size;gap=16;margin=28;top=102;bottom=52
 sheet=Image.new('RGB',(w*2+gap+margin*2,h+top+bottom),(12,21,28));d=ImageDraw.Draw(sheet)
 d.text((margin,19),title,font=F(23),fill=(232,240,241))
 for i,im in enumerate(ims):
  x=margin+i*(w+gap);d.text((x,65),labels[i],font=F(16),fill=(192,221,206));sheet.paste(im,(x,top))
 d.text((margin,top+h+16),sub,font=F(12),fill=(181,197,203));sheet.save(OUT/out,quality=94)
pair(['review-before-run.png','review-run.png'],['v0.12 · postura anterior','v0.13 · apoyos y brazos coordinados'],'distrito-cero-v0.13-comparacion.jpg',(250,205,805,747),'DISTRITO CERO / MOVIMIENTO','Motor real · misma cámara, luz, velocidad y fase de referencia · sin retoque del personaje')
pair(['review-hand.png','review-grip.png'],['Mano abierta','Flexión de estudio'],'distrito-cero-v0.13-manos.jpg',(275,220,752,690),'DISTRITO CERO / MANOS','Capturas del motor · no es contacto físico por dedo ni una nueva malla escaneada')
