// 3D world: one WebGL renderer, a scene graph built once, and timed "shots" that pose it.
import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { E, W, H, clamp, ease, lerp, smooth } from '../engine/core.js';

export { THREE };

// Shared uniforms for the bending deformation of the well (all deformable materials use them).
export const DEF = {
  uAmp: { value: 0 },                                        // exaggeration x deflection scale
  uDefl: { value: new Float32Array(128) },                   // lateral deflection samples (m) over y in [Y0, Y1]
  uStress: { value: new Float32Array(128) },                 // normalised stress samples (0..1)
  uStressMix: { value: 0 },
  uY0: { value: -60 }, uY1: { value: 24 },
  uGlowY: { value: -999 }, uGlow: { value: 0 },
};
export const DEF_N = 128;

const DEF_VERT_HEAD = `
uniform float uAmp; uniform float uDefl[${DEF_N}]; uniform float uY0; uniform float uY1;
uniform float uStress[${DEF_N}]; uniform float uStressMix; uniform float uGlowY; uniform float uGlow;
varying float vStress; varying float vWorldY;
float sampleArr(float y, bool st){
  float u = clamp((y - uY0) / (uY1 - uY0), 0.0, 1.0) * ${DEF_N - 1}.0;
  int i = int(floor(u)); float f = u - float(i); int j = min(i + 1, ${DEF_N - 1});
  float a = st ? uStress[i] : uDefl[i]; float b = st ? uStress[j] : uDefl[j];
  return mix(a, b, f);
}
`;

// make a material deformable (bending of the well) and optionally stress-coloured
export function deformable(mat, { stress = true } = {}) {
  mat.onBeforeCompile = (sh) => {
    Object.assign(sh.uniforms, DEF);
    sh.vertexShader = DEF_VERT_HEAD + sh.vertexShader.replace('#include <begin_vertex>', `
      #include <begin_vertex>
      vec4 wp0 = modelMatrix * vec4(transformed, 1.0);
      float dx = uAmp * sampleArr(wp0.y, false);
      transformed.x += dx;
      vStress = sampleArr(wp0.y, true);
      vWorldY = wp0.y;`);
    if (stress) {
      sh.fragmentShader = `uniform float uStressMix; uniform float uGlowY; uniform float uGlow; varying float vStress; varying float vWorldY;
vec3 cmap(float x){ x = clamp(x,0.0,1.0);
  vec3 a = vec3(0.10,0.25,0.65), b = vec3(0.12,0.75,0.95), c = vec3(0.98,0.85,0.25), d = vec3(1.0,0.32,0.22);
  return x < 0.33 ? mix(a,b,x/0.33) : (x < 0.66 ? mix(b,c,(x-0.33)/0.33) : mix(c,d,(x-0.66)/0.34)); }
` + sh.fragmentShader.replace('#include <emissivemap_fragment>', `
      #include <emissivemap_fragment>
      diffuseColor.rgb = mix(diffuseColor.rgb, cmap(vStress), uStressMix);
      totalEmissiveRadiance += cmap(vStress) * uStressMix * 0.35;
      float gl = uGlow * exp(-pow((vWorldY - uGlowY) / 0.18, 2.0));
      totalEmissiveRadiance += vec3(1.0, 0.45, 0.25) * gl;`);
    }
  };
  mat.customProgramCacheKey = () => 'deform' + (stress ? 's' : '');
  return mat;
}

// camera path: keys [{t, p:[x,y,z], l:[x,y,z], fov}] -> smooth interpolation
export function camPath(keys, e = ease.inOut3) {
  return (t) => {
    if (t <= keys[0].t) return keys[0];
    for (let i = 0; i < keys.length - 1; i++) {
      const a = keys[i], b = keys[i + 1];
      if (t <= b.t) {
        const u = e(clamp((t - a.t) / (b.t - a.t)));
        return { p: a.p.map((v, k) => lerp(v, b.p[k], u)), l: a.l.map((v, k) => lerp(v, b.l[k], u)), fov: lerp(a.fov ?? 35, b.fov ?? 35, u) };
      }
    }
    return keys[keys.length - 1];
  };
}

