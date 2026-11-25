#!/usr/bin/env python3
"""Real WebGL2 regression for the native mappedNormal shader function.

Analytical planar charts isolate tangent-space direction and strength. This is
software-GPU correctness evidence, not a gameplay capture or FPS benchmark.
"""
import hashlib
import json
import math
from pathlib import Path
import sys
import unittest
from playwright.sync_api import sync_playwright
from qa_support import launch_options

ROOT = Path(__file__).resolve().parents[1]


def shader_function(source):
    start = source.index('vec3 mappedNormal(')
    opening = source.index('{', start)
    depth = 1
    for index in range(opening+1,len(source)):
        depth += (source[index]=='{') - (source[index]=='}')
        if depth==0:
            return source[start:index+1]
    raise ValueError('Unterminated mappedNormal shader')


def dot(a,b): return sum(x*y for x,y in zip(a,b))
def unit(v): return [x/math.sqrt(dot(v,v)) for x in v]
def cross(a,b):
    return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]


def reference(uv, normal, sample, slope):
    # Invert the affine chart analytically; independent of screen derivatives.
    a,b,c,d = uv
    determinant = a*d-b*c
    n = unit(normal)
    if determinant==0:
        return n
    dpdu = [d/determinant,-c/determinant,(slope[0]*d-slope[1]*c)/determinant]
    dpdv = [-b/determinant,a/determinant,(-slope[0]*b+slope[1]*a)/determinant]
    projection = dot(dpdu,n)
    tangent = unit([x-projection*y for x,y in zip(dpdu,n)])
    bitangent = cross(n,tangent)
    handedness = 1 if dot(bitangent,dpdv)>=0 else -1
    bitangent = [x*handedness for x in bitangent]
    return unit([tangent[i]*sample[0]+bitangent[i]*sample[1]+n[i]*sample[2] for i in range(3)])


SETUP = r'''function(mappedNormal) {
 const canvas=document.createElement('canvas');canvas.width=64;canvas.height=64;
 document.body.append(canvas);
 const gl=canvas.getContext('webgl2',{antialias:false,preserveDrawingBuffer:true});
 if(!gl)throw Error('WebGL2 unavailable');
 if(!gl.getExtension('EXT_color_buffer_float'))throw Error('Float render target unavailable');
 const vertex=`#version 300 es
 precision highp float;
 in vec2 position;uniform mat2 chart;uniform vec2 slope;
 out vec3 vWorld;out vec2 vUV;
 void main(){vWorld=vec3(position,dot(position,slope));vUV=chart*position;
 gl_Position=vec4(position,0.,1.);}`;
 const fragment=`#version 300 es
 precision highp float;
 in vec3 vWorld;in vec2 vUV;uniform vec3 testNormal;uniform vec3 testSample;
 out vec4 result;
 ${mappedNormal}
 void main(){result=vec4(mappedNormal(normalize(testNormal),normalize(testSample)),1.);}`;
 function compile(type,source){const shader=gl.createShader(type);gl.shaderSource(shader,source);gl.compileShader(shader);
 if(!gl.getShaderParameter(shader,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(shader));return shader;}
 const program=gl.createProgram();gl.attachShader(program,compile(gl.VERTEX_SHADER,vertex));
 gl.attachShader(program,compile(gl.FRAGMENT_SHADER,fragment));gl.linkProgram(program);
 if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw Error(gl.getProgramInfoLog(program));
 gl.useProgram(program);
 const vao=gl.createVertexArray();gl.bindVertexArray(vao);
 const buffer=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,buffer);
 gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,3,-1,-1,3]),gl.STATIC_DRAW);
 const location=gl.getAttribLocation(program,'position');gl.enableVertexAttribArray(location);
 gl.vertexAttribPointer(location,2,gl.FLOAT,false,0,0);
 const texture=gl.createTexture();gl.bindTexture(gl.TEXTURE_2D,texture);
 gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.NEAREST);
 gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.NEAREST);
 gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA32F,64,64,0,gl.RGBA,gl.FLOAT,null);
 const framebuffer=gl.createFramebuffer();gl.bindFramebuffer(gl.FRAMEBUFFER,framebuffer);
 gl.framebufferTexture2D(gl.FRAMEBUFFER,gl.COLOR_ATTACHMENT0,gl.TEXTURE_2D,texture,0);
 if(gl.checkFramebufferStatus(gl.FRAMEBUFFER)!==gl.FRAMEBUFFER_COMPLETE)throw Error('Incomplete float framebuffer');
 gl.viewport(0,0,64,64);gl.disable(gl.DITHER);
 const uniforms=Object.fromEntries(['chart','slope','testNormal','testSample'].map(name=>[name,gl.getUniformLocation(program,name)]));
 window.measure=({uv,normal,sample,slope})=>{
  gl.uniformMatrix2fv(uniforms.chart,false,new Float32Array([uv[0],uv[2],uv[1],uv[3]]));
  gl.uniform2fv(uniforms.slope,new Float32Array(slope));
  gl.uniform3fv(uniforms.testNormal,new Float32Array(normal));
  gl.uniform3fv(uniforms.testSample,new Float32Array(sample));
  gl.clearColor(0,0,0,0);gl.clear(gl.COLOR_BUFFER_BIT);gl.drawArrays(gl.TRIANGLES,0,3);
  const pixels=new Float32Array(4);gl.readPixels(32,32,1,1,gl.RGBA,gl.FLOAT,pixels);
  const error=gl.getError();if(error!==gl.NO_ERROR)throw Error('GL error '+error);
  return Array.from(pixels);
 };
 const debug=gl.getExtension('WEBGL_debug_renderer_info');
 return {renderer:debug?gl.getParameter(debug.UNMASKED_RENDERER_WEBGL):gl.getParameter(gl.RENDERER),version:gl.getParameter(gl.VERSION)};
}'''


