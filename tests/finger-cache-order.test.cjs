'use strict';
// Each probe is a new process: no public reset API or artificial cache warmup
// is added to the game. Both paths use the real UI selection and pose pipeline.
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const crypto=require('node:crypto'),{execFileSync}=require('node:child_process');
const hash=value=>crypto.createHash('sha256').update(JSON.stringify(value)).digest('hex');
function probe(config){
 const {D,R,scene}=require('./helpers/sidearm_sight.cjs');
 D.App=class {};D.Audio=class {};vm.runInThisContext(fs.readFileSync('src/equipment-ui.js','utf8'));
 assert.equal(D.WeaponHandling.contactFitStats().cached,0,'probe must start with a fresh module cache');
 const tick=s=>{s.time+=1/60;s.equipmentStep(1/60,{});};
 function setup(id){const s=scene(id);s.free=true;s.player.crouch=config.crouch||0;s.equipment.pitch=config.pitch||0;s.appearance.neckLength=config.neck||0;
  D.WeaponHandling.beginEquip(s);s.equipment.handling.ready=1;s.equipment.handling.rifleAim=1;s.equipment.handling.longarmAim=1;return s;}
 function read(s){const saved=JSON.stringify(s.serialize()),handling=JSON.stringify(s.equipment.handling);
  const m=D.WeaponHandling.present(s),a=D.WeaponHandling.actor(s.player,m,s.equipment),p=R.pose(a,s.time);
  assert.equal(JSON.stringify(s.serialize()),saved,'presentation changed persistent gameplay');
  assert.equal(JSON.stringify(s.equipment.handling),handling,'presentation changed transient simulation');
  return{matrices:Array.from(p.matrices),rootY:p.rootY,grips:m.grips,palms:['L','R'].map(k=>R.palmPoint(p,a,k)),
   displayItem:m.displayItem,magazine:m.magazine,partPoints:[[0,0,0],[.03,-.18,-.02],[-.025,-.14,.04]].map(q=>m.partPoint(m.displayItem==='revolver'?'body':'magazine',q)),
   time:s.time,ammo:structuredClone(s.equipment.ammo),shots:s.equipment.shots};}
 // The warm path represents an earlier independently rendered actor/session.
 if(config.warm)read(setup(config.to));
 const s=setup(config.from);
 if(config.reload){s.equipment.ammo[config.from].loaded-=2;assert.ok(s.reloadWeapon());
  for(let i=0;i<Math.floor(D.Equipment.get(config.from).reload*.46*60);i++)tick(s);}
 const before=read(s),app={sim:s,renderer:{camera:{weaponPitch:s.equipment.pitch},handlingActor:()=>s.player},
  clearWeaponInput:()=>s.cancelEquipment(),closeArsenal(){},toast(){},updateEquipmentHUD(){}};
 D.EquipmentApp.prototype.selectEquipment.call(app,config.to,false);
 const first=read(s);assert.equal(first.displayItem,config.from);
 assert.deepEqual(first.matrices,before.matrices,'first pose changed');
 assert.deepEqual(first.partPoints,before.partPoints,'old visible piece changed at frame zero');
 const snapshots=[first];
 for(let i=1;i<=60;i++){tick(s);const row=read(s);if(i%9===0||i===60)snapshots.push(row);}
 assert.equal(s.equipment.handling.handoff,undefined);
 assert.deepEqual(s.equipment.ammo,before.ammo);
 s.equipment.ammo[config.to].loaded-=2;assert.ok(s.reloadWeapon());
 for(let i=0;i<=Math.ceil(D.Equipment.get(config.to).reload*60)+1;i++){
  const row=read(s);if(i%9===0)snapshots.push(row);tick(s);
 }
 // Check finite cardinality even when other families and actors are mounted.
 for(const id of ['pistol','rifle','smg','sniper','gauss','emp'])read(setup(id));
 const stats=D.WeaponHandling.contactFitStats();assert.equal(stats.cached,4);
 return{snapshots,profiles:stats.profiles.sort((a,b)=>a.profile.localeCompare(b.profile))};
}
if(process.argv[2]==='--probe'){
 process.stdout.write(JSON.stringify(probe(JSON.parse(process.argv[3]))));
}else{
 const test=require('node:test');
 const run=config=>JSON.parse(execFileSync(process.execPath,[__filename,'--probe',JSON.stringify(config)],{encoding:'utf8',timeout:30000,maxBuffer:8*1024*1024}));
 for(const [from,to]of [['rifle','pistol'],['pistol','rifle'],['rifle','revolver'],['revolver','rifle'],['smg','revolver'],['revolver','smg'],['pistol','smg'],['smg','pistol'],['pistol','shotgun'],['shotgun','pistol'],['shotgun','revolver'],['revolver','shotgun']])for(const reload of [false,true]){
  test(`${from} -> ${to}${reload?' from reload':''} has identical finger poses with cold or previously initialized cache`,()=>{
   for(const cfg of [{},{crouch:1,pitch:.3,neck:1}]){
    const cold=run({from,to,reload,...cfg}),warm=run({from,to,reload,warm:true,...cfg});
    assert.equal(hash(cold.profiles),hash(warm.profiles),'canonical finger fits depend on first displayed prop');
    assert.equal(hash(cold.snapshots),hash(warm.snapshots),'identical action yields order-dependent pose, magazine or gameplay');
   }
  });
 }
}
