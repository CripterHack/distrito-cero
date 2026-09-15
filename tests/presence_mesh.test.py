"""Scalp clearance regression using the actual quantized native output."""
from pathlib import Path
import json,struct,base64,unittest,math
from scipy.interpolate import PchipInterpolator
R=Path(__file__).resolve().parents[1]
class Mesh(unittest.TestCase):
 def test_hair_outside_skull(self):
  txt=(R/'src/hero-asset.js').read_text();d=json.loads(txt.split('DC.HeroAsset=',1)[1].rstrip().rstrip(';'))
  part=next(p for p in d['parts'] if p['name']=='hair');raw=base64.b64decode(part['data']);ys=[1.556,1.579,1.61,1.645,1.678,1.710,1.746,1.779,1.810,1.831];rx=PchipInterpolator(ys,[.054,.076,.096,.112,.124,.126,.121,.108,.078,.014]);front=PchipInterpolator(ys,[.081,.101,.106,.106,.109,.107,.105,.091,.064,.013]);back=PchipInterpolator(ys,[.047,.062,.079,.102,.114,.119,.117,.105,.079,.014]);minimum=10;checked=0
  for off in range(0,len(raw),24):
   px,py,pz=struct.unpack_from('<hhh',raw,off);x=px/10000/.72;y=(py/10000-1.60)/.98+1.63;z=pz/10000/.87
   if y<1.735 or y>1.823:continue
   radius=math.hypot(x/float(rx(y)),z/float(front(y)if z>=0 else back(y)));minimum=min(minimum,radius);checked+=1
  self.assertGreater(checked,500);self.assertGreater(minimum,.998,f'hair intersects scalp: normalized radius {minimum}')
if __name__=='__main__':unittest.main()
