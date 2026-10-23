// Procedural 3D models (metres, y up, seabed y = 0, well axis x = z = 0, wellhead datum y = 4.0).
// Inspired by the Blender equipment models on the claude/equinor-subsea-well-video-uisotu branch, rebuilt with
// the geometry of the NORSOK U-001 Figure J.1 wellhead: HP housing in the LP conductor housing in a template slot.
import * as THREE from 'three';
import { deformable, DEF } from './world.js';

export const DATUM = 4.0;
const TAU = Math.PI * 2;

// --------------------------------------------------------------------------------------------- textures
function canvasTex(w, h, draw, { repeat = [1, 1], srgb = true } = {}) {
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  const g = c.getContext('2d'); draw(g, w, h);
  const t = new THREE.CanvasTexture(c);
  t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(...repeat);
  if (srgb) t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 4;
  return t;
}
function rng(seed) { let s = seed >>> 0; return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296); }
function sandTex() {
  return canvasTex(512, 512, (g, w, h) => {
    const r = rng(7);
    g.fillStyle = '#b39a72'; g.fillRect(0, 0, w, h);
    for (let i = 0; i < 9000; i++) { const v = 150 + r() * 70 | 0; g.fillStyle = `rgba(${v},${v - 18},${v - 48},${0.25 + r() * 0.3})`; g.fillRect(r() * w, r() * h, 1 + r() * 2.5, 1 + r() * 2.5); }
    g.globalAlpha = 0.12;
    for (let y = 0; y < h; y += 9) { g.strokeStyle = y % 18 ? '#8d7556' : '#d1bb92'; g.beginPath(); for (let x = 0; x <= w; x += 8) g.lineTo(x, y + 3 * Math.sin(x * 0.05 + y * 0.3)); g.stroke(); }
    g.globalAlpha = 1;
  }, { repeat: [40, 40] });
}
function strataTex() {
  return canvasTex(1024, 2048, (g, w, h) => {
    const r = rng(11);
    const layers = [['#8a734f', 180], ['#7a6646', 280], ['#937c57', 220], ['#6c5b43', 320], ['#86704e', 260], ['#715f45', 400], ['#7d6849', 388]];
    let y = 0;
    for (const [c, hh] of layers) {
      g.fillStyle = c; g.fillRect(0, y, w, hh);
      const grd = g.createLinearGradient(0, y, 0, y + hh); grd.addColorStop(0, 'rgba(255,240,210,0.06)'); grd.addColorStop(1, 'rgba(20,12,4,0.16)');
      g.fillStyle = grd; g.fillRect(0, y, w, hh);
      y += hh;
    }
    // grains as soft round dots, bedding lines
    for (let i = 0; i < 26000; i++) {
      const v = r() * 70 | 0;
      g.fillStyle = `rgba(${50 + v},${40 + v},${28 + v},${0.10 + r() * 0.18})`;
      g.beginPath(); g.arc(r() * w, r() * h, 0.6 + r() * 1.6, 0, TAU); g.fill();
    }
    g.globalAlpha = 0.22; g.strokeStyle = '#3a3024'; g.lineWidth = 1.5;
    for (let i = 0; i < 90; i++) { const yy = r() * h; g.beginPath(); g.moveTo(0, yy); for (let x = 0; x <= w; x += 16) g.lineTo(x, yy + 5 * Math.sin(x * 0.012 + i)); g.stroke(); }
    g.globalAlpha = 1;
  }, { repeat: [1, 1] });
}
function hatchTex(base = '#dfe7ee', line = 'rgba(80,100,120,0.45)') {
  return canvasTex(128, 128, (g, w, h) => {
    g.fillStyle = base; g.fillRect(0, 0, w, h);
    g.strokeStyle = line; g.lineWidth = 3;
    for (let k = -h; k < w; k += 16) { g.beginPath(); g.moveTo(k, h); g.lineTo(k + h, 0); g.stroke(); }
  }, { repeat: [1, 1] });
}
function cementTex() {
  return canvasTex(256, 256, (g, w, h) => {
    const r = rng(5); g.fillStyle = '#8e979d'; g.fillRect(0, 0, w, h);
    for (let i = 0; i < 4000; i++) { const v = 110 + r() * 80 | 0; g.fillStyle = `rgba(${v},${v + 4},${v + 8},0.5)`; g.fillRect(r() * w, r() * h, 1 + r() * 2, 1 + r() * 2); }
  }, { repeat: [1, 6] });
}
function spriteTex() {
  return canvasTex(64, 64, (g, w, h) => {
    const gr = g.createRadialGradient(32, 32, 0, 32, 32, 32);
    gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(0.35, 'rgba(255,255,255,0.55)'); gr.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = gr; g.fillRect(0, 0, w, h);
  }, { srgb: false });
}
function rayTex() {
  return canvasTex(64, 256, (g, w, h) => {
    const gr = g.createLinearGradient(0, 0, 0, h);
    gr.addColorStop(0, 'rgba(255,255,255,0.9)'); gr.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = gr; g.fillRect(0, 0, w, h);
    const gx = g.createLinearGradient(0, 0, w, 0);
    gx.addColorStop(0, 'rgba(0,0,0,1)'); gx.addColorStop(0.5, 'rgba(0,0,0,0)'); gx.addColorStop(1, 'rgba(0,0,0,1)');
    g.globalCompositeOperation = 'destination-out'; g.fillStyle = gx; g.fillRect(0, 0, w, h);
  }, { srgb: false });
}

// --------------------------------------------------------------------------------------------- geometry
// Revolve a closed profile [[r, y], ...] about the y axis for phi in [phi0, phi1]; with caps on partial revolutions.
// Group 0 = revolved surface, group 1 = cut faces.
export function revolve(profile, { phi0 = 0, phi1 = TAU, seg = 72, caps = null } = {}) {
  const full = Math.abs(phi1 - phi0 - TAU) < 1e-6;
  const pts = profile.slice();
  // ensure counter-clockwise in (r, y) so normals point outward
  let area = 0;
  for (let i = 0; i < pts.length; i++) { const [a, b] = pts[i], [c, d] = pts[(i + 1) % pts.length]; area += a * d - c * b; }
  if (area < 0) pts.reverse();
  const pos = [], nor = [], uv = [], idx = [];
  const n = seg;
  // perimeter for uv.y
  let per = 0; const cum = [0];
  for (let i = 0; i < pts.length; i++) { const [a, b] = pts[i], [c, d] = pts[(i + 1) % pts.length]; per += Math.hypot(c - a, d - b); cum.push(per); }
  for (let e = 0; e < pts.length; e++) {
    const [r0, y0] = pts[e], [r1, y1] = pts[(e + 1) % pts.length];
    const len = Math.hypot(r1 - r0, y1 - y0); if (len < 1e-9) continue;
    const nr = (y1 - y0) / len, ny = -(r1 - r0) / len;      // outward normal in the profile plane (CCW)
    const base = pos.length / 3;
    for (let k = 0; k <= n; k++) {
      const ph = phi0 + (phi1 - phi0) * k / n, c = Math.cos(ph), s = Math.sin(ph);
      for (const [r, y, u] of [[r0, y0, cum[e]], [r1, y1, cum[e + 1]]]) {
        pos.push(r * c, y, r * s); nor.push(nr * c, ny, nr * s); uv.push(k / n * (full ? 6 : 3), u / per * 4);
      }
    }
    for (let k = 0; k < n; k++) {
      const a = base + k * 2, b = a + 1, c2 = a + 2, d = a + 3;
      idx.push(a, c2, b, b, c2, d);
    }
  }
  const g = new THREE.BufferGeometry();
  const surfCount = idx.length;
  if (!full && caps !== false) {
    const contour = pts.map(([r, y]) => new THREE.Vector2(r, y));
    const tris = THREE.ShapeUtils.triangulateShape(contour, []);
    for (const [ph, flip] of [[phi0, true], [phi1, false]]) {
      const c = Math.cos(ph), s = Math.sin(ph);
      // cap normal: tangent direction of the revolution, pointing out of the solid
      const tx = -s, tz = c;
      const nx = flip ? -tx : tx, nz = flip ? -tz : tz;
      const base = pos.length / 3;
      for (const [r, y] of pts) { pos.push(r * c, y, r * s); nor.push(nx, 0, nz); uv.push(r * 2.2, y * 2.2); }
      for (const [a, b, cc] of tris) { if (flip) idx.push(base + a, base + b, base + cc); else idx.push(base + a, base + cc, base + b); }
    }
  }
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  g.setAttribute('normal', new THREE.Float32BufferAttribute(nor, 3));
  g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
  g.setIndex(idx);
  g.addGroup(0, surfCount, 0);
  if (idx.length > surfCount) g.addGroup(surfCount, idx.length - surfCount, 1);
  return g;
}
const ring = (ri, ro, y0, y1) => [[ri, y0], [ro, y0], [ro, y1], [ri, y1]];

