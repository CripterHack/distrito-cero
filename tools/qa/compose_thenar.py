#!/usr/bin/env python3
"""Compose comparable renderer frames; no retouch, masks or generated imagery.
Pillow is an authoring-only dependency. Reports must share each case's camera.
"""
from pathlib import Path
import argparse,hashlib,json
from PIL import Image,ImageDraw,ImageFont

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--before',type=Path,required=True);p.add_argument('--after',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    before=json.loads((a.before/'report.json').read_text());after=json.loads((a.after/'report.json').read_text());b={x['name']:x for x in before['cases']};c={x['name']:x for x in after['cases']}
    names=['rifle-L-fore-c0','rifle-L-magazine-c0','pistol-L-pistolMagazine-c0'];a.output.mkdir(parents=True,exist_ok=True)
    font=ImageFont.load_default();canvas=Image.new('RGB',(1600,756*len(names)),(21,25,29));draw=ImageDraw.Draw(canvas)
    for i,name in enumerate(names):
        assert b[name]['camera']==c[name]['camera'],'Changed camera: '+name
        for j,folder in enumerate([a.before,a.after]):
            image=Image.open(folder/(name+'.png')).convert('RGB');assert image.size==(800,720)
            canvas.paste(image,(j*800,i*756+36));draw.text((j*800+18,i*756+8),('ANTES'if j==0 else'DESPUES')+' | '+name,font=font,fill='white')
    canvas.save(a.output/'comparison.jpg',quality=88)
    for stem,name in [('preview','rifle-L-fore-c0'),('preview-magazine','rifle-L-magazine-c0')]:
        out=Image.new('RGB',(512,276),(21,25,29));di=ImageDraw.Draw(out)
        for j,folder in enumerate([a.before,a.after]):
            im=Image.open(folder/(name+'.png')).convert('RGB').crop((245,208,565,528)).resize((256,256),Image.Resampling.LANCZOS)
            out.paste(im,(j*256,20));di.text((j*256+8,3),'ANTES'if j==0 else'DESPUES',font=font,fill='white')
        out.save(a.output/(stem+'.jpg'),quality=48,optimize=True)
    meta={'baseCommit':'ef905ece47bc8901c28c381ef081486e72fa8730','beforeHtmlSha256':before['sha256'],'afterHtmlSha256':after['sha256'],'cohort':'Fixed geometric band, without influence thresholds; 806 left and 803 right points.','captureContract':'Same camera/light/prepared clock. No retouch. Not a hardware FPS claim.','before':before['cases'],'after':after['cases'],'artisticAcceptance':'pending; bounded technical change, not hyperrealistic acceptance'}
    (a.output/'reference.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
