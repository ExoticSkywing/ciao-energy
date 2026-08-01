from playwright.sync_api import sync_playwright
URL='http://45.8.22.65:44118/mirror/index.html?benefits-diagnostic=2'
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,args=['--no-sandbox'])
 page=b.new_page(viewport={'width':390,'height':844})
 page.goto(URL,wait_until='domcontentloaded',timeout=60000); page.wait_for_timeout(10000)
 print('moduleErrors',page.evaluate("document.documentElement.dataset.ciaoSceneError||null"));print(page.evaluate("""() => [...document.querySelectorAll('section')].map((s,i)=>({i,id:s.id,cls:s.className,offsetTop:s.offsetTop,offsetHeight:s.offsetHeight,rect:s.getBoundingClientRect().toJSON()}))"""))
 for y in [0,844,1688,2532,3376,4220,5064,5908,6752]:
  page.evaluate('(y)=>window.scrollTo(0,y)',y);page.wait_for_timeout(500)
  print('Y',y,'scroll',page.evaluate('scrollY'),'active',page.evaluate("""() => [...document.querySelectorAll('section.is-benefits')].map(s=>[s.id,s.dataset.benefitActive,s.getBoundingClientRect().top,s.getBoundingClientRect().bottom,getComputedStyle(s.querySelector('.benefits_container')).opacity])"""))
 b.close()
