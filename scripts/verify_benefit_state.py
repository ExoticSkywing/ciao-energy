from playwright.sync_api import sync_playwright

URL = "http://45.8.22.65:44118/mirror/index.html?benefit-state-verify=1"
CHECKS = [(0.14, 0), (0.22, 1), (0.31, 2), (0.40, 3), (0.31, 2), (0.22, 1), (0.14, 0)]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 390, "height": 844})
    response = page.goto(URL, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(12000)
    for progress, expected in CHECKS:
        page.evaluate("p => scrollTo(0, p * (document.documentElement.scrollHeight - innerHeight))", progress)
        page.wait_for_timeout(700)
        state = page.evaluate("""() => ({
          stage:document.documentElement.dataset.copyStage,
          activeBenefit:document.documentElement.dataset.activeBenefit,
          sections:[...document.querySelectorAll('section.is-benefits')].map((s,i)=>({
            i,
            active:s.dataset.benefitActive,
            line:getComputedStyle(s).getPropertyValue('--benefits-line').trim(),
            text:(s.querySelector('.benefits_container')?.innerText||'').replace(/\s+/g,' ').trim(),
            visible:(()=>{const e=s.querySelector('.benefits_container');const c=e&&getComputedStyle(e);return !!e&&c.visibility!=='hidden'&&+c.opacity>.05})()
          })),
          icons:[...document.querySelectorAll('.benefits_icon-wrapper')].map((e,i)=>({i,active:e.classList.contains('is-active'),aria:e.getAttribute('aria-current'),border:getComputedStyle(e).borderColor,shadow:getComputedStyle(e).boxShadow}))
        })""")
        print(progress, state)
        assert state["stage"] == f"benefit-{expected+1}"
        assert state["activeBenefit"] == str(expected + 1)
        assert [s["i"] for s in state["sections"] if s["visible"]] == [expected]
        assert state["sections"][expected]["line"] == "1"
        assert len(state["sections"][expected]["text"]) > 80
        assert [i["i"] for i in state["icons"] if i["active"]] == [expected]
        assert state["icons"][expected]["aria"] == "step"
        assert state["icons"][expected]["shadow"] != "none"
    print("HTTP", response.status if response else None, "PASS")
    browser.close()
