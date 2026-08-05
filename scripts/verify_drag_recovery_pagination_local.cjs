const { chromium } = require('playwright'); // eslint-disable-line @typescript-eslint/no-require-imports

const executablePath = '/root/.hermes/cache/ms-playwright/chromium-1234/chrome-linux64/chrome';
const url = 'http://127.0.0.1:44119/mirror/index.html?drag-recovery-pagination-qa=1';

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath, args: ['--no-sandbox', '--disable-dev-shm-usage'] });
  const page = await browser.newPage({ viewport: { width: 1024, height: 640 }, deviceScaleFactor: 0.5 });
  const errors = [];
  page.on('pageerror', (error) => errors.push(`page: ${error}`));
  page.on('response', (response) => { if (response.status() >= 500) errors.push(`${response.status()}: ${response.url()}`); });
  await page.addInitScript(() => Object.defineProperty(window, 'devicePixelRatio', { configurable: true, get: () => 0.5 }));
  const response = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 90000 });
  await page.waitForTimeout(11000);
  await page.evaluate(() => {
    document.documentElement.dataset.copyStage = 'hero';
    const loader = document.querySelector('.loader');
    if (loader) { loader.style.pointerEvents = 'none'; loader.style.display = 'none'; }
  });
  const state = () => page.evaluate(() => ({ stage: document.documentElement.dataset.copyStage, index: window.__ciaoCarousel?.index, target: Number(window.__ciaoCarousel?.target?.toFixed(3)), holding: window.__ciaoSwipe?.holding, direction: window.__ciaoSwipe?.direction, lenisStopped: Boolean(window.__ciaoLenis?._isStopped), scrollY: Math.round(scrollY) }));
  const canvasBox = await page.locator('canvas').boundingBox();
  if (!canvasBox) throw new Error('Canvas not found');
  await page.mouse.move(canvasBox.x + canvasBox.width / 2, canvasBox.y + canvasBox.height / 2);
  await page.mouse.down();
  await page.mouse.move(canvasBox.x + canvasBox.width / 2 - 180, canvasBox.y + canvasBox.height / 2, { steps: 8 });
  await page.waitForTimeout(100);
  const interruptedBefore = await state();
  await page.evaluate(() => window.dispatchEvent(new Event('blur')));
  await page.waitForTimeout(120);
  const interruptedAfter = await state();
  await page.mouse.up();
  const paginationBox = await page.locator('.carousel_pagination').boundingBox();
  if (!paginationBox) throw new Error('Carousel pagination not found');
  const paginationBefore = await state();
  await page.mouse.move(paginationBox.x + paginationBox.width * 0.9, paginationBox.y + paginationBox.height / 2);
  await page.mouse.down();
  await page.mouse.move(paginationBox.x + paginationBox.width * 0.1, paginationBox.y + paginationBox.height / 2, { steps: 8 });
  await page.waitForTimeout(100);
  const paginationHeld = await state();
  await page.mouse.up();
  await page.waitForTimeout(900);
  const paginationAfter = await state();
  const result = { http: response?.status(), interruptedBefore, interruptedAfter, paginationBefore, paginationHeld, paginationAfter, paginationOwnerIsolated: paginationHeld.holding === false && paginationAfter.holding === false, errors };
  console.log(JSON.stringify(result, null, 2));
  if (result.http !== 200) throw new Error(`HTTP ${result.http}`);
  if (!interruptedBefore.holding || !interruptedBefore.lenisStopped) throw new Error('Could not reproduce active stopped Lenis drag');
  if (interruptedAfter.holding || interruptedAfter.direction !== 0 || interruptedAfter.lenisStopped) throw new Error('Interrupted drag did not restore swipe and Lenis');
  if (!result.paginationOwnerIsolated) throw new Error('Pagination was captured by global drag owner');
  if (Math.abs(paginationAfter.target - paginationBefore.target) < 1) throw new Error('Pagination scrub did not move carousel');
  if (errors.length) throw new Error(errors.join(' | '));
  await browser.close();
})().catch((error) => { console.error(error.stack || error); process.exitCode = 1; });
