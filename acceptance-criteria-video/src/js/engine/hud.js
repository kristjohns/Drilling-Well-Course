// Heads-up display: chapter chip, method-step tracker, clause reference chip, chapter title cards.
import { Actor, E, ease, W, H } from './core.js';
import { Scene, later } from './scene.js';

export const STEPS = [];

export function buildHud(T) {
  const S = new Scene(0, T.duration + 10, { fade: 0.01, parent: E.hud });
  E.hudScene = S;
  // chapter chips
  for (const c of T.j.chapters) {
    if (c.no === 0) continue;
    const t0 = c.title_card ? c.title_card[1] : c.start;
    const chip = S.div(`<span class="n">${String(c.no).padStart(2, '0')}</span>${c.title}`, { x: 48, y: 40, cls: 'chip' });
    const outro = c.beats.find((b) => b.name === 'outro');      // the outro plays without the chip
    chip.in(t0 + 0.2, 0.6, 'left').out(outro ? outro.start : c.end - 0.4, 0.4);
  }
  return S;
}

// clause reference chip at the bottom left
export function clause(text, t0, t1) {
  const S = E.hudScene;
  const a = S.div(text, { x: 48, y: 1080 - 40 - 36, cls: 'clause' });
  a.in(t0, 0.5, 'left').out(t1 - 0.3, 0.3);
  return a;
}

// chapter title card
export function titleCard(c, sub = '') {
  const [t0, t1] = c.title_card;
  const S = new Scene(t0, t1 + 0.35, { fade: 0.35, fadeOut: 0.5, z: 4 });
  const no = S.div(`CHAPTER ${String(c.no).padStart(2, '0')}`, { x: 160, y: 360, cls: 'ctitle no', style: "font-family:var(--mono);font-weight:700;font-size:30px;color:var(--cyan);letter-spacing:0.14em" });
  const tt = S.div(c.title, { x: 156, y: 410, style: 'font-weight:800;font-size:104px;letter-spacing:-0.03em;line-height:1.02;width:1500px' });
  const bar = S.div('', { x: 160, y: 560, w: 520, h: 6, cls: 'bar' });
  no.in(t0 + 0.1, 0.5, 'left');
  tt.in(t0 + 0.2, 0.7, 'write');
  bar.set(0, { sx: 0 }).to(t0 + 0.25, 0.9, { sx: 1 }, ease.out3);
  bar.el.style.transformOrigin = '0 50%';
  const se = sub ? S.div(sub, { x: 160, y: 600, cls: 'body', style: 'width:1400px' }) : null;
  if (se) se.in(t0 + 0.6, 0.6);
  // a title on two lines pushes the block apart, centred on the same middle
  later(() => {
    const extra = Math.max(0, tt.el.offsetHeight - 112);
    if (!extra) return;
    no.el.style.top = (360 - extra / 2) + 'px'; tt.el.style.top = (410 - extra / 2) + 'px';
    bar.el.style.top = (560 + extra / 2) + 'px'; if (se) se.el.style.top = (600 + extra / 2) + 'px';
  });
  E.sfx.push({ t: t0, type: 'whoosh' });
  return S;
}
