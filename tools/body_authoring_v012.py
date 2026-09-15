"""Offline native v0.12 body/hand authoring. Original surfaces, not a scanned body.
Skinning landmarks are read from the runtime skeleton by the calling generator.
"""
import numpy as np
from scipy.ndimage import gaussian_filter
from skimage.measure import marching_cubes

TORSO=[(0,.963,-.004,.170,.103),(0,1.02,-.002,.165,.102),(0,1.10,-.003,.170,.104),(0,1.19,-.006,.188,.114),(0,1.30,-.008,.207,.122),(0,1.375,-.006,.222,.112),(0,1.414,-.008,.224,.103),(0,1.444,-.010,.198,.092),(0,1.469,-.010,.123,.072),(0,1.495,-.010,.062,.056)]
SLEEVE=[(1.452,.216,.023,.030),(1.438,.224,.041,.052),(1.429,.241,.055,.063),(1.386,.255,.056,.065),(1.30,.266,.050,.060),(1.21,.274,.045,.053),(1.136,.282,.043,.049),(1.09,.286,.049,.055),(1.00,.291,.041,.048),(.918,.293,.035,.038),(.879,.293,.034,.036)]
PELVIS=[(0,.827,-.011,.108,.075),(0,.870,-.014,.162,.105),(0,.921,-.009,.177,.119),(0,.979,-.004,.170,.108),(0,1.025,-.003,.162,.101)]
LEG=[(.98,.087,-.003,.096,.103),(.878,.107,-.005,.096,.108),(.781,.109,-.006,.087,.101),(.668,.110,-.008,.074,.086),(.555,.108,.002,.061,.071),(.495,.108,.006,.057,.065),(.453,.108,.002,.058,.066),(.378,.108,-.013,.063,.075),(.291,.108,-.013,.052,.061),(.192,.108,-.006,.040,.047),(.112,.108,.001,.036,.043),(.084,.108,.002,.037,.043)]

def blend(a,b,t):
 t=float(np.clip(t,0,1));t=t*t*(3-2*t);return {a:1-t,b:t}

def hand_weights(point,k,rig):
 p=np.array(point);wx=rig['bones'][rig['ids']['hand'+k]][2][0]
 if p[1]>.863:return blend('hand'+k,'forearm'+k,(p[1]-.870)/.030)
 candidates=[]
 for finger in rig['fingers'][k]:
  points=[np.array(x) for x in finger['joints']+[finger['tip']]]
  for j,(a,b) in enumerate(zip(points[:-1],points[1:])):
   t=np.dot(p-a,b-a)/np.dot(b-a,b-a);dist=np.linalg.norm(p-(a+(b-a)*np.clip(t,0,1)))
   candidates.append((dist,finger,j,t))
 _,f,j,t=min(candidates,key=lambda x:x[0]);name=f['bones'][j]
 if j==0:
  # A broad, soft metacarpal/web transition keeps finger bases attached to the palm.
  influence=np.clip((t+.5)/.75,0,1)
  return blend('hand'+k,name,influence)
 if t<.22:return blend(f['bones'][j-1],name,(t+.18)/.4)
 if t>.82 and j<2:return blend(name,f['bones'][j+1],(t-.82)/.36)
 return {name:1.}

def garment_weights(cat,point,rig):
 x,y,z=point;x*=.9 if cat=='jacket' else 1;k='L'if x<0 else'R'
 if cat=='pants':
  if y>.868:return blend('thigh'+k,'pelvis',(y-.868)/.15)
  if y>.411:return blend('shin'+k,'thigh'+k,(y-.411)/.166)
  return blend('foot'+k,'shin'+k,(y-.09)/.108)
 body=blend('pelvis','spine',(y-.97)/.20) if y<1.17 else blend('spine','chest',(y-1.17)/.19)
 if y>1.475:return body
 # Keep the scapular cap attached, then skin the real sleeve to arm segments.
 if y>1.355:arm=blend('upperArm'+k,'clavicle'+k,(y-1.355)/.125)
 elif y>1.071:arm=blend('forearm'+k,'upperArm'+k,(y-1.071)/.132)
 else:arm=blend('hand'+k,'forearm'+k,(y-.873)/.09)
 t=float(np.clip((abs(x)-.145)/.115,0,1));t=t*t*(3-2*t);out={}
 for n,w in body.items():out[n]=out.get(n,0)+w*(1-t)
 for n,w in arm.items():out[n]=out.get(n,0)+w*t
 return out

