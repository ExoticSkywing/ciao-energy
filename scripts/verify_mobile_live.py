from pathlib import Path
from playwright.sync_api import sync_playwright

URL = "http://45.8.22.65:44119/"
out = Path("docs/evidence/mobile-live")
out.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
    context = browser.new_context(
        viewport={"width": 390, "height": 844},
        device_scale_factor=3,
        is_mobile=True,
        has_touch=True,
        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Mobile/15E148 Safari/604.1",
    )
    page = context.new_page()
    page.set_default_timeout(15000)
    page.set_default_navigation_timeout(60000)
    errors = []
    page.on("console", lambda m: errors.append(f"console:{m.type}:{m.text}") if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append(f"pageerror:{e}"))
    response = page.goto(URL, wait_until="domcontentloaded", timeout=60000)
    page.screenshot(path=str(out / "intro-early.png"))
    page.wait_for_timeout(3500)
    page.screenshot(path=str(out / "intro-mid.png"))
    frame = page.frames[-1]
    state = frame.evaluate("""() => ({
      viewport:[innerWidth,innerHeight],
      loader:getComputedStyle(document.querySelector('.local-intro')).visibility,
      pct:document.querySelector('.local-intro-percent')?.textContent,
      input:document.documentElement.dataset.ciaoInputReady,
      overflow:getComputedStyle(document.documentElement).overflow,
      canvas:{opacity:getComputedStyle(document.querySelector('canvas')).opacity, touch:getComputedStyle(document.querySelector('canvas')).touchAction},
      ui:Object.fromEntries(['.navbar','.navbar_logo-link','.navbar_sound','.navbar_menu-wrapper','.hud','.gamme_container','.carousel_title-collection','.carousel_pagination','.scroll_discover','.gamme_gradient-wrapper'].map(s=>{const e=document.querySelector(s); const c=e&&getComputedStyle(e); return [s,e?{display:c.display,opacity:c.opacity,visibility:c.visibility,rect:e.getBoundingClientRect().toJSON()}:null]}))
    })""")
    print({"http": response.status if response else None, "state": state, "errors": errors})
    page.wait_for_timeout(6000)
    browser.close()
