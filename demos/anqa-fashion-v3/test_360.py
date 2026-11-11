from pathlib import Path
import urllib.request,hashlib,json,math
from playwright.sync_api import sync_playwright,expect
R=Path(__file__).parent
(R/'review').mkdir(exist_ok=True)
data=(R/'ANQA_v3.html').read_bytes()
(R/'review/published-v3.html').write_bytes(data)
checks=[]
with sync_playwright() as w:
 b=w.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--enable-unsafe-swiftshader']);c=b.new_context(viewport={'width':1440,'height':900});p=c.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.goto('http://127.0.0.1:8913/review/published-v3.html',wait_until='load');c.set_offline(True);p.wait_for_function('ANQA_DEBUG.engine?.products.filter(Boolean).length===5');p.locator('#exploreRail').click();p.wait_for_timeout(1200);p.locator('#openSelected').click();p.wait_for_function('ANQA_DEBUG.state.detail.value===1')
 def signature():return p.evaluate('''()=>{const root=ANQA_DEBUG.engine.detailRoot,parts=[];root.traverse(m=>{if(m.isMesh){const a=m.geometry.attributes.position;let sum=0;for(let i=0;i<a.array.length;i++)sum+=a.array[i]*(i%13+1);parts.push([m.uuid,a.count,sum,m.material.map?.uuid||null]);}});return {root:root.uuid,parts,scale:root.scale.toArray()}}''')
 for kind in ['product','model']:
  if kind=='model':p.locator('#modelToggle').click();p.wait_for_function('ANQA_DEBUG.engine.detailKey==="coal-model"');p.wait_for_timeout(400)
  before=signature();turn=p.locator('#turnArea');box=turn.bounding_box();y=box['y']+box['height']*.5;distance=2*math.pi/.0085
  for lap in range(2):
   p.wait_for_function('Math.abs(ANQA_DEBUG.state.rotation.value-ANQA_DEBUG.state.rotation.target)<0.0003');x=box['x']+25;p.mouse.move(x,y);p.mouse.down();start=p.evaluate('ANQA_DEBUG.state.rotation.value')
   for step in range(37):
    p.mouse.move(x+distance*step/36,y+math.sin(step*.3)*18);p.wait_for_timeout(14)
    pose=p.evaluate('ANQA_DEBUG.engine.detailRoot.rotation.toArray().slice(0,3)');assert abs(pose[0])<1e-12 and abs(pose[2])<1e-12,pose
   p.wait_for_timeout(100);actual=p.evaluate('ANQA_DEBUG.engine.detailRoot.rotation.y');assert abs(actual-start-2*math.pi)<.01,(actual,start);assert signature()==before
   p.mouse.up()
  # Pure vertical dragging leaves the yaw untouched and never introduces pitch/roll.
  p.wait_for_function('Math.abs(ANQA_DEBUG.state.rotation.value-ANQA_DEBUG.state.rotation.target)<0.0003');x=box['x']+box['width']*.5;p.mouse.move(x,y);p.mouse.down();start=p.evaluate('ANQA_DEBUG.state.rotation.value');p.mouse.move(x,y-120,steps=8);p.wait_for_timeout(100);pose=p.evaluate('ANQA_DEBUG.engine.detailRoot.rotation.toArray().slice(0,3)');assert abs(pose[1]-start)<1e-9 and pose[0]==pose[2]==0;p.mouse.up();assert signature()==before
  checks.append(kind+': two full 360° horizontal mouse drags preserve object identity, all vertex data, textures and scale; vertical dragging causes no tilt or rotation')
 assert not errors,errors;b.close()
p=R/'verification.json';v=json.loads(p.read_text());v['passed'].extend(checks);v['validated_html_sha256']=hashlib.sha256(data).hexdigest();p.write_text(json.dumps(v,indent=2));(R/'verification.json').write_text(p.read_text());print('\n'.join(checks))