def hand_meshes(add,rig):
 """A watertight implicit union per hand, with webbing, thenar pad and tapered digits."""
 step=.0032
 for k,s in [('R',1),('L',-1)]:
  wx=rig['bones'][rig['ids']['hand'+k]][2][0]
  lo=np.array([wx-.050,.697,-.054]);hi=np.array([wx+.050,.910,.083])
  axes=[np.arange(lo[i],hi[i]+step,step)for i in range(3)];X=np.stack(np.meshgrid(*axes,indexing='ij'),axis=-1);field=np.ones(X.shape[:-1])*10
  def ell(center,radii):
   nonlocal field
   f=(np.sqrt(np.sum(((X-center)/radii)**2,axis=-1))-1)*min(radii);field=np.minimum(field,f)
  # Dorsum, thenar and hypothenar pads. Palm is wider across Z than across X.
  ell([wx,.842,-.001],[.0135,.049,.036])
  ell([wx,.883,-.001],[.0137,.026,.026])
  ell([wx-s*.009,.832,.023],[.0140,.031,.024])
  ell([wx-s*.002,.831,-.023],[.0125,.029,.017])
  for f in rig['fingers'][k]:
   nodes=[np.array(q) for q in f['joints']+[f['tip']]]
   for j,(a,b)in enumerate(zip(nodes[:-1],nodes[1:])):
    t=np.clip(np.sum((X-a)*(b-a),axis=-1)/np.sum((b-a)**2),0,1)
    # Taper with subtle knuckle bulges. No disconnected primitive finger segments.
    radius=f['radius']*(np.interp(t,[0,1],[[1.13,1.0],[1.0,.87],[.87,.61]][j]))
    d=np.linalg.norm(X-a-t[...,None]*(b-a),axis=-1)-radius
    field=np.minimum(field,d)
  field=gaussian_filter(field,.48)
  v,f,_,_=marching_cubes(field,0,spacing=(step,step,step),allow_degenerate=False);v+=lo
  # Sub-millimetre dorsal tendons follow the metacarpals and fade into the wrist.
  for digit in rig['fingers'][k]:
   if digit['name']=='thumb':continue
   progress=np.clip((v[:,1]-.81)/.076,0,1);center_z=digit['joints'][0][2]*(1-progress*.78)
   ridge=.0007*np.exp(-((v[:,2]-center_z)/.0034)**2)*np.sin(progress*np.pi)**2
   ridge*=np.clip((s*(v[:,0]-wx)-.002)/.010,0,1)
   v[:,0]+=s*ridge
  add('Continuous palm, webbing and five digits '+k,v,f,'skin','hand'+k)
  # Fit nail plates to the actual meshed dorsum by ray/triangle intersection along X.
  # Nominal analytic capsule radii differ from the filtered union and can bury nails.
  surface=v[f];origin=surface[:,0,1:];U=surface[:,1,1:]-origin;V=surface[:,2,1:]-origin
  det=U[:,0]*V[:,1]-U[:,1]*V[:,0];valid_tri=np.abs(det)>1e-12;den=np.where(valid_tri,det,1.)
  def dorsum(y,z):
   Q=np.array([y,z])-origin;b=(Q[:,0]*V[:,1]-Q[:,1]*V[:,0])/den;c=(U[:,0]*Q[:,1]-U[:,1]*Q[:,0])/den
   valid=valid_tri&(b>=-1e-7)&(c>=-1e-7)&(b+c<=1.0000001)
   if not valid.any():return None
   xx=surface[:,0,0]+b*(surface[:,1,0]-surface[:,0,0])+c*(surface[:,2,0]-surface[:,0,0])
   return s*np.max(s*xx[valid])

  # Nails are fitted shallow plates on the distal segment, not large floating blocks.
  for digit in rig['fingers'][k]:
   a=np.array(digit['joints'][2]);b=np.array(digit['tip']);direction=b-a
   side=np.cross(direction,[s,0,0]);side/=np.linalg.norm(side);p=[];tri=[];N=7;W=6
   for i in range(N):
    t=.30+.52*i/(N-1);width=digit['radius']*.58*np.sin(np.pi*(.22+.57*i/(N-1)))
    for j in range(W):
     u=-1+2*j/(W-1);c=a+direction*t+side*u*width
     c[0]+=s*(digit['radius']*(.87-.26*t)*np.sqrt(max(.30,1-(u*.65)**2))+.00010)
     fitted=dorsum(c[1],c[2])
     if fitted is not None:c[0]=fitted+s*.00025
     p.append(c)
   for i in range(N-1):
    for j in range(W-1):n=i*W+j;tri.extend([[n,n+1,n+W+1],[n,n+W+1,n+W]])
   add('Fitted nail '+k+digit['name'],p,tri,'nails','hand'+k)

