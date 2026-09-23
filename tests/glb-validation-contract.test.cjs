'use strict';
const test=require('node:test'), assert=require('node:assert/strict');
let checks;
try { checks=require('../tools/qa/validate_glb.cjs'); } catch(error) { if(error.code!=='MODULE_NOT_FOUND')throw error; }
test('missing or truncated reports cannot count as GLB validation',()=>{
 assert.equal(typeof checks?.checkReport,'function');
 for(const value of [null,{}, {issues:{numErrors:0,numWarnings:0,truncated:true}}, {issues:{numErrors:NaN,numWarnings:0,truncated:false}}]) {
  assert.throws(()=>checks.checkReport(value),/invalid|incomplete/i);
 }
});
test('a validator error fails acceptance without suppressing its diagnostic',()=>{
 assert.equal(typeof checks?.checkReport,'function');
 assert.throws(()=>checks.checkReport({issues:{numErrors:1,numWarnings:0,truncated:false}}),/1 error/);
});
test('warnings are reported separately, never counted as zero issues or art approval',()=>{
 assert.equal(typeof checks?.checkReport,'function');
 assert.deepEqual(checks.checkReport({issues:{numErrors:0,numWarnings:2,truncated:false}}),{errors:0,warnings:2});
});
