// Step through a remark deck with real key presses in headless Chrome; print, per press,
// which .step-N elements and SVG data-step layers show. Run through tools/check-steps.sh.
//
//   node tools/check-steps.mjs <node_modules with puppeteer-core> <chrome> <deck url> <first hash> <presses>
import { createRequire } from 'module';
const [,, nm, chrome, url, first, presses] = process.argv;
const require = createRequire(nm + '/');
const puppeteer = require('puppeteer-core');
const browser = await puppeteer.launch({ executablePath: chrome, args: ['--no-sandbox'] });
const page = await browser.newPage();
await page.setViewport({ width: 1210, height: 681 });
await page.goto(url + '#' + first, { waitUntil: 'networkidle0' });
await new Promise(r => setTimeout(r, 1000));
const state = () => page.evaluate(() => {
  const s = document.querySelector('.remark-visible .remark-slide-content');
  const hid = e => { const c = getComputedStyle(e); return c.visibility === 'hidden' || c.display === 'none'; };
  const html = [...s.querySelectorAll('[class*="step-"]')].map(e => e.className.match(/step-\d+/)[0].slice(5) + (hid(e) ? '-' : '+'));
  const svg = [...s.querySelectorAll('object')].map(o => { const d = o.contentDocument; return d ? [...d.querySelectorAll('[data-step]')].map(g => g.getAttribute('data-step') + (g.getAttribute('display') === 'none' || g.style.display === 'none' || g.style.visibility === 'hidden' ? '-' : '+')).join(' ') : 'nodoc'; });
  return location.hash + ' ' + (s.querySelector('h1')?.textContent || '').slice(0, 40) + ' | html ' + html.join(' ') + ' | svg ' + svg.join(' ; ');
});
for (let i = 0; i <= +presses; i++) {
  console.log(await state());
  if (i < +presses) { await page.keyboard.press('ArrowRight'); await new Promise(r => setTimeout(r, 350)); }
}
await browser.close();
