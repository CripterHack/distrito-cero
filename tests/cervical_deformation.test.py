from pathlib import Path
import json,subprocess,base64,numpy as np
R=Path(__file__).resolve().parents[1]
js="const fs=require('fs'),vm=require('vm');for(const n of ['core','character-motion','skin-rig','dual-quaternion'])vm.runInThisContext(fs.readFileSync('src/'+n+'.js','utf8'));console.log(JSON.stringify([{}, {lookYaw:.72},{lookYaw:-.72},{lookPitch:.22},{lookPitch:-.22},{lookYaw:.72,lookPitch:.22,lookRoll:.12}].map(n=>({n,palette:Array.from(DC.DualQuaternion.pack(DC.SkinRig.pose(n,1).matrices))}))));"
states=json.loads(subprocess.check_output(['node','-e',js],cwd=R))
DT=np.dtype([('p','<i2',3),('n','<i2',3),('uv','<u2',2),('j','u1',4),('w','u1',4)])
d=json.loads((R/'src/hero-asset.js').read_text().split('DC.HeroAsset=')[1].strip().rstrip(';'));data=np.frombuffer(base64.b64decode(next(p['data']for p in d['parts']if p['name']=='face')),DT)
pos=data['p'].astype(float)/1e4

def deform(palette):
 dq=np.array(palette).reshape(-1,8)[data['j']];sg=np.where(np.sum(dq[:,:,:4]*dq[:,0:1,:4],axis=2)<0,-1,1);q=np.sum(dq*(data['w']/255*sg)[:,:,None],axis=1);q/=np.linalg.norm(q[:,:4],axis=1)[:,None]
 r=q[:,:4];d=q[:,4:];d-=r*np.sum(r*d,axis=1)[:,None]
 trans=2*(r[:,3,None]*d[:,:3]-d[:,3,None]*r[:,:3]+np.cross(r[:,:3],d[:,:3]));cr=2*np.cross(r[:,:3],pos)
 return pos+r[:,3,None]*cr+np.cross(r[:,:3],cr)+trans
import unittest
class CervicalDeformation(unittest.TestCase):
 def test_cervical_edges_do_not_collapse_or_explode_in_sampled_motion(self):
  reference=deform(states[0]['palette']).reshape(-1,3,3);bind=pos.reshape(-1,3,3)
  mask=(bind[:,:,1].max(1)<1.61)&(bind[:,:,1].min(1)>1.447)
  for state in states:
   deformed=deform(state['palette']).reshape(-1,3,3)
   for k,j in [(0,1),(1,2),(2,0)]:
    l=np.linalg.norm(reference[:,k]-reference[:,j],axis=1);L=np.linalg.norm(deformed[:,k]-deformed[:,j],axis=1)
    ratio=(L/l)[mask&(l>.001)]
    self.assertGreater(float(ratio.min()),.30);self.assertLess(float(ratio.max()),1.8)
 def test_low_cervical_attachment_does_not_follow_head_turn(self):
  ref=deform(states[0]['palette']);mask=pos[:,1]<1.450
  for state in states[1:]:self.assertLess(float(np.max(np.linalg.norm((deform(state['palette'])-ref)[mask],axis=1))),.00005)
 def test_chin_retains_its_distance_to_forehead_when_head_turns(self):
  chin=np.where((pos[:,2]>.105)&(pos[:,1]>1.552)&(pos[:,1]<1.578))[0][0]
  top=np.argmin(np.linalg.norm(pos-[0,1.718,.090],axis=1))
  a=deform(states[0]['palette']);distance=np.linalg.norm(a[chin]-a[top])
  for state in states[1:]:
   a=deform(state['palette']);self.assertAlmostEqual(float(np.linalg.norm(a[chin]-a[top])),float(distance),places=5)
 def test_cervical_normals_point_outward_instead_of_turning_inside(self):
  t=pos.reshape(-1,3,3);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);c=t.mean(1);r=c-[0,0,-.018];r[:,1]=0
  mask=t[:,:,1].max(1)<1.540
  self.assertTrue(np.all(np.sum(n*r,axis=1)[mask]>0))
if __name__=='__main__':unittest.main()
