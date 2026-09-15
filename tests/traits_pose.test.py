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
JS="""const fs=require('fs'),vm=require('vm');for(const n of ['core','world','frontier-world','police','simulation','dynamics','interactions','frontier-simulation','occupancy','appearance','character-fit','character-motion','skin-rig','dual-quaternion'])vm.runInThisContext(fs.readFileSync('src/'+n+'.js','utf8'));
const points=JSON.parse(fs.readFileSync(0,'utf8'));
const states=[{}, {lookYaw:.85},{lookYaw:-.85},{lookPitch:.30},{lookPitch:-.27},{lookYaw:.70,lookPitch:.20,lookRoll:.12},{moveSpeed:6.2,sprintBlend:1,walk:4.35},{crouch:1},{seated:true},{seated:true,lookYaw:-.70},{reach:1,lookYaw:.3}];
console.log(JSON.stringify({groups:[-1,0,1].map(length=>{const drop=DC.CharacterFit.drop(length);return {length,drop,shapes:[-1,0,1].flatMap(build=>[-1,0,1].map(neck=>({build,neck,points:points.map(p=>DC.CharacterFit.point(DC.Appearance.shapePoint(p,40,build,0,neck),drop))}))),states:states.map(n=>({n,palette:Array.from(DC.DualQuaternion.pack(DC.SkinRig.pose({...n,neckDrop:drop},1).matrices))}))};})}));"""
a=json.loads(subprocess.check_output(['node','-e',JS],cwd=R,input=json.dumps(pos.tolist()).encode()))
def deform(palette,p):
 dq=np.array(palette).reshape(-1,8)[data['j']];sg=np.where(np.sum(dq[:,:,:4]*dq[:,0:1,:4],axis=2)<0,-1,1)
 q=np.sum(dq*(data['w']/255*sg)[:,:,None],axis=1);q/=np.linalg.norm(q[:,:4],axis=1)[:,None]
 r=q[:,:4];dual=q[:,4:];dual-=r*np.sum(r*dual,axis=1)[:,None]
 trans=2*(r[:,3,None]*dual[:,:3]-dual[:,3,None]*r[:,:3]+np.cross(r[:,:3],dual[:,:3]));cr=2*np.cross(r[:,:3],p)
 return p+r[:,3,None]*cr+np.cross(r[:,:3],cr)+trans

class FittedPoses(unittest.TestCase):
 def test_neck_diameter_stays_finite_in_297_combinations(self):
  band=(pos[:,1]>1.51)&(pos[:,1]<1.528)&(abs(pos[:,2]+.018)<.02);ids=np.where(band)[0];l=ids[np.argmin(pos[ids,0])];r=ids[np.argmax(pos[ids,0])]
  count=0
  for group in a['groups']:
   for sh in group['shapes']:
    p=np.array(sh['points']);ref=np.linalg.norm(p[l]-p[r]);self.assertGreater(ref,.103)
    for st in group['states']:
     x=deform(st['palette'],p);self.assertTrue(np.isfinite(x).all());ratio=np.linalg.norm(x[l]-x[r])/ref
     self.assertTrue(.90<ratio<1.10,(group['length'],sh['build'],sh['neck'],st['n'],ratio));count+=1
  self.assertEqual(count,297)
 def test_face_landmark_distances_preserved_by_length(self):
  face=(pos[:,1]>1.552)&(pos[:,2]>.07)
  for group in a['groups']:
   for sh in group['shapes']:
    delta=np.array(sh['points'])[face]-pos[face]
    self.assertLess(np.ptp(delta[:,1]),1e-10)
    self.assertAlmostEqual(delta[0,1],-group['drop'],places=10)
 def test_base_stays_anchored_to_chest_in_head_motion(self):
  root=pos[:,1]<1.450
  # Root vertices are constrained to the thorax. It may now rotate in a large
  # look turn, so compare against its actual rigid transform, not world position.
  for group in a['groups']:
   for sh in group['shapes']:
    p=np.array(sh['points'])
    for st in group['states'][:6]:
     x=deform(st['palette'],p)
     dq=np.array(st['palette']).reshape(-1,8)[2];rr=dq[:4];dd=dq[4:];tr=2*(rr[3]*dd[:3]-dd[3]*rr[:3]+np.cross(rr[:3],dd[:3]));cr=2*np.cross(rr[:3],p[root]);expected=p[root]+rr[3]*cr+np.cross(rr[:3],cr)+tr
     self.assertLess(np.linalg.norm(x[root]-expected,axis=1).max(),.00008)
 def test_fitted_neck_edges_not_degenerate_in_study_poses(self):
  active=(pos[tri][:,:,1].min(1)>1.450)&(pos[tri][:,:,1].max(1)<1.60)
  minimum=10.;maximum=0.
  for group in a['groups']:
   for sh in group['shapes']:
    p=np.array(sh['points']);ref=deform(group['states'][0]['palette'],p)[tri]
    for st in group['states'][1:6]:
     x=deform(st['palette'],p)[tri]
     for k,j in [(0,1),(1,2),(2,0)]:
      old=np.linalg.norm(ref[:,k]-ref[:,j],axis=1);new=np.linalg.norm(x[:,k]-x[:,j],axis=1);mask=active&(old>.001)
      ratio=new[mask]/old[mask];
      if ratio.min()<minimum:
       minimum=float(ratio.min());worst={'length':group['length'],'build':sh['build'],'neck':sh['neck'],'state':st['n'],'ratio':minimum,'point':pos[tri][mask][np.argmin(ratio)].tolist()}
      
      if ratio.max()>maximum:maximum=float(ratio.max());worstMax={'length':group['length'],'build':sh['build'],'neck':sh['neck'],'state':st['n'],'ratio':maximum,'point':pos[tri][mask][np.argmax(ratio)].tolist()}
  print('WORST',json.dumps(worst),'MAX',json.dumps(worstMax),flush=True)
  self.assertGreater(minimum,.20);self.assertLess(maximum,2.2)
  (R/'qa/v016/neck-pose-metrics.json').write_text(json.dumps({'edge_ratio_min':minimum,'edge_ratio_max':maximum,'fitted_pose_combinations':297}))
if __name__=='__main__':unittest.main()
