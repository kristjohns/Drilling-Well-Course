// Render the one-page cheat sheet (src/cheatsheet.html) to out/valve-cheat-sheet.pdf (+ .png preview)
import fs from 'node:fs';
import { chromium } from 'playwright';
import { startServer } from './server.mjs';

const { srv, url } = await startServer(0);
const browser = await chromium.launch();
const page = await (await browser.newContext({ viewport: { width: 1123, height: 794 }, deviceScaleFactor: 2 })).newPage();
page.on('pageerror', (e) => console.log('[pageerror]', e.message));
page.on('console', (m) => { if (m.type() === 'error') console.log('[console]', m.text()); });
await page.goto(`${url}/src/cheatsheet.html`);
await page.waitForFunction('window.__ready === true', null, { timeout: 60000 });
await page.evaluate(() => document.fonts.ready);
fs.mkdirSync('out', { recursive: true });
await page.pdf({ path: 'out/valve-cheat-sheet.pdf', width: '297mm', height: '210mm', printBackground: true, pageRanges: '1' });
await page.screenshot({ path: 'build/cheatsheet.png', clip: { x: 0, y: 0, width: 1123, height: 794 } });
console.log('wrote out/valve-cheat-sheet.pdf');
await browser.close(); srv.close();
