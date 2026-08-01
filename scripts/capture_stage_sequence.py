from pathlib import Path
from playwright.sync_api import sync_playwright

URLS = {
    "source": "https://www.ciaoenergy.com/?state-capture=1",
    "local": "http://45.8.22.65:44118/mirror/index.html?state-capture=1",
}
OUT = Path("docs/evidence/stage-sequence")
OUT.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    for name, url in URLS.items():
        page = browser.new_page(viewport={"width": 390, "height": 844})
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(12000)
        total = page.evaluate("document.documentElement.scrollHeight - innerHeight")
        print(name, total)
        for index, progress in enumerate([0, 0.08, 0.14, 0.18, 0.22, 0.27, 0.31, 0.36, 0.40, 0.45]):
            page.evaluate("p => scrollTo(0, p * (document.documentElement.scrollHeight - innerHeight))", progress)
            page.wait_for_timeout(1000)
            page.screenshot(path=str(OUT / f"{name}-{index:02d}-{progress:.2f}.png"), timeout=15000)
            text = page.evaluate("""() => [...document.querySelectorAll('.carousel_title-collection,.carousel_title-bis-wrapper,.profile_container,.benefits_container')].filter(e=>{const c=getComputedStyle(e);return c.visibility!=='hidden'&&+c.opacity>.05}).map(e=>({cls:e.className,text:(e.innerText||'').replace(/\\s+/g,' ').trim().slice(0,100)}))""")
            print(name, progress, text)
        page.close()
    browser.close()
