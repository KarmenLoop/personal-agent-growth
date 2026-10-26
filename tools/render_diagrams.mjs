// Copyright (C) 2026 KARMENLOOP Official Team. SPDX-License-Identifier: AGPL-3.0-only
// Development-only rendering. Runtime Python utilities need no Node packages.
import fs from 'node:fs/promises';
import path from 'node:path';
import http from 'node:http';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
import crypto from 'node:crypto';

const args = process.argv.slice(2);
const option = (key) => args[args.indexOf(key) + 1];
if (!args.includes('--mermaid-dir') || !args.includes('--playwright')) {
  throw new Error('Usage: node tools/render_diagrams.mjs --mermaid-dir /path/to/mermaid --playwright /path/to/playwright [--browser /path/to/chromium]');
}
const mermaid = path.resolve(option('--mermaid-dir'));
const require = createRequire(import.meta.url);
const { chromium } = require(path.resolve(option('--playwright')));
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const folder = path.join(root, 'docs/diagrams');
const hash = (data) => crypto.createHash('sha256').update(data).digest('hex');
const server = http.createServer(async (req, res) => {
  try {
    if (req.url === '/') {
      res.setHeader('Content-Type', 'text/html; charset=utf-8');
      res.end('<!doctype html><html><head><meta charset="utf-8"></head><body style="margin:24px;background:white"></body></html>');
      return;
    }
    const target = path.resolve(mermaid, '.' + decodeURIComponent(req.url));
    if (!target.startsWith(mermaid + path.sep)) throw new Error('Outside dependency root');
    res.setHeader('Content-Type', 'text/javascript');
    res.end(await fs.readFile(target));
  } catch { res.statusCode = 404; res.end('Not found'); }
});
await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
let browser;
try {
  browser = await chromium.launch({ headless: true, ...(args.includes('--browser') ? { executablePath: option('--browser') } : {}) });
  const page = await browser.newPage({ viewport: { width: 1600, height: 1000 } });
  await page.goto(`http://127.0.0.1:${server.address().port}/`);
  await page.evaluate(async () => {
    window.mermaid = (await import('/dist/mermaid.esm.min.mjs')).default;
    window.mermaid.initialize({ startOnLoad: false, securityLevel: 'strict', theme: 'base',
      themeVariables: { fontFamily: 'Arial, "PingFang SC", "Microsoft YaHei", sans-serif', fontSize: '17px', primaryColor: '#e4eefb', primaryTextColor: '#14273d', lineColor: '#526d86', tertiaryColor: '#eef5ef',
        cScale0: '#d7e6f7', cScale1: '#cddfdb', cScale2: '#e7def0', cScale3: '#f2e1c9', cScale4: '#dae7ed', cScale5: '#f1d9d9', cScale6: '#e1e8c9', cScale7: '#d7dbed',
        cScaleLabel0: '#14273d', cScaleLabel1: '#14273d', cScaleLabel2: '#14273d', cScaleLabel3: '#14273d', cScaleLabel4: '#14273d', cScaleLabel5: '#14273d', cScaleLabel6: '#14273d', cScaleLabel7: '#14273d' },
      mindmap: { padding: 22, useMaxWidth: false }, flowchart: { htmlLabels: false, useMaxWidth: false, curve: 'basis' }, sequence: { useMaxWidth: false } });
  });
  const records = [];
  for (const name of (await fs.readdir(folder)).filter(n => n.endsWith('.mmd')).sort()) {
    const source = await fs.readFile(path.join(folder, name), 'utf8');
    const result = await page.evaluate(async ({ source }) => {
      document.body.innerHTML = '';
      const { svg } = await window.mermaid.render('diagram', source);
      document.body.innerHTML = svg;
      const element = document.querySelector('svg');
      const box = element.viewBox.baseVal;
      return { svg, width: box.width, height: box.height, labels: element.querySelectorAll('text, .nodeLabel').length };
    }, { source });
    if (!(result.width > 0 && result.height > 0 && result.labels > 0)) throw new Error(`Empty diagram: ${name}`);
    const output = name.replace(/\.mmd$/, '.svg');
    await fs.writeFile(path.join(folder, output), result.svg + '\n');
    records.push({ source: name, source_sha256: hash(source), output, output_sha256: hash(result.svg + '\n'), width: result.width, height: result.height, labels: result.labels });
    process.stdout.write(JSON.stringify({ source: name, width: result.width, height: result.height, labels: result.labels }) + '\n');
  }
  const version = JSON.parse(await fs.readFile(path.join(mermaid, 'package.json'), 'utf8')).version;
  await fs.writeFile(path.join(folder, 'render-manifest.json'), JSON.stringify({ mermaid_version: version, renderer: 'Chromium via Playwright', scope: 'Actual SVG rendering, not Agent behavior acceptance', diagrams: records }, null, 2) + '\n');
} finally {
  if (browser) await browser.close();
  await new Promise(resolve => server.close(resolve));
}
