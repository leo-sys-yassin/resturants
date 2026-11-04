import json
from playwright.sync_api import sync_playwright
R='1f4996a9-3b3f-4ec1-baff-54df3f35bc65';W='22222222-2222-4222-8222-222222222222';O='33333333-3333-4333-8333-333333333333';T='44444444-4444-4444-8444-444444444444';S='55555555-5555-4555-8555-555555555555'
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);ctx=b.new_context(viewport={'width':390,'height':844},locale='en-US');pg=ctx.new_page();errors=[];pg.on('pageerror',lambda e:errors.append(str(e)));role='owner';sessions=[];waiters=[];draft=None;revision=0
 def route(r):
  global role,sessions,waiters,draft,revision
  url=r.request.url;method=r.request.method;body=r.request.post_data_json if r.request.post_data else None;data={}
  if '/auth/v1/token' in url: role='owner';data={'access_token':'owner-test'}
  elif url.endswith('/login'):role='waiter';data={'access_token':'waiter-test','restaurantId':R}
  elif url.endswith('/state'):data={'role':role,'userId':O if role=='owner' else W,'tables':[{'id':T,'number':1,'label':'','active':True}],'sessions':sessions,'waiters':waiters}
  elif url.endswith('/profile'):
   data={'role':role,'name':'Owner Test' if role=='owner' else 'Ali','username':'owner' if role=='owner' else 'ali','day':'2026-11-04','timezone':'Asia/Damascus','closedTables':3,'closedValueUSD':42,'openTables':0,'viewsToday':17,'staff':[],'series':[{'day':'2026-11-0'+str(n),'closed':n,'amount':n*10,'views':n*3} for n in range(1,8)]}
  elif url.endswith('/draft'):
   if method=='POST':draft=body['menu'];revision+=1
   data={'role':role,'menu':draft,'revision':revision}
  elif url.endswith('/catalog'):data={'config':{'nameEn':'EMBER','name':'إمبر','exchangeRate':12000},'groups':[],'products':[{'id':'burger','name':'برغر','en':'Burger','priceCurrency':'USD','priceAmount':5,'optionGroups':[]}]}
  elif url.endswith('/waiters') and method=='POST':waiters=[{'user_id':W,'username':body['username'],'display_name':body['name'],'active':True}];data={'id':W}
  elif url.endswith('/action'):
   action=body['action'];d=body['data']
   if action=='open':sessions=[{'id':S,'table_id':T,'waiter_id':W,'guests':d['guests'],'opened_at':'2026-11-04T12:00:00Z','revision':1,'basket':[],'feedbackToken':'a'*64}];data=sessions[0]
   elif action=='save':
    data={**sessions[0],'revision':sessions[0]['revision']+1,'guests':d['guests'],'basket':[{**l,'name':'برغر','nameEn':'Burger','unitUSD':5} for l in d['basket']]};sessions=[data]
   elif action=='close':sessions=[];data={'ok':True}
   else:data={'ok':True}
  elif url.endswith('/feedback') or url.endswith('/history'):data=[]
  r.fulfill(status=200,content_type='application/json',body=json.dumps(data))
 ctx.route('https://sewhqpwncbfbtaswejoy.supabase.co/**',route)
 pg.goto('http://127.0.0.1:8804/staff',wait_until='networkidle');pg.locator('#ownerMode').click();pg.locator('[name=user]').fill('owner@example.com');pg.locator('[name=password]').fill('test-password');pg.locator('#loginForm button[type=submit], #loginForm button.primary').click();pg.wait_for_selector('.dashboard-metrics');assert '17' in pg.locator('.dashboard-metrics').inner_text();assert pg.locator('.chart-column').count()==21
 for width in [360,768,1024,1440]:
  pg.set_viewport_size({'width':width,'height':900});assert pg.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),width
 pg.screenshot(path='/workspace/output/EMBER-admin-dashboard.png');pg.set_viewport_size({'width':390,'height':844})
 pg.locator('[data-tab=profile]').click();pg.wait_for_selector('.profile-card');assert '@owner' in pg.locator('.profile-card').inner_text();assert '$42.00' in pg.locator('.profile-stats').first.inner_text()
 pg.locator('#editMenu').click();frame=pg.frame_locator('#menuStudio iframe');frame.locator('#adminDialog[open]').wait_for();assert frame.locator('#cloudLogin').count()==0;assert frame.locator('#cloudPublish').is_hidden();frame.locator('[data-admin-tab=restaurant]').click();frame.locator('#rNameEn').fill('EMBER Tested');frame.locator('#restaurantForm button[type=submit]').click();frame.locator('#adminStatus').filter(has_text='saved').wait_for();assert draft['config']['nameEn']=='EMBER Tested';assert revision==1;__import__('pathlib').Path('/tmp/workspace-menu-save.json').write_text(json.dumps(draft))
 pg.locator('#returnWorkspace').click();pg.wait_for_selector('#menuStudio',state='detached');assert pg.locator('#loginForm').count()==0
 pg.locator('[data-tab=waiters]').click();pg.locator('[name=name]').fill('Ali');pg.locator('[name=username]').fill('ali');pg.locator('#generateCode').click();assert len(pg.locator('#newAccessCode').input_value())>=12;pg.locator('#waiterForm button.primary').click();pg.wait_for_selector('[data-toggle-waiter]');pg.locator('#logout').click()
 pg.locator('[name=user]').fill('ali');pg.locator('[name=password]').fill('test-secret-code');pg.locator('#loginForm button.primary').click();pg.wait_for_selector('[data-table]');assert pg.locator('[data-tab=waiters]').count()==0;assert pg.locator('[data-tab=feedback]').count()==0
 assert pg.locator('[data-tab=overview]').count()==0;assert pg.locator('#editMenu').count()==0;pg.locator('[data-tab=profile]').click();pg.wait_for_selector('.profile-card');assert '@ali' in pg.locator('.profile-card').inner_text();pg.locator('[data-tab=tables]').click()
 pg.locator('[data-table]').click();pg.locator('[name=guests]').fill('3');pg.locator('#openTableForm button.primary').click();pg.wait_for_selector('#productPicker');pg.locator('#productPicker').select_option('burger');pg.locator('#addLine [name=qty]').fill('2');pg.locator('#addLine button').click();assert '$10.00' in pg.locator('#basketTotal').inner_text();pg.locator('#saveSession').click();pg.wait_for_function("document.querySelector('#notice').textContent.includes('saved')")
 pg.locator('#sessionBack').click();pg.locator('#refresh').click();pg.locator('[data-table]').click();assert '$10.00' in pg.locator('#basketTotal').inner_text()
 pg.on('dialog',lambda d:d.accept());pg.locator('#closeSession').click();pg.wait_for_selector('[data-table]:not(.occupied)');pg.locator('[data-table]').click();pg.locator('#openTableForm button.primary').click();pg.wait_for_selector('#basketTotal');assert '$0.00' in pg.locator('#basketTotal').inner_text();pg.locator('#sessionBack').click()
 for w in [360,768,1024,1440]:
  pg.set_viewport_size({'width':w,'height':900});assert pg.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),w
 assert not errors,errors
 b.close();print('Owner dashboard charts and role-specific profiles; authenticated iframe draft save/return; waiter isolation; table lifecycle; desktop/tablet/mobile passed with mocked transport.')
