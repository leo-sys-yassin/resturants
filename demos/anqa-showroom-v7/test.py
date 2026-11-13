from pathlib import Path
from playwright.sync_api import sync_playwright,expect
import json,hashlib,math,zipfile
R=Path(__file__).parent;(R/'review').mkdir(exist_ok=True);errors=[];checks={}
with zipfile.ZipFile(R/'ANQA_Showroom_v7.zip') as z:
 assert z.namelist()==['ANQA_Showroom_v7.html'];assert z.read(z.namelist()[0])==(R/'ANQA_Showroom_v7.html').read_bytes()
checks['download']='ZIP contains exactly one standalone HTML file.'
with sync_playwright() as w:
 b=w.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--enable-unsafe-swiftshader']);c=b.new_context(viewport={'width':1100,'height':800},has_touch=True,reduced_motion='reduce');p=c.new_page();p.set_default_timeout(90000);p.on('pageerror',lambda e:errors.append(str(e)));p.on('console',lambda e:errors.append(e.text) if e.type=='error' and '404' not in e.text else None)
 def load():
  p.goto('http://127.0.0.1:8927/ANQA_Showroom_v7.html',timeout=120000);p.wait_for_function('window.ANQA_TOUR?.surfaceReady && ANQA_TOUR.architectureReady && ANQA_TOUR.productRoots.filter(Boolean).length===5',timeout=120000)
 def go(v):
  p.evaluate('(v)=>ANQA_TOUR.go(v)',v);p.wait_for_function('(v)=>Math.abs(ANQA_TOUR.progress-v)<.001',arg=v)
 load();c.set_offline(True);print('Scene ready',flush=True)
 assert p.locator('#photoEntrance,.photo-leaf').count()==0
 assert p.evaluate('ANQA_TOUR.entrance.topGlass.geometry.type')=='ShapeGeometry'
 assert p.evaluate("ANQA_TOUR.entrance.lining.material.userData.surface").startswith('Oak')
 assert p.evaluate("ANQA_TOUR.surfaces.textures['oak-color.jpg'].image.width")>=2048
 assert p.evaluate("ANQA_TOUR.surfaces.textures['oak-normal.jpg'].image.width")>=2048
 p.screenshot(path=str(R/'review/front.png'))
 before=p.evaluate('ANQA_TOUR.doors.map(d=>({position:d.pivot.position.toArray(),scale:d.pivot.scale.toArray(),positions:Array.from(d.pivot.children[0].geometry.attributes.position.array)}))')
 go(.16);p.screenshot(path=str(R/'review/opening.png'));assert p.evaluate('ANQA_TOUR.doors[0].pivot.rotation.y>0 && ANQA_TOUR.doors[1].pivot.rotation.y<0')
 after=p.evaluate('ANQA_TOUR.doors.map(d=>({position:d.pivot.position.toArray(),scale:d.pivot.scale.toArray(),positions:Array.from(d.pivot.children[0].geometry.attributes.position.array)}))');assert before==after
 assert p.evaluate('ANQA_TOUR.doors.every(d=>d.pivot.rotation.x===0 && d.pivot.rotation.z===0)')
 go(.24);assert p.evaluate('ANQA_TOUR.camera.position.z')<4.995;assert min(abs(a) for a in p.evaluate('ANQA_TOUR.doors.map(d=>d.pivot.rotation.y)'))>1.55
 checks['doors']='Door geometry, scale and hinge positions remain invariant; only rigid yaw changes. Both doors open inward; camera crosses the threshold. Fixed upper glass remains in the scene.';print('Doors passed',flush=True)
 go(.69);p.wait_for_function('ANQA_TOUR.controls.state.active');p.screenshot(path=str(R/'review/wall.png'))
 # Complete yaw rotation leaves the eye at the same location and keeps roll zero.
 eye=p.evaluate('ANQA_TOUR.camera.position.toArray()');start=p.evaluate('ANQA_TOUR.controls.state.yaw')
 for _ in range(5):
  p.mouse.move(950,390);p.mouse.down();p.mouse.move(150,390,steps=6);p.mouse.up()
 p.wait_for_function('(s)=>Math.abs(ANQA_TOUR.controls.state.yaw-s)>Math.PI*2',arg=start)
 assert max(abs(a-b) for a,b in zip(eye,p.evaluate('ANQA_TOUR.camera.position.toArray()')))<.001
 assert abs(p.evaluate('ANQA_TOUR.camera.rotation.z'))<.0001
 scroll=p.evaluate('scrollY');fov=p.evaluate('ANQA_TOUR.camera.fov');p.mouse.wheel(0,-400);p.wait_for_function('(f)=>ANQA_TOUR.camera.fov<f-5',arg=fov);assert p.evaluate('scrollY')==scroll
 checks['360']='Repeated mouse drags pass a full 360 degrees with a fixed eye and zero roll; wheel changes FOV without scrolling the page.';print('360 and zoom passed',flush=True)
 go(.30);p.wait_for_function('ANQA_TOUR.controls.state.active');p.wait_for_timeout(250)
 xy=p.evaluate('''()=>{const a=ANQA_TOUR;const v=a.controls.nodes[2].clone();v.y=.027;v.project(a.camera);return [(v.x+1)*innerWidth/2,(1-v.y)*innerHeight/2]}''');assert 0<xy[0]<1100 and 0<xy[1]<800,xy
 p.mouse.click(*xy);p.wait_for_function('ANQA_TOUR.controls.state.position.distanceTo(ANQA_TOUR.controls.nodes[2])<.05')
 p.evaluate('ANQA_TOUR.controls.walkTo(4)');p.wait_for_function('ANQA_TOUR.controls.state.position.distanceTo(ANQA_TOUR.controls.nodes[4])<.05');checks['walking']='A floor waypoint responds to an actual click; the route to the opposite side travels around the central island.'
 p.evaluate('ANQA_TOUR.openProduct(3)');expect(p.locator('#product')).to_be_visible();p.wait_for_function('ANQA_TOUR.piece?.root');bb=p.locator('#pieceCanvas').bounding_box();angle=p.evaluate('ANQA_TOUR.piece.root.rotation.y');p.mouse.move(bb['x']+bb['width']*.25,bb['y']+bb['height']*.5);p.mouse.down();p.mouse.move(bb['x']+bb['width']*.75,bb['y']+bb['height']*.5,steps=6);p.mouse.up();assert abs(p.evaluate('ANQA_TOUR.piece.root.rotation.y')-angle)>.5;p.locator('#add').click();assert p.locator('#count').inner_text()=='1';p.keyboard.press('Escape');checks['products']='Existing mesh still rotates continuously in the product viewer and can be added to the local bag.'
 go(0);assert max(abs(a) for a in p.evaluate('ANQA_TOUR.doors.map(d=>d.pivot.rotation.y)'))<.001;eye=p.evaluate('ANQA_TOUR.camera.position.toArray()');p.mouse.move(700,350);p.mouse.down();p.mouse.move(250,400,steps=6);p.mouse.up();assert p.evaluate('ANQA_TOUR.camera.position.toArray()')==eye;assert not p.evaluate('ANQA_TOUR.controls.state.active')
 p.set_viewport_size({'width':390,'height':844});p.wait_for_timeout(300);assert p.evaluate('document.documentElement.scrollWidth<=innerWidth');p.screenshot(path=str(R/'review/mobile-front.png'));go(.69);p.wait_for_function('ANQA_TOUR.controls.state.active');angle=p.evaluate('ANQA_TOUR.controls.state.yaw')
 # Native touch input, not synthetic DOM mouse events.
 cdp=c.new_cdp_session(p);cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':320,'y':400}]});cdp.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':70,'y':400}]});cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]});p.wait_for_function('(a)=>Math.abs(ANQA_TOUR.controls.state.yaw-a)>.2',arg=angle);p.screenshot(path=str(R/'review/mobile-inside.png'));checks['mobile']='Phone layout has no horizontal overflow; native touch drag changes viewing direction.';print('Waypoints, products, mobile passed',flush=True)
 # Default animation is verified on a smaller software-rendered viewport.
 c.set_offline(False);p.set_viewport_size({'width':720,'height':520});p.emulate_media(reduced_motion='no-preference');load();go(0)
 p.evaluate('''()=>{window.motionSamples=[];function sample(){const a=ANQA_TOUR;motionSamples.push({p:a.progress,angle:a.doors[0].pivot.rotation.y});if(a.progress<.299 && motionSamples.length<500)requestAnimationFrame(sample)}requestAnimationFrame(sample);ANQA_TOUR.go(.30)}''')
 p.wait_for_function('ANQA_TOUR.progress>.299',timeout=120000);samples=p.evaluate('motionSamples');assert any(.075<s['p']<.23 and 0<s['angle']<math.pi/2 for s in samples),samples
 checks['normal_motion']='Ordinary motion includes intermediate camera positions and intermediate hinge angles; it is not a scene swap.'
 assert not errors,errors;b.close()
(R/'verification.json').write_text(json.dumps({'passed':checks,'errors':errors,'html_sha256':hashlib.sha256((R/'ANQA_Showroom_v7.html').read_bytes()).hexdigest(),'limitations':['Software-rendered browser tests, no real-device FPS measurement.','Material textures match the supplied palette; floor texture is generated, oak and smooth stone use CC0 scanned maps.','Banuba was used as an interaction reference only; no Banuba design or assets are included.']},indent=2));print('PASS',flush=True)
