// One-page companion handout (A4 landscape) – rendered to PDF by tools/cheatsheet.mjs
import { H, S } from './lib/svg.js';
import { installDefs } from './art/defs.js';
import { buildTree, W } from './art/tree.js';

installDefs();
const sheet = document.getElementById('sheet');

const rows = [
  [1, 'PMV', 'Production master', 'Main isolation of the well; part of the secondary barrier', 'OPEN', '', 'Closes'],
  [2, 'PWV', 'Production wing', 'Opens and closes the way to the flowline; first valve to close in an ESD', 'OPEN', '', 'Closes'],
  [3, 'CHOKE', 'Production choke', 'Sets how much flows (pressure drop); the insert is retrievable', 'ADJUSTED', '', '–'],
  [4, 'PSV', 'Production swab', 'Vertical access for wireline / intervention tools', 'CLOSED', '', 'Closes'],
  [5, 'AMV', 'Annulus master', 'Access to the annulus (tubing–casing) for monitoring', 'OPEN', '', 'Closes'],
  [6, 'AWV', 'Annulus wing', 'Side outlet from the annulus', 'CLOSED', '', 'Closes'],
  [7, 'ASV', 'Annulus swab', 'Vertical access to the annulus', 'CLOSED', '', 'Closes'],
  [8, 'XOV', 'Crossover', 'With the AMV open: bleeds annulus pressure into the flowline', 'CLOSED', '', 'Closes'],
  [9, 'CIV', 'Chemical injection', 'Injects chemicals such as MEG to prevent hydrates', 'OPEN', 'when injecting', 'Closes'],
  [10, 'DHSV', 'Downhole safety', 'Closes the tubing deep in the well – the last line of defence', 'OPEN', '', 'Closes'],
];

sheet.append(
  H('header', {}, H('div', {}, H('div', { class: 'sub', text: 'Subsea production · vertical tree (VXT)' }), H('h1', { text: 'Valve cheat sheet' })),
    H('div', { class: 'sub', style: { textAlign: 'right' }, html: 'Companion to the video<br><b style="color:#0F1B26">The Subsea Christmas Tree: How It Works</b>' })));

/* tree illustration with numbered valves */
const treeBox = H('div', { class: 'tree' });
const svg = S('svg', { viewBox: '-640 -940 1290 960', width: 480, height: 470, preserveAspectRatio: 'xMidYMid meet' });
treeBox.append(svg);
const g = S('g');
svg.append(g);
const tree = buildTree(g);
// hide the dynamic overlays that belong to the animation only
Object.entries(tree.overlays).forEach(([k, o]) => { if (o.g && !['xover', 'ci'].includes(k)) o.g.setAttribute('opacity', 0); });
// the crossover and chemical-injection hardware are hidden by default (revealed in the animation): show them here
[tree.overlays.xover.g, tree.overlays.ci.g, tree.valves.XOV.g, tree.valves.CIV.g].forEach((n) => { n.style.opacity = 1; n.style.visibility = 'visible'; n.setAttribute('opacity', 1); });
const A = { 1: [0, 500], 2: [-230, 320], 3: [-400, 320], 4: [0, 110], 5: [150, 500], 6: [400, 320], 7: [150, 110], 8: [300, 130], 9: [-390, 430] };
Object.entries(A).forEach(([n, [x, y]]) => {
  const [wx, wy] = W(x, y);
  const off = { 1: [-70, 70], 2: [0, -150], 3: [0, -140], 4: [-70, -60], 5: [70, 70], 6: [0, -140], 7: [80, -60], 8: [0, -100], 9: [-60, 70] }[n];
  const px = wx + off[0], py = wy + off[1];
  g.append(S('path', { d: `M${wx} ${wy} L${px} ${py}`, stroke: '#FFC857', 'stroke-width': 7, fill: 'none' }), S('circle', { cx: wx, cy: wy, r: 14, fill: '#FFC857', stroke: '#06121C', 'stroke-width': 4 }),
    S('circle', { cx: px, cy: py, r: 34, fill: '#FFC857', stroke: '#06121C', 'stroke-width': 6 }), S('text', { x: px, y: py + 13, 'text-anchor': 'middle', fill: '#06121C', 'font-size': 38, 'font-weight': 800, style: { fontFamily: 'JetBrains Mono' }, text: n }));
});
// DHSV marker below the wellhead
const [dx, dy] = W(0, 880);
g.append(S('path', { d: `M${dx} ${dy - 30} V${dy - 5}`, stroke: '#FF4F6D', 'stroke-width': 8, 'marker-end': '' }), S('circle', { cx: dx + 130, cy: dy - 10, r: 34, fill: '#FF4F6D', stroke: '#06121C', 'stroke-width': 6 }),
  S('text', { x: dx + 130, y: dy + 3, 'text-anchor': 'middle', fill: '#fff', 'font-size': 34, 'font-weight': 800, style: { fontFamily: 'JetBrains Mono' }, text: '10' }),
  S('text', { x: dx + 180, y: dy + 2, fill: '#FFB3C0', 'font-size': 30, 'font-weight': 700, text: '↓ deep in the well (DHSV)' }));

