from playwright.sync_api import sync_playwright

URL = "http://45.8.22.65:44119/mirror/index.html?hero-swipe-verify=1"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
    page = browser.new_page(viewport={"width": 390, "height": 844}, has_touch=True, is_mobile=True)
    page.goto(URL, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(11000)
    cdp = page.context.new_cdp_session(page)

    def state():
        return page.evaluate("""() => ({index:window.__ciaoCarousel?.index,target:window.__ciaoCarousel?.target,scrollY})""")

    def swipe(x1, y1, x2, y2):
        cdp.send("Input.dispatchTouchEvent", {"type":"touchStart","touchPoints":[{"x":x1,"y":y1}]})
        for step in range(1, 9):
            x=x1+(x2-x1)*step/8; y=y1+(y2-y1)*step/8
            cdp.send("Input.dispatchTouchEvent", {"type":"touchMove","touchPoints":[{"x":x,"y":y}]})
            page.wait_for_timeout(35)
        cdp.send("Input.dispatchTouchEvent", {"type":"touchEnd","touchPoints":[]})
        page.wait_for_timeout(1500)

    before=state()
    swipe(320,420,80,420)
    after_horizontal=state()
    page.evaluate("scrollTo(0,0)")
    page.wait_for_timeout(300)
    swipe(195,700,195,250)
    after_vertical=state()
    print({"before":before,"after_horizontal":after_horizontal,"after_vertical":after_vertical})
    assert after_horizontal["index"] != before["index"], "horizontal swipe did not change carousel index"
    assert after_vertical["scrollY"] > 100, "vertical swipe did not scroll"
    browser.close()
