from pathlib import Path
from playwright.sync_api import sync_playwright
import json,hashlib,math,zipfile
R=Path(__file__).parent;errors=[]
with sync_playwright() as w:
 b=w.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--enable-unsafe-swiftshader']);p=b.new_page(viewport={'width':1100,'height':800},reduced_motion='reduce');p.set_default_timeout(90000);p.on('pageerror',lambda e:errors.append(str(e)));p.on('console',lambda e:errors.append(e.text) if e.type=='error' and '404' not in e.text else None)
 p.goto('http://127.0.0.1:8927/ANQA_Showroom_v7.html',timeout=120000);p.wait_for_function('window.ANQA_TOUR?.surfaceReady && ANQA_TOUR.architectureReady && ANQA_TOUR.productRoots.filter(Boolean).length===5',timeout=120000)
 assert p.locator('#world').evaluate('(e)=>getComputedStyle(e).filter')=='none'
 assert p.evaluate("ANQA_TOUR.surfaces.textures['oak-color.jpg'].image.width")==4096
 assert p.evaluate("ANQA_TOUR.entrance.topGlass.material.opacity")<=.04
 clear=p.evaluate('''()=>ANQA_TOUR.doors.map(d=>{const bar=d.pivot.children[1];const width=bar.geometry.parameters.width;const edge=d.pivot.position.x+bar.position.x+(d.side<0?-width/2:width/2);return {top:d.pivot.children[4].position.y+d.pivot.children[4].geometry.parameters.height/2,gap:Math.abs(edge-(d.side*1.4-d.side*.016))}})''')
 assert all(2.659-v['top']>=.008 and v['gap']>.002 for v in clear),clear
 p.screenshot(path=str(R/'review/front.png'));print('Door clearances and clear glazing passed',flush=True)
 local=p.evaluate('ANQA_TOUR.doors.map(d=>d.pivot.children.map(m=>({p:m.position.toArray(),s:m.scale.toArray(),geometry:m.geometry.uuid})))')
 for v in [.12,.17,.24]:
  p.evaluate('(v)=>ANQA_TOUR.go(v)',v);p.wait_for_function('(v)=>Math.abs(ANQA_TOUR.progress-v)<.001',arg=v)
  assert p.evaluate('ANQA_TOUR.doors.every(d=>d.pivot.rotation.x===0 && d.pivot.rotation.z===0)')
  assert p.evaluate('ANQA_TOUR.doors.map(d=>d.pivot.children.map(m=>({p:m.position.toArray(),s:m.scale.toArray(),geometry:m.geometry.uuid})))')==local
 assert p.evaluate('ANQA_TOUR.camera.position.z')<4.995
 p.evaluate('ANQA_TOUR.go(.69)');p.wait_for_function('Math.abs(ANQA_TOUR.progress-.69)<.001 && ANQA_TOUR.controls.state.active');p.screenshot(path=str(R/'review/wall.png'))
 assert p.evaluate("ANQA_TOUR.surfaces.get('BlackSteel',true).metalness")>.7
 p.evaluate('ANQA_TOUR.controls.walkTo(4)');p.wait_for_function('ANQA_TOUR.controls.state.position.distanceTo(ANQA_TOUR.controls.nodes[4])<.05');p.evaluate('ANQA_TOUR.controls.resetLook();ANQA_TOUR.controls.state.targetYaw=-Math.PI/2;ANQA_TOUR.controls.state.targetPitch=.55;ANQA_TOUR.controls.state.targetFov=50');p.wait_for_function('Math.abs(ANQA_TOUR.camera.fov-50)<.1');p.screenshot(path=str(R/'review/metal-close.png'));print('PBR specular surfaces rendered without errors',flush=True)
 assert not errors,errors;b.close()
with zipfile.ZipFile(R/'ANQA_Showroom_v7.zip') as z:
 assert z.namelist()==['ANQA_Showroom_v7.html'];assert z.read(z.namelist()[0])==(R/'ANQA_Showroom_v7.html').read_bytes()
v=json.loads((R/'verification.json').read_text());v.setdefault('functional_test_html_sha256',v['html_sha256']);v['html_sha256']=hashlib.sha256((R/'ANQA_Showroom_v7.html').read_bytes()).hexdigest();v['passed']['final_quality']='No canvas blur filter; 4K oak loaded; clear upper glass; >8 mm head clearance and >2 mm hinge-side clearance; rigid door parts invariant through three opening poses; physical metal highlights render without shader errors; ZIP still contains one HTML.';v['post_suite_changes']=['Preserved live direct specular lighting; baked atlas supplies diffuse lighting only.','Adjusted door profiles for mechanical clearance; tour controls and product behavior unchanged.'];(R/'verification.json').write_text(json.dumps(v,indent=2));print('PASS',flush=True)
