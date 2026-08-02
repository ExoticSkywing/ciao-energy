from playwright.sync_api import sync_playwright

URL = "http://45.8.22.65:44119/mirror/index.html?argument-gate-qa=1"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 390, "height": 844})
    page.goto(URL, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(12000)
    total = page.evaluate("document.documentElement.scrollHeight-innerHeight")
    states = []
    for progress in (0, 0.14, 0.31, 0.54, 0.62):
        page.evaluate("([y]) => scrollTo(0,y)", [total * progress])
        page.wait_for_timeout(900)
        states.append(page.evaluate("""() => {const a=document.querySelector('.argument_container'),c=getComputedStyle(a);return {stage:document.documentElement.dataset.copyStage,opacity:c.opacity,visibility:c.visibility}}"""))
    print(states)
    assert all(s["visibility"] == "hidden" for s in states[:3])
    assert states[3]["visibility"] == "visible"
    assert states[4]["visibility"] == "hidden"
    browser.close()