const table = H('table', {}, H('colgroup', {}, H('col', { style: { width: '26px' } }), H('col', { style: { width: '132px' } }), H('col'), H('col', { style: { width: '84px' } }), H('col', { style: { width: '66px' } })),
  H('thead', {}, H('tr', {}, H('th', { text: '' }), H('th', { text: 'Valve' }), H('th', { text: 'What it does' }), H('th', { text: 'Normal' }), H('th', { text: 'No pressure' }))),
  H('tbody', {}, ...rows.map(([n, tag, name, what, st, stSub, fs]) => H('tr', {},
    H('td', { class: 'n' }, H('span', { class: 'num', text: String(n) })),
    H('td', { class: 'v' }, H('div', { class: 'tag', text: tag }), H('div', { class: 'nm', text: name })),
    H('td', { text: what }),
    H('td', {}, H('div', { class: 'st ' + (st === 'OPEN' ? 'open' : st === 'CLOSED' ? 'closed' : 'adj'), text: st }), stSub ? H('div', { class: 'sub', text: stSub }) : null),
    H('td', {}, H('span', { class: 'st ' + (fs === 'Closes' ? 'closed' : ''), text: fs }))))));
sheet.append(H('div', { class: 'row1' }, treeBox, H('div', {}, table)));

const chips = (items) => H('div', { class: 'chips' }, ...items.map((c, i) => H('span', { class: 'chip' }, i ? H('span', { class: 'arrow', text: '→ ' }) : null, H('span', { html: c }))));
sheet.append(H('div', { class: 'row2' },
  H('div', { class: 'box' }, H('h3', { class: 'red', text: 'Emergency shutdown – closing order' }), chips(['1 PWV', '2 PMV', '3 DHSV']),
    H('p', { html: 'The wing valve is designed to close against the flow. The <b>downhole safety valve</b> closes last – the last line of defence.' })),
  H('div', { class: 'box' }, H('h3', { text: 'From command to motion' }), chips(['MCS', 'umbilical', 'SCM', 'solenoid', 'DCV', 'actuator']),
    H('p', { html: 'Valves are <b>held open by hydraulic pressure</b> and <b>closed by springs</b>. Lose power or pressure → the springs close the valve (fail-safe). Sensors report back; an ROV can operate the valves directly.' })),
  H('div', { class: 'box' }, H('h3', { text: 'Two independent, tested barriers' }),
    H('p', { style: { marginTop: '0' }, html: '<b class="blue">Primary:</b> tubing · packer · downhole safety valve' }),
    H('p', { html: '<b class="red">Secondary:</b> casing and cement · wellhead · tubing hanger · <b>tree with its valves</b>' }),
    H('p', { html: 'Barrier elements are tested regularly to prove they still work.' })),
  H('div', { class: 'box' }, H('h3', { text: 'Quiz answers' }),
    H('p', { style: { marginTop: '0' }, html: '<b>1 · B</b> – closes automatically when hydraulic pressure is lost' }),
    H('p', { html: '<b>2 · C</b> – the downhole safety valve' }),
    H('p', { html: '<b>3 · B</b> – the crossover valve (with the annulus master valve)' }))));

sheet.append(H('footer', {}, H('span', { text: 'Schematic overview for training. Verify details against current company procedures and standards.' }), H('span', { text: 'Numbers refer to the drawing above' })));
window.__ready = true;