function mesh(geo, mat, { cast = true, recv = true } = {}) { const m = new THREE.Mesh(geo, mat); m.castShadow = cast; m.receiveShadow = recv; return m; }
function beam(a, b, w, h, mat) {
  const A = new THREE.Vector3(...a), B = new THREE.Vector3(...b);
  const L = A.distanceTo(B);
  const m = mesh(new THREE.BoxGeometry(w, h, L), mat);
  m.position.copy(A).add(B).multiplyScalar(0.5);
  m.lookAt(B);
  return m;
}
function tubeBetween(a, b, r, mat, seg = 16) {
  const A = new THREE.Vector3(...a), B = new THREE.Vector3(...b);
  const L = A.distanceTo(B);
  const m = mesh(new THREE.CylinderGeometry(r, r, L, seg), mat);
  m.position.copy(A).add(B).multiplyScalar(0.5);
  m.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), B.clone().sub(A).normalize());
  return m;
}

// --------------------------------------------------------------------------------------------- materials
export function materials() {
  const std = (o) => new THREE.MeshStandardMaterial(o);
  const hatch = hatchTex();
  const M = {
    steel: deformable(std({ color: '#a9b8c6', metalness: 0.6, roughness: 0.36 })),
    steelDark: deformable(std({ color: '#6c7a88', metalness: 0.6, roughness: 0.4 })),
    lp: deformable(std({ color: '#8d9cab', metalness: 0.55, roughness: 0.42 })),
    cond: deformable(std({ color: '#a9b8c6', metalness: 0.6, roughness: 0.36 })),
    casing: deformable(std({ color: '#7f8c99', metalness: 0.55, roughness: 0.45 })),
    whx: deformable(std({ color: '#7f8c99', metalness: 0.55, roughness: 0.45 })),
    connDark: std({ color: '#3d4853', metalness: 0.55, roughness: 0.45 }),
    cut: deformable(std({ color: '#e6edf3', map: hatch, metalness: 0.1, roughness: 0.75, side: THREE.DoubleSide })),
    cutWarm: deformable(std({ color: '#f3e4cf', map: hatch, metalness: 0.1, roughness: 0.75, side: THREE.DoubleSide })),
    cement: deformable(std({ color: '#9aa3a9', map: cementTex(), roughness: 0.95, metalness: 0 }), { stress: false }),
    cementCut: deformable(std({ color: '#b3bbc1', map: cementTex(), roughness: 0.95, metalness: 0, side: THREE.DoubleSide }), { stress: false }),
    weld: deformable(std({ color: '#d8b46a', metalness: 0.5, roughness: 0.35, emissive: '#3a2a08' })),
    yellow: std({ color: '#e7ae1c', metalness: 0.15, roughness: 0.5 }),
    yellowDark: std({ color: '#b98510', metalness: 0.15, roughness: 0.55 }),
    yellowCut: std({ color: '#f6d77a', map: hatchTex('#f6d77a', 'rgba(120,80,10,0.45)'), roughness: 0.7, side: THREE.DoubleSide }),
    bop: deformable(std({ color: '#5d6b78', metalness: 0.55, roughness: 0.42 }), { stress: false }),
    bopDark: deformable(std({ color: '#3d4853', metalness: 0.55, roughness: 0.45 }), { stress: false }),
    bopYellow: deformable(std({ color: '#e7ae1c', metalness: 0.15, roughness: 0.5 }), { stress: false }),
    bopRed: deformable(std({ color: '#c0392b', metalness: 0.2, roughness: 0.5 }), { stress: false }),
    bopBlue: deformable(std({ color: '#2f6fb5', metalness: 0.2, roughness: 0.5 }), { stress: false }),
    white: std({ color: '#e9eef2', metalness: 0.05, roughness: 0.55 }),
    riserWhite: deformable(std({ color: '#e9eef2', metalness: 0.05, roughness: 0.55 }), { stress: false }),
    rigGrey: std({ color: '#c7cfd6', metalness: 0.2, roughness: 0.6 }),
    rigDark: std({ color: '#4a535c', metalness: 0.3, roughness: 0.6 }),
    rigRed: std({ color: '#b0322a', metalness: 0.2, roughness: 0.55 }),
    sand: std({ color: '#c2a679', map: sandTex(), roughness: 1, metalness: 0 }),
    strata: std({ color: '#ffffff', map: strataTex(), roughness: 1, metalness: 0, side: THREE.DoubleSide }),
    soilTop: std({ color: '#a88d64', map: sandTex(), roughness: 1, metalness: 0 }),
    glowAmber: new THREE.MeshBasicMaterial({ color: '#ffb547', transparent: true, opacity: 0.9, blending: THREE.AdditiveBlending, depthWrite: false }),
    glowCoral: new THREE.MeshBasicMaterial({ color: '#ff6f61', transparent: true, opacity: 0.9, blending: THREE.AdditiveBlending, depthWrite: false }),
    sprite: spriteTex(), ray: rayTex(),
    fe: feMaterial(),
  };
  return M;
}

// --------------------------------------------------------------------------------------------- wellhead system
// Layout (y up, datum 4.0): HP housing body to y 1.5, neck with guide ring at contact B (y 1.2), weld to the
// 20 in extension at y 1.1; LP conductor housing y 3.1 -> 1.0 with landing shoulder on template ring C (y 2.4);
// girth weld GW1 at y 1.0 (conductor housing -> 36 in conductor extension); mudline y 0; top of cement E at y -5.
export const WELL = {
  datum: DATUM, A: 3.0, B: 1.2, C: 2.4, D: 0.4, GW1: 1.0, mud: 0.0, toc: -5.0, whExtWeld: 1.1, bottom: -42,
  rCond: 0.4572, tCond: 0.0508, rSC: 0.254, tSC: 0.0254, rHole: 0.56, rLP: 0.4826,
};
// HP wellhead housing profile [r, y]: connector hub with grooves (y 3.46-4.0), a fillet (centre FILLET.c, radius FILLET.r)
// into the neck (r 0.35, the critical section of the worked example), landing ring on the LP housing (contact A), body,
// lower neck with the guide ring (contact B), weld prep to the extension. Bore 18 3/4 in.
export const FILLET = { c: [0.385, 3.405], r: 0.035 };
export const NECK = { ro: 0.35, ri: 0.238, y0: 3.165, y1: 3.405 };
const FILLET_ARC = Array.from({ length: 9 }, (_, k) => {
  const a = Math.PI / 2 + (Math.PI / 2) * k / 8;
  return [FILLET.c[0] + FILLET.r * Math.cos(a), FILLET.c[1] + FILLET.r * Math.sin(a)];
});
const RB = 0.238;
export const HP_PROFILE = [[RB, 4.0], [0.385, 4.0], [0.405, 3.97], [0.405, 3.86], [0.385, 3.84], [0.385, 3.78], [0.405, 3.76], [0.405, 3.66], [0.385, 3.64],
  [0.385, 3.58], [0.405, 3.56], [0.405, 3.46], ...FILLET_ARC, [0.35, 3.165], [0.381, 3.13], [0.425, 3.115], [0.425, 3.0], [0.381, 2.98],
  [0.381, 1.55], [0.30, 1.45], [0.30, 1.32], [0.388, 1.30], [0.388, 1.16], [0.30, 1.14], [0.272, 1.1], [RB - 0.016, 1.1], [RB - 0.016, 2.0], [RB, 2.1]];
