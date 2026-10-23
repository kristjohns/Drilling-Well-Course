// Chapter 5 — summary: when has the template interface failed? Sources and disclaimer.
import { E, ease, COL } from '../engine/core.js';
import { Scene, later } from '../engine/scene.js';
import { titleCard, clause } from '../engine/hud.js';
import { table } from './kit.js';

export async function build(E, T, D) {
  const ch = T.ch(5);
  titleCard(ch, 'When has the template interface failed?');
  const b = (id) => T.b(id), c = (id, n) => T.c(id, n);

  // ------------------------------------------------------------------ 5.1 the table
  {
    const B = b('5.1');
    const S = new Scene(B.start, B.end + 0.2);
    clause('U-001 13.3.6 · Annex B · EN 1993-1-1 6.2.1(5) · EN 1993-1-5 Annex C', B.start + 0.3, B.end);
    S.div('WHEN HAS IT FAILED?', { x: 110, y: 140, cls: 'kicker' }).in(B.start + 0.3, 0.6, 'left');
    const rows = [
      ['fn', 'Interface function', 'relative displacement uses up the margin to the end stops (100 mm, 0.3° tilt) · SLS, load factor 1.0', 'U-001 13.3.6 · Table A.2&nbsp;note&nbsp;d'],
      ['wh', 'Wellhead side', 'load > F<sub>d</sub> × capacity · σ<sub>y</sub> at 0.2 % plastic strain', 'U-001 Annex B · B.9'],
      ['tel', 'Template · elastic', 'von Mises at a point > f<sub>y</sub>/γ<sub>M0</sub>', 'EN 1993-1-1 6.2.1(5) · γ<sub>M</sub> from N-004'],
      ['tnl', 'Template · non-linear', 'maximum load (buckling) or 5 % principal membrane strain (tension) · α<sub>u</sub> &gt; α<sub>1</sub>α<sub>2</sub> (C.2)', 'EN 1993-1-5 Annex C (informative) · NA'],
      ['two', '2 % strain', 'not a criterion of EN 1993-1-5', '—'],
    ];
    const card = S.card(`<table class="t sum"><thead><tr><th class="l">Where</th><th class="l">Failed when</th><th class="l">Source</th></tr></thead><tbody>${rows.map(([, a, w, s]) => `<tr><td class="l" style="font-weight:700;color:#e9f2f9">${a}</td><td class="l" style="white-space:normal;width:820px">${w}</td><td class="l" style="white-space:normal;width:440px;color:#4fd1ff;font-family:var(--mono);font-size:19px">${s}</td></tr>`).join('')}</tbody></table>`,
      { x: 110, y: 200, w: 1700, cls: 'glass' });
    card.el.querySelector('table').style.fontSize = '24px';
    card.in(c('5.1', 'fn') - 0.6, 0.5, 'rise');
    later(() => {
      const trs = [...card.el.querySelectorAll('tbody tr')];
      trs.forEach((el, i) => {
        for (const td of el.querySelectorAll('td')) { td.style.paddingTop = '16px'; td.style.paddingBottom = '16px'; td.style.verticalAlign = 'top'; }
        const a = S.track(new (card.constructor)(el, { o: 0 }));
        a.in(c('5.1', rows[i][0]) - 0.2, 0.5, 'none');
        if (i === 4) el.querySelectorAll('td')[1].style.color = '#ffb547';
      });
    });
  }

  // ------------------------------------------------------------------ 5.2 sources and disclaimer
  {
    const B = b('5.2');
    const S = new Scene(B.start, B.end + 2.0, { fadeOut: 1.2 });
    S.div('Sources', { x: 110, y: 150, cls: 'h2' }).in(B.start + 0.3, 0.6, 'write');
    const src = [
      'NORSOK U-001:2026 Subsea production systems — 3.1.12, 3.1.22, 13.3.6, Annex A (Table A.2), Annex B, Annex J (Figure J.1)',
      'NORSOK N-001 Integrity of offshore structures · NORSOK N-004:2022 Design of offshore structures',
      'NS-EN ISO 13628-15:2011 clause 5.4 (as called up by U-001 13.3.6.1)',
      'EN 1993-1-1:2005 Eurocode 3 — 3.2.1, 6.2.1(5) · EN 10025-2 (S355 yield strength by thickness)',
      'NS-EN 1993-1-5:2006+A2:2019 Eurocode 3 — Annex C (informative): C.6, Figure C.2, C.7, C.8, C.9 · EN 1993-1-14:2025',
    ];
    src.forEach((s, i) => S.div(`<span style="color:#4fd1ff;margin-right:14px">·</span>${s}`, { x: 120, y: 260 + i * 62, cls: 'small', style: 'font-size:25px' }).in(B.start + 0.6 + i * 0.35, 0.5, 'left'));
    const disc = S.card(`<div style="font-weight:700;font-size:26px;margin-bottom:8px">Teaching inputs</div><div class="small" style="font-size:23px">The slot ring, its load, the load share and the material factors are illustrative, not project data. The ring was analysed with a fibre beam model; a real check models the plates, welds, struts and contact. Verify every clause against the editions and the National Annex of your design basis.</div>`,
      { x: 110, y: 600, w: 1700, cls: 'glass' });
    disc.in(c('5.2', 'src'), 0.6, 'rise');
    const end = S.div('The template interface · a follow-up to “Acceptance criteria for structural analysis”', { x: 960, y: 900, cls: 'small', anchor: 'cm', style: 'color:#7f97aa' });
    end.in(c('5.2', 'src') + 2.0, 0.8);
  }
}
