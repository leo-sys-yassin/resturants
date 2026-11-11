from playwright.sync_api import sync_playwright,expect
from pathlib import Path
import json,time
R=Path(__file__).parent;(R/'review').mkdir(exist_ok=True)
checks=[];errors=[];bad_responses=[]
with sync_playwright() as w:
 b=w.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);ctx=b.new_context(viewport={'width':1440,'height':900});p=ctx.new_page();p.on('pageerror',lambda e:errors.append(str(e)));p.on('response',lambda r:bad_responses.append(r.url) if r.status>=400 else None)
 p.goto('http://127.0.0.1:8912',wait_until='networkidle');p.wait_for_function("document.querySelector('#heroCanvas').dataset.ready==='true'");p.screenshot(path=str(R/'review/hero-final.png'))
 expect(p.locator('.wordmark')).to_contain_text('ANQA');assert p.locator('[data-view]').count()==0
 intro=p.locator('#heroCanvas').get_attribute('data-frame');p.evaluate('window.scrollTo({top:240,behavior:"instant"})');p.wait_for_timeout(250);assert p.locator('#heroCanvas').get_attribute('data-frame')!=intro
 p.locator('#backToRail').evaluate('(el)=>el.click()');p.wait_for_timeout(1600);p.wait_for_function("[...document.querySelectorAll('.garment canvas')].every(c=>c.dataset.ready==='true')")
 p.screenshot(path=str(R/'review/rail-final.png'));assert p.locator('.garment').count()==5
 # Hovering does not inject motion. A physical drag does, then motion settles.
 p.wait_for_timeout(700);p.mouse.move(650,430);p.mouse.move(690,460,steps=8);angles=p.locator('.garment-body').evaluate_all('(a)=>a.map(e=>e.style.transform)');assert all('rotateZ(0deg)' in x for x in angles)
 p.mouse.move(700,470);p.mouse.down();p.mouse.move(390,470,steps=18);p.mouse.up();p.wait_for_timeout(1000);expect(p.locator('#captionMeta')).to_contain_text('Wine');p.locator('#railPrev').click();p.wait_for_timeout(1100)
 # Click the garment itself (not the separate caption) to catch pointer-capture bugs.
 p.locator('.garment[data-product="0"]').click(position={'x':150,'y':180});p.wait_for_timeout(650);expect(p.locator('#detailShell')).to_be_visible()
 canvas=p.locator('#turntableCanvas');expect(canvas).to_have_attribute('data-ready','true');assert p.locator('#detailCard').evaluate('(e)=>getComputedStyle(e).boxShadow')=='none'
 def drag_turn():
  box=canvas.bounding_box();x=box['x']+100;y=box['y']+box['height']*.55;p.mouse.move(x,y);p.mouse.down();seen=set()
  for step in range(81):
   p.mouse.move(x+step*7.75,y);p.wait_for_timeout(18);seen.add(canvas.get_attribute('data-frame'))
  p.mouse.up();p.wait_for_timeout(400);assert len(seen)>=45,len(seen)
  return len(seen)
 count=drag_turn();checks.append(f'Pointer rotation traverses {count} distinct frames in one drag; no four-view buttons')
 canvas.focus();p.keyboard.press('Home');p.wait_for_timeout(650)
 p.locator('#modelToggle').click();p.wait_for_function("document.querySelector('#turntableCanvas').dataset.asset==='coal-model-360' && document.querySelector('#turntableCanvas').dataset.ready==='true'");introframes=[]
 for _ in range(9):introframes.append(canvas.get_attribute('data-frame'));p.wait_for_timeout(220)
 assert len(set(introframes))>3
 p.wait_for_timeout(900);drag_turn();canvas.focus();p.keyboard.press('Home');p.wait_for_timeout(650)
 for _ in range(12):p.keyboard.press('ArrowRight')
 p.wait_for_timeout(750);assert canvas.get_attribute('data-frame')=='32';p.screenshot(path=str(R/'review/model-back-final.png'))
 p.locator('[data-variant="1"]').click();p.wait_for_function("document.querySelector('#turntableCanvas').dataset.asset==='wine-model-360' && document.querySelector('#turntableCanvas').dataset.ready==='true'");expect(p.locator('#colorName')).to_have_text('WINE');assert canvas.get_attribute('data-frame')=='32'
 p.locator('[data-size="L"]').click();p.locator('#qtyPlus').click();p.locator('#addToBag').click();p.locator('#bagButton').click();p.wait_for_timeout(550);expect(p.locator('#bagTotal')).to_have_text('$168.00');expect(p.locator('#bagCount')).to_have_text('2');p.locator('#checkout').click();expect(p.locator('#infoTitle')).to_have_text('Your selection.');p.keyboard.press('Escape')
 p.locator('#sizeGuideInline').click();expect(p.locator('#infoDialog table tbody tr')).to_have_count(5);p.keyboard.press('Escape');p.locator('#detailBack').click();p.wait_for_timeout(1600);expect(p.locator('#openSelected')).to_be_in_viewport()
 # All products both modes load the correct atlas; the same controls rotate every item.
 for product,key in enumerate(['coal','wine','oat','forest','sky']):
  p.locator(f'[data-open="{product}"]').click();p.wait_for_timeout(650)
  for kind in ['product','model']:
   if kind=='model':p.locator('#modelToggle').click()
   p.wait_for_function('(key)=>{const c=document.querySelector("#turntableCanvas");return c.dataset.ready==="true"&&c.dataset.asset===key}',arg=key+'-'+kind+'-360')
   canvas.focus();p.keyboard.press('ArrowRight');p.wait_for_timeout(220);assert canvas.get_attribute('data-frame')!='0'
  p.locator('#closeDetail').click();p.wait_for_timeout(650)
 checks.append('Five products × both modes: correct atlases, keyboard rotation, generated back/side views, intro gesture and angle-preserving swatches passed')
 p.evaluate('window.scrollTo({top:0,behavior:"instant"})');p.wait_for_timeout(150);p.locator('#searchButton').click();p.locator('#searchInput').fill('sky');expect(p.locator('.search-result')).to_have_count(1);p.locator('.search-result').click();p.wait_for_timeout(650);expect(p.locator('#detailName')).to_have_text('Air Tee');p.keyboard.press('Escape');p.wait_for_timeout(650)
 p.reload(wait_until='networkidle');expect(p.locator('#bagCount')).to_have_text('2');p.locator('#bagButton').click();p.wait_for_timeout(550);p.locator('[data-remove="0"]').click();expect(p.locator('#bagCount')).to_have_text('0');p.keyboard.press('Escape')
 checks.append('Rail pointer selection, no hover wobble, frameless detail, back buttons, sizes, quantities, cart totals/persistence, search, size guide and Escape passed')
 for width,height in [(1280,800),(1440,900),(1920,1080)]:
  p.set_viewport_size({'width':width,'height':height});p.evaluate('window.scrollTo({top:0,behavior:"instant"})');p.wait_for_timeout(250);assert p.evaluate('document.documentElement.scrollWidth<=innerWidth');p.locator('#exploreRail').click();p.wait_for_timeout(1500);p.locator('#openSelected').click();p.wait_for_timeout(650);p.locator('#modelToggle').click();p.wait_for_timeout(2800)
  card=p.locator('#detailCard').bounding_box();controls=p.locator('#visualControls').bounding_box();assert card['x']>controls['x']+controls['width'];assert card['y']+card['height']<height;assert controls['y']+controls['height']<height
  p.screenshot(path=str(R/f'review/desktop-{width}.png'));p.locator('#detailBack').click();p.wait_for_timeout(1400);p.locator('#backToHero').click();p.wait_for_timeout(1200);assert p.evaluate('scrollY')<5
 reduced=b.new_context(viewport={'width':1440,'height':900},reduced_motion='reduce');q=reduced.new_page();q.goto('http://127.0.0.1:8912');q.locator('#exploreRail').click();q.wait_for_timeout(150);q.locator('#openSelected').click();q.wait_for_timeout(150);expect(q.locator('#detailShell')).to_be_visible()
 assert not errors,errors;assert not bad_responses,bad_responses
 checks.append('1280×800, 1440×900, 1920×1080 layouts and reduced motion passed; zero browser errors or failed responses')
 b.close()
(R/'verification.json').write_text(json.dumps({'passed':checks,'browser_errors':errors,'failed_responses':bad_responses},indent=2));print('\n'.join(checks))