// outside radius of the housing at height y (the outer profile runs monotonically down from [0.385, 4.0] to [0.272, 1.1])
const HP_OUTER = HP_PROFILE.slice(1, HP_PROFILE.length - 3);
export function hpOuter(y) {
  if (y >= 4.0) return 0.385;
  for (let i = 0; i < HP_OUTER.length - 1; i++) {
    const [r0, y0] = HP_OUTER[i], [r1, y1] = HP_OUTER[i + 1];
    if (y <= y0 && y >= y1) return y0 === y1 ? Math.max(r0, r1) : r0 + (r1 - r0) * (y0 - y) / (y0 - y1);
  }
  return 0.272;
}
export const hpInner = (y) => (y >= 2.1 ? RB : y <= 2.0 ? RB - 0.016 : RB - 0.016 * (2.1 - y) / 0.1);

// --------------------------------------------------------------------------------------------- FE view of the housing
// Uniforms of the FE contour material. Stresses are evaluated per fragment from per-height arrays: axial stress
// sa = c0(y) + c1(y) * x (tension + bending about the z axis, tension side x > 0), Lame hoop/radial stresses from the
// pressure, a fillet peak sa *= 1 + (Kt - 1) exp(-d / delta) with d the distance to the fillet surface. Plastic mode:
// equivalent plastic strain ep = max(0, kappa(y) |x| - sy / E). The field is a teaching stand-in, not an FE result.
export const FE_N = 96, FE_Y0 = 1.0, FE_Y1 = 4.1;
export const FEU = {
  uFE: { value: 0 }, uMode: { value: 0 }, uP: { value: 0 }, uKt: { value: 1.5 }, uDel: { value: 0.012 },
  uFc: { value: new THREE.Vector2(...FILLET.c) }, uFr: { value: FILLET.r }, uVmax: { value: 800 }, uBands: { value: 9 },
  uEyl: { value: 517 / 207000 }, uRi: { value: new Float32Array(FE_N) }, uRo: { value: new Float32Array(FE_N) },
  uC0: { value: new Float32Array(FE_N) }, uC1: { value: new Float32Array(FE_N) }, uKap: { value: new Float32Array(FE_N) },
  uFeY0: { value: FE_Y0 }, uFeY1: { value: FE_Y1 }, uGhost: { value: 0 },
};
for (let i = 0; i < FE_N; i++) { const y = FE_Y0 + (FE_Y1 - FE_Y0) * i / (FE_N - 1); FEU.uRi.value[i] = hpInner(y); FEU.uRo.value[i] = hpOuter(y); }

export function feMaterial(base = '#9aa8b5') {
  const mat = new THREE.MeshStandardMaterial({ color: base, metalness: 0.2, roughness: 0.6, side: THREE.DoubleSide, envMapIntensity: 0.6 });
  mat.onBeforeCompile = (sh) => {
    Object.assign(sh.uniforms, FEU);
    sh.vertexShader = 'varying vec3 vFeWP;\n' + sh.vertexShader.replace('#include <worldpos_vertex>', '#include <worldpos_vertex>\nvFeWP = (modelMatrix * vec4(transformed, 1.0)).xyz;');
    sh.fragmentShader = `varying vec3 vFeWP;
uniform float uFE; uniform float uMode; uniform float uP; uniform float uKt; uniform float uDel; uniform vec2 uFc; uniform float uFr;
uniform float uVmax; uniform float uBands; uniform float uEyl; uniform float uFeY0; uniform float uFeY1; uniform float uGhost;
uniform float uRi[${FE_N}]; uniform float uRo[${FE_N}]; uniform float uC0[${FE_N}]; uniform float uC1[${FE_N}]; uniform float uKap[${FE_N}];
float feA(float y, int k) {
  float u = clamp((y - uFeY0) / (uFeY1 - uFeY0), 0.0, 1.0) * ${FE_N - 1}.0;
  int i = int(floor(u)); float f = u - float(i); int j = min(i + 1, ${FE_N - 1});
  float a = k == 0 ? uRi[i] : k == 1 ? uRo[i] : k == 2 ? uC0[i] : k == 3 ? uC1[i] : uKap[i];
  float b = k == 0 ? uRi[j] : k == 1 ? uRo[j] : k == 2 ? uC0[j] : k == 3 ? uC1[j] : uKap[j];
  return mix(a, b, f);
}
vec3 jet(float u) { u = clamp(u, 0.0, 1.0); return clamp(vec3(1.5 - abs(4.0 * u - 3.0), 1.5 - abs(4.0 * u - 2.0), 1.5 - abs(4.0 * u - 1.0)), 0.0, 1.0); }
` + sh.fragmentShader.replace('#include <emissivemap_fragment>', `
      #include <emissivemap_fragment>
      if (uFE > 0.001) {
        float y = vFeWP.y, x = vFeWP.x, rr = length(vFeWP.xz);
        float ri = feA(y, 0), ro = feA(y, 1);
        rr = clamp(rr, ri, ro);
        vec3 col;
        float line = 0.0;
        if (uMode < 0.5) {
          float sa = feA(y, 2) + feA(y, 3) * x;
          float d = max(length(vec2(rr, y) - uFc) - uFr, 0.0);
          float w = smoothstep(uFc.y - 0.08, uFc.y - 0.015, y) * (1.0 - smoothstep(uFc.y + uFr + 0.01, uFc.y + uFr + 0.04, y));
          sa *= 1.0 + (uKt - 1.0) * exp(-d / uDel) * w;
          float A = uP * ri * ri / (ro * ro - ri * ri);
          float sh = A * (1.0 + ro * ro / (rr * rr)), sr = A * (1.0 - ro * ro / (rr * rr));
          float vm = sqrt(0.5 * ((sa - sh) * (sa - sh) + (sh - sr) * (sh - sr) + (sr - sa) * (sr - sa)));
          float u = clamp(vm / uVmax, 0.0, 0.9999);
          col = jet((floor(u * uBands) + 0.5) / uBands);
        } else {
          float ep = max(0.0, feA(y, 4) * abs(x) - uEyl);
          if (ep <= 1e-7) col = vec3(0.16, 0.30, 0.62);
          else if (ep < 0.002) col = mix(vec3(0.10, 0.55, 0.95), vec3(0.20, 0.90, 0.95), ep / 0.002);
          else col = jet(0.62 + 0.38 * clamp(log2(ep / 0.002) / 3.3, 0.0, 1.0));
          float fw = fwidth(ep) * 1.6 + 1e-6;
          line = 1.0 - smoothstep(0.0, fw, abs(ep - 0.002));
        }
        col = mix(col, vec3(1.0), line * 0.9);
        diffuseColor.rgb = mix(diffuseColor.rgb, col * 0.5, uFE);
        totalEmissiveRadiance += col * 0.62 * uFE;
        metalnessFactor *= 1.0 - uFE; roughnessFactor = mix(roughnessFactor, 0.95, uFE);
      }
      diffuseColor.a *= 1.0 - uGhost;`);
  };
  mat.customProgramCacheKey = () => 'fe';
  return mat;
}

// fill the FE arrays for a load state at the wellhead datum: moment Mw (MNm), shear Qw (MN), true wall tension Tw (MN),
// pressure p (MPa). The hub takes the load in from the connector over its grooves; below the landing ring part of the
// load goes to the conductor housing (visual taper, not a load-share analysis).
export function feSetElastic({ Mw, Qw, Tw, p }) {
  for (let i = 0; i < FE_N; i++) {
    const y = FE_Y0 + (FE_Y1 - FE_Y0) * i / (FE_N - 1);
    const ri = FEU.uRi.value[i], ro = FEU.uRo.value[i];
    const A = Math.PI * (ro * ro - ri * ri), I = Math.PI / 4 * (ro ** 4 - ri ** 4);
    const up = y >= 4.0 ? 0 : y <= 3.47 ? 1 : (4.0 - y) / 0.53;
    const tin = up * up * (3 - 2 * up);
    const down = y >= 3.0 ? 1 : y <= 2.0 ? 0.35 : 0.35 + 0.65 * (y - 2.0);
    const M = (Mw + Qw * Math.max(0, 4.0 - y)) * tin * down;
    FEU.uC0.value[i] = Tw * tin * down / A;
    FEU.uC1.value[i] = M / I;
  }
  FEU.uP.value = p; FEU.uMode.value = 0;
}

