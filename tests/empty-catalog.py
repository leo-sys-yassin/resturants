from playwright.sync_api import sync_playwright
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);pg=b.new_page(locale='en-US');errors=[];pg.on('pageerror',lambda e:errors.append(str(e)));pg.goto('http://127.0.0.1:8804',wait_until='networkidle')
 original=pg.evaluate('EmberMenuStore.snapshot().products[0]')
 pg.evaluate("(()=>{const d=EmberMenuStore.snapshot();d.products=[];d.groups=[['menu','المنيو','','Menu','']];EmberMenuStore.save(d)})()")
 pg.reload(wait_until='networkidle');assert pg.locator('.dish-scene').count()==0;assert pg.locator('.hero-thumb').count()==0;assert pg.locator('#menuUnavailable').is_visible();pg.locator('#openAdmin').click();assert pg.locator('#adminDialog').is_visible();pg.locator('#adminClose').click()
 pg.evaluate("p=>{const d=EmberMenuStore.snapshot();p.id='custom-item';p.category='menu';p.name='طبق جديد';p.en='New dish';d.products=[p];EmberMenuStore.save(d)}",original)
 pg.reload(wait_until='networkidle');assert pg.locator('.dish-scene').count()==1;assert pg.locator('.hero-thumb').count()==1;assert pg.locator('#heroDishName').inner_text()=='New dish'

 assert not errors,errors;b.close();print('An empty new restaurant survives reload, shows no demo dishes and still permits management.')
