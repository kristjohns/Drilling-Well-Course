// Scene 21 – Check your understanding (590 – 640 s) ---------------------------------------------
// Three questions: the question is read, the options appear, a 6 s think-pause with countdown, then the answer.
import { H, S } from '../lib/svg.js';
import { makeScene } from '../lib/scene.js';
import { installDefs } from '../art/defs.js';
import { GateValve } from '../art/valve.js';
import { gauge } from '../lib/ui.js';

const CY = '#2ED0FF', OR = '#FF9A3C', YEL = '#FFC857', GRN = '#3BDB86', RED = '#FF3B5C', TEAL = '#34D8A8';

export function build(root, E) {
  const { T, tl, gsap, show, hide, fadeIn, fadeOut, window_, sfx, animate, Flow } = E;
  installDefs();
  const w = (id, word, n = 0) => T.word('quiz.' + id, word, n);
  const bt = (id) => T.beat('quiz.' + id);
  const { el, svg } = makeScene(root, E, 'quiz', {});

  /* ------------------------------------------------------------ b1: title card ---- */
  const b1 = bt('b1');
  const title = H('div', { class: 'abs', style: { left: '96px', top: '300px', width: '1300px' } },
    H('div', { class: 'kicker', style: { color: YEL, marginBottom: '18px' }, text: 'Quiz' }),
    H('div', { class: 'h1', text: 'Check your understanding' }));
  el.append(title);
  show(title, b1.start - 0.1, 0.8, { y: 30 });
  const dotsRow = H('div', { class: 'abs', style: { left: '96px', top: '620px', display: 'flex', gap: '28px', alignItems: 'center' } });
  const bigDots = [1, 2, 3].map((n) => H('div', { style: { width: '110px', height: '110px', borderRadius: '50%', display: 'grid', placeItems: 'center', font: '800 56px var(--mono)', color: '#06121C', background: YEL } }, String(n)));
  dotsRow.append(...bigDots, H('div', { style: { font: '600 40px var(--font)', color: '#AFC0CE', marginLeft: '12px' }, text: 'questions' }));
  el.append(dotsRow);
  bigDots.forEach((d, i) => { tl.fromTo(d, { autoAlpha: 0, scale: 0.4 }, { autoAlpha: 1, scale: 1, duration: 0.5, ease: 'back.out(2.4)', immediateRender: true }, w('b1', 'Three') + i * 0.3); });
  show(dotsRow.lastChild, w('b1', 'questions') - 0.1, 0.5, { x: 20, y: 0 });
  hide(title, bt('q1').start - 0.35, 0.5); hide(dotsRow, bt('q1').start - 0.35, 0.5);

  /* ------------------------------------------------------ progress pills (top right) ---- */
  const prog = H('div', { class: 'abs', style: { right: '96px', top: '50px', display: 'flex', gap: '12px' } });
  const pills = [1, 2, 3].map((n) => H('div', { style: { width: '46px', height: '46px', borderRadius: '50%', display: 'grid', placeItems: 'center', font: '800 24px var(--mono)', color: '#AFC0CE', border: '2px solid rgba(170,200,225,.35)', background: 'rgba(5,16,26,.7)' } }, String(n)));
  prog.append(...pills);
  el.append(prog);
  show(prog, bt('q1').start - 0.3, 0.5, { y: -10 }); hide(prog, T.scene('quiz').end - 0.4, 0.4);

  /* ----------------------------------------------------------------- questions ---- */
  /** build one question screen */
  const mkQ = (i, qId, aId, text, opts, correct, caption, reveal) => {
    const q = bt(qId), a = bt(aId);
    const tIn = q.start - 0.35, tOut = a.end + 0.5;
    const g = H('div', { class: 'scene', style: { background: 'none' } });
    el.append(g);
    window_(g, tIn, tOut, { fi: 0.4, fo: 0.45 });
    // progress pill state
    tl.to(pills[i], { borderColor: YEL, color: YEL, duration: 0.3 }, tIn);
    tl.to(pills[i], { borderColor: GRN, color: '#06121C', backgroundColor: GRN, duration: 0.3 }, a.start + 0.3);
    // kicker + question (words light up as they are spoken)
    g.append(H('div', { class: 'kicker abs', style: { left: '96px', top: '150px', color: YEL }, text: `Question ${i + 1} of 3` }));
    const toks = text.split(/\s+/);
    const skip = q.words.length - toks.length;           // "Question one." precedes the displayed text
    const qEl = H('div', { class: 'abs', style: { left: '96px', top: '196px', width: '1500px', font: '800 54px/1.14 var(--font)', letterSpacing: '-0.01em' } });
    const spans = toks.map((tk) => H('span', { style: { opacity: 0.22 }, text: tk + ' ' }));
    qEl.append(...spans);
    g.append(qEl);
    spans.forEach((sp, k) => tl.to(sp, { opacity: 1, duration: 0.18 }, q.start + q.words[k + skip].s));
    // options
    const oy = 440, oh = 168, ow = 552, gap = 36;
    const cards = opts.map((o, k) => {
      const c = H('div', { class: 'abs', style: { left: 96 + k * (ow + gap) + 'px', top: oy + 'px', width: ow + 'px', height: oh + 'px', borderRadius: '22px', background: 'linear-gradient(160deg,rgba(18,44,66,.9),rgba(8,24,38,.92))', border: '2px solid rgba(170,200,225,.25)', display: 'flex', alignItems: 'center', gap: '22px', padding: '0 28px', boxSizing: 'border-box', boxShadow: '0 18px 50px rgba(0,0,0,.4)' } },
        H('div', { style: { width: '66px', height: '66px', borderRadius: '50%', flex: 'none', display: 'grid', placeItems: 'center', font: '800 38px var(--mono)', color: '#06121C', background: '#AFC0CE' } }, 'ABC'[k]),
        H('div', { style: { font: '600 32px/1.22 var(--font)', color: '#EEF4F9' }, text: o }));
      g.append(c);
      const tc = q.end - 1.2 + k * 0.45;
      show(c, tc, 0.55, { y: 28 });
      return c;
    });
    // countdown (think-time): bar shrinks, number counts down
    const tC0 = q.end + 0.25, tC1 = a.start - 0.2;
    const cd = H('div', { class: 'abs', style: { left: '1640px', top: '170px', width: '184px', height: '184px', borderRadius: '50%', display: 'grid', placeItems: 'center', background: 'rgba(5,16,26,.9)', border: `6px solid ${YEL}`, font: '800 96px var(--mono)', color: YEL, boxSizing: 'border-box' }, text: '6' });
    g.append(cd);
    show(cd, tC0 - 0.2, 0.4, { scale: 0.6 }); hide(cd, a.start - 0.1, 0.3);
    animate(tC0 - 0.05, tC1 + 0.05, (t) => { cd.textContent = String(Math.max(1, Math.ceil(tC1 - t))); });
    const think = H('div', { class: 'abs', style: { left: '1640px', top: '366px', width: '184px', textAlign: 'center', font: '600 26px var(--font)', color: YEL }, text: 'Think about it' });
    g.append(think);
    show(think, tC0, 0.4, { y: 8 }); hide(think, a.start - 0.1, 0.3);
    const bar = H('div', { class: 'abs', style: { left: '96px', top: '640px', width: '1728px', height: '8px', borderRadius: '4px', background: YEL, transformOrigin: '0 0', opacity: 0 } });
    g.append(bar);
    tl.fromTo(bar, { opacity: 0, scaleX: 1 }, { opacity: 0.9, duration: 0.2, immediateRender: false }, tC0);
    tl.to(bar, { scaleX: 0, duration: tC1 - tC0, ease: 'none' }, tC0);
    tl.to(bar, { opacity: 0, duration: 0.2 }, tC1);
    // answer
    cards.forEach((c, k) => {
      if (k === correct) {
        tl.to(c, { borderColor: GRN, backgroundColor: 'rgba(14,70,40,.88)', duration: 0.35 }, a.start);
        tl.to(c.firstChild, { backgroundColor: GRN, duration: 0.35 }, a.start);
        const ck = H('div', { class: 'abs', style: { right: '20px', top: '-22px', width: '52px', height: '52px', borderRadius: '50%', display: 'grid', placeItems: 'center', background: GRN, color: '#06121C', font: '800 34px var(--font)', border: '3px solid #06121C' }, text: '✓' });
        c.append(ck);
        tl.fromTo(ck, { autoAlpha: 0, scale: 0.3 }, { autoAlpha: 1, scale: 1, duration: 0.45, ease: 'back.out(3)', immediateRender: true }, a.start + 0.1);
      } else {
        tl.to(c, { opacity: 0.32, duration: 0.4 }, a.start + 0.1);
      }
    });
    sfx(a.start, 'chime', 0.7);
    // explanation caption + visual
    const cp = H('div', { class: 'abs', style: { left: '96px', top: '650px', width: '1728px', font: '600 34px/1.3 var(--font)', color: '#DCE6EE' }, html: caption });
    g.append(cp);
    show(cp, a.start + 0.5, 0.6, { y: 16 });
    const rv = reveal(g, a);
    return { g, a, q };
  };

  /* ===== Q1 : fail-safe closed ===== */
  mkQ(0, 'q1', 'a1', 'What does fail-safe closed mean for a tree valve?',
    ['The valve is always kept closed', 'The valve closes automatically when hydraulic pressure is lost', 'The valve closes only when an operator gives a command'], 1,
    'No hydraulic pressure → the <span style="color:#FFC857">spring</span> closes the valve.',
    (g, a) => {
      const s = S('svg', { viewBox: '0 0 1920 1080', style: { position: 'absolute', inset: 0, width: '1920px', height: '1080px', overflow: 'visible' } });
      g.append(s);
      const rg = S('g');
      s.append(rg);
      const vx = 1240, vy = 842, vs = 1.3;
      rg.append(S('path', { d: `M${vx} ${vy - 105} V${vy + 100}`, stroke: '#93A8B8', 'stroke-width': 34, fill: 'none' }), S('path', { d: `M${vx} ${vy - 105} V${vy + 100}`, stroke: '#050B11', 'stroke-width': 20, fill: 'none' }));
      const valve = GateValve(rg, { x: vx, y: vy, bw: 40, act: 'fs', f0: 1, scale: vs });
      const proc = Flow(rg, `M${vx} ${vy - 105} V${vy + 100}`, { color: OR, w: 9, gap: 24 });
      const gg = gauge(rg, { x: 300, y: 842, r: 78, max: 250, label: 'HYDRAULIC SUPPLY', unit: 'bar', color: CY, v0: 250 });
      // hydraulic line from the gauge to the actuator end-cap
      const [ax, ay] = valve.toWorld(...valve.anchors.actEndLocal);
      const hpath = `M${300 + 94} ${ay} H${ax}`;
      rg.insertBefore(S('path', { d: hpath, stroke: 'rgba(46,208,255,.25)', 'stroke-width': 9, fill: 'none', 'stroke-linecap': 'round' }), valve.g);
      const hyd = Flow(rg, hpath, { color: CY, w: 7, gap: 20 });
      const dot = S('circle', { cx: vx + 190, cy: vy, r: 13, fill: GRN }), tO = S('text', { x: vx + 214, y: vy + 11, fill: GRN, 'font-size': 32, 'font-weight': 800, style: { fontFamily: 'var(--mono)' }, text: 'OPEN' }), tC = S('text', { x: vx + 214, y: vy + 11, fill: RED, 'font-size': 32, 'font-weight': 800, style: { fontFamily: 'var(--mono)' }, text: 'CLOSED', opacity: 0 });
      rg.append(dot, tO, tC);
      fadeIn(rg, a.start + 0.2, 0.5);
      proc.show(a.start + 0.2, 0.4); proc.speed(a.start + 0.2, 70, 0.8);
      hyd.show(a.start + 0.2, 0.4); hyd.speed(a.start + 0.2, 60, 0.8);
      const tLose = w('a1', 'closes');
      gg.to(tLose, 1.5, 0, 'power2.in');
      hyd.speed(tLose + 0.2, 0, 1.0); hyd.hide(tLose + 1.4, 0.4);
      valve.close(tLose + 1.0, 0.8, 'power3.in');
      proc.speed(tLose + 1.4, 0, 0.4); proc.hide(tLose + 2.0, 0.4);
      sfx(tLose + 1.7, 'clunk', 0.9);
      tl.to(dot, { attr: { fill: RED }, duration: 0.15 }, tLose + 1.7); tl.to(tO, { opacity: 0, duration: 0.1 }, tLose + 1.7); tl.to(tC, { opacity: 1, duration: 0.1 }, tLose + 1.7);
      const lost = S('text', { x: 300, y: 954, 'text-anchor': 'middle', fill: RED, 'font-size': 26, 'font-weight': 800, style: { fontFamily: 'var(--mono)' }, text: 'PRESSURE LOST', opacity: 0 });
      rg.append(lost);
      tl.fromTo(lost, { opacity: 0 }, { opacity: 1, duration: 0.3, immediateRender: true }, w('a1', 'lost') - 0.1);
    });

  /* ===== Q2 : which valve closes last ===== */
  mkQ(1, 'q2', 'a2', 'In an emergency shutdown, which valve closes last?',
    ['The wing valve', 'The master valve', 'The downhole safety valve'], 2,
    'Wing valve first, then the master valve – the <span style="color:#FF4F6D">downhole safety valve</span> last.',
    (g, a) => {
      const row = H('div', { class: 'abs', style: { left: '96px', top: '770px', width: '1728px', display: 'flex', alignItems: 'center', gap: '24px' } });
      const tile = (n, name, sub, col) => H('div', { style: { flex: '1', height: '150px', borderRadius: '20px', background: 'linear-gradient(160deg,rgba(18,44,66,.9),rgba(8,24,38,.92))', border: '2px solid rgba(170,200,225,.25)', display: 'flex', alignItems: 'center', gap: '20px', padding: '0 26px', boxSizing: 'border-box' } },
        H('div', { style: { width: '60px', height: '60px', borderRadius: '50%', display: 'grid', placeItems: 'center', background: col, color: '#06121C', font: '800 34px var(--mono)', flex: 'none' } }, String(n)),
        H('div', {}, H('div', { style: { font: '800 38px var(--mono)', color: '#EEF4F9' }, text: name }), H('div', { style: { font: '500 24px var(--font)', color: '#AFC0CE', marginTop: '4px' }, text: sub })));
      const t1 = tile(1, 'PWV', 'wing valve', '#FF8A9B'), t2 = tile(2, 'PMV', 'master valve', '#FF8A9B'), t3 = tile(3, 'DHSV', 'downhole safety valve', RED);
      const arr = () => H('div', { style: { font: '800 54px var(--font)', color: '#6F879A', flex: 'none' }, text: '→' });
      const a1 = arr(), a2 = arr();
      row.append(t1, a1, t2, a2, t3);
      g.append(row);
      [[t1, 0], [a1, 0.25], [t2, 0.5], [a2, 0.75], [t3, 1.0]].forEach(([n, d]) => show(n, a.start + 0.2 + d, 0.5, { y: 24 }));
      tl.to(t3, { borderColor: RED, boxShadow: '0 0 40px rgba(255,59,92,.5)', duration: 0.4 }, w('a2', 'downhole') - 0.1);
      const last = H('div', { class: 'abs', style: { right: '30px', top: '-20px', padding: '6px 16px', borderRadius: '10px', background: RED, color: '#fff', font: '800 22px var(--mono)' }, text: 'LAST' });
      t3.style.position = 'relative'; t3.append(last);
      tl.fromTo(last, { autoAlpha: 0, y: 10 }, { autoAlpha: 1, y: 0, duration: 0.4, immediateRender: true }, w('a2', 'last') - 0.1);
    });

  /* ===== Q3 : crossover valve ===== */
  mkQ(2, 'q3', 'a3', 'Which valve do you open, together with the annulus master valve, to bleed annulus pressure into the flowline?',
    ['The chemical injection valve', 'The crossover valve', 'The swab valve'], 1,
    'Annulus master valve + <span style="color:#BC8FFF">crossover valve</span> open → annulus pressure bleeds into the flowline.',
    (g, a) => {
      const s = S('svg', { viewBox: '0 0 1920 1080', style: { position: 'absolute', inset: 0, width: '1920px', height: '1080px', overflow: 'visible' } });
      g.append(s);
      const rg = S('g');
      s.append(rg);
      const y0 = 874;
      rg.append(S('rect', { x: 130, y: y0 - 30, width: 360, height: 60, rx: 14, fill: 'rgba(52,216,168,.16)', stroke: TEAL, 'stroke-width': 3 }), S('text', { x: 310, y: y0 + 10, 'text-anchor': 'middle', fill: TEAL, 'font-size': 26, 'font-weight': 800, style: { fontFamily: 'var(--mono)' }, text: 'ANNULUS' }),
        S('rect', { x: 1360, y: y0 - 30, width: 440, height: 60, rx: 14, fill: 'rgba(255,154,60,.16)', stroke: OR, 'stroke-width': 3 }), S('text', { x: 1580, y: y0 + 10, 'text-anchor': 'middle', fill: OR, 'font-size': 26, 'font-weight': 800, style: { fontFamily: 'var(--mono)' }, text: 'FLOWLINE' }),
        S('path', { d: `M490 ${y0} H1360`, stroke: '#93A8B8', 'stroke-width': 26, fill: 'none' }), S('path', { d: `M490 ${y0} H1360`, stroke: '#050B11', 'stroke-width': 16, fill: 'none' }));
      const vAMV = GateValve(rg, { x: 700, y: y0, rot: 90, bw: 26, act: 'fs', f0: 0 });
      const vXOV = GateValve(rg, { x: 1090, y: y0, rot: 90, bw: 26, act: 'fs', f0: 0 });
      const lab = (x, text, col) => S('text', { x, y: y0 + 56, 'text-anchor': 'middle', fill: col, 'font-size': 26, 'font-weight': 800, style: { fontFamily: 'var(--mono)' }, text });
      rg.append(lab(700, 'AMV', '#EEF4F9'), lab(1090, 'XOV', '#BC8FFF'));
      const f = Flow(rg, `M490 ${y0} H1360`, { color: TEAL, w: 9, gap: 24 });
      fadeIn(rg, a.start + 0.2, 0.5);
      vAMV.open(a.start + 0.5, 0.9); vXOV.open(w('a3', 'crossover') - 0.1, 0.9);
      f.show(w('a3', 'crossover') + 0.6, 0.4); f.speed(w('a3', 'crossover') + 0.6, 80, 0.8);
      sfx(w('a3', 'crossover'), 'slide', 0.5);
    });

  hide(prog, T.scene('quiz').end - 0.4, 0.4);
}
