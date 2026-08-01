from playwright.sync_api import sync_playwright
URL='http://45.8.22.65:44119/mirror/index.html?profile-title-verify=1'
with sync_playwright() as p:
    b=p.chromium.launch(headless=True,args=['--no-sandbox'])
    page=b.new_page(viewport={'width':390,'height':844})
    r=page.goto(URL,wait_until='domcontentloaded',timeout=60000)
    page.wait_for_timeout(12000)
    total=page.evaluate('document.documentElement.scrollHeight-innerHeight')
    page.evaluate('(y)=>scrollTo(0,y)',total*.08)
    page.wait_for_timeout(2500)
    state=page.evaluate("""() => ({
      stage:document.documentElement.dataset.copyStage,
      carouselIndex:(document.documentElement.__ciaoCarousel||window.__ciaoCarousel)?.index,
      fallback:(()=>{const e=document.querySelector('.local-profile-title'),c=getComputedStyle(e),b=e.getBoundingClientRect();return {text:e.textContent.trim(),visible:c.visibility!=='hidden'&&Number(c.opacity)>.05,color:c.color,font:c.fontSize,rect:{x:b.x,y:b.y,w:b.width,h:b.height}}})(),
      titleSlides:[...document.querySelectorAll('.carousel_title-bis-wrapper .carousel_title-b')].map((e,i)=>{const c=getComputedStyle(e),b=e.getBoundingClientRect();return {i,text:e.textContent.replace(/\s+/g,' ').trim(),visible:c.visibility!=='hidden'&&Number(c.opacity)>.05,opacity:c.opacity,color:c.color,font:c.fontSize,display:c.display,rect:{x:b.x,y:b.y,w:b.width,h:b.height}}}),
      descs:[...document.querySelectorAll('.carousel_desc')].map((e,i)=>{const c=getComputedStyle(e);return {i,text:e.textContent.replace(/\\s+/g,' ').trim().slice(0,100),visible:c.visibility!=='hidden'&&Number(c.opacity)>.05}}),
      icons:[...document.querySelectorAll('.benefits_icon-wrapper')].map((e,i)=>({i,active:e.classList.contains('is-active')}))
    })""")
    page.screenshot(path='docs/evidence/profile-title-fixed.png')
    print('HTTP',r.status if r else None,state)
    assert state['stage']=='profile'
    assert state['fallback']['visible'] and state['fallback']['text'].upper()=='DOUBLELITCHI'
    assert 115 <= state['fallback']['rect']['w'] <= 145
    assert state['fallback']['rect']['h']>45 and state['fallback']['rect']['h']<70
    assert 30 <= float(state['fallback']['font'].replace('px','')) <= 38
    assert not any(x['active'] for x in state['icons'])
    print('PASS')
    b.close()