// equivalent plastic strain mode: curvature per height for a bending moment M (MNm) at the neck. kNeck is the neck
// curvature from the section model (model.json); thicker sections get the curvature of a bilinear tube law.
export function feSetPlastic(M, kNeck, { E = 207000, sy = 517 } = {}) {
  for (let i = 0; i < FE_N; i++) {
    const y = FE_Y0 + (FE_Y1 - FE_Y0) * i / (FE_N - 1);
    const ri = FEU.uRi.value[i], ro = FEU.uRo.value[i];
    const up = y >= 4.0 ? 0 : y <= 3.47 ? 1 : (4.0 - y) / 0.53;
    const tin = up * up * (3 - 2 * up);
    const down = y >= 3.0 ? 1 : y <= 2.0 ? 0.35 : 0.35 + 0.65 * (y - 2.0);
    const Mi = M * tin * down;
    let k;
    if (Math.abs(ro - NECK.ro) < 1e-3 && y < NECK.y1 + 0.004) k = kNeck * tin * down;
    else k = kappaTube(Mi, ro, ri, E, sy);
    FEU.uKap.value[i] = k;
  }
  FEU.uMode.value = 1;
}
// curvature of a tube (bilinear elastic-perfectly plastic) under pure bending M (MNm), by bisection on the moment
const _kt = new Map();
function kappaTube(M, ro, ri, E, sy) {
  const key = ro.toFixed(4) + ri.toFixed(4);
  let tab = _kt.get(key);
  if (!tab) {
    tab = [];
    const ey = sy / E, nr = 24, nt = 96;
    for (let j = 0; j <= 80; j++) {
      const kap = 1e-5 * Math.pow(1.13, j);
      let m = 0;
      for (let a = 0; a < nr; a++) for (let b = 0; b < nt; b++) {
        const r = ri + (a + 0.5) * (ro - ri) / nr, th = (b + 0.5) * 2 * Math.PI / nt, x = r * Math.cos(th);
        const e = kap * x, s = Math.max(-sy, Math.min(sy, E * e));
        m += s * x * r * (ro - ri) / nr * 2 * Math.PI / nt;
      }
      tab.push([kap, m]);
    }
    _kt.set(key, tab);
  }
  if (M <= tab[0][1]) return tab[0][0] * M / tab[0][1];
  for (let j = 0; j < tab.length - 1; j++) if (M <= tab[j + 1][1]) return tab[j][0] + (tab[j + 1][0] - tab[j][0]) * (M - tab[j][1]) / (tab[j + 1][1] - tab[j][1]);
  return tab[tab.length - 1][0] * 4;
}

// cut half of the housing with an FE mesh drawn on it, and the stress classification line at the fillet root
export function feHousing(M) {
  const g = new THREE.Group(); g.name = 'feHousing';
  const mat = M.fe;
  const geo = revolve(HP_PROFILE, { phi0: Math.PI, phi1: 2 * Math.PI, seg: 72 });
  const m = new THREE.Mesh(geo, [mat, mat]); m.castShadow = true; m.receiveShadow = true; g.add(m);
  // mesh lines: rows at constant y (finer near the fillet), columns at constant fraction of the wall
  const rows = [];
  for (let y = 4.0; y > 1.1; ) {
    rows.push(y);
    const near = Math.abs(y - 3.42) < 0.07 ? 0.008 : y > 2.9 ? 0.022 : 0.055;
    y -= near;
  }
  rows.push(1.1);
  const fr = [0, 0.18, 0.34, 0.48, 0.6, 0.71, 0.8, 0.875, 0.94, 1];
  const pts = [];
  const z = 0.0018;
  for (const side of [-1, 1]) {
    for (const y of rows) { const ri = hpInner(y), ro = hpOuter(y); pts.push(side * ri, y, z, side * ro, y, z); }
    for (const f of fr) for (let k = 0; k < rows.length - 1; k++) {
      const y0 = rows[k], y1 = rows[k + 1];
      const a = hpInner(y0) + f * (hpOuter(y0) - hpInner(y0)), b = hpInner(y1) + f * (hpOuter(y1) - hpInner(y1));
      pts.push(side * a, y0, z, side * b, y1, z);
    }
  }
  // the outside surface: rings every other row and meridians every 7.5 degrees
  for (let k = 0; k < rows.length; k += 2) {
    const y = rows[k], ro = hpOuter(y) + 0.0015;
    for (let j = 0; j < 24; j++) {
      const a0 = Math.PI + Math.PI * j / 24, a1 = Math.PI + Math.PI * (j + 1) / 24;
      pts.push(ro * Math.cos(a0), y, ro * Math.sin(a0), ro * Math.cos(a1), y, ro * Math.sin(a1));
    }
  }
  for (let j = 1; j < 24; j++) {
    const a = Math.PI + Math.PI * j / 24;
    for (let k = 0; k < rows.length - 1; k++) {
      const y0 = rows[k], y1 = rows[k + 1], r0 = hpOuter(y0) + 0.0015, r1 = hpOuter(y1) + 0.0015;
      pts.push(r0 * Math.cos(a), y0, r0 * Math.sin(a), r1 * Math.cos(a), y1, r1 * Math.sin(a));
    }
  }
  const lg = new THREE.BufferGeometry(); lg.setAttribute('position', new THREE.Float32BufferAttribute(pts, 3));
  const lines = new THREE.LineSegments(lg, new THREE.LineBasicMaterial({ color: '#0a1622', transparent: true, opacity: 0.5, depthWrite: false }));
  lines.renderOrder = 2; g.add(lines);
  // SCL across the wall at the fillet root, tension side (x > 0)
  const sm = new THREE.MeshBasicMaterial({ color: '#ffffff', transparent: true, opacity: 1, depthTest: false });
  const ys = NECK.y1, L = NECK.ro - NECK.ri;
  const bar = new THREE.Mesh(new THREE.CylinderGeometry(0.0035, 0.0035, L, 10), sm);
  bar.rotation.z = Math.PI / 2; bar.position.set(NECK.ri + L / 2, ys, 0.004); bar.renderOrder = 5;
  const cap0 = new THREE.Mesh(new THREE.SphereGeometry(0.008, 12, 8), sm); cap0.position.set(NECK.ri, ys, 0.004); cap0.renderOrder = 5;
  const cap1 = cap0.clone(); cap1.position.set(NECK.ro, ys, 0.004);
  const scl = new THREE.Group(); scl.add(bar, cap0, cap1); scl.visible = false; g.add(scl);
  g.userData = { mesh: m, lines, scl, sclMat: sm };
  return g;
}

export function wellhead(M, { cut = false, depth = WELL.bottom, seg = 96 } = {}) {
  const g = new THREE.Group(); g.name = cut ? 'wellCut' : 'well';
  const o = cut ? { phi0: Math.PI, phi1: TAU, seg: seg / 2 } : { seg };
  const mat = (m, c = M.cut) => (cut ? [m, c] : m);
  const add = (name, geo, m) => { const x = mesh(geo, m); x.name = name; g.add(x); return x; };
  const W = WELL;
  // HP wellhead housing: hub with H4-like grooves, body, neck with guide ring (contact B), bore 18 3/4 in
  add('hp', revolve(HP_PROFILE, o), mat(M.steel));
  // WH extension (20 in x 1.25 in) and surface casing (20 in x 1 in)
  add('whx', revolve(ring(W.rSC - 0.0318, W.rSC, -0.6, 1.1), o), mat(M.whx));
  add('sc', revolve(ring(W.rSC - W.tSC, W.rSC, depth, -0.6), o), mat(M.casing));
  add('whxWeld', revolve(ring(W.rSC - 0.01, W.rSC + 0.012, 1.085, 1.115), o), mat(M.weld, M.cutWarm));
  // LP conductor housing: landing shoulder sits on template ring C; tapers to the 36 in conductor at GW1
  const lp = [[0.392, 3.1], [0.4826, 3.1], [0.4826, 2.66], [0.565, 2.64], [0.565, 2.47], [0.4826, 2.45], [0.4826, 1.55], [0.4572, 1.25],
    [0.4572, 1.0], [0.4064, 1.0], [0.4064, 1.3], [0.392, 1.35]];
  add('lp', revolve(lp, o), mat(M.lp));
  // contact rings A (HP landing ring on the LP top) are part of the profiles; conductor extension + conductor
  add('cond', revolve(ring(W.rCond - W.tCond, W.rCond, depth, 1.0), o), mat(M.cond));
  add('gw1', revolve(ring(W.rCond - 0.012, W.rCond + 0.013, 0.985, 1.015), o), mat(M.weld, M.cutWarm));
  // conductor connectors every ~12 m below the mudline
  for (const yc of [-11.5, -23.5, -35.5]) add('conn', revolve([[W.rCond - W.tCond, yc - 0.35], [W.rCond + 0.035, yc - 0.3], [W.rCond + 0.035, yc + 0.3], [W.rCond - W.tCond, yc + 0.35]], o), mat(M.steelDark));
  // cement: outside the conductor (to the hole wall) from the mudline down, inside annulus below top of cement
  add('cemOut', revolve(ring(W.rCond, W.rHole, depth, 0.0), o), mat(M.cement, M.cementCut));
  add('cemIn', revolve(ring(W.rSC, W.rCond - W.tCond, depth, W.toc), o), mat(M.cement, M.cementCut));
  g.userData.parts = Object.fromEntries(g.children.map((c) => [c.name, c]));
  return g;
}

