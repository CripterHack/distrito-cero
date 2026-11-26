'use strict';
// Export the canonical seating pose and access guides in car-local metres.
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const crypto = require('node:crypto');
const sources = ['core','world','frontier-world','police','simulation','dynamics','interactions',
  'frontier-simulation','occupancy','character-motion','skin-rig','renderer','reactive-renderer'];

function sampleCabin(shiftX=0, shiftZ=0) {
  const ctx = vm.createContext({performance});
  const sourceHashes = {};
  for (const name of sources) {
    const data = fs.readFileSync(path.join(__dirname,'../src',name+'.js'));
    sourceHashes[name] = crypto.createHash('sha256').update(data).digest('hex');
    vm.runInContext(data.toString(),ctx,{filename:name+'.js'});
  }
  const D = ctx.DC, sim = new D.Simulation(new D.FrontierWorld(1337));
  sim.free = true;
  const car = sim.cars[1];
  sim.cars.forEach((other,i) => Object.assign(other,{x:300+i*6,z:0,speed:0,parked:true}));
  Object.assign(car,{x:4+shiftX,z:40+shiftZ,yaw:0,driver:null,owned:true,steerAngle:0});
  Object.assign(sim.player,{x:car.x-2.25,z:car.z+.1,y:0,car:null,yaw:Math.PI/2});
  sim.startAccess();
  const a = sim.access;
  if (a?.kind !== 'enter') throw Error('Native entry fixture is obstructed');
  const local = ({x,y=0,z}) => [x-car.x,y,z-car.z];
  const approach = local(a.door);
  a.elapsed = a.approach + a.opening/2;
  const openingHand = local(sim.accessPlayerPose().handTargets.R);
  const entry = Array.from({length:17}, (_,i) => {
    a.elapsed = a.approach + a.opening + a.entry*i/16 + Number.EPSILON;
    return local(sim.accessPlayerPose());
  });
  sim.access = null;
  car.driver = D.driverProfile(car);
  const actor = sim.driverPose(car), posed = D.SkinRig.pose(actor,1.25);
  const seatOrigin = local(actor);
  const skeleton = D.SkinRig.bones.map(([name,parent,bind],index) => {
    const matrix = posed.matrices.subarray(16*index,16*(index+1));
    const [x,y,z] = D.SkinRig.transform(matrix,bind);
    return {name,parent,point:[seatOrigin[0]+x*posed.scale,posed.rootY+y*posed.scale,seatOrigin[2]+z*posed.scale]};
  });
  // Record the actual near-vehicle instances at zero suspension, yaw and damage.
  // Select each known part by its authored size, requiring a single driver-side match.
  const parts = [];
  D.Renderer.prototype.renderCar.call({
    currentSim:sim,currentTime:0,assetParts:[{name:'BODY_shell',key:'shell'}],
    meshes:{steeringRing:true},dynamic:{},
    add(_,mesh,x,y,z,sx,sy,sz) {parts.push({mesh,p:[x-car.x,y,z-car.z],size:[sx,sy,sz]});}
  }, {...car,doorOpen:0,doorSide:-1});
  function driverPart(mesh,sizes) {
    const matches = parts.filter(({mesh:m,p,size}) => m===mesh && p[0]<0 && size.every((v,k)=>v===sizes[k]));
    if(matches.length!==1) throw Error('Native cabin part changed: '+mesh+' '+sizes);
    return matches[0];
  }
  const door = driverPart('body',[.035,.30,1.7]);
  const wheel = D.VehicleCabin.wheel;
  return {schema:1,axes:'X right, Y up, Z forward; metres',sourceHashes,approach,openingHand,entry,seatOrigin,skeleton,
    wheelCenter:[wheel.x,wheel.y,wheel.z], wheelRadius:wheel.radius, wheelTilt:wheel.tilt,
    grips:Object.fromEntries(Object.entries(D.VehicleCabin.hands(car)).map(([side,p])=>[side,local(p)])),
    cushionCenter:driverPart('body',[.48,.15,.57]).p, backrestCenter:driverPart('body',[.45,.60,.16]).p,
    hinge:[door.p[0],door.p[1],door.p[2]+door.size[2]/2],
    closedHandle:driverPart('box',[.03,.036,.21]).p};
}
module.exports = {sampleCabin};
if (require.main===module) {
  if(process.argv.length!==3) throw Error('Usage: node tools/sample_sedan_cabin.cjs NEW_JSON');
  fs.writeFileSync(process.argv[2],JSON.stringify(sampleCabin(),null,2)+'\n',{flag:'wx'});
}