def shoe_meshes(add,loft,ellipsoid):
 """Longitudinal shoe last with a flatter outsole, toe spring and actual instep."""
 from scipy.interpolate import PchipInterpolator
 profile=np.array([[-.075,.024,.070],[-.061,.048,.114],[-.026,.052,.147],[.019,.052,.140],[.062,.057,.114],[.113,.057,.092],[.163,.049,.081],[.190,.032,.063],[.205,.006,.040]])
 zvals=np.linspace(profile[0,0],profile[-1,0],33);width=PchipInterpolator(profile[:,0],profile[:,1])(zvals);top=PchipInterpolator(profile[:,0],profile[:,2])(zvals)
 for k,s in [('L',-1),('R',1)]:
  center=s*.108;seg=24
  for material in ['rubber','sole']:
   p=[];tri=[]
   for j,(z,w,h)in enumerate(zip(zvals,width,top)):
    for i in range(seg):
     a=i*2*np.pi/seg
     # Flat bottom and restrained toe uplift, a shaped shoe rather than a scaled sphere.
     yy=max(-.55,np.sin(a));yy=(yy+.55)/1.55
     if material=='rubber':y=.036+(h-.036)*yy;xx=w*np.cos(a)
     else:y=.015+.024*yy;xx=(w+.002)*np.cos(a)
     p.append([center+xx,y,z])
   for j in range(len(zvals)-1):
    for i in range(seg):a=j*seg+i;b=j*seg+(i+1)%seg;tri.extend([[a,b,b+seg],[a,b+seg,a+seg]])
   for i in range(1,seg-1):tri.extend([[0,i+1,i],[(len(zvals)-1)*seg,(len(zvals)-1)*seg+i,(len(zvals)-1)*seg+i+1]])
   add('Shaped shoe '+material+k,p,tri,material,'foot'+k)
  for i in range(5):
   z=.003+i*.018;y=float(PchipInterpolator(profile[:,0],profile[:,2])(z))+.0017
   ellipsoid('Textile lace'+k+str(i),(center,y,z),(.024+i*.0004,.0014,.0018),'sole','foot'+k,12,4)
  # Heel pull loop and small tongue use the same foot transform.
  loft('Tongue '+k,[(center,.088,-.007,.019,.024),(center,.15,-.007,.018,.021),(center,.164,-.008,.015,.013)],'pants','foot'+k,16,2)
