from playwright.sync_api import sync_playwright
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);pg=b.new_page(locale='en-US',viewport={'width':390,'height':844});pg.goto('http://127.0.0.1:8804',wait_until='networkidle')
 pg.evaluate("(()=>{const d=EmberMenuStore.snapshot();Object.assign(d.config,{instagram:'https://instagram.com/restaurant',facebook:'https://facebook.com/restaurant',whatsapp:'+963900000000'});EmberMenuStore.save(d)})()")
 assert pg.locator('#restaurantContact a[href*="instagram"]').count()==1
 pg.locator('#openAdmin').click();pg.locator('[data-admin-tab="restaurant"]').click();pg.locator('[data-contact-visible="instagram"]').uncheck();pg.locator('[data-contact-visible="whatsapp"]').uncheck();pg.locator('#restaurantForm button[type=submit]').click()
 pg.wait_for_function('EmberMenuStore.config.contactVisibility.instagram===false');pg.locator('#adminClose').click()
 assert pg.locator('#restaurantContact a[href*="instagram"]').count()==0
 assert pg.locator('#restaurantContact a[href*="wa.me"]').count()==0
 assert pg.locator('#restaurantContact a[href*="facebook"]').count()==1
 assert pg.evaluate('EmberMenuStore.config.instagram')=='https://instagram.com/restaurant'
 pg.reload(wait_until='networkidle');assert pg.locator('#restaurantContact a[href*="instagram"]').count()==0
 pg.locator('#openAdmin').click();pg.locator('[data-admin-tab="restaurant"]').click();pg.locator('[data-contact-visible="instagram"]').check();pg.locator('#restaurantForm button[type=submit]').click();pg.wait_for_function('EmberMenuStore.config.contactVisibility.instagram===true');pg.locator('#adminClose').click()
 assert pg.locator('#restaurantContact a[href*="instagram"]').count()==1
 b.close();print('Independent visibility toggles: hide, keep link, persist across reload and show again passed.')
