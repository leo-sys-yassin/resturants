from playwright.sync_api import sync_playwright
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);pg=b.new_page(locale='ar-SY',viewport={'width':1440,'height':1000});errors=[];pg.on('pageerror',lambda e:errors.append(str(e)));pg.goto('http://127.0.0.1:8804',wait_until='networkidle');pg.wait_for_timeout(900)
 stage=pg.locator('#burgerStage').bounding_box();top=pg.locator('[data-ingredient=ref-top]').bounding_box();assert stage['width']>650;assert 400<top['width']<650
 pg.screenshot(path='/workspace/output/EMBER-desktop-updated.png')
 scenes=pg.locator('.dish-scene');assert scenes.count()==11
 for i in [0,1,2]:
  scene=scenes.nth(i);scene.scroll_into_view_if_needed();pg.wait_for_timeout(950);visual=scene.locator('.scene-visual');assert 'is-revealed' in visual.get_attribute('class');assert visual.evaluate('e=>getComputedStyle(e).opacity')=='1';box=visual.bounding_box();copy=scene.locator('.scene-copy').bounding_box();assert (box['x']<copy['x'])==(i%2==0)
 scenes.nth(1).scroll_into_view_if_needed();pg.wait_for_timeout(300);pg.screenshot(path='/workspace/output/EMBER-desktop-menu-updated.png')
 for w in [320,390,768,820,1024,1280,1440,1920]:
  pg.set_viewport_size({'width':w,'height':1000});pg.evaluate('scrollTo(0,0)');pg.wait_for_timeout(120);assert pg.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),w
 pg.set_viewport_size({'width':390,'height':844});pg.evaluate('scrollTo(0,0)');pg.screenshot(path='/workspace/output/EMBER-mobile-updated.png');assert not errors,errors
 rp=b.new_page(viewport={'width':1440,'height':1000},reduced_motion='reduce');rp.goto('http://127.0.0.1:8804',wait_until='networkidle');assert rp.locator('.burger-atmosphere').evaluate('e=>getComputedStyle(e).display')=='none';assert rp.locator('.scene-visual').first.evaluate('e=>getComputedStyle(e).opacity')=='1';b.close();print('Larger desktop burger, alternating category layout, on-entry reveals, 8 widths and reduced motion passed.')
