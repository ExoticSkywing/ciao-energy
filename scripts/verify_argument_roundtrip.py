from playwright.sync_api import sync_playwright

URL = "http://45.8.22.65:44119/mirror/index.html?argument-roundtrip=1"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width":390,"height":844})
    page.goto(URL, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(12000)
    metrics = page.evaluate("""() => ({full:document.querySelector('.section.is-full-gamme').offsetTop})""")
    ys = [metrics["full"]-844-120, metrics["full"]-844+120, metrics["full"]-844-120]
    states=[]
    for y in ys:
        page.evaluate("y=>scrollTo(0,y)", y)
        page.wait_for_timeout(900)
        states.append(page.evaluate("""() => {const a=document.querySelector('.argument_container'),c=getComputedStyle(a);return {stage:document.documentElement.dataset.copyStage,visibility:c.visibility,opacity:c.opacity}}"""))
    print(states)
    assert [s["visibility"] for s in states] == ["visible","hidden","visible"]
    browser.close()