// smooth camera path: C1 in time (Catmull-Rom tangents from neighbouring keys), at rest at the first and last key
export function camSpline(keys) {
  const n = keys.length;
  const tan = (i, f) => {
    if (i === 0 || i === n - 1) return keys[i][f].map(() => 0);
    const a = keys[i - 1], b = keys[i + 1];
    return a[f].map((v, k) => (b[f][k] - v) / (b.t - a.t));
  };
  const TG = keys.map((k, i) => ({ p: tan(i, 'p'), l: tan(i, 'l') }));
  return (t) => {
    if (t <= keys[0].t) return keys[0];
    if (t >= keys[n - 1].t) return keys[n - 1];
    let i = 0; while (keys[i + 1].t < t) i++;
    const a = keys[i], b = keys[i + 1], dt = b.t - a.t, u = (t - a.t) / dt;
    const h00 = 2 * u ** 3 - 3 * u ** 2 + 1, h10 = u ** 3 - 2 * u ** 2 + u, h01 = -2 * u ** 3 + 3 * u ** 2, h11 = u ** 3 - u ** 2;
    const hp = (f) => a[f].map((v, k) => h00 * v + h10 * dt * TG[i][f][k] + h01 * b[f][k] + h11 * dt * TG[i + 1][f][k]);
    return { p: hp('p'), l: hp('l'), fov: lerp(a.fov ?? 35, b.fov ?? 35, ease.inOut(u)) };
  };
}

export class World {
  constructor(canvas) {
    this.canvas = canvas;
    this.shots = [];
    this.lastKey = null;
    this.active = null;
    this.models = {};
  }
  async init() {
    const r = this.renderer = new THREE.WebGLRenderer({ canvas: this.canvas, antialias: true, preserveDrawingBuffer: true, powerPreference: 'high-performance' });
    r.setPixelRatio(1);
    r.setSize(W, H, false);
    r.outputColorSpace = THREE.SRGBColorSpace;
    r.toneMapping = THREE.ACESFilmicToneMapping;
    r.toneMappingExposure = 1.05;
    r.shadowMap.enabled = true;
    r.shadowMap.type = THREE.PCFShadowMap;
    r.localClippingEnabled = true;
    const scene = this.scene = new THREE.Scene();
    const pm = new THREE.PMREMGenerator(r);
    this.env = pm.fromScene(new RoomEnvironment(), 0.04).texture;
    scene.environment = this.env;
    scene.background = new THREE.Color('#0a3550');
    scene.fog = new THREE.FogExp2('#0a3550', 0.02);
    this.camera = new THREE.PerspectiveCamera(35, W / H, 0.05, 3000);
    // lights: a cool key from above (sunlight filtered by water), warm-ish fill, hemisphere
    const key = this.key = new THREE.DirectionalLight('#e3f4ff', 2.4);
    key.position.set(18, 40, 22);
    key.castShadow = true;
    key.shadow.mapSize.set(2048, 2048);
    Object.assign(key.shadow.camera, { left: -16, right: 16, top: 16, bottom: -16, near: 1, far: 120 });
    key.shadow.bias = -0.0005;
    scene.add(key); scene.add(key.target);
    this.fill = new THREE.DirectionalLight('#9fc8e8', 0.7); this.fill.position.set(-20, 10, -10); scene.add(this.fill);
    this.hemi = new THREE.HemisphereLight('#8cc4e6', '#3b2f22', 0.75); scene.add(this.hemi);
    this.lightDefaults = { keyCol: key.color.clone(), keyI: key.intensity, keyPos: key.position.clone(), fillCol: this.fill.color.clone(), fillI: this.fill.intensity,
      hemiSky: this.hemi.color.clone(), hemiGround: this.hemi.groundColor.clone(), hemiI: this.hemi.intensity, exposure: r.toneMappingExposure };
    const { buildModels } = await import('./models.js');
    await buildModels(this);
  }
  // register a shot; spec: {cam(t) -> {p,l,fov}, update(t), show: [names], bg, fog, panel:{x,y,w,h}, key(t) -> string}
  shot(t0, t1, spec) { this.shots.push({ t0, t1, ...spec }); this.shots.sort((a, b) => a.t0 - b.t0); }
  setVisible(names) {
    for (const k in this.models) { const m = this.models[k]; if (m && m.isObject3D) m.visible = names.includes(k); }
  }
  render(t) {
    const s = this.shots.find((x) => t >= x.t0 && t < x.t1);
    const cv = this.canvas;
    if (!s) { if (cv.style.visibility !== 'hidden') cv.style.visibility = 'hidden'; this.active = null; return; }
    if (this.active !== s) {
      this.active = s;
      this.lastKey = null;
      const p = s.panel || { x: 0, y: 0, w: W, h: H };
      this.renderer.setSize(Math.round(p.w * (s.scale || 1)), Math.round(p.h * (s.scale || 1)), false);
      cv.style.left = p.x + 'px'; cv.style.top = p.y + 'px'; cv.style.width = p.w + 'px'; cv.style.height = p.h + 'px';
      cv.style.borderRadius = s.panel ? '20px' : '0';
      this.camera.aspect = p.w / p.h;
      this.camera.updateProjectionMatrix();
      this.setVisible(s.show || []);
      this.resetLights();
      this.scene.background = new THREE.Color(s.bg || '#0a3550');
      this.scene.fog.color.set(s.fogColor || s.bg || '#0a3550');
    }
    // opacity of the canvas (fade in/out at shot ends)
    const fi = s.fadeIn ?? 0.6, fo = s.fadeOut ?? 0.6;
    const o = Math.min(fi > 0 ? clamp((t - s.t0) / fi) : 1, fo > 0 ? clamp((s.t1 - t) / fo) : 1);
    const os = o.toFixed(3);
    if (cv.style.opacity !== os) cv.style.opacity = os;
    if (cv.style.visibility !== 'visible') cv.style.visibility = 'visible';
    const c = s.cam(t);
    const fog = typeof s.fog === 'function' ? s.fog(t) : (s.fog ?? 0.02);
    const key = s.key ? s.key(t) : `${t.toFixed(4)}`;
    const stateKey = key + '|' + c.p.map((v) => v.toFixed(4)).join(',') + c.l.map((v) => v.toFixed(4)).join(',') + (c.fov || 35).toFixed(3) + fog.toFixed(5);
    if (stateKey === this.lastKey) return;          // nothing moved: keep the previous image
    this.lastKey = stateKey;
    this.camera.position.set(...c.p);
    this.camera.lookAt(...c.l);
    if (c.fov && Math.abs(c.fov - this.camera.fov) > 1e-4) { this.camera.fov = c.fov; this.camera.updateProjectionMatrix(); }
    this.scene.fog.density = fog;
    if (s.update) s.update(t);
    this.renderer.render(this.scene, this.camera);
  }
  // shots that relight the scene (e.g. dawn) set lights in update(); every new shot starts from the defaults
  resetLights() {
    const d = this.lightDefaults;
    this.key.color.copy(d.keyCol); this.key.intensity = d.keyI; this.key.position.copy(d.keyPos);
    this.fill.color.copy(d.fillCol); this.fill.intensity = d.fillI;
    this.hemi.color.copy(d.hemiSky); this.hemi.groundColor.copy(d.hemiGround); this.hemi.intensity = d.hemiI;
    this.renderer.toneMappingExposure = d.exposure;
    this.scene.environmentIntensity = 1;
    if (this.resetModels) this.resetModels();
  }
  // world point -> stage pixels (for HTML labels), using the camera pose at time t
  project(v, t) {
    const s = this.shots.find((x) => t >= x.t0 && t < x.t1);
    if (!s) return { x: -999, y: -999, z: 1 };
    const c = s.cam(t);
    const cam = this._pcam || (this._pcam = new THREE.PerspectiveCamera());
    const p = s.panel || { x: 0, y: 0, w: W, h: H };
    cam.fov = c.fov || 35; cam.aspect = p.w / p.h; cam.near = 0.05; cam.far = 3000; cam.updateProjectionMatrix();
    cam.position.set(...c.p); cam.lookAt(...c.l); cam.updateMatrixWorld();
    const q = new THREE.Vector3(...v).project(cam);
    return { x: p.x + (q.x + 1) / 2 * p.w, y: p.y + (1 - q.y) / 2 * p.h, z: q.z };
  }
}

