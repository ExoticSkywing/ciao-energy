from playwright.sync_api import sync_playwright

URL = "http://45.8.22.65:44119/mirror/index.html?cross-layer-verify=2"
SELECTORS = [
    ".gamme_container",
    ".carousel_title-collection",
    ".profile_container",
    ".carousel_title-bis-wrapper",
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
    page = browser.new_page(viewport={"width": 390, "height": 844})
    response = page.goto(URL, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(10000)
    benefits = page.locator("section.is-benefits")
    print("HTTP", response.status if response else None, "COUNT", benefits.count())

    for index in [0, 1, 2, 3, 2, 1, 0]:
        benefits.nth(index).scroll_into_view_if_needed(timeout=60000)
        page.wait_for_timeout(1200)
        state = page.evaluate(
            """(selectors) => {
              const read = (selector) => {
                const el = document.querySelector(selector);
                if (!el) return null;
                const c = getComputedStyle(el);
                return {selector, visible: c.opacity !== '0' && c.visibility !== 'hidden', text: (el.innerText || '').replace(/\\s+/g,' ').trim().slice(0,70)};
              };
              const roots = selectors.map(read);
              const benefits = [...document.querySelectorAll('section.is-benefits')].map((s,i) => {
                const el=s.querySelector('.benefits_container'), c=getComputedStyle(el);
                return {selector:'#benefits-'+(i+1), visible:c.opacity!=='0'&&c.visibility!=='hidden', text:(el.innerText||'').replace(/\\s+/g,' ').trim().slice(0,70)};
              });
              return [...roots,...benefits];
            }""",
            SELECTORS,
        )
        visible = [item for item in state if item and item["visible"]]
        print("AT", index + 1, visible)
        assert len(visible) == 1, (index + 1, visible)
        assert visible[0]["selector"] == f"#benefits-{index + 1}", visible
    browser.close()
