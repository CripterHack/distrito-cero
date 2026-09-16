/* Test-only independent samples of quantized skin against fictional prop volumes. */
const fs=require('fs'),vm=require('vm');
for(const n of ['core','world','frontier-world','police','simulation','dynamics','interactions','frontier-simulation','occupancy','appearance','character-fit','weapon-handling','equipment','equipment-simulation','character-motion','skin-rig','dual-quaternion','hero-asset','equipment-geometry'])vm.runInThisContext(fs.readFileSync('src/'+n+'.js','utf8'));
vm.runInThisContext(fs.readFileSync('tools/qa/finger_surfaces.js','utf8'));
module.exports=globalThis.DC_FINGER_QA;
