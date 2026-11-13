from pathlib import Path
from playwright.sync_api import sync_playwright
r=Path(__file__).parent
with sync_playwright() as w:
 b=w.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--enable-unsafe-swiftshader']);p=b.new_page(viewport={'width':1000,'height':760},reduced_motion='reduce');p.goto('http://127.0.0.1:8930/ANQA_Showroom_v10.html',timeout=120000);p.wait_for_function('window.ANQA_TOUR?.architectureReady && ANQA_TOUR.surfaceReady && ANQA_TOUR.labelsReady && ANQA_TOUR.productRoots.filter(Boolean).length===5',timeout=120000)
 p.evaluate('ANQA_TOUR.go(.30)');p.wait_for_function('ANQA_TOUR.controls.state.active')
 p.evaluate('''()=>{const a=ANQA_TOUR,s=a.controls.state,c=a.camera.clone();a.controls.walkTo(0);s.route=[];s.position.set(1.55,1.18,2.65);c.position.copy(s.position);c.lookAt(0,.39,.75);s.yaw=s.targetYaw=c.rotation.y;s.pitch=s.targetPitch=c.rotation.x;s.fov=s.targetFov=52;for(const id of ['tour','tip','tourlabel','intro','home','reset','bag','menu','progress']){const e=document.getElementById(id);if(e)e.style.visibility='hidden'}}''');p.wait_for_function('ANQA_TOUR.camera.fov===52');p.screenshot(path=str(r/'review/table-detail.png'));b.close();print('Table review captured')
