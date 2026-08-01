from playwright.sync_api import sync_playwright

URL = "http://45.8.22.65:44119/mirror/index.html?copy-timing-verify=1"
CHECKPOINTS = [0, 0.08, 0.14, 0.18, 0.22, 0.27, 0.31, 0.36, 0.40, 0.45, 0.40, 0.31, 0.22, 0.14, 0.08, 0]
SELECTORS = [
    ".carousel_title-collection",
    ".profile_container",
    ".carousel_title-bis-wrapper",
    "#benefits-1 .benefits_container",
    "#benefits-2 .benefits_container",
    "#benefits-3 .benefits_container",
    "#benefits-4 .benefits_container",
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 390, "height": 844})
    response = page.goto(URL, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(12000)
    for progress in CHECKPOINTS:
        page.evaluate("p => scrollTo(0, p * (document.documentElement.scrollHeight - innerHeight))", progress)
        page.wait_for_timeout(700)
        state = page.evaluate("""selectors => ({
          stage: document.documentElement.dataset.copyStage,
          visible: selectors.filter(s=>{const e=document.querySelector(s);if(!e)return false;const c=getComputedStyle(e);return c.visibility!=='hidden'&&+c.opacity>.05}).map(s=>({selector:s,text:(document.querySelector(s).innerText||'').replace(/\s+/g,' ').trim().slice(0,70)}))
        })""", SELECTORS)
        print(progress, state)
        expected = "hero" if progress < .075 else "profile" if progress < .135 else "benefit-1" if progress < .205 else "benefit-2" if progress < .295 else "benefit-3" if progress < .385 else "benefit-4" if progress < .475 else "none"
        assert state["stage"] == expected, (progress, state, expected)
        expected_count = 2 if expected == "profile" else 1 if expected != "none" else 0
        assert len(state["visible"]) == expected_count, (progress, state)
    print("HTTP", response.status if response else None, "PASS")
    browser.close()
