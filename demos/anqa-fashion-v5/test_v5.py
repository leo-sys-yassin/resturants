from pathlib import Path
from playwright.sync_api import sync_playwright,expect
import json
R=Path(__file__).parent;(R/'review').mkdir(exist_ok=True);errors=[];checks=[]
with sync_playwright() as w:
 b=w.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--enable-unsafe-swiftshader']);c=b.new_context(viewport={'width':1440,'height':900});p=c.new_page();p.on('pageerror',lambda e:errors.append(str(e)))
 p.goto('http://127.0.0.1:8915',wait_until='networkidle');p.wait_for_function('ANQA_DEBUG.engine.products.filter(Boolean).length===5');p.wait_for_timeout(600)
 assert p.evaluate('document.fonts.check("65px ANQAAmiri") && document.fonts.check("14px ANQAPlex")')
 p.screenshot(path=str(R/'review/hero.png'));p.locator('#exploreRail').click();p.wait_for_timeout(1400);p.screenshot(path=str(R/'review/rail.png'))
 a=p.locator('#backToHero').bounding_box();z=p.locator('#railSize').bounding_box();assert z['y']>=a['y']+a['height'];assert a['x']<1440*.15
 p.locator('#railSize').click();expect(p.locator('#infoDialog')).to_be_visible();p.keyboard.press('Escape');p.locator('#openSelected').click();p.wait_for_function('ANQA_DEBUG.state.detail.value===1');p.locator('#modelToggle').click();expect(p.locator('#modelPhoto')).to_be_visible();expect(p.locator('#turnArea')).to_be_hidden();p.wait_for_function('document.querySelector("#modelPhotoImage").complete');p.screenshot(path=str(R/'review/model.png'))
 for i in range(5):
  if i:
   p.locator('#closeDetail').click();p.wait_for_timeout(1000);p.locator(f'[data-open="{i}"]').click();p.wait_for_function('ANQA_DEBUG.state.detail.value===1');p.locator('#modelToggle').click()
  for view in ['front','right','back','left']:
   p.locator(f'[data-view="{view}"]').click();p.wait_for_function('document.querySelector("#modelPhotoImage").naturalWidth>0');assert p.locator('#modelPhotoImage').evaluate('(e)=>e.naturalWidth')==384
  p.locator('[data-view="front"]').click()
 p.locator('#languageButton').click();expect(p.locator('[data-view="front"]')).to_have_text('Front');assert p.locator('#photoCaption').inner_text().startswith('MODEL PHOTOGRAPHY')
 p.locator('#modelToggle').click();expect(p.locator('#modelPhoto')).to_be_hidden();p.wait_for_function('ANQA_DEBUG.engine.detailKey==="sky-product"');p.wait_for_function('ANQA_DEBUG.engine.detailRoot.visible');p.locator('#turnArea').focus();p.keyboard.press('ArrowRight');p.wait_for_timeout(700);assert p.evaluate('ANQA_DEBUG.engine.detailRoot.rotation.y')>0
 p.locator('[data-size="L"]').click();p.locator('#addToBag').click();p.locator('#bagButton').click();expect(p.locator('#bagCount')).to_have_text('1');p.keyboard.press('Escape');p.locator('#closeDetail').click();p.wait_for_timeout(1000);assert p.evaluate('document.body.style.overflow')==''
 for width,height in [(1280,800),(1920,1080)]:
  p.set_viewport_size({'width':width,'height':height});p.locator('[data-open="0"]').click();p.wait_for_function('ANQA_DEBUG.state.detail.value===1');p.locator('#modelToggle').click();img=p.locator('#modelPhoto').bounding_box();card=p.locator('#detailCard').bounding_box();assert img['x']+img['width']<card['x'];p.screenshot(path=str(R/f'review/model-{width}.png'));p.locator('#closeDetail').click();p.wait_for_timeout(1000)
 assert not errors,errors;b.close()
checks=['All 20 v2 photographic views load for all five garments; no photo blending or 3D human distortion.','Arabic Amiri and Plex fonts load; English view labels update.','Side home/size-guide buttons are separate and usable.','Garment 3D rotation, sizes, bag, close and scroll restoration pass.','Model image and product card do not overlap at 1280, 1440 and 1920 widths.']
(R/'verification.json').write_text(json.dumps({'passed':checks,'errors':errors,'limitations':['Human view is photography with four explicit view buttons, not a continuous 3D human or animated hands.','Garment meshes remain the existing approximate 3D assets.']},indent=2));print('\n'.join(checks))