class NativeTangentFrame(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = shader_function((ROOT/'src/renderer.js').read_text())
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(**launch_options())
        cls.page = cls.browser.new_page()
        cls.page.set_content('<!doctype html><title>Native tangent frame regression</title>')
        metadata = cls.page.evaluate(SETUP,cls.source)
        print(json.dumps({'shaderSha256':hashlib.sha256(cls.source.encode()).hexdigest(),'browser':cls.browser.version,**metadata}),file=sys.stderr)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close();cls.playwright.stop()

    def check_chart(self,uv,normal=(0,0,1),sample=(.3,.4,1),slope=(0,0),expected=None):
        if expected is None:
            expected = reference(uv,normal,sample,slope)
        actual = self.page.evaluate('values => window.measure(values)',{'uv':uv,'normal':normal,'sample':sample,'slope':slope})
        self.assertEqual(actual[3],1,'Pixel must have been drawn')
        self.assertTrue(all(isinstance(v,(int,float)) and math.isfinite(v) for v in actual))
        self.assertLess(max(abs(x-y) for x,y in zip(actual,expected)),2e-5,
            f'chart={uv}, expected={expected}, measured={actual[:3]}')

    def test_identity_and_rotated_charts_keep_normal_direction(self):
        c=math.sqrt(.5)
        for uv in [(1,0,0,1),(0,1,-1,0),(c,c,-c,c)]:
            with self.subTest(uv=uv):self.check_chart(uv)

    def test_anisotropic_uv_scale_preserves_normal_strength(self):
        for uv in [(3,0,0,.5),(.5,0,0,3)]:
            with self.subTest(uv=uv):self.check_chart(uv)

    def test_skew_and_mirrored_charts_use_inverse_jacobian_orientation(self):
        for uv in [(1,.8,.3,1),(-1,0,0,1),(-1,.8,.3,1)]:
            with self.subTest(uv=uv):self.check_chart(uv)

    def test_inclined_plane_and_smoothed_normal_use_orthonormal_frame(self):
        for normal in [(-.4,-.2,1),(.1,-.1,1)]:
            with self.subTest(normal=normal):self.check_chart((1,.8,.3,1),normal=normal,slope=(.4,.2))

    def test_singular_uvs_return_finite_surface_normal(self):
        for uv in [(0,0,0,0),(1,1,1,1)]:
            with self.subTest(uv=uv):self.check_chart(uv,normal=(-.4,-.2,1),slope=(.4,.2))

    def test_near_parallel_chart_falls_back_but_uniform_small_chart_remains_valid(self):
        # A determinant alone is not a conditioning test. The first chart has
        # almost parallel UV axes; the second remains orthogonal at small scale.
        normal=(-.4,-.2,1)
        self.check_chart((1,1,1,1+2**-20),normal=normal,slope=(.4,.2),expected=unit(normal))
        self.check_chart((1e-4,0,0,1e-4),normal=normal,slope=(.4,.2))


if __name__=='__main__':unittest.main()
