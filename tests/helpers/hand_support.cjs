'use strict';
require('./finger_surfaces.cjs');
require('node:vm').runInThisContext(require('node:fs').readFileSync('tools/qa/hand_support_surfaces.js','utf8'));
module.exports=globalThis.DC_HAND_SUPPORT_QA;
