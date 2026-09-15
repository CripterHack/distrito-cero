"""Measure the actual neck mesh across constitutions and animated production poses.
These checks are bounded geometric regressions, not exhaustive self-collision or biomechanics.
"""
import base64,json,subprocess,unittest
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1]
DT=np.dtype([('p','<i2',3),('n','<i2',3),('uv','<u2',2),('j','u1',4),('w','u1',4)])
d=json.loads((R/'src/hero-asset.js').read_text().split('DC.HeroAsset=')[1].strip().rstrip(';'))
raw=np.frombuffer(base64.b64decode(next(p['data'] for p in d['parts'] if p['name']=='face')),DT)
v,first,inv=np.unique(raw['p'],axis=0,return_index=True,return_inverse=True);data=raw[first];pos=v/1e4;tri=inv.reshape(-1,3)
JS="""const fs=require('fs'),vm=require('vm');for(const n of ['core','world','frontier-world','police','simulation','dynamics','interactions','frontier-simulation','occupancy','appearance','character-motion','skin-rig','dual-quaternion'])vm.runInThisContext(fs.readFileSync('src/'+n+'.js','utf8'));
const points=JSON.parse(fs.readFileSync(0,'utf8'));
const states=[{}, {lookYaw:.85},{lookYaw:-.85},{lookPitch:.30},{lookPitch:-.27},{lookYaw:.70,lookPitch:.20,lookRoll:.12},{moveSpeed:6.2,sprintBlend:1,walk:4.35},{crouch:1},{seated:true},{seated:true,lookYaw:-.70},{reach:1,lookYaw:.3}];
console.log(JSON.stringify({shapes:[-1,0,1].flatMap(build=>[-1,0,1].map(neck=>({build,neck,points:points.map(p=>DC.Appearance.shapePoint(p,40,build,0,neck))}))),states:states.map(n=>({n,palette:Array.from(DC.DualQuaternion.pack(DC.SkinRig.pose(n,1).matrices))}))}));"""
a=json.loads(subprocess.check_output(['node','-e',JS],cwd=R,input=json.dumps(pos.tolist()).encode()))
def deform(palette,p):
 dq=np.array(palette).reshape(-1,8)[data['j']];sg=np.where(np.sum(dq[:,:,:4]*dq[:,0:1,:4],axis=2)<0,-1,1)
 q=np.sum(dq*(data['w']/255*sg)[:,:,None],axis=1);q/=np.linalg.norm(q[:,:4],axis=1)[:,None]
 r=q[:,:4];dual=q[:,4:];dual-=r*np.sum(r*dual,axis=1)[:,None]
 trans=2*(r[:,3,None]*dual[:,:3]-dual[:,3,None]*r[:,:3]+np.cross(r[:,:3],dual[:,:3]));cr=2*np.cross(r[:,:3],p)
 return p+r[:,3,None]*cr+np.cross(r[:,:3],cr)+trans
class Poses(unittest.TestCase):
 def test_midneck_diameter_is_retained_during_99_pose_constitution_pairs(self):
  band=(pos[:,1]>1.51)&(pos[:,1]<1.528)&(abs(pos[:,2]+.018)<.02)
  ids=np.where(band)[0];l=ids[np.argmin(pos[ids,0])];r=ids[np.argmax(pos[ids,0])]
  ratios=[]
  for sh in a['shapes']:
   p=np.array(sh['points']);ref=np.linalg.norm(p[l]-p[r]);self.assertGreater(ref,.103)
   for st in a['states']:
    x=deform(st['palette'],p);self.assertTrue(np.isfinite(x).all());ratio=np.linalg.norm(x[l]-x[r])/ref;ratios.append(float(ratio));self.assertTrue(.93<ratio<1.08,ratio)
  self.assertEqual(len(ratios),99)
 def test_no_extra_edge_collapse_for_all_proportions_and_neck_poses(self):
  mask=pos[tri]
  active=(mask[:,:,1].min(1)>1.447)&(mask[:,:,1].max(1)<1.60)
  for sh in a['shapes']:
   p=np.array(sh['points']);ref=deform(a['states'][0]['palette'],p)[tri]
   for st in a['states'][:6]:
    x=deform(st['palette'],p)[tri]
    for k,j in [(0,1),(1,2),(2,0)]:
     old=np.linalg.norm(ref[:,k]-ref[:,j],axis=1);new=np.linalg.norm(x[:,k]-x[:,j],axis=1);m=active&(old>.001)
     ratio=new[m]/old[m];self.assertGreater(ratio.min(),.4);self.assertLess(ratio.max(),1.8)
 def test_body_root_stays_on_chest_and_jaw_on_head_with_all_proportions(self):
  root=pos[:,1]<1.450;chin=np.where((pos[:,2]>.105)&(pos[:,1]>1.552)&(pos[:,1]<1.578))[0][0];fore=np.argmin(np.linalg.norm(pos-[0,1.718,.090],axis=1))
  for sh in a['shapes']:
   p=np.array(sh['points']);ref=deform(a['states'][0]['palette'],p);dist=np.linalg.norm(ref[chin]-ref[fore])
   for st in a['states'][1:6]:
    x=deform(st['palette'],p);self.assertLess(np.linalg.norm(x[root]-ref[root],axis=1).max(),.00005);self.assertAlmostEqual(np.linalg.norm(x[chin]-x[fore]),dist,places=5)
if __name__=='__main__':unittest.main()
