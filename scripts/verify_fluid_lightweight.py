from playwright.sync_api import sync_playwright

URL = "http://45.8.22.65:44119/mirror/index.html?fluid-light-qa=1"

def media_state(page):
    return page.evaluate("""() => [...document.querySelectorAll('.argument_video')].map((item, i) => {
      const video = item.querySelector('video');
      const style = getComputedStyle(item);
      return {i, src: video.currentSrc, time: video.currentTime, paused: video.paused,
        ready: video.readyState, opacity: style.opacity, visibility: style.visibility};
    })""")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
    page = browser.new_page(viewport={"width": 390, "height": 844})
    response = page.goto(URL, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(10000)
    target = page.evaluate("""() => {
      const section = document.querySelector('.section.is-argument');
      const y = scrollY + section.getBoundingClientRect().top + 120;
      scrollTo(0, y);
      return {y, ready: document.documentElement.dataset.fluidControllerReady};
    }""")
    page.wait_for_timeout(1600)
    before = media_state(page)
    page.wait_for_timeout(1400)
    after = media_state(page)
    page.evaluate("scrollTo(0, 0)")
    page.wait_for_timeout(1000)
    left = media_state(page)
    errors = page.evaluate("window.__fluidTestErrors || []")
    active_before = [x for x in before if not x['paused']]
    active_after = [x for x in after if not x['paused']]
    assert response and response.status == 200
    assert target['ready'] == '1'
    assert len(active_before) == 1 and len(active_after) == 1
    assert active_before[0]['i'] == active_after[0]['i'] == 0
    assert active_after[0]['time'] > active_before[0]['time'] + 0.8
    assert active_after[0]['ready'] >= 2
    assert '/mirror/media/argument/double-litchi.mp4' in active_after[0]['src']
    assert all(x['paused'] for x in left)
    print({'http': response.status, 'target': target, 'before': before, 'after': after, 'left': left, 'errors': errors})
    browser.close()
