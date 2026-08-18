import playwright from "/root/.hermes/profiles/frontend/workspace/apple-lotus-study/node_modules/playwright/index.js";

const { chromium } = playwright;
const BASE_URL = process.env.IPHONE_ACTOR_MVP_URL || "http:" + "//127.0.0.1:44121/?qa=iphone-actor-mvp";
const browser = await chromium.launch({ headless: true, args: ["--disable-dev-shm-usage"] });
const results = {};
for (const viewport of [
  { name: "desktop", width: 1440, height: 900 },
  { name: "mobile", width: 390, height: 844 },
]) {
  const page = await browser.newPage({ viewport: { width: viewport.width, height: viewport.height } });
  await page.goto(`${BASE_URL}${BASE_URL.includes("?") ? "&" : "?"}viewport=${viewport.name}`, { waitUntil: "domcontentloaded", timeout: 120000 });
  await page.waitForTimeout(1000);
  const frame = page.frames().find((candidate) => candidate.url().includes("/mirror/"));
  if (!frame) throw new Error("mirror frame unavailable");
  await frame.waitForFunction(() => document.documentElement.dataset.iphoneActorMvp === "ready", undefined, { timeout: 120000 });
  await frame.evaluate(() => window.__ciaoLoader?.skip?.());
  await page.waitForTimeout(900);
  const initial = await frame.evaluate(() => window.__ciaoIPhoneActorMvp.diagnostics());
  await frame.evaluate(() => window.__ciaoIPhoneActorMvp.carousel.goTo(1));
  await page.waitForTimeout(2600);
  const moved = await frame.evaluate(() => window.__ciaoIPhoneActorMvp.diagnostics());
  await frame.evaluate(() => window.__ciaoIPhoneActorMvp.carousel.goTo(0));
  await page.waitForTimeout(2600);
  const returned = await frame.evaluate(() => window.__ciaoIPhoneActorMvp.diagnostics());
  const pass = initial.iphoneActorCount === 1 && initial.canActorCount === initial.actorCount - 1 && initial.sprite.opacity === "1" &&
    Math.abs(initial.position[0]) < 0.2 && Math.abs(moved.position[0]) > 1 && Math.abs(returned.position[0]) < 0.2;
  results[viewport.name] = { initial, moved, returned, pass };
  await page.close();
}
await browser.close();
const pass = Object.values(results).every((result) => result.pass);
console.log(JSON.stringify({ pass, ...results }, null, 2));
if (!pass) process.exitCode = 1;
