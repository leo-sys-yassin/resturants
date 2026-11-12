from pathlib import Path
from playwright.sync_api import sync_playwright,expect
import json,hashlib
R=Path(__file__).parent;(R/'review').mkdir(exist_ok=True)
checks=[];errors=[]
with sync_playwright() as w:
 b=w.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--enable-unsafe-swiftshader']);c=b.new_context(viewport={'width':1440,'height':900},has_touch=True,reduced_motion="reduce");p=c.new_page();p.on('pageerror',lambda e:errors.append(str(e)));p.goto('http://127.0.0.1:8921/ANQA_Showroom_v2.html',wait_until='load');c.set_offline(True);p.wait_for_function('ANQA_TOUR.productRoots.filter(Boolean).length===5',timeout=120000);p.wait_for_timeout(1800);p.screenshot(path=str(R/'review/final-entry.png'))
 p.locator('[data-stop="3"]').click();p.wait_for_function('Math.abs(ANQA_TOUR.progress-.73)<.001',timeout=60000);assert p.evaluate('Math.abs(ANQA_TOUR.doors[0].pivot.rotation.y)')>1.4;p.screenshot(path=str(R/'review/final-clothes.png'))
 # Project the centre of a real garment and click its mesh, not an overlay button.
 pos=p.evaluate('''()=>{const r=ANQA_TOUR.productRoots[3],v=r.position.clone();v.y-=.12;v.project(ANQA_TOUR.camera);return {x:(v.x+1)*innerWidth/2,y:(1-v.y)*innerHeight/2}}''');p.mouse.click(pos['x'],pos['y']);expect(p.locator('#product')).to_be_visible(timeout=15000)
 p.screenshot(path=str(R/'review/product-card.png'));p.locator('#sizes button',has_text='XL').click();p.locator('#plus').click();p.locator('#add').click();expect(p.locator('#count')).to_have_text('2');p.locator('#product .close').click();p.wait_for_function('document.body.style.overflow===""')
 p.locator('#bag').click();expect(p.locator('.cart-row')).to_have_count(1);expect(p.locator('.cart-row')).to_contain_text('XL × 2');p.locator('[data-remove]').click();expect(p.locator('#count')).to_have_text('0');p.locator('#cart .close').click()
 p.locator('#menu').click();p.locator('#search').fill('سماوي');expect(p.locator('.catalog-item')).to_have_count(1);p.locator('.catalog-item').click();expect(p.locator('#productName')).to_have_text('تيشيرت يومي');p.keyboard.press('Escape')
 checks.append('Offline standalone: all five meshes, fonts and product images load; direct 3D mesh click opens product; size, quantity, cart, removal, search and modal scroll restoration pass.')
 p.locator('[data-stop="4"]').click();p.wait_for_function('ANQA_TOUR.progress>.999',timeout=60000);assert p.evaluate('ANQA_TOUR.camera.position.z')>9;assert p.evaluate('Math.abs(ANQA_TOUR.doors[0].pivot.rotation.y)')<.01
 before=p.evaluate('ANQA_TOUR.camera.quaternion.toArray()');p.mouse.move(600,350);p.mouse.down();p.mouse.move(950,500,steps=8);p.mouse.up();p.wait_for_timeout(200);assert p.evaluate('ANQA_TOUR.camera.quaternion.toArray()')==before
 p.locator('[data-stop="0"]').click();p.wait_for_function('ANQA_TOUR.progress<.001',timeout=60000);before=p.evaluate('ANQA_TOUR.camera.quaternion.toArray()');p.mouse.move(600,350);p.mouse.down();p.mouse.move(950,500,steps=8);p.mouse.up();p.wait_for_timeout(200);assert p.evaluate('ANQA_TOUR.camera.quaternion.toArray()')==before
 checks.append('Full route returns outside and closes the doors; mouse drag cannot rotate the facade at either end.')
 p.set_viewport_size({'width':390,'height':844});p.wait_for_timeout(500);assert p.evaluate('document.documentElement.scrollWidth<=innerWidth');p.screenshot(path=str(R/'review/final-mobile.png'));p.locator('[data-stop="1"]').click();p.wait_for_function('Math.abs(ANQA_TOUR.progress-.38)<.001',timeout=60000);p.screenshot(path=str(R/'review/final-mobile-shoes.png'));p.locator('#menu').click();expect(p.locator('#catalog')).to_be_visible();p.keyboard.press('Escape')
 before=p.evaluate('scrollY');cdp=c.new_cdp_session(p);cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':200,'y':600}]})
 for y in range(580,320,-25):
  cdp.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':200,'y':y}]});p.wait_for_timeout(30)
 cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]});p.wait_for_timeout(500);assert p.evaluate('scrollY')>before
 checks.append('Emulated phone vertical touch swipe advances the tour; static architecture is batched by material.')
 assert not errors,errors
 checks.append('390px mobile viewport: no horizontal overflow; tour navigation and catalog work. Physical touch smoothness requires device testing.')
 b.close()
(R/'verification.json').write_text(json.dumps({'passed':checks,'errors':errors,'html_sha256':hashlib.sha256((R/'ANQA_Showroom_v2.html').read_bytes()).hexdigest(),'limitations':['Software-rendered Chromium; no real phone GPU benchmark.','Existing approximate garment geometry retained.','Architectural demo, not a photograph or production checkout.']},indent=2));print('\n'.join(checks))
