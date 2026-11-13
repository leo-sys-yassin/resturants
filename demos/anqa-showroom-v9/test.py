from pathlib import Path
from playwright.sync_api import sync_playwright,expect
import json,hashlib,math,zipfile,struct
R=Path(__file__).parent;errors=[];checks={}
with zipfile.ZipFile(R/'ANQA_Showroom_v9.zip') as z:
 assert z.namelist()==['ANQA_Showroom_v9.html'];assert z.read(z.namelist()[0])==(R/'ANQA_Showroom_v9.html').read_bytes()
layout=json.loads((R/'layout.json').read_text());assert sum(n.startswith('Matte black steel shoe shelf') for n in layout['objects'])==12;assert not any('spotlight' in n.lower() or 'spot lens' in n.lower() for n in layout['objects'])
bin=(R/'assets/architecture.glb').read_bytes();length=struct.unpack_from('<I',bin,12)[0];gltf=json.loads(bin[20:20+length]);batches=sum(len(m['primitives']) for m in gltf['meshes']);assert batches<=11
assert json.loads((R/'structure-verification.json').read_text())['exported_foundation_components_contact_floor']>=5
checks['static_scene']='12 matte black footwear shelves; LED channels instead of spotlight heads; warm beige plaster and walnut furniture; merged architectural batches.'
with sync_playwright() as w:
 b=w.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--enable-unsafe-swiftshader']);c=b.new_context(viewport={'width':800,'height':600},has_touch=True,reduced_motion='reduce');p=c.new_page();p.set_default_timeout(90000);p.on('pageerror',lambda e:errors.append(str(e)));p.on('console',lambda e:errors.append(e.text) if e.type=='error' and '404' not in e.text else None)
 def load():
  p.goto('http://127.0.0.1:8929/ANQA_Showroom_v9.html',timeout=120000);p.wait_for_function('window.ANQA_TOUR?.surfaceReady && ANQA_TOUR.architectureReady && ANQA_TOUR.streetReady && ANQA_TOUR.labelsReady && ANQA_TOUR.productRoots.filter(Boolean).length===5',timeout=120000)
 def go(v):
  p.evaluate('(v)=>ANQA_TOUR.go(v)',v);p.wait_for_function('(v)=>Math.abs(ANQA_TOUR.progress-v)<.001',arg=v)
 load();c.set_offline(True);print('Ready offline',flush=True)
 assert p.evaluate('ANQA_TOUR.scene.getObjectsByProperty("isSpotLight",true).length')==0
 assert not p.evaluate('ANQA_TOUR.renderer.shadowMap.enabled')
 assert p.evaluate('ANQA_TOUR.entrance.stone.geometry.groups.length')==2
 assert p.evaluate("ANQA_TOUR.surfaces.get('BlackSteel').roughness")>=.9
 assert p.evaluate("ANQA_TOUR.surfaces.get('BlackSteel').metalness")<=.15
 assert p.evaluate("ANQA_TOUR.entrance.lining.material.userData.surface")=='WalnutSurface'
 assert p.evaluate('ANQA_TOUR.interiorLabels.items.filter(m=>m.userData.labelKind==="category").every(m=>m.position.y>3.05)')
 assert p.locator('#world').evaluate('(e)=>getComputedStyle(e).filter')=='none'
 p.screenshot(path=str(R/'review/front.png'))
 rigid=p.evaluate('ANQA_TOUR.doors.map(d=>d.pivot.children.map(c=>[c.geometry.uuid,c.position.toArray(),c.scale.toArray()]))')
 for v in [.12,.17,.24]:
  go(v);assert p.evaluate('ANQA_TOUR.doors.every(d=>d.pivot.rotation.x===0 && d.pivot.rotation.z===0)');assert p.evaluate('ANQA_TOUR.doors.map(d=>d.pivot.children.map(c=>[c.geometry.uuid,c.position.toArray(),c.scale.toArray()]))')==rigid
 assert p.evaluate('ANQA_TOUR.camera.position.z')<4.995
 # Hinged leaves swing outside: both glazing centroids advance to exterior +Z.
 assert p.evaluate('''()=>{ANQA_TOUR.scene.updateMatrixWorld(true);return ANQA_TOUR.doors.every(d=>d.pivot.children.find(m=>m.name==='Rigid flat door glazing').getWorldPosition(ANQA_TOUR.camera.position.clone()).z>5.5)}''')
 # Upper porch step is 35mm above datum. Both leaves clear it by at least 5mm.
 assert p.evaluate('''()=>{ANQA_TOUR.scene.updateMatrixWorld(true);return ANQA_TOUR.doors.every(d=>d.pivot.children.every(m=>{const a=m.geometry.attributes.position,v=ANQA_TOUR.camera.position.clone();for(let i=0;i<a.count;i++){v.fromBufferAttribute(a,i).applyMatrix4(m.matrixWorld);if(v.y<.0399)return false}return true}))}''')
 assert json.loads((R/'ceiling-verification.json').read_text())['matches_v8_exactly']
 checks['doors']='Rigid outward-opening doors with fixed hinges through three poses; both leaf centres swing toward exterior +Z; camera passes through the actual opening; both frames clear the 35mm porch step.'
 checks['ceiling']='Exact v8 geometry, transforms, light positions, counts and light properties verified from Blender source scenes.'
 assert p.evaluate('ANQA_TOUR.camera.fov')==66
 go(.38);p.screenshot(path=str(R/'review/footwear.png'));go(.53);p.screenshot(path=str(R/'review/branding.png'));go(.69);p.wait_for_function('ANQA_TOUR.controls.state.active');p.screenshot(path=str(R/'review/interior.png'));print('Materials, labels, doors passed',flush=True)
 eye=p.evaluate('ANQA_TOUR.camera.position.toArray()');start=p.evaluate('ANQA_TOUR.controls.state.yaw')
 for _ in range(6):
  p.mouse.move(700,300);p.mouse.down();p.mouse.move(100,300,steps=4);p.mouse.up()
 p.wait_for_function('(s)=>ANQA_TOUR.controls.state.yaw-s < -Math.PI*2',arg=start)
 assert p.evaluate('ANQA_TOUR.camera.position.toArray()')==eye
 scroll=p.evaluate('scrollY');fov=p.evaluate('ANQA_TOUR.camera.fov');p.mouse.wheel(0,-400);p.wait_for_function('(f)=>ANQA_TOUR.camera.fov<f-5',arg=fov);assert p.evaluate('scrollY')==scroll
 checks['look']='Full 360 yaw with the reference drag direction and no camera orbit; wheel zoom leaves page scroll unchanged.'
 # Only simple proxies participate in frequent interaction ray tests.
 assert p.evaluate('ANQA_TOUR.interactionObjects.filter(m=>m.userData.product!==undefined).every(m=>m.name==="Product interaction proxy" && m.parent===ANQA_TOUR.productRoots[m.userData.product])')
 tris=p.evaluate('ANQA_TOUR.interactionObjects.reduce((s,m)=>s+(m.geometry.index?m.geometry.index.count:m.geometry.attributes.position.count)/3,0)');assert tris<1000
 # Look down to an actually visible near waypoint, avoiding clicks through the island.
 go(.30);p.wait_for_function('ANQA_TOUR.controls.state.active');p.mouse.move(400,320);p.mouse.down();p.mouse.move(400,180,steps=4);p.mouse.up();p.wait_for_function('ANQA_TOUR.controls.state.pitch<-.15')
 xy=p.evaluate('''()=>{const a=ANQA_TOUR,v=a.controls.nodes[1].clone();v.y=.027;v.project(a.camera);return [(v.x+1)*innerWidth/2,(1-v.y)*innerHeight/2]}''');assert 0<xy[0]<800 and 0<xy[1]<500,xy
 p.mouse.click(*xy);p.wait_for_function('ANQA_TOUR.controls.state.position.distanceTo(ANQA_TOUR.controls.nodes[1])<.05');assert p.locator('#location').inner_text()=='رفوف الأحذية'
 p.evaluate('ANQA_TOUR.controls.walkTo(4)');p.wait_for_function('ANQA_TOUR.controls.state.position.distanceTo(ANQA_TOUR.controls.nodes[4])<.05');assert p.locator('#location').inner_text()=='مجموعة الملابس'
 checks['walking']='Actual visible waypoint click works; paths go around the island; HUD follows manual destinations.'
 go(.69);p.wait_for_function('ANQA_TOUR.controls.state.active');xy=p.evaluate('''()=>{const a=ANQA_TOUR,v=a.productRoots[3].position.clone().project(a.camera);return [(v.x+1)*innerWidth/2,(1-v.y)*innerHeight/2]}''');p.mouse.move(*xy);p.wait_for_function('ANQA_TOUR.hovered===3');p.mouse.click(*xy);expect(p.locator('#product')).to_be_visible();p.wait_for_function('ANQA_TOUR.piece?.root');pc=p.locator('#pieceCanvas').bounding_box();old=p.evaluate('ANQA_TOUR.piece.root.rotation.y');p.mouse.move(pc['x']+pc['width']*.2,pc['y']+pc['height']*.5);p.mouse.down();p.mouse.move(pc['x']+pc['width']*.8,pc['y']+pc['height']*.5,steps=6);p.mouse.up();assert abs(p.evaluate('ANQA_TOUR.piece.root.rotation.y')-old)>.5;p.locator('#add').click();assert p.locator('#count').inner_text()=='1';p.keyboard.press('Escape')
 checks['products']='An actual proxy hit opens the garment; its mesh rotates continuously and can be added to the local bag.';print('360, walking, product proxy passed',flush=True)
 go(.30);p.wait_for_function('ANQA_TOUR.controls.state.active');p.evaluate('ANQA_TOUR.controls.resetLook();ANQA_TOUR.controls.state.targetYaw=Math.PI;ANQA_TOUR.controls.state.targetPitch=-.05');p.wait_for_function('Math.abs(ANQA_TOUR.controls.state.yaw-Math.PI)<.01');p.screenshot(path=str(R/'review/street-view.png'));calls=p.evaluate('ANQA_TOUR.frameStats.calls');assert calls<80,calls
 # No animation/render loop remains active once the view settles.
 p.wait_for_timeout(500);idle=p.evaluate('ANQA_TOUR.frameStats.renders');p.wait_for_timeout(400);assert p.evaluate('ANQA_TOUR.frameStats.renders')==idle
 checks['rendering']={'architecture_batches':batches,'interaction_triangles':tris,'street_view_draw_calls':calls,'live_shadow_maps':False,'idle_render_loop':False}
 # Review all four wall directions from the same clear aisle, preserving view controls.
 go(.30);p.wait_for_function('ANQA_TOUR.controls.state.active')
 for angle,name in [(0,'wall-back'),(math.pi/2,'wall-left'),(math.pi,'wall-front'),(-math.pi/2,'wall-right')]:
  p.evaluate('(a)=>{ANQA_TOUR.controls.state.targetYaw=a;ANQA_TOUR.controls.state.targetPitch=0;ANQA_TOUR.controls.resetLook();ANQA_TOUR.controls.state.targetYaw=a}',angle);p.wait_for_function('(a)=>Math.abs(ANQA_TOUR.controls.state.yaw-a)<.01',arg=angle);p.screenshot(path=str(R/'review'/f'{name}.png'))
 assert p.evaluate('ANQA_TOUR.camera.fov')==66
 checks['four_walls']='Four directional browser screenshots captured; repeating the same stop retains control and reset preserves the wider FOV.'
 go(0);p.set_viewport_size({'width':390,'height':844});p.wait_for_timeout(250);assert p.evaluate('document.documentElement.scrollWidth<=innerWidth');p.screenshot(path=str(R/'review/mobile-front.png'));go(.69);p.wait_for_function('ANQA_TOUR.controls.state.active');before=p.evaluate('ANQA_TOUR.controls.state.yaw');cdp=c.new_cdp_session(p);cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':320,'y':400}]});cdp.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':70,'y':400}]});cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]});p.wait_for_function('(a)=>ANQA_TOUR.controls.state.yaw<a-.2',arg=before);p.screenshot(path=str(R/'review/mobile-interior.png'));checks['mobile']='Native touch drag and narrow layout work offline without overflow.'
 # Normal-motion entry and the final turn do not jump or roll through a zero-length look vector.
 c.set_offline(False);p.set_viewport_size({'width':720,'height':520});p.emulate_media(reduced_motion='no-preference');load();go(0)
 p.evaluate('''()=>{window.motionSamples=[];function sample(){const a=ANQA_TOUR;motionSamples.push({p:a.progress,angle:a.doors[0].pivot.rotation.y,roll:a.camera.rotation.z});if(a.progress<.299&&motionSamples.length<500)requestAnimationFrame(sample)}requestAnimationFrame(sample);ANQA_TOUR.go(.30)}''');p.wait_for_function('ANQA_TOUR.progress>.299',timeout=120000);samples=p.evaluate('motionSamples');assert any(.075<s['p']<.23 and -math.pi/2<s['angle']<0 for s in samples);assert max(abs(s['roll']) for s in samples)<.0001
 p.evaluate('ANQA_TOUR.go(.94)');p.wait_for_function('ANQA_TOUR.progress>.939',timeout=120000);p.evaluate('''()=>{window.turnSamples=[];function sample(){turnSamples.push(ANQA_TOUR.camera.rotation.y);if(ANQA_TOUR.progress<.999&&turnSamples.length<500)requestAnimationFrame(sample)}requestAnimationFrame(sample);ANQA_TOUR.go(1)}''');p.wait_for_function('ANQA_TOUR.progress>.999',timeout=120000);angles=p.evaluate('turnSamples');assert len(angles)>2;assert max(abs(b-a) for a,b in zip(angles,angles[1:]))<1.2
 checks['normal_motion']='Outward entry has intermediate door angles and no roll; the exit turn interpolates yaw continuously.';assert not errors,errors;b.close()
(R/'verification.json').write_text(json.dumps({'passed':checks,'errors':errors,'html_sha256':hashlib.sha256((R/'ANQA_Showroom_v9.html').read_bytes()).hexdigest(),'limitations':['Software Chromium tests; draw-call counts are structural measurements, not real-device FPS.','Opposite buildings are a photographic generated backdrop; the pavement, road and curbs are 3D.','Room illumination and resting garment shadows are baked; live LED area lights shade the interactive garments.']},indent=2));print('PASS',flush=True)
