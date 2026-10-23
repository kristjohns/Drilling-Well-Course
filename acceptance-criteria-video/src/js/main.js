// Boot: data -> HUD -> 3D world -> chapters -> fonts -> layout -> ready. Render mode exposes __seek(t).
import { E, W, H } from './engine/core.js';
import { runLayout, installGlobalDefs } from './engine/scene.js';
import { Timeline } from './engine/timeline.js';
import { buildHud } from './engine/hud.js';

const q = new URLSearchParams(location.search);

async function boot() {
  try {
    const [tl, model] = await Promise.all([
      fetch('data/timeline.json').then((r) => r.json()),
      fetch('data/model.json').then((r) => r.json()),
    ]);
    const T = new Timeline(tl);
    E.T = T; E.data = model; E.sfx = [];
    E.root = document.getElementById('stage');
    installGlobalDefs(E.root);
    E.layer = document.getElementById('layer');
    E.hud = document.getElementById('hud');
    buildHud(T);
    const only = q.get('ch') ? q.get('ch').split(',').map(Number) : null;
    // 3D world (lazy: only if a chapter uses it)
    const { World } = await import('./three/world.js');
    E.world = new World(document.getElementById('gl'));
    await E.world.init();
    const chapters = (await import('./scenes/index.js')).chapters;
    for (const [no, mod] of chapters) {
      if (only && !only.includes(no)) continue;
      await mod.build(E, T, model);
    }
    // fonts: make sure KaTeX + Inter + JetBrains Mono are loaded before measuring
    const fams = ['KaTeX_Main', 'KaTeX_Math', 'KaTeX_Size1', 'KaTeX_Size2', 'KaTeX_Size3', 'KaTeX_Size4', 'KaTeX_AMS'];
    await Promise.all(fams.map((f) => document.fonts.load(`40px ${f}`)).concat([
      document.fonts.load('italic 40px KaTeX_Math'), document.fonts.load('bold 40px KaTeX_Main'), document.fonts.load('italic 40px KaTeX_Main'),
      document.fonts.load('700 40px Inter'), document.fonts.load('500 40px Inter'), document.fonts.load('800 40px Inter'),
      document.fonts.load('600 40px "JetBrains Mono"')]));
    await document.fonts.ready;
    runLayout();
    runLayout();
    window.__duration = T.duration;
    window.__shots = E.world.shots.map((s) => [s.t0, s.t1]);      // 3D shot intervals (the renderer schedules them apart)
    window.__sfx = E.sfx;
    // __seek returns whether the picture can have changed: any DOM mutation or a WebGL draw. The renderer re-uses the
    // previous screenshot when it has not, which makes the many static holds almost free to render.
    const mo = new MutationObserver(() => {});
    mo.observe(E.root, { subtree: true, attributes: true, characterData: true, childList: true });
    window.__seek = (t) => { E.world.didRender = false; E.seek(t); const changed = mo.takeRecords().length > 0 || E.world.didRender; return changed; };
    E.seek(Number(q.get('t') || 0));
    window.__ready = true;
    if (q.get('play')) play(T, Number(q.get('t') || 0));
    else fit();
  } catch (e) {
    console.error(e);
    window.__error = String(e && e.stack || e);
  }
}

function fit() {
  if (q.get('render')) return;
  const s = Math.min(innerWidth / W, innerHeight / H);
  E.stageScale = s;
  E.root.style.transform = `scale(${s})`;
}

function play(T, t0) {
  fit();
  const audio = new Audio('../build/audio/mix.wav');
  const go = () => {
    audio.currentTime = t0;
    audio.play().catch(() => {});
    const start = performance.now() - t0 * 1000;
    const loop = () => { const t = audio.paused ? (performance.now() - start) / 1000 : audio.currentTime; E.seek(t); requestAnimationFrame(loop); };
    loop();
  };
  document.body.addEventListener('click', go, { once: true });
}

addEventListener('resize', fit);
boot();
