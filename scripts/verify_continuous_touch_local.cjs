const { chromium } = require('playwright'); // eslint-disable-line @typescript-eslint/no-require-imports

const executablePath = '/root/.hermes/cache/ms-playwright/chromium-1234/chrome-linux64/chrome';
const url = 'http://127.0.0.1:44119/mirror/index.html?touch-continuous-drag-qa=1';

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath, args: ['--no-sandbox', '--disable-dev-shm-usage'] });
  const context = await browser.newContext({
    viewport: { width: 390, height: 844 },
    deviceScaleFactor: 0.5,
    isMobile: true,
    hasTouch: true,
  });
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', (error) => errors.push(String(error)));
  await page.addInitScript(() => Object.defineProperty(window, 'devicePixelRatio', { configurable: true, get: () => 0.5 }));
  const response = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 90000 });
  await page.waitForFunction(() => document.documentElement.dataset.ciaoInputReady === 'true', { timeout: 30000 });
  await page.waitForTimeout(250);
  await page.evaluate(() => { const loader = document.querySelector('.loader'); if (loader) { loader.style.pointerEvents='none'; loader.style.display='none'; } });
  const cdp = await context.newCDPSession(page);

  const state = () => page.evaluate(() => ({
    stage: document.documentElement.dataset.copyStage,
    index: window.__ciaoCarousel?.index,
    target: Number(window.__ciaoCarousel?.target?.toFixed(3)),
    position: Number(window.__ciaoCarousel?.position?.toFixed(3)),
    holding: window.__ciaoSwipe?.holding,
    active: window.__ciaoSwipe?.active,
    direction: window.__ciaoSwipe?.direction,
    scrollY: Math.round(scrollY),
  }));

  async function drag(x1, x2, y) {
    const frames = [];
    await cdp.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x: x1, y }] });
    frames.push(await state());
    for (let step = 1; step <= 14; step++) {
      const x = x1 + (x2 - x1) * step / 14;
      await cdp.send('Input.dispatchTouchEvent', { type: 'touchMove', touchPoints: [{ x, y }] });
      await page.waitForTimeout(80);
      frames.push(await state());
    }
    await cdp.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
    await page.waitForTimeout(800);
    frames.push(await state());
    return frames;
  }

  async function dragWithRetry(x1, x2, y) {
    for (let attempt = 0; attempt < 2; attempt++) {
      const frames = await drag(x1, x2, y);
      if (new Set(frames.slice(0, -1).map((frame) => frame.target)).size >= 5) return frames;
      await page.waitForTimeout(500);
    }
    return drag(x1, x2, y);
  }

  const hero = await dragWithRetry(340, 50, 430);
  const total = await page.evaluate(() => document.documentElement.scrollHeight - innerHeight);
  await page.evaluate((destination) => scrollTo(0, destination), total * 0.1);
  await page.waitForTimeout(1200);
  const profileBefore = await state();
  const profile = await drag(50, 340, 430);

  async function reverseWhileHeld() {
    const start = await state();
    await cdp.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x: 60, y: 430 }] });
    for (let step = 1; step <= 10; step++) {
      await cdp.send('Input.dispatchTouchEvent', { type: 'touchMove', touchPoints: [{ x: 60 + 25 * step, y: 430 }] });
      await page.waitForTimeout(60);
    }
    const turn = await state();
    for (let step = 1; step <= 10; step++) {
      await cdp.send('Input.dispatchTouchEvent', { type: 'touchMove', touchPoints: [{ x: 310 - 25 * step, y: 430 }] });
      await page.waitForTimeout(60);
    }
    const reversed = await state();
    await cdp.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
    await page.waitForTimeout(500);
    return { start, turn, reversed, end: await state() };
  }
  const reversal = await reverseWhileHeld();

  await page.evaluate((destination) => scrollTo(0, destination), total * 0.17);
  await page.waitForTimeout(900);
  const benefitBefore = await state();
  const benefitAttempt = await drag(340, 50, 430);

  await page.reload({ waitUntil: 'domcontentloaded', timeout: 90000 });
  await page.waitForFunction(() => document.documentElement.dataset.ciaoInputReady === 'true' && document.documentElement.dataset.copyStage === 'hero', { timeout: 30000 });
  await page.waitForTimeout(250);
  await page.evaluate((destination) => scrollTo(0, destination), total * 0.1);
  await page.waitForTimeout(900);
  await page.evaluate(() => {
    const swipe = window.__ciaoSwipe;
    swipe.holding = true;
    swipe.direction = 1;
    swipe.deltaX = 5;
  });
  const interruptionBefore = await state();
  await page.evaluate(() => window.dispatchEvent(new Event('blur')));
  await page.waitForTimeout(100);
  const interruptionAfter = await state();

  const summarize = (frames) => ({
    heldIndexes: [...new Set(frames.slice(0, -1).map((frame) => frame.index))],
    heldTargets: [...new Set(frames.slice(0, -1).map((frame) => frame.target))],
    start: frames[0],
    end: frames.at(-1),
  });
  const result = { http: response?.status(), hero: summarize(hero), profileBefore, profile: summarize(profile), reversal, benefitBefore, benefitAttempt: summarize(benefitAttempt), interruptionBefore, interruptionAfter, errors };
  console.log(JSON.stringify(result, null, 2));
  if (result.hero.heldTargets.length < 5) throw new Error('Touch Hero did not move continuously while held');
  if (profileBefore.stage !== 'profile') throw new Error(`Touch Profile stage not reached: ${profileBefore.stage}`);
  if (result.profile.heldIndexes.length < 2 || result.profile.heldTargets.length < 5) throw new Error('Touch Profile did not move continuously while held');
  if (Math.abs(result.profile.end.scrollY - profileBefore.scrollY) > 3) throw new Error('Touch horizontal Profile drag moved vertical scroll');
  if (!(reversal.turn.target < reversal.start.target && reversal.reversed.target > reversal.turn.target)) throw new Error('Touch direction reversal did not reverse the live carousel target');
  if (Math.abs(reversal.end.scrollY - reversal.start.scrollY) > 3) throw new Error('Touch reversal moved vertical scroll');
  if (!String(benefitBefore.stage).startsWith('benefit-')) throw new Error(`Benefit stage not reached: ${benefitBefore.stage}`);
  if (result.benefitAttempt.end.target !== benefitBefore.target) throw new Error('Carousel changed from a horizontal drag in Benefits');
  if (!interruptionBefore.holding || interruptionAfter.holding || interruptionAfter.direction !== 0) throw new Error('Blur did not recover the in-flight touch drag');
  if (errors.length) throw new Error(errors.join(' | '));
  await browser.close();
})().catch((error) => { console.error(error.stack || error); process.exitCode = 1; });