// --------------------------------------------------------------------------------------------- template
// 4-slot template; our well sits in slot (0,0); template centre at (-2.6, -2.6) (x, z). Rings: C (upper) y 2.4, D y 0.4.
// cut = true removes everything in front of the section plane z = 0 and halves the slots on that plane.
export function template(M, { cutFront = false } = {}) {
  const g = new THREE.Group(); g.name = cutFront ? 'templateCut' : 'template';
  const cx = -2.6, cz = -2.6, s = 2.6, half = 5.6, top = 2.9;
  const Y = M.yellow, Yd = M.yellowDark;
  const slots = [[cx - s, cz - s], [cx + s, cz - s], [cx - s, cz + s], [cx + s, cz + s]];
  const box = (a, b, w = 0.32, h = 0.32, m = Y) => {
    a = a.slice(); b = b.slice();
    if (cutFront) {
      if (a[2] > 0.01 && b[2] > 0.01) return null;
      for (const [p, q] of [[a, b], [b, a]]) if (p[2] > 0.01) { const u = (0 - q[2]) / (p[2] - q[2]); for (let k = 0; k < 3; k++) p[k] = q[k] + (p[k] - q[k]) * u; }
      if (Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]) < 0.05) return null;
    }
    const x = beam(a, b, w, h, m); g.add(x); return x;
  };
  for (const y of [0.25, top]) {
    const c = [[cx - half, cz - half], [cx + half, cz - half], [cx + half, cz + half], [cx - half, cz + half]];
    for (let i = 0; i < 4; i++) { const [x0, z0] = c[i], [x1, z1] = c[(i + 1) % 4]; box([x0, y, z0], [x1, y, z1], 0.42, 0.42); }
    // centreline girders between the slots
    box([cx - half, y, cz], [cx + half, y, cz], 0.34, 0.42, Yd);
    box([cx, y, cz - half], [cx, y, cz + half], 0.34, 0.42, Yd);
  }
  for (const [x, z] of [[cx - half, cz - half], [cx + half, cz - half], [cx + half, cz + half], [cx - half, cz + half]]) box([x, 0.25, z], [x, top, z], 0.45, 0.45);
  for (const zz of [cz - half]) { box([cx - half, 0.25, zz], [cx, top, zz], 0.18, 0.18, Yd); box([cx + half, 0.25, zz], [cx, top, zz], 0.18, 0.18, Yd); }
  for (const xx of [cx - half, cx + half]) { box([xx, 0.25, cz - half], [xx, top, cz], 0.18, 0.18, Yd); box([xx, 0.25, cz + half], [xx, top, cz], 0.18, 0.18, Yd); }
  // slot rings (C at y 2.4, D at y 0.4) and guide funnels; slots on the section plane are halved with hatched faces
  for (const [x, z] of slots) {
    const onCut = cutFront && Math.abs(z) < 0.01;
    const o = onCut ? { phi0: Math.PI, phi1: TAU, seg: 48 } : { seg: 64 };
    const mm = (m) => (onCut ? [m, M.yellowCut] : m);
    const ringC = mesh(revolve(ring(0.567, 0.80, 2.33, 2.46), o), mm(Y)); ringC.position.set(x, 0, z); g.add(ringC);
    const ringD = mesh(revolve(ring(0.459, 0.72, 0.30, 0.50), o), mm(Y)); ringD.position.set(x, 0, z); g.add(ringD);
    const funnel = mesh(revolve([[0.64, 2.46], [0.80, 2.46], [1.28, 3.06], [1.18, 3.10]], o), mm(Yd)); funnel.position.set(x, 0, z); g.add(funnel);
    // axis-aligned struts from the rings to the girders that bound the slot's cell
    const ex = [x < cx ? cx - half + 0.2 : cx + 0.17, x < cx ? cx - 0.17 : cx + half - 0.2];     // cell x-limits
    const ez = [z < cz ? cz - half + 0.2 : cz + 0.17, z < cz ? cz - 0.17 : cz + half - 0.2];
    for (const [yy, r0] of [[2.395, 0.79], [0.40, 0.71]]) {
      box([x - r0, yy, z], [ex[0], yy, z], 0.22, 0.26, Yd); box([x + r0, yy, z], [ex[1], yy, z], 0.22, 0.26, Yd);
      box([x, yy, z - r0], [x, yy, ez[0]], 0.22, 0.26, Yd); box([x, yy, z + r0], [x, yy, ez[1]], 0.22, 0.26, Yd);
    }
    if (onCut) { g.userData.ringC = ringC; g.userData.ringD = ringD; }
  }
  for (const [x, z] of [[cx - half - 1.2, cz - half - 1.2], [cx + half + 1.2, cz - half - 1.2], [cx + half + 1.2, cz + half + 1.2], [cx - half - 1.2, cz + half + 1.2]]) {
    if (cutFront && z > 0.5) continue;
    const ca = mesh(new THREE.CylinderGeometry(1.6, 1.6, 1.4, 48), Yd); ca.position.set(x, 0.5, z); g.add(ca);
    const top2 = mesh(new THREE.CylinderGeometry(1.65, 1.65, 0.12, 48), Y); top2.position.set(x, 1.2, z); g.add(top2);
    box([x, 1.1, z], [x + Math.sign(cx - x) * 1.6, 0.4, z + Math.sign(cz - z) * 1.6], 0.3, 0.3, Yd);
  }
  g.userData = { ...g.userData, slots, cx, cz, top };
  return g;
}

