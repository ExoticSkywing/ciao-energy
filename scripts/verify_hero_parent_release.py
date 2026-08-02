from playwright.sync_api import sync_playwright

URL = "http://45.8.22.65:44119/mirror/index.html?parent-release-qa=1"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 390, "height": 844})
    page.goto(URL, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(1000)
    last = None
    states = []
    for _ in range(600):
        state = page.evaluate("""() => {
          const get = s => getComputedStyle(document.querySelector(s));
          return {
            percent: document.querySelector('.loader_percent')?.textContent,
            phase: document.documentElement.dataset.ciaoIntroMotion,
            released: document.documentElement.dataset.ciaoHeroIntroReleased,
            loaderOpacity: get('.loader').opacity,
            loaderDisplay: get('.loader').display,
            heroOpacity: get('.gamme_container').opacity,
            heroVisibility: get('.gamme_container').visibility,
            glowVisibility: get('.gamme_gradient-wrapper').visibility,
            benefitsVisibility: get('.benefits_nav').visibility,
          };
        }""")
        key = tuple(state.values())
        if key != last:
            states.append(state)
            print(state)
            last = key
        if state["loaderDisplay"] == "none":
            break
        page.wait_for_timeout(80)
    assert any(s["released"] == "true" and s["heroVisibility"] == "visible" and s["glowVisibility"] == "visible" for s in states)
    assert all(s["benefitsVisibility"] == "hidden" for s in states if s["phase"] != "complete")
    assert states[-1]["loaderDisplay"] == "none"
    browser.close()
