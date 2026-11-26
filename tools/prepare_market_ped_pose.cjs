'use strict';
// Bake the reviewed glTF's rigid local animation tracks; FK stays in the game so
// blends maintain joint lengths throughout the transition.
const {accessor} = require('./export_human_tangents.cjs');

function buildPose(doc, binary) {
  const skin = doc.skins[0], joints = skin.joints;
  const root = joints.indexOf(skin.skeleton);
  const indices = new Map(joints.map((node, index) => [node, index]));
  const parents = joints.map(() => -1), order = [];
  function visit(joint, parent) {
    if (order.includes(joint)) throw Error('Repeated joint in the market pedestrian hierarchy');
    order.push(joint);
    parents[joint] = parent;
    for (const child of doc.nodes[joints[joint]].children || []) visit(indices.get(child), joint);
  }
  if (root < 0 || joints.length !== 49) throw Error('Expected the fitted 49-joint skin');
  visit(root, -1);
  if (order.length !== joints.length) throw Error('Disconnected market pedestrian skin');
  // All rest orientations in this fitted GLB are identity. Its inverse bind
  // matrices are translations by the negative rest position in model space.
  const localBind = joints.map(id => {
    const node = doc.nodes[id];
    if (node.rotation || node.scale || node.matrix || node.translation?.length !== 3)
      throw Error('Expected a translated market pedestrian bind joint');
    return node.translation;
  });
  const globalBind = [];
  for (const joint of order) {
    const parent = parents[joint];
    globalBind[joint] = localBind[joint].map((v,k) => v + (parent < 0 ? 0 : globalBind[parent][k]));
  }
  const ibm = doc.accessors[skin.inverseBindMatrices], view = doc.bufferViews[ibm.bufferView];
  if (ibm.type !== 'MAT4' || ibm.componentType !== 5126 || ibm.count !== joints.length || ibm.sparse)
    throw Error('Invalid inverse bind matrices');
  for (const joint of order) {
    const offset = (view.byteOffset || 0) + (ibm.byteOffset || 0) + joint * (view.byteStride || 64);
    for (let k=0;k<16;k++) {
      const expected = k>=12 && k<=14 ? -globalBind[joint][k-12] : +(k%5===0);
      if (!(Math.abs(binary.readFloatLE(offset+4*k)-expected)<1e-6)) throw Error('Incompatible inverse bind matrix');
    }
  }
  const clips = {};
  for (const animation of doc.animations) {
    if (!['Marcha','Reposo','Carrera'].includes(animation.name)) continue;
    const firstInput = animation.samplers[0].input, times = accessor(doc,binary,firstInput);
    const frames = times.a.count, duration = times.value(frames-1);
    for (let i=0;i<frames;i++) {
      if (!(Math.abs(times.value(i)-duration*i/(frames-1))<1e-5)) throw Error('Expected uniform sample times');
    }
    const tracks = [];
    for (const channel of animation.channels) {
      const sampler = animation.samplers[channel.sampler], target = channel.target;
      const joint = indices.get(target.node), translation = target.path === 'translation';
      if (sampler.input!==firstInput || (sampler.interpolation||'LINEAR')!=='LINEAR' || joint===undefined ||
          (translation ? joint!==root : target.path!=='rotation'))
        throw Error('Unsupported market pedestrian animation channel');
      const values = accessor(doc,binary,sampler.output), components = translation ? 3 : 4;
      if (values.a.count!==frames || values.width!==components || values.a.componentType!==5126)
        throw Error('Unexpected market pedestrian keys');
      const samples = Buffer.concat(Array.from({length:frames},(_,i)=>values.row(i)));
      const first = values.row(0);
      const constant = Array.from({length:frames},(_,i)=>values.row(i).equals(first)).every(Boolean);
      tracks.push({joint, translation, data:(constant ? first : samples).toString('base64')});
    }
    clips[animation.name] = {duration, frames, tracks};
  }
  if (!clips.Marcha || !clips.Reposo) throw Error('Missing market pedestrian locomotion');
  return {root, parents, order, localBind:localBind.flat(), globalBind:globalBind.flat(), clips};
}

module.exports = {buildPose};
