from playwright.sync_api import sync_playwright

URL = "http://45.8.22.65:44118/mirror/index.html?hero-swipe-repro=4"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
    page = browser.new_page(viewport={"width": 390, "height": 844}, has_touch=True, is_mobile=True)
    page.goto(URL, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(11000)

    state_js = """() => ({
      index: window.__ciaoCarousel?.index,
      target: window.__ciaoCarousel?.target,
      position: window.__ciaoCarousel?.position,
      inputReady: document.documentElement.dataset.ciaoInputReady,
      scrollY,
      canvas: (() => { const e=document.querySelector('canvas'),c=getComputedStyle(e); return {rect:e.getBoundingClientRect().toJSON(),pointer:c.pointerEvents,touch:c.touchAction,z:c.zIndex}; })(),
      hit: (() => { const e=document.elementFromPoint(innerWidth/2,innerHeight/2); return {tag:e?.tagName,cls:e?.className}; })(),
      gamme: (()=>{const e=document.querySelector('.gamme_container'),c=getComputedStyle(e);return {opacity:c.opacity,visibility:c.visibility,pointer:c.pointerEvents,z:c.zIndex};})()
    })"""
    before = page.evaluate(state_js)
    page.touchscreen.tap(195, 420)
    cdp = page.context.new_cdp_session(page)
    cdp.send("Input.dispatchTouchEvent", {"type": "touchStart", "touchPoints": [{"x": 320, "y": 420}]})
    for x in [290, 260, 230, 200, 170, 140, 110, 80]:
        cdp.send("Input.dispatchTouchEvent", {"type": "touchMove", "touchPoints": [{"x": x, "y": 420}]})
        page.wait_for_timeout(40)
    cdp.send("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": []})
    page.wait_for_timeout(1800)
    after = page.evaluate(state_js)
    print({"before": before, "after": after})
    browser.close()