// --------------------------------------------------------------------------------------------- BOP stack + LMRP + LFJ
export function bopStack(M) {
  const g = new THREE.Group(); g.name = 'bop';
  const y0 = DATUM;              // connector bottom sits on the wellhead datum
  const add = (geo, m, p = [0, 0, 0], r = null) => { const x = mesh(geo, m); x.position.set(...p); if (r) x.rotation.set(...r); g.add(x); return x; };
  const lathe = (pr, m) => add(revolve(pr, { seg: 64 }), m);
  lathe([[0.41, y0 - 0.55], [0.82, y0 - 0.55], [0.82, y0 + 0.9], [0.62, y0 + 1.15], [0.25, y0 + 1.15], [0.25, y0 + 0.02], [0.41, y0 + 0.02]], M.bopDark);       // WH connector over the hub
  for (const [i, yc] of [[0, y0 + 1.9], [1, y0 + 3.0], [2, y0 + 4.1]].map((a) => a)) {
    add(new THREE.BoxGeometry(1.6, 0.95, 1.3), M.bop, [0, yc, 0]);
    for (const s of [-1, 1]) {
      add(new THREE.CylinderGeometry(0.42, 0.42, 0.65, 40), i === 2 ? M.bopRed : M.bopYellow, [s * 1.12, yc, 0], [0, 0, Math.PI / 2]);
      add(new THREE.CylinderGeometry(0.52, 0.52, 0.45, 40), M.bop, [s * 1.62, yc, 0], [0, 0, Math.PI / 2]);
    }
  }
  lathe([[0.25, y0 + 4.7], [0.85, y0 + 4.7], [0.95, y0 + 5.1], [0.95, y0 + 5.8], [0.7, y0 + 6.3], [0.25, y0 + 6.3]], M.bopDark);   // lower annular
  lathe([[0.25, y0 + 6.5], [0.92, y0 + 6.5], [0.92, y0 + 7.4], [0.62, y0 + 7.6], [0.25, y0 + 7.6]], M.bop);                          // LMRP connector
  lathe([[0.25, y0 + 7.8], [0.85, y0 + 7.8], [0.95, y0 + 8.2], [0.95, y0 + 8.9], [0.7, y0 + 9.4], [0.25, y0 + 9.4]], M.bopDark);   // upper annular
  lathe([[0.25, y0 + 9.6], [0.66, y0 + 9.6], [0.72, y0 + 10.3], [0.46, y0 + 11.4], [0.3, y0 + 12.4], [0.25, y0 + 12.4]], M.bop);   // adapter
  const fj = lathe([[0.2, y0 + 12.9], [0.55, y0 + 12.9], [0.62, y0 + 13.3], [0.62, y0 + 14.1], [0.4, y0 + 14.5], [0.2, y0 + 14.5]], M.bopDark); // lower flex joint (centre ~ datum + 13.7)
  // frame + accumulators + pods
  const s = 1.9;
  for (const [x, z] of [[-s, -s], [s, -s], [s, s], [-s, s]]) add(new THREE.BoxGeometry(0.2, 9.8, 0.2), M.bopYellow, [x, y0 + 4.9, z]);
  for (const yy of [y0 + 0.2, y0 + 4.6, y0 + 6.4, y0 + 9.7]) {
    for (const z of [-s, s]) add(new THREE.BoxGeometry(2 * s, 0.16, 0.16), M.bopYellow, [0, yy, z]);
    for (const x of [-s, s]) add(new THREE.BoxGeometry(0.16, 0.16, 2 * s), M.bopYellow, [x, yy, 0]);
  }
  for (let k = 0; k < 6; k++) add(new THREE.CylinderGeometry(0.2, 0.2, 1.8, 20), M.bopYellow, [-1.4 + k * 0.56, y0 + 8.4, -s + 0.35]);
  add(new THREE.BoxGeometry(0.75, 1.5, 0.75), M.bopBlue, [-1.2, y0 + 8.3, s - 0.4]);
  add(new THREE.BoxGeometry(0.75, 1.5, 0.75), M.bopYellow, [1.2, y0 + 8.3, s - 0.4]);
  for (const x of [-1.15, 1.15]) add(new THREE.CylinderGeometry(0.06, 0.06, 12, 10), M.steel, [x, y0 + 6.5, 1.0]);
  g.userData = { lfj: y0 + 13.7 };
  return g;
}

// --------------------------------------------------------------------------------------------- riser, rig, sea
export function riserColumn(M, { y0 = DATUM + 14.5, y1 = 356, joint = 22.9 } = {}) {
  const g = new THREE.Group(); g.name = 'riser';
  const pipe = mesh(new THREE.CylinderGeometry(0.27, 0.27, y1 - y0, 24), M.steel); pipe.position.y = (y0 + y1) / 2; g.add(pipe);
  let y = y0 + 1.5; let k = 0;
  while (y + joint * 0.8 < y1 - 25) {
    const buoy = mesh(new THREE.CylinderGeometry(0.62, 0.62, joint * 0.86, 32), k < 2 ? M.steelDark : M.riserWhite);
    buoy.position.y = y + joint * 0.43; g.add(buoy);
    const fl = mesh(new THREE.CylinderGeometry(0.45, 0.45, 0.35, 24), M.steelDark); fl.position.y = y + joint * 0.93; g.add(fl);
    y += joint; k++;
  }
  for (const x of [-0.5, 0.5]) { const l = mesh(new THREE.CylinderGeometry(0.07, 0.07, y1 - y0, 8), M.steelDark); l.position.set(x, (y0 + y1) / 2, 0.66); g.add(l); }
  return g;
}

export function rig(M) {
  const g = new THREE.Group(); g.name = 'rig';
  const add = (geo, m, p, r = null) => { const x = mesh(geo, m); x.position.set(...p); if (r) x.rotation.set(...r); g.add(x); return x; };
  // two pontoons, six columns, deck box, derrick, cranes, helideck (deck ~ 30 m above the waterline)
  for (const z of [-26, 26]) add(new THREE.BoxGeometry(110, 9, 16), M.rigRed, [0, -13, z]);
  for (const x of [-42, 0, 42]) for (const z of [-26, 26]) add(new THREE.CylinderGeometry(7, 7, 32, 32), M.rigGrey, [x, 0, z]);
  add(new THREE.BoxGeometry(100, 9, 74), M.rigGrey, [0, 19, 0]);
  add(new THREE.BoxGeometry(96, 1.2, 70), M.rigDark, [0, 24, 0]);
  // derrick lattice
  const der = new THREE.Group(); der.position.set(0, 24, 0); g.add(der);
  const H = 58, b0 = 9, b1 = 2.6;
  const corner = (k, y) => { const b = b0 + (b1 - b0) * y / H; const a = k * Math.PI / 2 + Math.PI / 4; return [Math.cos(a) * b, y, Math.sin(a) * b]; };
  for (let k = 0; k < 4; k++) der.add(tubeBetween(corner(k, 0), corner(k, H), 0.45, M.white, 8));
  for (let y = 0; y < H; y += 7) for (let k = 0; k < 4; k++) {
    der.add(tubeBetween(corner(k, y), corner((k + 1) % 4, y), 0.22, M.white, 6));
    der.add(tubeBetween(corner(k, y), corner((k + 1) % 4, y + 7), 0.18, M.white, 6));
  }
  add(new THREE.BoxGeometry(10, 3, 10), M.rigRed, [0, 24 + H + 1.5, 0]);
  // cranes and helideck
  add(new THREE.CylinderGeometry(1.4, 1.8, 10, 16), M.bopYellow, [-40, 29, -30]);
  const boom = tubeBetween([-40, 33, -30], [-12, 46, -42], 0.8, M.bopYellow, 10); g.add(boom);
  add(new THREE.CylinderGeometry(13, 13, 1, 40), M.rigDark, [44, 30, 26]);
  add(new THREE.BoxGeometry(18, 8, 14), M.white, [36, 28, -22]);
  add(new THREE.BoxGeometry(14, 6, 10), M.rigGrey, [-30, 27, 20]);
  // deck and derrick lights (warm white), red aviation light on the crown block
  const lamp = (p, col, r) => { const s = glowBall(M, col, r); s.material.depthTest = true; s.position.set(...p); g.add(s); return s; };
  for (const x of [-48, -24, 0, 24, 48]) for (const z of [-36, 36]) lamp([x, 25.2, z], '#ffd9a0', 0.55);
  for (const y of [34, 48, 62, 76]) lamp([0, y, 0], '#ffe2b8', 0.4);
  lamp([0, 24 + 58 + 3.4, 0], '#ff3b30', 0.7);
  lamp([44, 31, 26], '#9fe1ff', 0.5);
  return g;
}

