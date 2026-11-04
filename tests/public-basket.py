from playwright.sync_api import sync_playwright
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 pg=b.new_page(viewport={'width':390,'height':844},locale='en-US')
 pg.add_init_script("localStorage.setItem('ember-cart-v4',JSON.stringify([{product:'cheeseburger',qty:2,extras:[],note:'old'}]))")
 pg.goto('http://127.0.0.1:8804',wait_until='networkidle')
 assert pg.locator('#cartDock').is_hidden()
 pg.locator('[data-preview="cheeseburger"]').click();pg.locator('#scene-burgers .scene-add').click();pg.locator('#addToCart').click()
 assert pg.locator('#cartDock').is_visible()
 assert pg.evaluate("localStorage.getItem('ember-cart-v4')") is None
 pg.reload(wait_until='networkidle');assert pg.locator('#cartDock').is_hidden()
 pg.locator('[data-preview="cheeseburger"]').click();pg.locator('#scene-burgers .scene-add').click();pg.locator('#addToCart').click()
 pg.evaluate("dispatchEvent(new PageTransitionEvent('pagehide',{persisted:true}));dispatchEvent(new PageTransitionEvent('pageshow',{persisted:true}))")
 assert pg.locator('#cartDock').is_hidden()
 b.close();print('Public cart: old saved basket ignored, new choices work, no persistence, reload and page return empty.')
