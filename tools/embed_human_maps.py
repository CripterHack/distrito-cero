#!/usr/bin/env python3
"""Deterministic embedding of locally licensed maps. No network."""
from pathlib import Path
from PIL import Image
import json,base64
R=Path(__file__).resolve().parents[1];maps={}
for name,file,space in [('albedo','skin-repaired.webp','srgb'),('normal','normal.webp','linear'),('roughness','roughness.webp','linear')]:
 p=R/'assets/anatomy-source'/file;im=Image.open(p);maps[name]={'width':im.width,'height':im.height,'colorSpace':space,'uri':'data:image/webp;base64,'+base64.b64encode(p.read_bytes()).decode()}
code="""/* CC0 HM08/Aksel maps. Prepared through Higgsfield sandbox, embedded offline. */
'use strict';(function(D){
 const maps=MAPS;
 const referenceSkin=Object.freeze([.44,.275,.185]);
 function tint(skin){return referenceSkin.map((v,i)=>Math.max(.12,Math.min(3.5,(Number.isFinite(skin?.[i])?skin[i]:v)/v)));}
 D.HumanMaterials=Object.freeze({...maps,referenceSkin,tint,source:'MakeHuman HM08 / Aksel Skin by Mindfront; CC0',version:1});
})(DC);
"""
(R/'src/human-materials.js').write_text(code.replace('MAPS',json.dumps(maps,separators=(',',':'))))
