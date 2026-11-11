from playwright.sync_api import sync_playwright,expect
from pathlib import Path
import json,time,statistics
R=Path(__file__).parent;checks=[];errors=[];responses=[];metrics={}
with sync_playwright() as w:
 b=w.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--enable-unsafe-swiftshader']);c=b.new_context(viewport={'width':1440,'height':900});p=c.new_page();p.on('pageerror',lambda e:errors.append(str(e)));p.on('response',lambda r:responses.append(r.url) if r.status>=400 else None)
 p.goto('http://127.0.0.1:8913',wait_until='networkidle');p.wait_for_function('ANQA_DEBUG.engine?.hero && ANQA_DEBUG.engine.products.filter(Boolean).length===5');p.wait_for_timeout(1500);expect(p.locator('html')).to_have_attribute('lang','ar');expect(p.locator('#menuButton')).to_have_text('القائمة');assert p.evaluate('document.fonts.check("14px ANQAArabic")');assert not p.evaluate('ANQA_DEBUG.engine.rail.visible');p.screenshot(path=str(R/'review/hero-ar-final.png'))
 n=p.evaluate('ANQA_DEBUG.engine.stats.renders');p.wait_for_timeout(800);assert p.evaluate('ANQA_DEBUG.engine.stats.renders')==n
 checks.append('Arabic is the default; embedded Arabic font loads; idle rendering stops completely')
 p.locator('#languageButton').click();expect(p.locator('html')).to_have_attribute('dir','ltr');expect(p.locator('#menuButton')).to_have_text('MENU');p.screenshot(path=str(R/'review/hero-en-final.png'));p.locator('#exploreRail').click();p.wait_for_timeout(1800)
 p.wait_for_function('ANQA_DEBUG.state.scroll.value===ANQA_DEBUG.state.scroll.target');hook=p.evaluate('ANQA_DEBUG.engine.hookError()');metrics['max_hook_gap_pixels']=max(hook)*900/10;assert metrics['max_hook_gap_pixels']<1,hook;p.screenshot(path=str(R/'review/rail-final.png'))
 p.evaluate('''()=>{window.anqaFrameTimes=[];window.anqaDrawTimes=[];const e=ANQA_DEBUG.engine,old=e.draw.bind(e);e.draw=()=>{const t=performance.now();old();anqaDrawTimes.push(performance.now()-t);anqaFrameTimes.push(t)}}''')
 p.mouse.move(720,430);p.mouse.down()
 for i in range(50):p.mouse.move(720-i*6.2,430);p.wait_for_timeout(17)
 p.mouse.up();p.wait_for_timeout(1500);expect(p.locator('#captionMeta')).to_contain_text('Wine');timing=p.evaluate('({frames:anqaFrameTimes,drawTimes:anqaDrawTimes})');durations=timing['drawTimes'];metrics['rail_render_cpu_ms_p95']=sorted(durations)[int(len(durations)*.95)];intervals=[y-x for x,y in zip(timing['frames'],timing['frames'][1:]) if 1<y-x<2000];metrics['software_gpu_frame_interval_ms_median']=statistics.median(intervals);p.locator('#railPrev').click();p.wait_for_timeout(1500)
 p.wait_for_function('ANQA_DEBUG.state.sway.every(v=>v===0)');p.mouse.move(650,400);p.mouse.move(690,450,steps=8);assert p.evaluate('ANQA_DEBUG.state.sway.every(v=>v===0)')
 checks.append('Rail drag, selection and quiet sway work; all hook contact gaps stay below one screen pixel')
 p.locator('[data-product="0"]').click(position={'x':170,'y':200});p.wait_for_timeout(1100);expect(p.locator('#detailShell')).to_be_visible();p.wait_for_function('ANQA_DEBUG.engine.detailKey==="coal-product"');p.screenshot(path=str(R/'review/detail-final.png'))
 def signature():return p.evaluate('''()=>{const r=ANQA_DEBUG.engine.detailRoot,meshes=[];r.traverse(m=>{if(m.isMesh&&m.geometry.attributes.position.count>1000){const a=m.geometry.attributes.position;let sum=0;for(let i=0;i<a.array.length;i++)sum+=a.array[i]*(i%7+1);meshes.push([m.uuid,a.count,a.version,sum,m.material.map?.uuid,m.morphTargetInfluences?.length||0]);}});return {scale:r.scale.toArray(),meshes}}''')
 def rotate_drag():
  box=p.locator('#turnArea').bounding_box();x=box['x']+70;y=box['y']+box['height']*.55;p.mouse.move(x,y);p.mouse.down();angles=[]
  for i in range(65):p.mouse.move(x+i*8,y);p.wait_for_timeout(16);angles.append(p.evaluate('ANQA_DEBUG.engine.detailRoot.rotation.y'))
  p.mouse.up();p.wait_for_timeout(600);assert len(set(round(a,3) for a in angles))>45
 p.wait_for_function('ANQA_DEBUG.state.detail.value===1');a=signature();rotate_drag();assert signature()==a;assert all(m[-1]==0 for m in a['meshes']);checks.append('Garment rotation changes only the rigid 3D transform: vertex data, scale and texture remain identical; no morph targets')
 p.locator('#modelToggle').click();p.wait_for_function('ANQA_DEBUG.engine.detailKey==="coal-model"');p.wait_for_timeout(700);p.wait_for_function('ANQA_DEBUG.state.detail.value===1');a=signature();rotate_drag();assert signature()==a;checks.append('Human rotation preserves the same geometry, scale and fixed surface texture throughout the drag')
 p.locator('#turnArea').focus();p.keyboard.press('Home');p.wait_for_timeout(900)
 for _ in range(12):p.keyboard.press('ArrowRight')
 p.wait_for_timeout(900);assert abs(float(p.locator('#rotationAngle').inner_text().replace('°',''))-180)<1;p.screenshot(path=str(R/'review/model-back-final.png'))
 p.locator('[data-variant="1"]').click();p.wait_for_function('ANQA_DEBUG.engine.detailKey==="wine-model"');expect(p.locator('#colorName')).to_have_text('Wine');assert '180' in p.locator('#rotationAngle').inner_text()
 p.locator('[data-size="L"]').click();p.locator('#qtyPlus').click();p.locator('#addToBag').click();p.locator('#bagButton').click();expect(p.locator('#bagTotal')).to_have_text('$168');expect(p.locator('#bagCount')).to_have_text('2');p.locator('#reviewBag').click();expect(p.locator('#infoTitle')).to_have_text('Your selection.');p.keyboard.press('Escape');p.locator('#inlineSize').click();expect(p.locator('tbody tr')).to_have_count(5);p.keyboard.press('Escape');p.locator('#languageButton').click();expect(p.locator('#detailName')).to_have_text('هودي أساسي');p.screenshot(path=str(R/'review/detail-ar-final.png'));p.locator('#bagButton').click();expect(p.locator('#drawerTitle')).to_have_text('حقيبتك');expect(p.locator('#drawerContent h3')).to_have_text('هودي أساسي');p.keyboard.press('Escape');p.locator('#detailBack').click();p.wait_for_timeout(1800)
 for i,key in enumerate(['coal','wine','oat','forest','sky']):
  p.locator(f'[data-open="{i}"]').click();p.wait_for_timeout(900)
  for kind in ['product','model']:
   if kind=='model':p.locator('#modelToggle').click()
   p.wait_for_function('(id)=>ANQA_DEBUG.engine.detailKey===id',arg=key+'-'+kind);p.locator('#turnArea').focus();p.keyboard.press('ArrowRight');p.wait_for_timeout(400);assert p.evaluate('ANQA_DEBUG.engine.detailRoot.rotation.y')>0
  p.locator('#closeDetail').click();p.wait_for_timeout(1000)
 checks.append('All ten models work; Arabic/English details, colours, sizes, quantity, bag total, size guide and back navigation passed')
 p.locator('#searchButton').click();p.locator('#searchInput').fill('سماوي');expect(p.locator('.search-result')).to_have_count(1);p.locator('.search-result').click();p.wait_for_timeout(800);expect(p.locator('#detailName')).to_have_text('تيشيرت يومي');p.keyboard.press('Escape');p.wait_for_timeout(900);p.reload(wait_until='networkidle');expect(p.locator('html')).to_have_attribute('lang','ar');expect(p.locator('#bagCount')).to_have_text('2')
 for width,height in [(1280,800),(1440,900),(1920,1080)]:
  p.set_viewport_size({'width':width,'height':height});p.evaluate('window.scrollTo({top:0,behavior:"instant"})');p.wait_for_timeout(700);assert p.evaluate('document.documentElement.scrollWidth<=innerWidth');p.locator('#exploreRail').click();p.wait_for_timeout(1700);p.locator('#openSelected').click();p.wait_for_timeout(1000);p.locator('#modelToggle').click();p.wait_for_timeout(600)
  card=p.locator('#detailCard').bounding_box();controls=p.locator('#visualControls').bounding_box();assert card['x']>controls['x']+controls['width'];assert card['y']+card['height']<height;assert controls['y']+controls['height']<height;p.screenshot(path=str(R/f'review/desktop-{width}.png'));p.locator('#detailBack').click();p.wait_for_timeout(1800)
 checks.append('Arabic search, language/cart persistence, keyboard rotation, and layouts at 1280×800, 1440×900, 1920×1080 passed')
 assert not errors,errors;assert not responses,responses;b.close()
(R/'verification.json').write_text(json.dumps({'passed':checks,'metrics':metrics,'browser_errors':errors,'failed_responses':responses},indent=2));print(json.dumps({'checks':checks,'metrics':metrics},indent=2))
