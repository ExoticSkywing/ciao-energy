from playwright.sync_api import sync_playwright

URL = "http://45.8.22.65:44119/mirror/index.html?profile-carousel-qa=1"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 390, "height": 844}, has_touch=True, is_mobile=True)
    page.goto(URL, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_function("getComputedStyle(document.querySelector('.loader')).display === 'none'", timeout=60000)
    total = page.evaluate("document.documentElement.scrollHeight-innerHeight")
    page.evaluate("y => scrollTo(0,y)", total * 0.10)
    page.wait_for_timeout(1000)
    cdp = page.context.new_cdp_session(page)
    def state():
        return page.evaluate("""() => { const c=window.__ciaoCarousel; const title=[...document.querySelectorAll('.carousel_title-b')].find(e=>{const s=getComputedStyle(e);return s.visibility!=='hidden'&&Number(s.opacity)>.1}); const desc=[...document.querySelectorAll('.carousel_desc')].find(e=>{const s=getComputedStyle(e);return s.visibility!=='hidden'&&Number(s.opacity)>.1}); return {stage:document.documentElement.dataset.copyStage,index:c?.index,title:title?.innerText,desc:desc?.innerText.slice(0,80),primary:getComputedStyle(document.documentElement).getPropertyValue('--color-scheme-1--taste-primary').trim(),scrollY}; }""")
    def swipe(x1,y1,x2,y2):
        cdp.send("Input.dispatchTouchEvent", {"type":"touchStart","touchPoints":[{"x":x1,"y":y1}]})
        for step in range(1,9):
            cdp.send("Input.dispatchTouchEvent", {"type":"touchMove","touchPoints":[{"x":x1+(x2-x1)*step/8,"y":y1+(y2-y1)*step/8}]})
        cdp.send("Input.dispatchTouchEvent", {"type":"touchEnd","touchPoints":[]})
        page.wait_for_timeout(1800)
    before=state(); swipe(320,420,80,420); after=state(); print({"before":before,"after":after})
    assert before["stage"] == "profile" and after["stage"] == "profile"
    assert after["index"] != before["index"]
    assert after["title"] != before["title"] and after["desc"] != before["desc"]
    assert after["primary"] != before["primary"]
    assert abs(after["scrollY"]-before["scrollY"]) < 5
    browser.close()
