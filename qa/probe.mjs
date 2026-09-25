// Upmore visual/interaction probe harness.
// Usage: node qa/probe.mjs <url> <outdir> [viewport WxH]
// Handles the sandbox egress proxy via an in-process CONNECT relay
// (Chromium ignores *_PROXY vars; direct CONNECTs die at the gateway).
import { chromium } from 'playwright-core';
import net from 'node:net';
import fs from 'node:fs';
import os from 'node:os';

const url = process.argv[2];
const outdir = process.argv[3] || '/tmp/probe';
const [vw, vh] = (process.argv[4] || '390x844').split('x').map(Number);
fs.mkdirSync(outdir, { recursive: true });

const proxyServer = process.env.HTTPS_PROXY || process.env.https_proxy;
const launchOpts = {
  executablePath: os.homedir() + '/.cache/ms-playwright/chromium-1243/chrome-linux/chrome',
  args: ['--font-render-hinting=none'],
};
let relay = null;
if (proxyServer) {
  const u = new URL(proxyServer);
  relay = net.createServer((client) => {
    let buf = Buffer.alloc(0), up = null, sent = false;
    client.on('data', (c) => {
      if (!sent) {
        buf = Buffer.concat([buf, c]);
        if (buf.includes('\r\n\r\n')) {
          sent = true;
          up = net.connect(Number(u.port) || 3128, u.hostname, () => up.write(buf));
          up.on('data', (d) => client.write(d));
          up.on('error', () => client.destroy());
          up.on('close', () => client.end());
        }
      } else if (up) up.write(c);
    });
    client.on('error', () => { if (up) up.destroy(); });
  });
  await new Promise((r) => relay.listen(0, '127.0.0.1', r));
  launchOpts.proxy = { server: 'http://127.0.0.1:' + relay.address().port };
  launchOpts.ignoreHTTPSErrors = true;
}

const browser = await chromium.launch(launchOpts);
const ctx = await browser.newContext({ ignoreHTTPSErrors: true, viewport: { width: vw, height: vh } });
const page = await ctx.newPage();
const errors = [];
page.on('console', (m) => { if (m.type() === 'error') errors.push('[console] ' + m.text()); });
page.on('pageerror', (e) => errors.push('[pageerror] ' + e.message));
page.on('requestfailed', (r) => errors.push('[reqfail] ' + r.url()));

await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 45000 });
await page.waitForTimeout(1500);
await page.screenshot({ path: outdir + '/shot-1.png' });
console.log(JSON.stringify({ url, errors: errors.slice(0, 20), errorCount: errors.length }));
await browser.close();
if (relay) relay.close();
