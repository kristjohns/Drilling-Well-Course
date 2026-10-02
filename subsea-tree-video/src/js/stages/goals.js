// Scene 2 – Learning objectives (31 – 57 s) ---------------------------------------
import { H, S } from '../lib/svg.js';
import { makeScene, iconSvg } from '../lib/scene.js';
import { icons } from '../art/icons.js';
import { installDefs } from '../art/defs.js';

export function build(root, E) {
  const { T, A, tl, show, hide, fadeIn, fadeOut, stagger, gsap } = E;
  installDefs();
  const { el, svg, sc } = makeScene(root, E, 'goals');

  const kicker = H('div', { class: 'kicker abs', style: { left: '96px', top: '150px', color: '#FFC857' }, text: 'Learning objectives' });
  const title = H('div', { class: 'h2 abs', style: { left: '96px', top: '188px' }, text: 'What you will learn' });
  el.append(kicker, title);
  show(kicker, T.start('goals.b1') - 0.2, 0.6);
  show(title, T.start('goals.b1') - 0.1, 0.7);

  const items = [
    { ic: icons.template, col: '#2ED0FF', text: 'Place the tree in a subsea production system and name its four jobs', beat: 'b2' },
    { ic: icons.valve, col: '#34D8A8', text: 'Identify the main valves and explain what each one does', beat: 'b3' },
    { ic: icons.spring, col: '#FFC857', text: 'Explain why the valves are fail-safe closed and how they are controlled', beat: 'b4' },
    { ic: () => icons.shields(), col: '#FF4F6D', text: 'Describe how the tree works as a well barrier', beat: 'b5' },
    { ic: icons.pin, col: '#BC8FFF', text: 'Recognise the trees used on the Norwegian shelf today', beat: 'b6' },
  ];
  const x0 = 96, y0 = 320, w = 1080, h = 106, gap = 16;
  const cards = items.map((it, i) => {
    const card = H('div', { class: 'card', style: { left: x0 + 'px', top: y0 + i * (h + gap) + 'px', width: w + 'px', height: h + 'px', display: 'flex', alignItems: 'center', gap: '24px', padding: '0 30px 0 26px' } });
    const num = H('div', { style: { width: '54px', height: '54px', borderRadius: '50%', flex: 'none', display: 'grid', placeItems: 'center', font: '700 28px var(--mono)', color: '#06121C', background: it.col } }, String(i + 1));
    const ico = iconSvg(it.ic('#EEF4F9'), 62);
    const txt = H('div', { style: { font: '600 31px/1.22 var(--font)', color: '#EEF4F9' }, text: it.text });
    const bar = H('div', { style: { position: 'absolute', left: '0', top: '14px', bottom: '14px', width: '6px', borderRadius: '3px', background: it.col, opacity: 0 } });
    card.append(bar, num, ico, txt);
    el.append(card);
    return { card, bar, num, ico, txt, it };
  });
  // slots appear dimmed while "five things" is said; each lights up on its own beat
  cards.forEach((c, i) => {
    const t0 = T.start('goals.b1') + 1.9 + i * 0.12;
    tl.fromTo(c.card, { autoAlpha: 0, x: -30 }, { autoAlpha: 0.32, x: 0, duration: 0.5, ease: 'power3.out', immediateRender: true }, t0);
    const tb = T.start('goals.' + c.it.beat);
    tl.to(c.card, { autoAlpha: 1, duration: 0.35, ease: 'power2.out' }, tb - 0.05);
    tl.to(c.bar, { opacity: 1, duration: 0.3 }, tb);
    tl.fromTo(c.num, { scale: 1 }, { scale: 1.18, duration: 0.25, ease: 'back.out(3)', yoyo: true, repeat: 1, immediateRender: false }, tb);
    const tn = i < 4 ? T.start('goals.' + items[i + 1].beat) : T.end('goals.b6') + 0.4;
    tl.to(c.card, { autoAlpha: 0.62, duration: 0.5 }, tn - 0.05);
    tl.to(c.bar, { opacity: 0, duration: 0.4 }, tn);
    E.sfx(tb, 'tick', 0.6);
  });
  // the big icon on the right
  const stage = S('g', { transform: 'translate(1520 560)' });
  svg.append(stage);
  const glow = S('circle', { r: 250, fill: 'url(#gGlowCyan)', opacity: 0.22 });
  const ring = S('circle', { r: 214, fill: 'rgba(8,26,42,.55)', stroke: 'rgba(170,200,225,.22)', 'stroke-width': 2 });
  stage.append(glow, ring);
  const big = items.map((it, i) => {
    const g = S('g', { transform: 'scale(2.35)' });
    const ico = it.ic(it.col);
    ico.querySelectorAll('[stroke-width]').forEach((n) => n.setAttribute('stroke-width', (parseFloat(n.getAttribute('stroke-width')) * 0.62).toFixed(2)));
    g.append(ico);
    stage.append(g);
    gsap.set(ico, { autoAlpha: 0 });
    const tb = T.start('goals.' + it.beat);
    const tn = i < 4 ? T.start('goals.' + items[i + 1].beat) : T.end('goals.b6') + 0.3;
    tl.fromTo(ico, { autoAlpha: 0, y: 14 }, { autoAlpha: 1, y: 0, duration: 0.55, ease: 'power3.out', immediateRender: false }, tb);
    tl.to(ico, { autoAlpha: 0, duration: 0.35 }, tn - 0.05);
    return ico;
  });
  fadeIn(stage, T.start('goals.b1') + 0.8, 0.8);
  tl.to(glow, { attr: { fill: 'url(#gGlowWarm)' }, duration: 0.01 }, T.start('goals.b4'));
}
