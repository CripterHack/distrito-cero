'use strict';
const test=require('node:test'), assert=require('node:assert/strict');
const fs=require('node:fs'),os=require('node:os'),path=require('node:path'),crypto=require('node:crypto');
const {spawnSync}=require('node:child_process');
const hash=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
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

// This adapter exercises the CLI's asynchronous input-integrity boundary, not
// Khronos geometry validation. Its full report must survive a rejected export.
function validationFixture(change,inspect){
 const root=fs.mkdtempSync(path.join(os.tmpdir(),'dc-validation-integrity-'));
 try{
  const output=path.join(root,'export'),dependency=path.join(root,'validator');
  fs.mkdirSync(output);fs.mkdirSync(dependency);
  let json=JSON.stringify({asset:{version:'2.0'},extras:{fixture:'input-integrity'}});
  json+=' '.repeat((4-json.length%4)%4);
  const bytes=Buffer.alloc(20+Buffer.byteLength(json));
  bytes.write('glTF');bytes.writeUInt32LE(2,4);bytes.writeUInt32LE(bytes.length,8);
  bytes.writeUInt32LE(Buffer.byteLength(json),12);bytes.writeUInt32LE(0x4e4f534a,16);bytes.write(json,20);
  const file=path.join(output,'human.glb'),manifestFile=path.join(output,'source-manifest.json');
  const manifest={schema:1,file:'human.glb',sha256:hash(bytes),artisticAcceptance:'pending'};
  const manifestBytes=JSON.stringify(manifest)+'\n';
  fs.writeFileSync(file,bytes);fs.writeFileSync(manifestFile,manifestBytes);
  const report={issues:{numErrors:0,numWarnings:0,numInfos:1,numHints:0,truncated:false,
   messages:[{code:'TEST_FIXTURE',message:'Input-integrity adapter; not official validation',severity:2,pointer:''}]}};
  const mutation=change==='glb'
   ? `fs.appendFileSync(${JSON.stringify(file)},'changed during validation');`
   : change==='manifest'? `fs.appendFileSync(${JSON.stringify(manifestFile)},' ');`:'';
  fs.writeFileSync(path.join(dependency,'package.json'),JSON.stringify({name:'gltf-validator',version:'2.0.0-dev.3.10',main:'index.cjs'}));
  fs.writeFileSync(path.join(dependency,'index.cjs'),`
   const fs=require('node:fs');
   module.exports={version:()=> 'input-integrity-test-adapter',validateBytes:async()=>{
    await new Promise(resolve=>setImmediate(resolve));
    ${mutation}
    return ${JSON.stringify(report)};
   }};
  `);
  const run=spawnSync(process.execPath,[path.resolve(__dirname,'../tools/qa/validate_glb.cjs'),output,dependency],{encoding:'utf8'});
  assert.ifError(run.error);
  const saved=JSON.parse(fs.readFileSync(path.join(output,'validator-report.json'),'utf8'));
  assert.deepEqual(saved.report,report,'preserve the complete diagnostic even on rejection');
  assert.equal(saved.sha256,hash(bytes));
  assert.equal(saved.sourceManifestSha256,hash(manifestBytes));
  inspect({run,output,manifest,saved});
 }finally{fs.rmSync(root,{recursive:true,force:true});}
}

test('unchanged inputs retain successful validation and exact report provenance',()=>{
 validationFixture(null,({run,output,manifest})=>{
  assert.equal(run.status,0,run.stderr);
  const accepted=JSON.parse(fs.readFileSync(path.join(output,'validated-manifest.json'),'utf8'));
  assert.equal(accepted.officialValidation,'passed');
  assert.equal(accepted.sha256,manifest.sha256);
  assert.equal(accepted.artisticAcceptance,'pending');
  assert.equal(accepted.validationReportSha256,hash(fs.readFileSync(path.join(output,'validator-report.json'))));
 });
});

for(const change of ['glb','manifest'])test(`${change} replacement during validation rejects acceptance but keeps diagnostics`,()=>{
 validationFixture(change,({run,output})=>{
  assert.equal(run.status,1,run.stdout);
  assert.match(run.stderr,/input changed during validation/i);
  assert.equal(fs.existsSync(path.join(output,'validated-manifest.json')),false);
 });
});
