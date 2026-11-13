from pathlib import Path
from playwright.sync_api import sync_playwright,expect
import json,hashlib,math
R=Path(__file__).parent;(R/'review').mkdir(exist_ok=True);errors=[];checks={}
with sync_playwright() as w:
 b=w.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--enable-unsafe-swiftshader']);c=b.new_context(viewport={'width':1100,'height':800},has_touch=True,reduced_motion='reduce');p=c.new_page();p.set_default_timeout(90000);p.on('pageerror',lambda e:errors.append(str(e)));p.on('console',lambda e:errors.append(e.text) if e.type=='error' and '404' not in e.text else None)
 p.goto('http://127.0.0.1:8926/ANQA_Showroom_v6.html',wait_until='load',timeout=120000)
 print('Page loaded',flush=True);p.wait_for_function('window.ANQA_TOUR?.architectureReady && ANQA_TOUR.productRoots.filter(Boolean).length===5',timeout=120000);p.wait_for_timeout(800);c.set_offline(True);print('Scene ready',flush=True)
 assert p.locator('#photoEntrance,.photo-stage,.photo-leaf').count()==0
 assert p.evaluate('ANQA_TOUR.facade.children[0].geometry.type')=='ExtrudeGeometry'
 assert p.evaluate('ANQA_TOUR.doors.length')==2
 assert p.evaluate("ANQA_TOUR.scene.getObjectsByProperty('name','Open rack upright').length")==12
 fixed=p.evaluate('ANQA_TOUR.doors.map(d=>d.pivot.position.toArray())')
 p.screenshot(path=str(R/'review/facade-closed.png'));print('Facade captured',flush=True)
 # Opening happens inside the WebGL scene, about stationary hinge pivots.
 p.evaluate('ANQA_TOUR.go(.16)');p.wait_for_function('Math.abs(ANQA_TOUR.progress-.16)<.001');p.wait_for_timeout(500)
 angles=p.evaluate('ANQA_TOUR.doors.map(d=>d.pivot.rotation.y)');assert angles[0]>.3 and angles[1]<-.3
 assert p.evaluate('ANQA_TOUR.doors.map(d=>d.pivot.position.toArray())')==fixed
 p.screenshot(path=str(R/'review/facade-opening.png'))
 p.evaluate('ANQA_TOUR.go(.24)');p.wait_for_function('Math.abs(ANQA_TOUR.progress-.24)<.001');p.wait_for_timeout(500)
 assert p.evaluate('ANQA_TOUR.camera.position.z')<4.85
 assert all(abs(a)>1.4 for a in p.evaluate('ANQA_TOUR.doors.map(d=>d.pivot.rotation.y)'))
 p.screenshot(path=str(R/'review/through-door.png'));print('Door traversal passed',flush=True);checks['entrance']='Single WebGL world; fixed hinges, opposite opening rotations, camera passes through actual aperture; no photo overlay.'
 p.evaluate('ANQA_TOUR.go(.69)');p.wait_for_function('Math.abs(ANQA_TOUR.progress-.69)<.001');p.wait_for_timeout(500)
 p.screenshot(path=str(R/'review/right-wall.png'));print('Wall captured',flush=True)
 p.evaluate('ANQA_TOUR.openProduct(3)');expect(p.locator('#product')).to_be_visible();p.wait_for_function('ANQA_TOUR.piece?.root');pc=p.locator('#pieceCanvas');bb=pc.bounding_box();before=p.evaluate('ANQA_TOUR.piece.root.rotation.y');p.mouse.move(bb['x']+bb['width']*.3,bb['y']+bb['height']*.5);p.mouse.down();p.mouse.move(bb['x']+bb['width']*.7,bb['y']+bb['height']*.5,steps=8);p.mouse.up();after=p.evaluate('ANQA_TOUR.piece.root.rotation.y');assert abs(after-before)>.5
 assert p.evaluate('ANQA_TOUR.piece.root.rotation.x')==0;checks['garment']='Existing garment remains a continuous yaw-rotated mesh; product details open.'
 p.locator('#sizes button').filter(has_text='L').first.click();p.locator('#plus').click();p.locator('#add').click();assert p.locator('#count').inner_text()=='2';p.keyboard.press('Escape')
 p.evaluate('ANQA_TOUR.go(0)');p.wait_for_function('ANQA_TOUR.progress<.001');p.wait_for_timeout(400);assert max(abs(a) for a in p.evaluate('ANQA_TOUR.doors.map(d=>d.pivot.rotation.y)'))==0
 p.mouse.move(400,400);p.mouse.down();p.mouse.move(700,440);p.mouse.up();assert abs(p.evaluate('ANQA_TOUR.camera.position.x'))<.001
 checks['return']='Returning closes both doors; facade cannot be orbited.'
 p.set_viewport_size({'width':390,'height':844});p.wait_for_timeout(500);assert p.evaluate('document.documentElement.scrollWidth<=innerWidth');p.screenshot(path=str(R/'review/mobile-facade.png'))
 p.evaluate('ANQA_TOUR.go(.69)');p.wait_for_function('Math.abs(ANQA_TOUR.progress-.69)<.001');p.wait_for_timeout(500);p.screenshot(path=str(R/'review/mobile-wall.png'));checks['mobile']='Phone viewport renders same world offline without horizontal overflow.'
 # Confirm ordinary (non-reduced) motion actually progresses through intermediate poses.
 c.set_offline(False);p.emulate_media(reduced_motion='no-preference');p.reload();p.wait_for_function('window.ANQA_TOUR?.architectureReady',timeout=120000);p.evaluate('ANQA_TOUR.go(0)');p.wait_for_function('ANQA_TOUR.progress<.001',timeout=90000)
 p.evaluate('ANQA_TOUR.go(.30)');values=[]
 for _ in range(12):
  p.wait_for_timeout(100);values.append(p.evaluate('ANQA_TOUR.progress'))
 p.wait_for_function('ANQA_TOUR.progress>.299',timeout=90000);assert any(.005<v<.29 for v in values),values;checks['motion']='Default motion produces intermediate camera and door states, not a scene swap.'
 assert not errors,errors;b.close()
(R/'verification.json').write_text(json.dumps({'passed':checks,'errors':errors,'html_sha256':hashlib.sha256((R/'ANQA_Showroom_v6.html').read_bytes()).hexdigest(),'limits':['Software Chromium; hardware frame rates not measured.','Reference image mapped onto facade stone geometry; live interior differs from photographed interior.']},indent=2));print('PASS',flush=True)
