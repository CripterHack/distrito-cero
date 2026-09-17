'use strict';
require('./finger_surfaces.cjs');
require('node:vm').runInThisContext(require('node:fs').readFileSync('tools/qa/thenar_surfaces.js','utf8'));
module.exports={...globalThis.DC_THENAR_QA,D:globalThis.DC,R:globalThis.DC.SkinRig};
