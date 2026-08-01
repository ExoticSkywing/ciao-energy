from playwright.sync_api import sync_playwright
URL='http://45.8.22.65:44118/mirror/index.html?benefits-reverse=1'
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,args=['--no-sandbox'])
 page=b.new_page(viewport={'width':390,'height':844})
 page.goto(URL,wait_until='domcontentloaded',timeout=60000);page.wait_for_timeout(10000)
 page.wait_for_selector('section.is-benefits',state='attached',timeout=60000)
 secs=page.locator('section.is-benefits')
 for idx in [0,1,2,3,2,1,0]:
  secs.nth(idx).scroll_into_view_if_needed();page.wait_for_timeout(1500)
  state=page.evaluate("""() => [...document.querySelectorAll('section.is-benefits')].map(s=>{const c=s.querySelector('.benefits_container'),cs=getComputedStyle(c);return {id:s.id,visible:cs.visibility==='visible'&&Number(cs.opacity)>.5,text:(c.innerText||'').replace(/\\s+/g,' ').slice(0,50)}})""")
  print(idx+1,state)
 b.close()