export function seaSurface(M) {
  const geo = new THREE.PlaneGeometry(2400, 2400, 160, 160); geo.rotateX(-Math.PI / 2);
  const mat = new THREE.MeshStandardMaterial({ color: '#0e4a6b', metalness: 0.1, roughness: 0.25, side: THREE.DoubleSide, transparent: true, opacity: 0.94 });
  mat.onBeforeCompile = (sh) => {
    sh.uniforms.uTime = M.uTime;
    Object.assign(sh.uniforms, { uSunDir: M.sun.dir, uSunCol: M.sun.col, uSunI: M.sun.i, uSkyCol: M.sun.sky });
    sh.vertexShader = 'uniform float uTime;\nvarying vec3 vSeaWP;\n' + sh.vertexShader.replace('#include <begin_vertex>', `
      #include <begin_vertex>
      vec2 p = position.xz;
      float h = 1.6*sin(p.x*0.045 + uTime*0.62) + 1.1*sin(p.y*0.06 - uTime*0.81 + p.x*0.02) + 0.5*sin((p.x+p.y)*0.13 + uTime*1.3);
      transformed.y += h;`).replace('#include <worldpos_vertex>', '#include <worldpos_vertex>\nvSeaWP = (modelMatrix * vec4(transformed, 1.0)).xyz;');
    // sun glitter and sky reflection from the analytic wave slope plus fine ripples (seen from above only)
    sh.fragmentShader = 'uniform float uTime; uniform vec3 uSunDir; uniform vec3 uSunCol; uniform vec3 uSkyCol; uniform float uSunI; varying vec3 vSeaWP;\n' +
      sh.fragmentShader.replace('#include <emissivemap_fragment>', `
      #include <emissivemap_fragment>
      if (gl_FrontFacing && uSunI > 0.0) {
        vec2 q = vSeaWP.xz; float tt = uTime;
        float c1 = cos(q.x*0.045 + tt*0.62), c2 = cos(q.y*0.06 - tt*0.81 + q.x*0.02), c3 = cos((q.x+q.y)*0.13 + tt*1.3);
        float sx = 1.6*0.045*c1 + 1.1*0.02*c2 + 0.5*0.13*c3, sz = 1.1*0.06*c2 + 0.5*0.13*c3;
        sx += 0.07*sin(q.x*0.9 + q.y*0.4 + tt*2.1) + 0.05*sin(q.x*2.3 - q.y*1.7 + tt*3.3) + 0.035*sin(q.x*4.1 + q.y*3.7 - tt*4.0) + 0.02*sin(q.x*9.3 - q.y*7.1 + tt*5.0);
        sz += 0.07*cos(q.y*1.1 - q.x*0.3 + tt*1.9) + 0.05*cos(q.y*2.9 + q.x*1.3 - tt*2.7) + 0.035*cos(q.y*4.3 - q.x*3.1 + tt*3.6) + 0.02*cos(q.y*8.7 + q.x*6.9 - tt*4.6);
        vec3 nW = normalize(vec3(-sx, 1.0, -sz));
        vec3 Vw = normalize(cameraPosition - vSeaWP);
        vec3 Rw = reflect(-Vw, nW);
        float sd = max(dot(Rw, normalize(uSunDir)), 0.0);
        float fres = 0.02 + 0.98 * pow(1.0 - max(dot(nW, Vw), 0.0), 5.0);
        totalEmissiveRadiance += uSunCol * (pow(sd, 1400.0) * 60.0 + pow(sd, 90.0) * 1.6 + pow(sd, 8.0) * 0.08) * uSunI;
        totalEmissiveRadiance += uSkyCol * fres * 0.85 * uSunI;
      }`);
  };
  const m = new THREE.Mesh(geo, mat); m.name = 'sea'; m.position.y = 354; m.receiveShadow = false;
  return m;
}

// sky dome: vertical gradient (zenith -> horizon -> below) with a sun disc and halo; colours/sun from M.sun and M.sky
export function skyDome(M) {
  const mat = new THREE.ShaderMaterial({
    side: THREE.BackSide, depthWrite: false, fog: false,
    uniforms: { uTop: M.sky.top, uHor: M.sky.hor, uLow: M.sky.low, uSunDir: M.sun.dir, uSunCol: M.sun.col, uDisc: M.sky.disc },
    vertexShader: `varying vec3 vDir;
      void main() { vec4 wp = modelMatrix * vec4(position, 1.0); vDir = wp.xyz - cameraPosition; gl_Position = projectionMatrix * viewMatrix * wp; }`,
    fragmentShader: `uniform vec3 uTop; uniform vec3 uHor; uniform vec3 uLow; uniform vec3 uSunDir; uniform vec3 uSunCol; uniform float uDisc; varying vec3 vDir;
      void main() {
        vec3 d = normalize(vDir); float h = d.y;
        vec3 c = h > 0.0 ? mix(uHor, uTop, pow(clamp(h * 1.6, 0.0, 1.0), 0.55)) : mix(uHor, uLow, clamp(-h * 8.0, 0.0, 1.0));
        float s = max(dot(d, normalize(uSunDir)), 0.0);
        c += uSunCol * (smoothstep(0.99955, 0.99975, s) * 6.0 * uDisc + pow(s, 220.0) * 1.2 * uDisc + pow(s, 9.0) * 0.32 * uDisc);
        gl_FragColor = vec4(c, 1.0);
        #include <tonemapping_fragment>
        #include <colorspace_fragment>
      }`,
  });
  const m = new THREE.Mesh(new THREE.SphereGeometry(1900, 64, 32), mat);
  m.frustumCulled = false; m.renderOrder = -10;
  return m;
}

// --------------------------------------------------------------------------------------------- seabed, soil
export function seabed(M, { cut = false } = {}) {
  const g = new THREE.Group(); g.name = cut ? 'seabedCut' : 'seabed';
  const mat = M.sand.clone();
  mat.onBeforeCompile = (sh) => {
    sh.uniforms.uTime = M.uTime;
    sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\nvarying vec3 vWP;').replace('#include <worldpos_vertex>', '#include <worldpos_vertex>\nvWP = (modelMatrix * vec4(transformed,1.0)).xyz;');
    sh.fragmentShader = 'uniform float uTime; varying vec3 vWP;\n' + sh.fragmentShader.replace('#include <emissivemap_fragment>', `
      #include <emissivemap_fragment>
      vec2 q = vWP.xz * 0.55;
      float c = 0.0;
      for (int i = 0; i < 3; i++) { float fi = float(i);
        q += vec2(sin(q.y*1.7 + uTime*(0.5+0.17*fi)), cos(q.x*1.3 - uTime*(0.4+0.13*fi)));
        c += pow(abs(sin(q.x + q.y)), 18.0); }
      totalEmissiveRadiance += vec3(0.35, 0.55, 0.65) * c * 0.22 * smoothstep(60.0, 0.0, length(vWP.xz));`);
  };
  if (!cut) {
    const geo = new THREE.PlaneGeometry(900, 900, 220, 220); geo.rotateX(-Math.PI / 2);
    const p = geo.attributes.position;
    for (let i = 0; i < p.count; i++) { const x = p.getX(i), z = p.getZ(i); const r = Math.hypot(x, z); p.setY(i, r < 9 ? 0 : 0.12 * Math.sin(x * 0.31) * Math.cos(z * 0.23) + 0.05 * Math.sin(x * 1.7 + z * 1.1)); }
    geo.computeVertexNormals();
    const m = new THREE.Mesh(geo, mat); m.receiveShadow = true; g.add(m);
  } else {
    // back half of the seabed (z < 0) and a soil block whose front face (z = 0) shows the strata
    const geo = new THREE.PlaneGeometry(400, 200, 120, 60); geo.rotateX(-Math.PI / 2); geo.translate(0, 0, -100);
    const m = new THREE.Mesh(geo, mat); m.receiveShadow = true; g.add(m);
    const face = new THREE.Mesh(new THREE.PlaneGeometry(400, 60), M.strata); face.position.set(0, -30, -0.58); g.add(face);
    M.strata.map.repeat.set(8, 1);
    const holeMask = new THREE.Mesh(new THREE.PlaneGeometry(2 * WELL.rHole, 60), new THREE.MeshBasicMaterial({ color: '#000', colorWrite: false })); // placeholder (cut well draws over)
    holeMask.visible = false; g.add(holeMask);
  }
  g.userData.mat = mat;
  return g;
}

