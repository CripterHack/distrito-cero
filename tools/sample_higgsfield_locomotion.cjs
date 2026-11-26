'use strict';
// Sample the runtime's actual gait, ground contacts and upper-body palette.
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const ctx = vm.createContext({});
for (const name of ['core', 'character-motion', 'skin-rig']) {
  const file = path.join(__dirname, '..', 'src', name + '.js');
  vm.runInContext(fs.readFileSync(file, 'utf8'), ctx, { filename: file });
}
const D = ctx.DC;
function sample(name, speed, count, sprintBlend = 0) {
  const duration = speed ? 1 / D.NaturalMotion.gait(speed,sprintBlend).hz : 4;
  const frames = [];
  for (let i = 0; i <= count; i++) {
    const phase = i === count ? 0 : 2 * Math.PI * i / count;
    // A periodic sweep of the idle sampler starts and finishes at rest.
    const gameTime = i === count ? 0 : i * duration / count;
    const time = speed ? gameTime : 2 - 2 * Math.cos(phase);
    const input = { moveSpeed: speed, walk: speed ? phase : 0, sprintBlend };
    const pose = D.SkinRig.pose(input, time);
    frames.push({ t: i * duration / count, rootY: pose.rootY, feet: pose.feet,
                  matrices: Array.from(pose.matrices) });
  }
  return { name, frames };
}
process.stdout.write(JSON.stringify({ bones: D.SkinRig.bones,
  clips: [sample('Marcha', 1.35, 40), sample('Reposo', 0, 64), sample('Carrera', 3.78, 40, .5)] }));