// Fill the deformation arrays from a model profile (z down from datum, values per node).
export function setProfile(z, v, stress, { datumY = 4.0, smax = null } = {}) {
  const y0 = DEF.uY0.value, y1 = DEF.uY1.value;
  const zs = z.map((zz) => datumY - zz);           // world y of each node (descending)
  const n = DEF_N;
  const smx = smax || Math.max(...stress.map(Math.abs), 1e-9);
  // above the datum the stack rotates rigidly with the slope of the top segment
  const slope = (v[0] - v[1]) / (zs[0] - zs[1]);     // dv/dy at the datum
  for (let i = 0; i < n; i++) {
    const y = y0 + (y1 - y0) * i / (n - 1);
    let val, st;
    if (y >= zs[0]) { val = v[0] + slope * (y - zs[0]); st = 0; }
    else if (y <= zs[zs.length - 1]) { val = v[v.length - 1]; st = 0; }
    else {
      let k = 0; while (k < zs.length - 1 && zs[k + 1] > y) k++;
      const f = (zs[k] - y) / (zs[k] - zs[k + 1]);
      val = v[k] + (v[k + 1] - v[k]) * f;
      st = Math.abs(stress[k] + (stress[k + 1] - stress[k]) * f) / smx;
    }
    DEF.uDefl.value[i] = val;
    DEF.uStress.value[i] = st;
  }
}
