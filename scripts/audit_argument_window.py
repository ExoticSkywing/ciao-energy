from playwright.sync_api import sync_playwright

URLS = {
    "source": "https://www.ciaoenergy.com/",
    "local": "http://45.8.22.65:44119/mirror/index.html?argument-window-audit=1",
}

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    for name, url in URLS.items():
        page = browser.new_page(viewport={"width": 390, "height": 844})
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(12000)
        metrics = page.evaluate("""() => {const a=document.querySelector('.section.is-argument'),f=document.querySelector('.section.is-full-gamme');return {argTop:a.offsetTop,argHeight:a.offsetHeight,fullTop:f.offsetTop,fullHeight:f.offsetHeight,max:document.documentElement.scrollHeight-innerHeight}}""")
        print(name, metrics)
        points = [metrics["argTop"]-1, metrics["argTop"]+1, metrics["argTop"]+metrics["argHeight"]*.5, metrics["fullTop"]-1, metrics["fullTop"]+1, metrics["fullTop"]+metrics["fullHeight"]*.5]
        for y in points:
            page.evaluate("y=>scrollTo(0,y)", y)
            page.wait_for_timeout(600)
            print(name, round(y), page.evaluate("""() => {const a=document.querySelector('.argument_container'),c=getComputedStyle(a);return {stage:document.documentElement.dataset.copyStage||'',op:c.opacity,vis:c.visibility,y:scrollY}}"""))
        page.close()
    browser.close()
