from playwright.sync_api import sync_playwright,expect
from pathlib import Path
import json
R=Path(__file__).parent
with sync_playwright() as w:
 b=w.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--enable-unsafe-swiftshader'])
 p=b.new_page(viewport={'width':1440,'height':900});p.goto('http://127.0.0.1:8914',wait_until='networkidle');p.wait_for_function('ANQA_DEBUG.engine.products.filter(Boolean).length===5')
 p.locator('#exploreRail').click();p.wait_for_timeout(1600);p.locator('#openSelected').click();p.wait_for_function('ANQA_DEBUG.state.detail.value===1');p.mouse.move(470,450);p.mouse.wheel(0,550);p.wait_for_timeout(300)
 assert p.locator('#detailCard').evaluate('(e)=>e.scrollTop')>0,'Wheel over the scene must scroll information'
 assert p.evaluate('ANQA_DEBUG.state.rotation.value')==0,'Wheel must never turn model'
 p.locator('#bagButton').click();p.keyboard.press('Escape');assert p.evaluate('document.body.style.overflow')=='hidden'
 p.locator('#closeDetail').click();p.wait_for_timeout(1200);assert p.evaluate('document.body.style.overflow')==''
 y=p.evaluate('scrollY');p.mouse.move(720,420);p.mouse.wheel(0,800);p.wait_for_timeout(500);assert p.evaluate('scrollY')>y
 p.locator('#menuButton').click();p.keyboard.press('Escape');assert p.evaluate('document.body.style.overflow')==''
 p.evaluate('scrollTo(0,0)');p.wait_for_timeout(400);p.screenshot(path=str(R/'review/hero-v4.png'))
 p.locator('#exploreRail').click();p.wait_for_timeout(1200);p.screenshot(path=str(R/'review/rail-v4.png'));b.close()
 f=R/'verification.json';d=json.loads(f.read_text());d['passed'].append('Wheel over detail scene scrolls information without rotation; nested bag and menu restore scrolling; page wheel exits pinned section.');d['limitations']=['Human and garment meshes remain approximate v3 assets; shape defects remain unresolved.','No skeletal hand animation.','Software GPU used; hardware smoothness not measured.'];f.write_text(json.dumps(d,indent=2))
 print('Scroll regression checks passed')
