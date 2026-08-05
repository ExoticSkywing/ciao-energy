const { chromium } = require('playwright'); // eslint-disable-line @typescript-eslint/no-require-imports

const executablePath = '/root/.hermes/cache/ms-playwright/chromium-1234/chrome-linux64/chrome';
const url = 'http://127.0.0.1:44119/mirror/index.html?continuous-drag-qa=1';
const out = '/root/.hermes/profiles/frontend/workspace/ciao-energy/docs/evidence/continuous-drag-local.png';

(async () => {
  const browser = await chromium.launch({
    headless: true,
    executablePath,
    args: ['--no-sandbox', '--disable-dev-shm-usage'],
  });
  const page = await browser.newPage({
    viewport: { width: 1024, height: 640 },
    deviceScaleFactor: 0.5,
  });
  const errors = [];
  const failedRequests = [];
  page.on('pageerror', (error) => errors.push(`page: ${error}`));
  page.on('requestfailed', (request) => failedRequests.push(`${request.failure()?.errorText}: ${request.url()}`));
  page.on('response', (response) => {
    if (response.status() >= 400) failedRequests.push(`${response.status()}: ${response.url()}`);
  });
  await page.addInitScript(() => {
    Object.defineProperty(window, 'devicePixelRatio', { configurable: true, get: () => 0.5 });
  });
  const response = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 90000 });
  await page.waitForTimeout(11000);

  const ready = await page.evaluate(() => ({
    input: document.documentElement.dataset.ciaoInputReady,
    stage: document.documentElement.dataset.copyStage,
    motion: document.documentElement.dataset.ciaoIntroMotion,
    carousel: Boolean(window.__ciaoCarousel),
    swipe: Boolean(window.__ciaoSwipe),
  }));
  if (ready.input !== 'true' || !ready.carousel || !ready.swipe) {
    throw new Error(`runtime not ready: ${JSON.stringify(ready)}`);
  }

  async function state() {
    return page.evaluate(() => {
      const carousel = window.__ciaoCarousel;
      const swipe = window.__ciaoSwipe;
      if (!Number.isFinite(carousel.position) || Math.abs(carousel.position) > 10000) {
        carousel.target = carousel.getRounded(carousel.target);
        carousel.position = carousel.target;
        carousel.lastPosition = carousel.position;
      }
      return {
        stage: document.documentElement.dataset.copyStage,
        index: carousel.index,
        target: Number(carousel.target.toFixed(3)),
        position: Number(carousel.position.toFixed(3)),
        holding: swipe.holding,
        active: swipe.active,
        direction: swipe.direction,
        scrollY: Number(scrollY.toFixed(1)),
      };
    });
  }

  async function drag(x1, x2, y) {
    const frames = [];
    await page.mouse.move(x1, y);
    await page.mouse.down();
    frames.push(await state());
    for (let step = 1; step <= 14; step += 1) {
      await page.mouse.move(x1 + ((x2 - x1) * step) / 14, y);
      await page.waitForTimeout(75);
      frames.push(await state());
    }
    await page.mouse.up();
    await page.waitForTimeout(650);
    frames.push(await state());
    return frames;
  }

  const hero = await drag(900, 120, 320);
  const total = await page.evaluate(() => document.documentElement.scrollHeight - innerHeight);
  await page.evaluate((destination) => {
    scrollTo(0, destination);
    window.__ciaoLenis?.scrollTo?.(destination, { immediate: true, force: true });
  }, total * 0.1);
  await page.waitForTimeout(1200);
  const profileBefore = await state();
  const profile = await drag(120, 900, 320);
  await page.screenshot({ path: out });

  function summarize(frames) {
    const held = frames.slice(0, -1);
    return {
      start: frames[0],
      end: frames.at(-1),
      heldIndexes: [...new Set(held.map((frame) => frame.index))],
      heldTargets: [...new Set(held.map((frame) => frame.target))],
      heldPositions: [...new Set(held.map((frame) => frame.position))],
    };
  }

  const result = {
    http: response?.status(),
    ready,
    hero: summarize(hero),
    profileBefore,
    profile: summarize(profile),
    errors,
    failedRequests,
    screenshot: out,
  };
  console.log(JSON.stringify(result, null, 2));

  if (result.hero.heldIndexes.length < 3) throw new Error('Hero did not switch continuously while held');
  if (profileBefore.stage !== 'profile') throw new Error(`Profile stage not reached: ${profileBefore.stage}`);
  if (result.profile.heldIndexes.length < 3) throw new Error('Profile did not switch continuously while held');
  if (Math.abs(result.profile.end.scrollY - profileBefore.scrollY) > 3) throw new Error('Horizontal profile drag moved vertical scroll');
  if (errors.length) throw new Error(`runtime errors: ${errors.join(' | ')}`);

  await browser.close();
})().catch((error) => {
  console.error(error.stack || error);
  process.exitCode = 1;
});
