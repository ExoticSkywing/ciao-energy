from playwright.sync_api import sync_playwright

URL = "http://45.8.22.65:44119/mirror/index.html?glow-colors=1"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 390, "height": 844}, has_touch=True, is_mobile=True)
    page.goto(URL, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(11000)
    states = []
    for step in range(6):
        page.evaluate("window.__ciaoCarousel.next()")
        page.wait_for_timeout(1900)
        states.append(page.evaluate("""() => { const r=getComputedStyle(document.documentElement),g=document.querySelector('.gamme_gradient'); return {index:window.__ciaoCarousel.index,primary:r.getPropertyValue('--color-scheme-1--taste-primary').trim(),secondary:r.getPropertyValue('--color-scheme-1--taste-secondary').trim(),transform:getComputedStyle(g).transform,display:getComputedStyle(g).display}; }"""))
    print(states)
    assert all(s["display"] == "block" for s in states)
    assert len(set((s["primary"], s["secondary"]) for s in states)) >= 5
    assert len(set(s["transform"] for s in states)) >= 5
    browser.close()
