"""Compose labeled, equally cropped renderer screenshots. No image synthesis or retouching."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
R=Path(__file__).resolve().parents[1];O=R/'qa/v010';OUT=Path('/mnt/data')
font=Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf');bold=font.with_name('DejaVuSans-Bold.ttf')
def ft(size,b=False):return ImageFont.truetype(str(bold if b else font),size)
records=[]
def board(filename,title,sub,pair,crop,labels,footer):
 a,b=[Image.open(O/name).convert('RGB')for name in pair];assert a.size==b.size
 w,h=crop[2]-crop[0],crop[3]-crop[1];cw,ch=round(w*1.6),round(h*1.6);gap=24;W=cw*2+gap*3;H=ch+180
 canvas=Image.new('RGB',(W,H),'#111b24');d=ImageDraw.Draw(canvas)
 d.text((gap,20),title,font=ft(24,True),fill='#eef3f3');d.text((gap,58),sub,font=ft(13),fill='#aebfca')
 for i,(im,label) in enumerate(zip([a,b],labels)):
  x=gap+i*(cw+gap);d.text((x,90),label,font=ft(16,True),fill='#b3d5cc');canvas.paste(im.crop(crop).resize((cw,ch),Image.Resampling.LANCZOS),(x,120))
 d.text((gap,H-36),footer,font=ft(12),fill='#aebfca');canvas.save(OUT/filename,quality=92,subsampling=0)
 records.append({'output':filename,'sources':[{'file':n,'sha256':hashlib.sha256((O/n).read_bytes()).hexdigest()}for n in pair],'crop':crop,'same_crop_for_both':True,'scale':1.6,'alterations':'Equal crop/resizing plus labels outside images only. No model retouching, generative images or artificial in-game performance.'})
board('distrito-cero-v0.10-comparacion.jpg','DISTRITO CERO · CUERPO COMPLETO','Comparación de versiones sobre la misma escena del juego',('review-before-full.png','review-full.png'),(307,167,589,600),('v0.9 · Anatomía','v0.10 · Constitución'),'Misma cámara, iluminación y pose de reposo. Capturas del renderer WebGL.')
board('distrito-cero-v0.10-manos.jpg','DISTRITO CERO · MANOS ARTICULADAS','Una superficie continua por mano y tres articulaciones por dedo',('review-hand.png','review-hand-grip.png'),(284,162,594,533),('Mano extendida','Flexión máxima de prueba'),'Poses de inspección, no simulación de contacto físico individual por dedo.')
(O/'composition.json').write_text(json.dumps(records,indent=2,ensure_ascii=False))
