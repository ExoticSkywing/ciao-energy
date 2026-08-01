from playwright.sync_api import sync_playwright

URL = "http://45.8.22.65:44118/mirror/index.html?benefits-repro=5"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
    page = browser.new_page(viewport={"width":390,"height":844}, user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Mobile/15E148 Safari/604.1")
    page.goto(URL, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(10000)
    sections = page.locator("section.is-benefits")
    count = sections.count()
    print("count", count)
    for idx in range(count):
        sections.nth(idx).scroll_into_view_if_needed()
        page.wait_for_timeout(1800)
        state = page.evaluate("""() => [...document.querySelectorAll('section.is-benefits')].map((s,i)=>{
          const c=s.querySelector('.benefits_container');
          const cs=getComputedStyle(c);
          return {i,id:s.id,text:(s.querySelector('.benefits_text')?.innerText||'').replace(/\\s+/g,' ').slice(0,220),opacity:cs.opacity,visibility:cs.visibility,display:cs.display,rect:c.getBoundingClientRect().toJSON(),active:document.querySelectorAll('.benefits_icon-wrapper')[i]?.classList.contains('is-active')}
        })""")
        print("AT",idx+1,state)
    browser.close()
