// 在 Docker 的 Puppeteer 映像檔內執行；用法見產品專章的圖片來源說明。
// 保留官方網頁的原始文字與樣式，僅裁切到指定章節。
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const puppeteer = require('/home/pptruser/node_modules/puppeteer');

const outputDir = process.argv[2] || '/work/img';
const records = [];

async function captureSection(page, url, id, endSelector, filename) {
  await page.goto(url, {waitUntil: 'networkidle2', timeout: 45000});
  const section = await page.$('#' + id);
  if (!section) throw new Error(`找不到章節 ${id}`);
  await section.evaluate(el => el.scrollIntoView());
  await page.evaluate(() => document.fonts.ready);
  const clip = await page.evaluate(({id, endSelector}) => {
    const start = document.getElementById(id);
    let end = start.nextElementSibling;
    while (end && !end.matches(endSelector)) end = end.nextElementSibling;
    const article = start.closest('article') || start.parentElement;
    const bounds = article.getBoundingClientRect();
    const first = start.getBoundingClientRect();
    // 選項頁把各套件放在獨立分頁容器；該分頁內可能只有一個 h2。
    const bottom = end ? end.getBoundingClientRect().y
      : start.parentElement.getBoundingClientRect().bottom;
    return {x: bounds.x, y: first.y + window.scrollY,
      width: bounds.width, height: bottom - first.y};
  }, {id, endSelector});
  await page.screenshot({path: path.join(outputDir, filename), clip});
  records.push({filename, source: url + '#' + id, kind: 'official-web-section-screenshot'});
}

async function downloadDiagram(page, url, filename) {
  await page.goto(url, {waitUntil: 'networkidle2', timeout: 45000});
  const info = await page.evaluate(() => {
    const heading = document.querySelector('#block-diagram');
    let next = heading.nextElementSibling;
    const items = [];
    while (next && !/^H[123]$/.test(next.tagName)) {
      for (const img of next.querySelectorAll('img')) {
        if (img.getBoundingClientRect().width > 0) items.push({src: img.src, alt: img.alt});
      }
      if (next.tagName === 'IMG') items.push({src: next.src, alt: next.alt});
      next = next.nextElementSibling;
    }
    return items;
  });
  if (info.length !== 1) throw new Error(`方塊圖數量應為 1，實際為 ${JSON.stringify(info)}`);
  const response = await page.goto(info[0].src, {waitUntil: 'load', timeout: 45000});
  if (!response.ok()) throw new Error(`下載失敗 ${response.status()}`);
  const bytes = await response.buffer();
  fs.writeFileSync(path.join(outputDir, filename), bytes);
  const record = {filename, source: info[0].src, manual: url + '#block-diagram',
    kind: 'official-original-diagram', alt: info[0].alt};
  // Panther 原圖為透明底白字；以瀏覽器深色背景截圖，讓淺色文件也能閱讀。
  // 另存原始位元組，保留未經渲染的官方證據。
  if (filename === 'husarion-panther-block-diagram.png') {
    const original = filename.replace('.png', '-original.png');
    fs.writeFileSync(path.join(outputDir, original), bytes);
    records.push({...record, filename: original});
    await page.setViewport({width: 2671, height: 1500, deviceScaleFactor: 1});
    await page.goto('about:blank');
    await page.setContent('<body style="margin:0;background:#111827">' +
      '<img style="display:block" src="data:image/png;base64,' + bytes.toString('base64') + '"></body>',
      {waitUntil: 'domcontentloaded', timeout: 15000});
    await page.$eval('img', img => img.decode());
    await (await page.$('img')).screenshot({path: path.join(outputDir, filename)});
    record.kind = 'official-diagram-browser-screenshot';
    record.background = '#111827';
  }
  records.push(record);
}

(async () => {
  const browser = await puppeteer.launch({headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']});
  try {
    const page = await browser.newPage();
    await page.setViewport({width: 1500, height: 1100, deviceScaleFactor: 1.5});
    await captureSection(page, 'https://husarion.com/manuals/panther/panther-options/',
      'user-computers', 'h2', 'husarion-panther-computers.png');
    await captureSection(page, 'https://husarion.com/manuals/rosbot-xl/rosbot-xl-options/',
      'basic-package', 'h2', 'husarion-rosbot-xl-computers.png');
    await downloadDiagram(page, 'https://husarion.com/manuals/panther/',
      'husarion-panther-block-diagram.png');
    await downloadDiagram(page, 'https://husarion.com/manuals/rosbot-xl/',
      'husarion-rosbot-xl-block-diagram.png');
    for (const record of records) {
      const bytes = fs.readFileSync(path.join(outputDir, record.filename));
      record.sha256 = crypto.createHash('sha256').update(bytes).digest('hex');
      record.bytes = bytes.length;
    }
    fs.writeFileSync(path.join(outputDir, 'husarion-source-captures.json'),
      JSON.stringify({captured_at: new Date().toISOString(),
        browser: await browser.version(), records}, null, 2) + '\n');
    console.log(JSON.stringify(records, null, 2));
  } finally {
    await browser.close();
  }
})().catch(error => {console.error(error); process.exitCode = 1;});
