from pathlib import Path
from playwright.sync_api import sync_playwright
R=Path(__file__).parent
with sync_playwright() as w:
 b=w.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--enable-unsafe-swiftshader']);p=b.new_page(viewport={'width':1100,'height':800},reduced_motion='reduce');p.set_default_timeout(90000);p.on('pageerror',lambda e:print('ERROR',e,flush=True));p.on('console',lambda e:print('CONSOLE',e.text[:1200],flush=True) if e.type=='error' else None);p.goto('http://127.0.0.1:8928/ANQA_Showroom_v8.html',timeout=120000);p.wait_for_function('window.ANQA_TOUR?.surfaceReady && ANQA_TOUR.architectureReady && ANQA_TOUR.streetReady && ANQA_TOUR.labelsReady && ANQA_TOUR.productRoots.filter(Boolean).length===5',timeout=120000);print('Ready',flush=True)
 for progress,name in [(0,'front'),(.38,'footwear'),(.69,'interior')]:
  p.evaluate('(v)=>ANQA_TOUR.go(v)',progress);p.wait_for_function('(v)=>Math.abs(ANQA_TOUR.progress-v)<.001',arg=progress);p.wait_for_timeout(250);p.screenshot(path=str(R/'review'/f'{name}.png'));print(name,flush=True)
 p.evaluate('ANQA_TOUR.go(.30)');p.wait_for_function('Math.abs(ANQA_TOUR.progress-.30)<.001 && ANQA_TOUR.controls.state.active');p.evaluate('ANQA_TOUR.controls.resetLook();ANQA_TOUR.controls.state.targetYaw=Math.PI;ANQA_TOUR.controls.state.targetPitch=-.05');p.wait_for_timeout(500);p.screenshot(path=str(R/'review/street-view.png'));print('street',flush=True);print(p.evaluate('JSON.stringify(ANQA_TOUR.frameStats)'),flush=True);b.close()
