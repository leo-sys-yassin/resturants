from pathlib import Path
from playwright.sync_api import sync_playwright,expect
import json,hashlib,subprocess,zipfile,math
r=Path(__file__).parent;errors=[];old=json.loads((r/'verification.json').read_text())
for name in ['app.js','controls.js','facade.js','labels.js','data.js','assets/architecture.glb']:
 assert subprocess.check_output(['git','show',':demos/anqa-showroom-v10/'+name])==(r/name).read_bytes(),name
with zipfile.ZipFile(r/'ANQA_Showroom_v10.zip') as z:
 assert z.namelist()==['ANQA_Showroom_v10.html'];assert z.read(z.namelist()[0])==(r/z.namelist()[0]).read_bytes()
with sync_playwright() as w:
 b=w.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--enable-unsafe-swiftshader']);c=b.new_context(viewport={'width':800,'height':600},has_touch=True,reduced_motion='reduce');p=c.new_page();p.set_default_timeout(90000)
 def watch(page):
  page.on('pageerror',lambda e:errors.append(str(e)));page.on('console',lambda e:errors.append(e.text) if e.type=='error' and '404' not in e.text else None)
 def ready(page):
  page.goto('http://127.0.0.1:8930/ANQA_Showroom_v10.html',timeout=120000);page.wait_for_function('window.ANQA_TOUR?.architectureReady && ANQA_TOUR.surfaceReady && ANQA_TOUR.labelsReady && ANQA_TOUR.streetReady && ANQA_TOUR.productRoots.filter(Boolean).length===5',timeout=120000)
 def go(value):
  p.evaluate('(v)=>ANQA_TOUR.go(v)',value);p.wait_for_function('(v)=>Math.abs(ANQA_TOUR.progress-v)<.001',arg=value)
 watch(p);ready(p);c.set_offline(True);assert p.locator('header').evaluate('(e)=>getComputedStyle(e).backgroundImage')=='none';assert p.locator('#world').evaluate('(e)=>getComputedStyle(e).filter')=='none'
 assert p.evaluate("ANQA_TOUR.surfaces.get('WalnutSurface',true).map.image.width")==2048
 assert p.evaluate("ANQA_TOUR.surfaces.get('WalnutSurface',true).lightMap.image.width")==3072
 assert p.evaluate("ANQA_TOUR.surfaces.get('WalnutSurface',true).map!==ANQA_TOUR.surfaces.get('WalnutSurface',true).lightMap")
 p.screenshot(path=str(r/'review/front.png'))
 for v,name in [(.38,'footwear'),(.69,'interior')]:go(v);p.screenshot(path=str(r/'review'/f'{name}.png'))
 go(.30);p.wait_for_function('ANQA_TOUR.controls.state.active')
 for a,name in [(0,'wall-back'),(math.pi/2,'wall-left'),(math.pi,'wall-front'),(-math.pi/2,'wall-right')]:
  p.evaluate('(a)=>{ANQA_TOUR.controls.resetLook();ANQA_TOUR.controls.state.targetYaw=a;ANQA_TOUR.controls.state.targetPitch=0}',a);p.wait_for_function('(a)=>Math.abs(ANQA_TOUR.controls.state.yaw-a)<.01',arg=a);p.screenshot(path=str(r/'review'/f'{name}.png'))
 print('Final shader, sharp textures and four views passed',flush=True)
 p.locator('#menu').click();p.locator('[data-product="3"]').click();expect(p.locator('#product')).to_be_visible();p.wait_for_function('ANQA_TOUR.piece?.root');before=p.evaluate('ANQA_TOUR.piece.root.rotation.y');p.locator('#pieceCanvas').focus();p.keyboard.press('ArrowRight');assert p.evaluate('ANQA_TOUR.piece.root.rotation.y')>before;p.locator('#add').click();assert p.locator('#count').inner_text()=='1';p.keyboard.press('Escape')
 p.set_viewport_size({'width':390,'height':844});go(.69);p.wait_for_function('ANQA_TOUR.controls.state.active');before=p.evaluate('ANQA_TOUR.controls.state.yaw');cdp=c.new_cdp_session(p)
 for event,points in [('touchStart',[{'x':320,'y':400}]),('touchMove',[{'x':70,'y':400}]),('touchEnd',[])]:cdp.send('Input.dispatchTouchEvent',{'type':event,'touchPoints':points})
 p.wait_for_function('(v)=>ANQA_TOUR.controls.state.yaw<v-.2',arg=before);assert p.evaluate('document.documentElement.scrollWidth<=innerWidth');p.screenshot(path=str(r/'review/mobile-interior.png'))
 c2=b.new_context(viewport={'width':390,'height':500},device_scale_factor=2,reduced_motion='reduce');p2=c2.new_page();watch(p2);ready(p2);assert p2.evaluate('ANQA_TOUR.renderer.getPixelRatio()')==2;assert p2.locator('#world').evaluate('(e)=>e.width')==780;p2.screenshot(path=str(r/'review/retina-front.png'));assert not errors,errors;b.close()
old.setdefault('full_suite_html_sha256_before_final_material_tuning',old['html_sha256']);old['html_sha256']=hashlib.sha256((r/'ANQA_Showroom_v10.html').read_bytes()).hexdigest();old['passed']['final_material_followup']='Final HTML rechecked offline: shader compiles without console errors, 2K photographic wood independent of 3K lighting, no header haze or scene filter, four wall views, product rotation/cart, native mobile touch and 2x density. Full-suite navigation/product/geometry sources unchanged.';old['errors']=errors
(r/'verification.json').write_text(json.dumps(old,indent=2));print('FINAL PASS',flush=True)
