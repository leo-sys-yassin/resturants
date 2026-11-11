from playwright.sync_api import sync_playwright,expect
from pathlib import Path
import json
R=Path(__file__).parent
(R/'review').mkdir(exist_ok=True)
results=[]; errors=[]
with sync_playwright() as w:
 b=w.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 c=b.new_context(viewport={'width':1440,'height':900});p=c.new_page();p.on('pageerror',lambda e:errors.append(str(e)))
 p.goto('http://127.0.0.1:8910',wait_until='networkidle');p.wait_for_timeout(300)
 initial=p.locator('.garment').first.get_attribute('style');p.locator('#exploreRail').click();p.wait_for_timeout(1400)
 assert p.locator('.garment').count()==5
 assert initial!=p.locator('.garment').first.get_attribute('style')
 assert float(p.locator('#railSvg').evaluate('(e)=>getComputedStyle(e).opacity'))>.99
 before=p.locator('.garment').first.get_attribute('style');p.locator('#railNext').click();p.wait_for_timeout(180);during=p.locator('.garment').first.get_attribute('style');p.wait_for_timeout(750);after=p.locator('.garment').first.get_attribute('style');assert before!=during!=after
 expect(p.locator('#captionMeta')).to_contain_text('Wine')
 p.locator('#railPrev').click();p.wait_for_timeout(900)
 # Native pointer drag on the rail, then restore charcoal.
 p.mouse.move(725,580);p.mouse.down();p.mouse.move(410,580,steps=12);p.mouse.up();p.wait_for_timeout(900)
 expect(p.locator('#captionMeta')).to_contain_text('Wine');p.locator('#railPrev').click();p.wait_for_timeout(900)
 p.locator('#openSelected').click();p.wait_for_timeout(700)
 for product in range(5):
  if product:
   p.locator('#closeDetail').click();p.wait_for_timeout(650)
   p.locator(f'[data-open="{product}"]').click();p.wait_for_timeout(700)
  seen=[]
  for mode in ['product','model']:
   p.locator('#garmentMode' if mode=='product' else '#modelMode').click()
   for direction in range(4):
    p.locator(f'[data-view="{direction}"]').click();p.wait_for_timeout(100)
    img=p.locator(f'.garment[data-product="{product}"] .front-layer');img.evaluate('(e)=>e.decode()')
    src=img.get_attribute('src');assert f'-{mode}-' in src;seen.append(src)
    assert img.evaluate('(e)=>e.naturalWidth>0')
  assert len(set(seen))==8
 results.append('All 40 genuine directional assets load and change per product/mode/view')
 p.locator('#closeDetail').click();p.wait_for_timeout(650)
 p.locator('[data-open="0"]').click();p.wait_for_timeout(700);p.locator('#modelMode').click();p.locator('[data-view="2"]').click();p.locator('[data-variant="1"]').click();p.wait_for_timeout(750)
 expect(p.locator('#colorName')).to_have_text('WINE');assert p.locator('[data-product="1"] .front-layer').get_attribute('src').endswith('wine-model-back.webp')
 p.locator('[data-size="L"]').click();p.locator('#qtyPlus').click();p.locator('#addToBag').click();p.locator('#bagButton').click();p.wait_for_timeout(600)
 expect(p.locator('#bagTotal')).to_have_text('$168.00');expect(p.locator('#bagCount')).to_have_text('2');expect(p.locator('.bag-row p')).to_contain_text('L')
 p.locator('#checkout').click();expect(p.locator('#infoTitle')).to_have_text('Your selection.');p.keyboard.press('Escape')
 p.locator('#sizeGuideInline').click();expect(p.locator('#infoDialog table tbody tr')).to_have_count(5);p.keyboard.press('Escape');p.locator('#closeDetail').click();p.wait_for_timeout(650)
 p.locator('#searchButton').click();p.locator('#searchInput').fill('sky');expect(p.locator('.search-result')).to_have_count(1);p.locator('.search-result').click();p.wait_for_timeout(600);expect(p.locator('#detailName')).to_have_text('Air Tee');p.keyboard.press('Escape');p.wait_for_timeout(650)
 p.reload(wait_until='networkidle');expect(p.locator('#bagCount')).to_have_text('2')
 p.locator('#bagButton').click();p.wait_for_timeout(550);p.locator('[data-remove="0"]').click();expect(p.locator('#bagCount')).to_have_text('0');p.keyboard.press('Escape')
 results.append('Scroll, spring rail, pointer drag, swatches, sizing, quantity, cart, persistence, search, size guide and modal dismissal passed')
 for width,height in [(1280,800),(1440,900),(1920,1080)]:
  p.set_viewport_size({'width':width,'height':height});p.evaluate('window.scrollTo(0,0)');p.wait_for_timeout(500);assert p.evaluate('document.documentElement.scrollWidth<=innerWidth')
  p.locator('#exploreRail').click();p.wait_for_timeout(1400);p.locator('#openSelected').click();p.wait_for_timeout(650);p.locator('#modelMode').click();p.wait_for_timeout(450)
  card=p.locator('#detailCard').bounding_box();controls=p.locator('#visualControls').bounding_box();assert card['x']>controls['x']+controls['width'];assert card['y']+card['height']<height;assert controls['y']+controls['height']<height
  p.screenshot(path=str(R/f'review/desktop-{width}.png'));p.locator('#closeDetail').click();p.wait_for_timeout(650)
 assert not p.locator('img').evaluate_all('(a)=>a.some(i=>!i.complete||!i.naturalWidth)')
 rc=b.new_context(viewport={'width':1440,'height':900},reduced_motion='reduce');q=rc.new_page();q.goto('http://127.0.0.1:8910');q.locator('#exploreRail').click();q.wait_for_timeout(150);q.locator('#openSelected').click();q.wait_for_timeout(100);expect(q.locator('#detailShell')).to_be_visible()
 assert not errors,errors
 results.append('1280×800, 1440×900, 1920×1080 and reduced motion passed; zero browser errors')
 b.close()
(R/'verification.json').write_text(json.dumps({'passed':results,'browser_errors':errors},indent=2));print('\n'.join(results))
