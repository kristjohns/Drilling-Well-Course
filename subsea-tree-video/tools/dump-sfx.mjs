// Dump the sound-effect cue list (exported by the scene builders) to build/sfx.json
import fs from 'node:fs';
import { chromium } from 'playwright';
import { startServer } from './server.mjs';

const { srv, url } = await startServer(0);
const browser = await chromium.launch();
const page = await (await browser.newContext({ viewport: { width: 1920, height: 1080 } })).newPage();
page.on('pageerror', (e) => console.log('[pageerror]', e.message));
await page.goto(`${url}/src/index.html?render=1`);
await page.waitForFunction('window.__ready === true || window.__error', null, { timeout: 120000 });
const err = await page.evaluate('window.__error');
if (err) { console.error(err); process.exit(1); }
const cues = await page.evaluate('window.__sfx()');
fs.mkdirSync('build', { recursive: true });
fs.writeFileSync('build/sfx.json', JSON.stringify(cues, null, 1));
const by = {};
cues.forEach((c) => (by[c.name] = (by[c.name] || 0) + 1));
console.log(cues.length, 'cues', by);
await browser.close(); srv.close();
