// Boot: load fonts + narration timings, build every stage in chronological order,
// expose window.__seek(t) for the renderer and an optional real-time preview player.
import * as E from './engine.js';
import { H } from './lib/svg.js';
import { buildStages } from './stages/index.js';

const params = new URLSearchParams(location.search);

function fitStage() {
  const st = document.getElementById('stage');
  if (params.has('render')) { st.style.transform = 'none'; return; }
  const s = Math.min(innerWidth / 1920, innerHeight / 1080);
  st.style.transform = `scale(${s})`;
}

async function boot() {
  fitStage();
  addEventListener('resize', fitStage);
  await Promise.all([
    document.fonts.load('400 30px Inter'), document.fonts.load('500 30px Inter'), document.fonts.load('600 30px Inter'),
    document.fonts.load('700 30px Inter'), document.fonts.load('800 30px Inter'),
    document.fonts.load('500 20px "JetBrains Mono"'), document.fonts.load('700 20px "JetBrains Mono"'),
  ]);
  await document.fonts.ready;
  const timings = await (await fetch('/src/data/timings.json', { cache: 'no-store' })).json();
  E.T.load(timings);
  const root = document.getElementById('scenes');
  const hud = document.getElementById('hud');
  buildStages(root, hud, E);
  buildHud(hud, E);
  // fade in from / out to black
  const fade = H('div', { style: { position: 'absolute', inset: '0', background: '#000', pointerEvents: 'none', opacity: 1, zIndex: 50 } });
  document.getElementById('stage').append(fade);
  E.A.fromTo(0, fade, { opacity: 1 }, { opacity: 0, duration: 0.9, ease: 'power1.out', immediateRender: true });
  E.A.to(E.T.dur - 1.0, fade, { opacity: 1, duration: 1.0, ease: 'power1.in' });
  window.__duration = E.T.dur;
  window.__seek = (t) => E.renderAt(t);
  window.__sfx = () => E.SFX.slice().sort((a, b) => a.t - b.t);
  E.renderAt(Number(params.get('t') || 0));
  window.__ready = true;
  if (params.has('play')) startPlayer();
}

/** Chapter label + progress bar */
function buildHud(hud, E) {
  const chapters = E.T.data.scenes.filter((s) => s.chapter);
  chapters.forEach((s, i) => {
    const el = H('div', { class: 'chapter' }, H('span', { class: 'num', text: String(i + 1).padStart(2, '0') }), H('span', { class: 'name', text: s.chapter }));
    hud.append(el);
    const next = chapters[i + 1];
    const t0 = s.start + 0.8, t1 = (next ? next.start : E.T.dur) - 0.2;
    if (s.id === 'intro') return;           // cold open stays clean
    E.A.fromTo(t0, el, { autoAlpha: 0, x: -14 }, { autoAlpha: 1, x: 0, duration: 0.5, ease: 'power3.out', immediateRender: true });
    E.A.to(t1 - 0.4, el, { autoAlpha: 0, duration: 0.4 });
  });
  const prog = H('div', { class: 'progress' }, H('i'));
  hud.append(prog);
  const bar = prog.firstChild;
  E.animate(0, 1e9, (t) => { bar.style.width = (100 * Math.min(1, t / E.T.dur)).toFixed(3) + '%'; });
}

/** Real-time preview with narration audio: ?play=1 */
function startPlayer() {
  const audio = new Audio('/build/narration.wav');
  let t0 = null;
  const tick = (now) => {
    if (t0 === null) { t0 = now; audio.currentTime = 0; audio.play().catch(() => {}); }
    const t = (now - t0) / 1000;
    E.renderAt(Math.min(t, E.T.dur));
    if (t < E.T.dur) requestAnimationFrame(tick);
  };
  addEventListener('click', () => requestAnimationFrame(tick), { once: true });
  document.title = '▶ click to play';
}

boot().catch((e) => { console.error(e); window.__error = String(e && e.stack || e); });