// --------------------------------------------------------------------------------------------- particles, rays, markers
export function marineSnow(M, { n = 2600, box = [80, 70, 80], center = [0, 30, 0], name = 'snow' } = {}) {
  const r = rng(3); const a = new Float32Array(n * 3);
  for (let i = 0; i < n; i++) { a[i * 3] = center[0] + (r() - 0.5) * box[0]; a[i * 3 + 1] = center[1] + (r() - 0.5) * box[1]; a[i * 3 + 2] = center[2] + (r() - 0.5) * box[2]; }
  const geo = new THREE.BufferGeometry(); geo.setAttribute('position', new THREE.BufferAttribute(a, 3));
  const mat = new THREE.PointsMaterial({ color: '#cfe8ff', size: 0.09, map: M.sprite, transparent: true, opacity: 0.7, depthWrite: false, sizeAttenuation: true });
  const p = new THREE.Points(geo, mat); p.name = name;
  p.userData.base = a.slice(); p.userData.box = box; p.userData.center = center;
  return p;
}
export function updateSnow(p, t) {
  const a = p.geometry.attributes.position.array, b = p.userData.base, [bx, by, bz] = p.userData.box, c = p.userData.center;
  for (let i = 0; i < a.length; i += 3) {
    a[i] = b[i] + 0.25 * Math.sin(t * 0.3 + i);
    let y = b[i + 1] - t * 0.18;
    y = ((y - (c[1] - by / 2)) % by + by) % by + (c[1] - by / 2);
    a[i + 1] = y;
    a[i + 2] = b[i + 2] + 0.25 * Math.cos(t * 0.27 + i * 0.5);
  }
  p.geometry.attributes.position.needsUpdate = true;
}
// snow in a box that travels with the camera (wraps around it), for fast camera moves through the water column
export function updateSnowCam(p, t, c) {
  const a = p.geometry.attributes.position.array, b = p.userData.base, [bx, by, bz] = p.userData.box;
  const wrap = (v, o, s) => o + ((((v - o) % s) + 1.5 * s) % s) - s / 2;
  for (let i = 0; i < a.length; i += 3) {
    a[i] = wrap(b[i] + 0.25 * Math.sin(t * 0.3 + i), c[0], bx);
    a[i + 1] = wrap(b[i + 1] - t * 0.18, c[1], by);
    a[i + 2] = wrap(b[i + 2] + 0.25 * Math.cos(t * 0.27 + i * 0.5), c[2], bz);
  }
  p.geometry.attributes.position.needsUpdate = true;
}
export function godRays(M, { n = 7, y = 60, spread = 40 } = {}) {
  const g = new THREE.Group(); g.name = 'rays';
  const r = rng(9);
  for (let i = 0; i < n; i++) {
    const m = new THREE.Mesh(new THREE.PlaneGeometry(4 + r() * 6, 90), new THREE.MeshBasicMaterial({ map: M.ray, color: '#9fdcff', transparent: true, opacity: 0.08 + r() * 0.06, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide, fog: false }));
    m.position.set((r() - 0.5) * spread, y - 20, (r() - 0.5) * spread - 10);
    m.rotation.set(0, r() * Math.PI, (r() - 0.5) * 0.4);
    m.userData.phase = r() * 10;
    g.add(m);
  }
  return g;
}
export function glowBall(M, color = '#ffb547', r = 0.18) {
  const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: M.sprite, color, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, depthTest: false }));
  s.scale.set(r * 6, r * 6, 1);
  return s;
}

// --------------------------------------------------------------------------------------------- build everything
export async function buildModels(world) {
  const M = materials();
  M.uTime = { value: 0 };
  // sun + sky (defaults: no glitter, neutral overcast); shots that use them set the values in update()
  M.sun = { dir: { value: new THREE.Vector3(0.35, 0.8, 0.45).normalize() }, col: { value: new THREE.Color('#fff1d6') }, i: { value: 0 }, sky: { value: new THREE.Color('#8fb1c8') } };
  M.sky = { top: { value: new THREE.Color('#5d7f9c') }, hor: { value: new THREE.Color('#b9c9d4') }, low: { value: new THREE.Color('#33495f') }, disc: { value: 0 } };
  const SKY0 = { dir: M.sun.dir.value.clone(), col: M.sun.col.value.clone(), i: 0, sky: M.sun.sky.value.clone(), top: M.sky.top.value.clone(), hor: M.sky.hor.value.clone(), low: M.sky.low.value.clone() };
  world.resetModels = () => {
    world.clip.constant = 1e4;
    DEF.uAmp.value = 0; DEF.uStressMix.value = 0; DEF.uGlow.value = 0; DEF.uGlowY.value = -999;
    const parts = world.models.wellCut && world.models.wellCut.userData.parts;
    if (parts) for (const k in parts) parts[k].position.y = 0;
    if (world.models.connCut) world.models.connCut.position.y = 0;
    M.cond.emissive.setRGB(0, 0, 0);
    for (const k of ['steel', 'lp', 'casing', 'whx', 'cond', 'yellow', 'yellowDark', 'connDark']) M[k].emissive.setRGB(0, 0, 0);
    FEU.uFE.value = 0; FEU.uMode.value = 0;
    if (world.models.feHousing) world.models.feHousing.userData.scl.visible = false;
    if (world.models.riser) world.models.riser.rotation.set(0, 0, 0);
    M.sun.dir.value.copy(SKY0.dir); M.sun.col.value.copy(SKY0.col); M.sun.i.value = 0; M.sun.sky.value.copy(SKY0.sky);
    M.sky.top.value.copy(SKY0.top); M.sky.hor.value.copy(SKY0.hor); M.sky.low.value.copy(SKY0.low); M.sky.disc.value = 0;
  };
  world.M = M;
  world.clip = new THREE.Plane(new THREE.Vector3(0, 0, -1), 1e4);     // keeps z <= constant
  for (const k of ['steel', 'steelDark', 'lp', 'cond', 'casing', 'whx', 'cement', 'weld', 'sand', 'strata', 'soilTop', 'yellow', 'yellowDark']) M[k].clippingPlanes = [world.clip];
  const S = world.scene;
  const reg = (name, obj) => { obj.name = name; world.models[name] = obj; S.add(obj); obj.visible = false; return obj; };
  reg('well', wellhead(M));
  reg('feHousing', feHousing(M));
  reg('wellCut', wellhead(M, { cut: true }));
  reg('template', template(M));
  reg('templateCut', template(M, { cutFront: true }));
  // stand-alone wellhead connector (cut half), sits on the datum; used where the BOP is not shown
  reg('connCut', (() => {
    const g = new THREE.Group();
    const geo = revolve([[0.41, 3.45], [0.82, 3.45], [0.82, 4.9], [0.62, 5.15], [0.25, 5.15], [0.25, 4.02], [0.41, 4.02]], { phi0: Math.PI, phi1: TAU, seg: 48 });
    const m = new THREE.Mesh(geo, [M.connDark, M.cut]); m.castShadow = true;
    g.add(m); return g;
  })());
  reg('bop', bopStack(M));
  reg('riser', riserColumn(M));
  reg('rig', (() => { const r = rig(M); r.position.set(0, 354, 0); return r; })());
  reg('sea', seaSurface(M));
  reg('sky', skyDome(M));
  reg('seabed', seabed(M));
  reg('seabedCut', seabed(M, { cut: true }));
  const sb = world.models.seabed.children[0]; sb.material.clippingPlanes = [world.clip];
  const face = new THREE.Mesh(new THREE.PlaneGeometry(400, 60), M.strata); face.position.set(0, -30.02, 0); reg('sliceFace', face);
  reg('snow', marineSnow(M));
  reg('snowHigh', marineSnow(M, { center: [0, 200, 0], box: [120, 300, 120], n: 3000, name: 'snowHigh' }));
  const sc = reg('snowCam', marineSnow(M, { center: [0, 0, 0], box: [34, 34, 34], n: 2200, name: 'snowCam' }));
  sc.frustumCulled = false; sc.material = sc.material.clone(); sc.material.size = 0.07; sc.material.opacity = 0.55;
  reg('rays', godRays(M));
  // contact markers A-H (positions on the cut plane z ~ +0.02)
  const mk = new THREE.Group();
  const P = { F: [0, 4.0], A: [0.42, 3.05], B: [0.388, 1.22], C: [0.6, 2.42], D: [0.5, 0.4], E: [0.33, -5.0], G: [-8.2, 0.05], H: [0.5, -3.0] };
  for (const k in P) { const b = glowBall(M, '#ffb547', 0.12); b.position.set(P[k][0], P[k][1], 0.05); b.name = k; mk.add(b); }
  mk.userData.P = P;
  reg('markers', mk);
  world.update = (t) => { M.uTime.value = t; };
}
