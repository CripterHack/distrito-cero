/* v0.16: canonical surface space -> fitted cervical bind space, in metres.
   UVs and material masks remain canonical. The rig uses the SAME fitted anchors.
   This is appearance only, not a modification to gameplay collision capsules. */
'use strict';
(function(D){
 const low=1.447,high=1.550,ramp=.008,span=high-low,den=span-ramp;
 // Integrating a trapezoidal derivative avoids concentrating all compression in
 // the middle (a cubic smoothstep's peak slope was too high for a short neck).
 const weight=y=>{const t=D.clamp(y-low,0,span);return t<ramp?t*t/(2*ramp*den):t>span-ramp?1-(span-t)*(span-t)/(2*ramp*den):(t-ramp/2)/den;};
 const slope=y=>{const t=y-low;return t<=0||t>=span?0:t<ramp?t/(ramp*den):t>span-ramp?(span-t)/(ramp*den):1/den;};
 function drop(length=0){return .045-D.clamp(Number.isFinite(length)?length:0,-1,1)*.012;}
 function point(p,amount){return[p[0],p[1]-amount*weight(p[1]),p[2]];}
 function normal(n,y,amount){const sy=1-amount*slope(y),v=[n[0],n[1]/Math.max(sy,.1),n[2]],l=Math.hypot(...v);return v.map(x=>x/l);}
 function fittedBones(bones,amount){return bones.map(([name,parent,p])=>[name,parent,point(p,amount)]);}
 D.CharacterFit=Object.freeze({low,high,weight,slope,drop,point,normal,fittedBones});
})(DC);
