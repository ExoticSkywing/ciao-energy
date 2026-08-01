from playwright.sync_api import sync_playwright

URL = "http://45.8.22.65:44119/mirror/index.html?benefit-motion-verify=1"
SEQUENCE = [(0.14, 1), (0.22, 2), (0.31, 3), (0.40, 4), (0.31, 3), (0.22, 2), (0.14, 1)]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
    page = browser.new_page(viewport={"width": 390, "height": 844})
    page.goto(URL, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(12000)
    total = page.evaluate("document.documentElement.scrollHeight-innerHeight")
    last_count = 0
    for progress, expected in SEQUENCE:
        page.evaluate("y=>scrollTo(0,y)", total * progress)
        page.wait_for_timeout(80)
        early = page.evaluate("""() => ({
          stage:document.documentElement.dataset.copyStage,
          count:Number(document.documentElement.dataset.benefitAnimationCount||0),
          active:Number(document.documentElement.dataset.activeBenefit||0),
          pieces:[...document.querySelectorAll(`#benefits-${document.documentElement.dataset.activeBenefit} .benefits_container [data-anim]`)].map(e=>{const c=getComputedStyle(e);return {opacity:Number(c.opacity),transform:c.transform}})
        })""")
        page.wait_for_timeout(850)
        settled = page.evaluate("""() => ({
          stage:document.documentElement.dataset.copyStage,
          count:Number(document.documentElement.dataset.benefitAnimationCount||0),
          active:Number(document.documentElement.dataset.activeBenefit||0),
          visible:[...document.querySelectorAll('.benefits_container')].map((e,i)=>{const c=getComputedStyle(e);return {i:i+1,visible:c.visibility!=='hidden'&&Number(c.opacity)>.05}}).filter(x=>x.visible),
          pieces:[...document.querySelectorAll(`#benefits-${document.documentElement.dataset.activeBenefit} .benefits_container [data-anim]`)].map(e=>{const c=getComputedStyle(e);return {opacity:Number(c.opacity),transform:c.transform}})
        })""")
        print(progress, "early", early, "settled", settled)
        assert early["active"] == expected and settled["active"] == expected
        assert early["count"] > last_count
        assert len(settled["visible"]) == 1 and settled["visible"][0]["i"] == expected
        if early["pieces"]:
            assert any(x["opacity"] < 0.95 or x["transform"] != "none" for x in early["pieces"])
            assert all(x["opacity"] > 0.95 for x in settled["pieces"])
        last_count = settled["count"]
    print("PASS", last_count)
    browser.close()
