'use strict';
// Development-only official Khronos validation. Never bundled into the game.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const PIN='2.0.0-dev.3.10';
const hash=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
function checkReport(report){
 const issues=report?.issues;
 if(!issues || !Number.isInteger(issues.numErrors) || issues.numErrors<0 ||
    !Number.isInteger(issues.numWarnings) || issues.numWarnings<0 || issues.truncated!==false)
  throw new Error('Invalid or incomplete official validation report');
 if(issues.numErrors)throw new Error(`GLB validation found ${issues.numErrors} error(s)`);
 return {errors:issues.numErrors,warnings:issues.numWarnings};
}
async function main(){
 const [directory,dependency]=process.argv.slice(2);
 if(!directory||!dependency||process.argv.length!==4)throw new Error('Usage: node tools/qa/validate_glb.cjs EXPORT_DIRECTORY VALIDATOR_MODULE_DIRECTORY');
 const root=path.resolve(directory),moduleRoot=path.resolve(dependency);
 const info=JSON.parse(fs.readFileSync(path.join(moduleRoot,'package.json'),'utf8'));
 if(info.name!=='gltf-validator'||info.version!==PIN)throw new Error('Unexpected official validator package/version');
 const validator=require(moduleRoot);
 const manifestBytes=fs.readFileSync(path.join(root,'source-manifest.json'));
 const manifest=JSON.parse(manifestBytes);
 if(typeof manifest.file!=='string'||path.basename(manifest.file)!==manifest.file||!manifest.file.endsWith('.glb'))throw new Error('Invalid local GLB filename');
 const bytes=fs.readFileSync(path.join(root,manifest.file)),sha256=hash(bytes);
 if(sha256!==manifest.sha256)throw new Error('GLB does not match source manifest');
 const report=await validator.validateBytes(new Uint8Array(bytes),{
  uri:manifest.file,format:'glb',maxIssues:0,writeTimestamp:false,
  externalResourceFunction:async()=>{throw new Error('Current export must be self-contained');}
 });
 const envelope={schema:1,sha256,sourceManifestSha256:hash(manifestBytes),validatorPackage:info.version,
  validatorVersion:validator.version(),report};
 // Preserve full diagnostics even when the official report fails acceptance.
 fs.writeFileSync(path.join(root,'validator-report.json'),JSON.stringify(envelope,null,2)+'\n',{flag:'wx'});
 const counts=checkReport(report);
 const accepted={...manifest,officialValidation:'passed',validatorPackage:info.version,
  validationCounts:counts,validationReportSha256:hash(fs.readFileSync(path.join(root,'validator-report.json')))};
 fs.writeFileSync(path.join(root,'validated-manifest.json'),JSON.stringify(accepted,null,2)+'\n',{flag:'wx'});
 console.log(JSON.stringify({file:manifest.file,sha256,...counts,artisticAcceptance:'pending'}));
}
module.exports={checkReport};
if(require.main===module)main().catch(error=>{console.error(error.message);process.exitCode=1;});
