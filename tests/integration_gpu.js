// Development-only transform feedback of the ACTUAL production vertex shader.
// Does not patch the distributed shader. Output checked against CPU morph plus Jacobian.
() => {
 const r=DC_APP.renderer,g=r.gl;
 const shader=g.getAttachedShaders(r.sceneProgram).find(s=>g.getShaderParameter(s,g.SHADER_TYPE)===g.VERTEX_SHADER);
 const compile=(type,src)=>{const s=g.createShader(type);g.shaderSource(s,src);g.compileShader(s);if(!g.getShaderParameter(s,g.COMPILE_STATUS))throw Error(g.getShaderInfoLog(s));return s;};
 const v=compile(g.VERTEX_SHADER,g.getShaderSource(shader)),f=compile(g.FRAGMENT_SHADER,'#version 300 es\nprecision highp float;out vec4 color;void main(){color=vec4(1.);}');
 const program=g.createProgram();g.attachShader(program,v);g.attachShader(program,f);g.transformFeedbackVaryings(program,['vWorld','vNormal'],g.INTERLEAVED_ATTRIBS);g.linkProgram(program);if(!g.getProgramParameter(program,g.LINK_STATUS))throw Error(g.getProgramInfoLog(program));
 const vao=g.createVertexArray(),buf=g.createBuffer(),feedback=g.createTransformFeedback(),texture=g.createTexture();
 g.useProgram(program);g.bindVertexArray(vao);g.bindTransformFeedback(g.TRANSFORM_FEEDBACK,feedback);g.bindBuffer(g.TRANSFORM_FEEDBACK_BUFFER,buf);g.bufferData(g.TRANSFORM_FEEDBACK_BUFFER,24,g.DYNAMIC_READ);g.bindBufferBase(g.TRANSFORM_FEEDBACK_BUFFER,0,buf);
 const u=n=>g.getUniformLocation(program,n),identity=new Float32Array([1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]);
 for(const n of ['uVP','uLightVP','uReflectVP'])g.uniformMatrix4fv(u(n),false,identity);
 g.uniformMatrix4fv(u('uBones[0]'),false,DC.SkinRig.rest());g.uniform1i(u('uSkinned'),1);g.uniform1f(u('uTime'),1);g.uniform3f(u('uChunkOffset'),0,0,0);
 g.uniform1i(u('uCrowdBones'),3);g.uniform1i(u('uCrowdDuals'),8);g.uniform1i(u('uCharacterLooks'),9);
 g.activeTexture(g.TEXTURE9);g.bindTexture(g.TEXTURE_2D,texture);g.texParameteri(g.TEXTURE_2D,g.TEXTURE_MIN_FILTER,g.NEAREST);g.texParameteri(g.TEXTURE_2D,g.TEXTURE_MAG_FILTER,g.NEAREST);
 g.vertexAttrib4f(3,0,0,0,0);g.vertexAttrib4f(5,1,1,1,1);g.vertexAttrib4f(6,0,0,0,200);g.vertexAttrib4f(7,4,0,0,0);g.vertexAttrib4f(8,1,0,0,0);g.vertexAttrib2f(2,.5,.2);
 const unit=a=>{const l=Math.hypot(...a);return a.map(x=>x/l);},cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
 const n=unit([.73,.21,.66]),cases=[];
 for(const material of [40,31])for(const build of [-1,0,1])for(const neck of [-1,0,1])for(const point of [[.062,1.515,.019],[.086,1.480,-.010],[.030,1.557,.110],[.109,1.452,.048]]){
  g.texImage2D(g.TEXTURE_2D,0,g.RGBA32F,1,1,0,g.RGBA,g.FLOAT,new Float32Array([build,0,0,neck]));g.vertexAttrib4f(4,1,1,1,material);g.vertexAttrib3fv(0,point);g.vertexAttrib3fv(1,n);
  g.enable(g.RASTERIZER_DISCARD);g.beginTransformFeedback(g.POINTS);g.drawArrays(g.POINTS,0,1);g.endTransformFeedback();g.disable(g.RASTERIZER_DISCARD);
  const out=new Float32Array(6);g.getBufferSubData(g.TRANSFORM_FEEDBACK_BUFFER,0,out);
  const expected=DC.Appearance.shapePoint(point,material,build,0,neck),e=.0003,columns=[0,1,2].map(k=>{const a=[...point],b=[...point];a[k]+=e;b[k]-=e;const A=DC.Appearance.shapePoint(a,material,build,0,neck),B=DC.Appearance.shapePoint(b,material,build,0,neck);return A.map((v,i)=>(v-B[i])/(2*e));});
  const cof=[cross(columns[1],columns[2]),cross(columns[2],columns[0]),cross(columns[0],columns[1])],normal=unit([0,1,2].map(i=>cof.reduce((s,c,j)=>s+c[i]*n[j],0)));
  cases.push({material,build,neck,point,positionError:Math.max(...expected.map((v,i)=>Math.abs(out[i]-v))),normalError:Math.max(...normal.map((v,i)=>Math.abs(out[i+3]-v)))});
 }
 g.bindTransformFeedback(g.TRANSFORM_FEEDBACK,null);g.bindBufferBase(g.TRANSFORM_FEEDBACK_BUFFER,0,null);g.deleteTransformFeedback(feedback);g.deleteBuffer(buf);g.deleteVertexArray(vao);g.deleteTexture(texture);g.deleteProgram(program);g.deleteShader(v);g.deleteShader(f);
 return {cases,gl:g.getError(),maxPositionError:Math.max(...cases.map(c=>c.positionError)),maxNormalError:Math.max(...cases.map(c=>c.normalError))};
}
