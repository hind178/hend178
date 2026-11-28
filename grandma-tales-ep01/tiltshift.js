// Tilt-shift post: scene (MSAA + depth) → CoC = mix(physical DOF, screen-space band) → spiral gather → grade.
// Follows the style's formula: CoC = mix(aper·(1/focus − 1/z), sign(dy)·amp·(max(0,|dy|−w)/0.5)^1.2, mix), clamped.
import * as THREE from 'three';
import { FullScreenQuad } from 'three/addons/postprocessing/Pass.js';

const VS = `varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0., 1.); }`;

export function makeTiltShift(renderer, scene, camera, w, h, ssaa = 1) {
  const W = Math.round(w * ssaa), H = Math.round(h * ssaa);
  const rt = new THREE.WebGLRenderTarget(W, H, { samples: 4, type: THREE.HalfFloatType, depthTexture: new THREE.DepthTexture(W, H, THREE.FloatType) });
  const rtC = new THREE.WebGLRenderTarget(W, H, { type: THREE.HalfFloatType });
  const rtG = new THREE.WebGLRenderTarget(W, H, { type: THREE.HalfFloatType });
  const coc = new FullScreenQuad(new THREE.ShaderMaterial({
    uniforms: { tColor: { value: null }, tDepth: { value: null }, focus: { value: 10 }, aper: { value: 100 }, maxCoc: { value: 24 }, near: { value: .1 }, far: { value: 500 },
      bandY: { value: .5 }, bandW: { value: .08 }, amp: { value: 20 }, mixv: { value: .7 }, aspect: { value: h / w } },
    vertexShader: VS,
    fragmentShader: `#include <packing>
      varying vec2 vUv; uniform sampler2D tColor, tDepth; uniform float focus, aper, maxCoc, near, far, bandY, bandW, amp, mixv;
      void main(){
        float z = -perspectiveDepthToViewZ(texture2D(tDepth, vUv).x, near, far);
        float phys = aper * (1.0/focus - 1.0/z);
        float dy = vUv.y - bandY;
        float band = sign(dy) * amp * pow(max(0.0, abs(dy) - bandW) / 0.5, 1.2);
        float c = clamp(mix(phys, band, mixv), -maxCoc, maxCoc);
        gl_FragColor = vec4(texture2D(tColor, vUv).rgb, c);
      }` }));
  const gather = new FullScreenQuad(new THREE.ShaderMaterial({
    uniforms: { tIn: { value: null }, res: { value: new THREE.Vector2(W, H) }, maxCoc: { value: 24 } },
    vertexShader: VS,
    fragmentShader: `varying vec2 vUv; uniform sampler2D tIn; uniform vec2 res; uniform float maxCoc;
      float hash(vec2 p){ return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453); }
      void main(){
        vec4 c0 = texture2D(tIn, vUv); float a0 = abs(c0.a);
        if (maxCoc < .5) { gl_FragColor = vec4(c0.rgb, 1.); return; }
        vec3 acc = c0.rgb / (a0*a0 + 1.); float wsum = 1. / (a0*a0 + 1.);
        float rot = hash(gl_FragCoord.xy) * 6.2832;
        const int N = 72;
        for (int i = 0; i < N; i++) {
          float r = maxCoc * sqrt((float(i) + .5) / float(N));
          float th = float(i) * 2.39996 + rot;
          vec4 s = texture2D(tIn, vUv + vec2(cos(th), sin(th)) * r / res);
          float sa = abs(s.a);
          if (s.a > c0.a) sa = min(sa, max(a0, 0.));   // far samples don't bleed onto nearer sharp ones
          float w = smoothstep(r - 1.5, r + .5, sa) / (sa*sa + 1.);
          acc += s.rgb * w; wsum += w;
        }
        gl_FragColor = vec4(acc / wsum, 1.);
      }` }));
  const grade = new FullScreenQuad(new THREE.ShaderMaterial({
    uniforms: { tIn: { value: null }, sat: { value: 1.3 }, contrast: { value: .22 }, warm: { value: .5 }, vig: { value: .32 }, exposure: { value: 1 }, aspect: { value: w / h } },
    vertexShader: VS,
    fragmentShader: `varying vec2 vUv; uniform sampler2D tIn; uniform float sat, contrast, warm, vig, exposure, aspect;
      vec3 neutral(vec3 c){ // Khronos PBR Neutral
        float s = .8 - .04; float d = .15; float x = min(c.r, min(c.g, c.b)); float off = x < .08 ? x - 6.25*x*x : .04; c -= off;
        float p = max(c.r, max(c.g, c.b)); if (p < s) return c; float d2 = 1. - s; float np = 1. - d2*d2/(p + d2 - s); c *= np/p; float g = 1. - 1./(d*(p - np) + 1.); return mix(c, np*vec3(1.), g); }
      vec3 srgb(vec3 c){ return mix(c * 12.92, 1.055 * pow(c, vec3(1./2.4)) - .055, step(.0031308, c)); }
      void main(){
        vec3 c = texture2D(tIn, vUv).rgb * exposure;
        c *= mix(vec3(1.), vec3(1.07, 1.0, .9), warm * smoothstep(.0, .8, dot(c, vec3(.33))));
        float l = dot(c, vec3(.2126, .7152, .0722)); c = max(mix(vec3(l), c, sat), 0.);
        c = c * (1. + contrast) / (1. + contrast * c / (c + .6));
        c = neutral(c);
        vec2 d = vUv - .5; d.x *= aspect; c *= 1. - vig * smoothstep(.2, .75, length(d));
        gl_FragColor = vec4(srgb(clamp(c, 0., 1.)), 1.);
      }` }));
  const P = { focus: 10, aper: 100, maxCoc: 24, bandY: .5, bandW: .08, amp: 20, mixv: .7, sat: 1.3, contrast: .22, warm: .5, vig: .32, exposure: 1 };
  function render() {
    renderer.setRenderTarget(rt); renderer.clear(); renderer.render(scene, camera);
    const u = coc.material.uniforms;
    Object.assign(u.tColor, { value: rt.texture }); u.tDepth.value = rt.depthTexture;
    u.focus.value = P.focus; u.aper.value = P.aper * ssaa; u.maxCoc.value = P.maxCoc * ssaa; u.near.value = camera.near; u.far.value = camera.far;
    u.bandY.value = P.bandY; u.bandW.value = P.bandW; u.amp.value = P.amp * ssaa; u.mixv.value = P.mixv;
    renderer.setRenderTarget(rtC); coc.render(renderer);
    const g = gather.material.uniforms; g.tIn.value = rtC.texture; g.maxCoc.value = P.maxCoc * ssaa;
    renderer.setRenderTarget(rtG); gather.render(renderer);
    const q = grade.material.uniforms; q.tIn.value = rtG.texture;
    for (const k of ['sat', 'contrast', 'warm', 'vig', 'exposure']) q[k].value = P[k];
    renderer.setRenderTarget(null); grade.render(renderer);
  }
  return { P, render };
}
