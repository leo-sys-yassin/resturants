from playwright.sync_api import sync_playwright
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for width,height in [(390,844),(390,667),(768,1024),(1440,900),(1920,1080)]:
  pg=b.new_page(viewport={'width':width,'height':height},locale='ar-SY');errors=[];pg.on('pageerror',lambda e:errors.append(str(e)));pg.goto('http://127.0.0.1:8804',wait_until='networkidle');pg.wait_for_timeout(300)
  for sy in [0,20,40,60,80,110,130]:
   pg.evaluate('y=>scrollTo(0,y)',sy);pg.wait_for_timeout(110)
   bounds=pg.locator('.whole-ingredient').evaluate_all('(els)=>els.map(e=>{const r=e.getBoundingClientRect();return{top:r.top,bottom:r.bottom,left:r.left,right:r.right}})')
   progress=float(pg.locator('#burgerStage').get_attribute('data-explosion'))
   if .01<progress<.999:
    assert min(r['top'] for r in bounds)>=0,(width,height,sy,progress,bounds)
    assert max(r['bottom'] for r in bounds)<=height,(width,height,sy,progress,bounds)
  if width>=1000:assert pg.locator('[data-ingredient=ref-top]').bounding_box()['width']<650
  scene=pg.locator('.dish-scene').first;anchor=scene.evaluate("e=>{const h=e.querySelector('.scene-heading');return e.getBoundingClientRect().top+scrollY+h.offsetHeight+parseFloat(getComputedStyle(e).paddingTop)}")
  pg.evaluate('y=>scrollTo(0,y)',anchor-height*.85);pg.wait_for_timeout(450);start=float(scene.get_attribute('data-reveal-progress'));clip1=scene.locator('.scene-visual').evaluate('e=>getComputedStyle(e).clipPath')
  pg.evaluate('y=>scrollTo(0,y)',anchor-height*.45);pg.wait_for_timeout(450);end=float(scene.get_attribute('data-reveal-progress'));clip2=scene.locator('.scene-visual').evaluate('e=>getComputedStyle(e).clipPath')
  assert end>start+.4,(width,start,end);assert clip1!=clip2;assert pg.evaluate('document.documentElement.scrollWidth<=innerWidth+1');assert not errors,errors
  if width==1440:pg.evaluate('scrollTo(0,0)');pg.wait_for_timeout(250);pg.screenshot(path='/workspace/output/EMBER-burger-refined-desktop.png')
  if width==390 and height==844:pg.evaluate('scrollTo(0,0)');pg.wait_for_timeout(250);pg.screenshot(path='/workspace/output/EMBER-burger-refined-mobile.png')
  pg.close()
 rp=b.new_page(viewport={'width':390,'height':844},reduced_motion='reduce');rp.goto('http://127.0.0.1:8804',wait_until='networkidle');assert rp.locator('.scene-visual').first.evaluate('e=>getComputedStyle(e).clipPath')=='none';b.close();print('Burger remains visible while opening; reference plate clipping/scale/slide tracks scroll on 5 viewports; reduced motion passes.')
