from playwright.sync_api import sync_playwright
from pathlib import Path

url = "http://45.8.22.65:44118/mirror/index.html?argument-fluid-diagnose=1"
out = Path("docs/evidence/argument-fluid")
out.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
    page = browser.new_page(viewport={"width": 390, "height": 844})
    response = page.goto(url, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(12000)
    state = page.evaluate("""() => {
      const section = document.querySelector('.section.is-argument');
      const y = section ? section.offsetTop + innerHeight * .12 : 0;
      scrollTo(0, y);
      return {y, top: section?.offsetTop || null};
    }""")
    page.wait_for_timeout(1800)
    before = page.evaluate("""() => {
      const videos=[...document.querySelectorAll('.argument_video video')];
      const wrappers=[...document.querySelectorAll('.argument_video')];
      return videos.map((v,i)=>({i,currentTime:v.currentTime,paused:v.paused,readyState:v.readyState,error:v.error?.code||null,src:v.currentSrc,opacity:getComputedStyle(wrappers[i]).opacity}));
    }""")
    page.screenshot(path=str(out / "frame-a.png"))
    page.wait_for_timeout(1600)
    after = page.evaluate("""() => [...document.querySelectorAll('.argument_video video')].map((v,i)=>({i,currentTime:v.currentTime,paused:v.paused,readyState:v.readyState,error:v.error?.code||null,src:v.currentSrc,opacity:getComputedStyle(document.querySelectorAll('.argument_video')[i]).opacity}))""")
    page.screenshot(path=str(out / "frame-b.png"))
    print("HTTP", response.status if response else None, "SCROLL", state)
    print("BEFORE", before)
    print("AFTER", after)
    browser.close()
