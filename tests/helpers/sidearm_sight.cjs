'use strict';
const {D,R}=require('./finger_surfaces.cjs');
require('node:vm').runInThisContext(require('node:fs').readFileSync('tools/qa/sidearm_sight.js','utf8'));
module.exports={...globalThis.DC_SIDEARM_SIGHT_QA,D,R};
