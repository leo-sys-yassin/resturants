import json
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);ctx=b.new_context(viewport={'width':390,'height':844},locale='en-US');inbox=[];failure=0;errors=[]
 def route(r):
  global failure
  u=r.request.url;data={};status=200
  if u.endswith('/menu-feedback'):
   body=r.request.post_data_json
   if failure:status=failure
   else:inbox.append({'id':str(len(inbox)+1),'source':'menu','rating':body['rating'],'comment':body['comment'],'created_at':'2026-11-04T14:00:00Z'});status=201
  elif '/auth/v1/token' in u:data={'access_token':'owner-test'}
  elif u.endswith('/state'):data={'role':'owner','userId':'owner','tables':[],'sessions':[],'waiters':[]}
  elif u.endswith('/catalog'):data={'config':{'name':'أمبر','nameEn':'EMBER'},'products':[],'groups':[]}
  elif u.endswith('/profile'):data={'role':'owner','name':'Owner','username':'owner','day':'2026-11-04','timezone':'Asia/Damascus','closedTables':0,'closedValueUSD':0,'openTables':0,'viewsToday':0,'series':[],'staff':[]}
  elif u.endswith('/feedback'):data=inbox
  r.fulfill(status=status,content_type='application/json',body=json.dumps(data))
 ctx.route('https://sewhqpwncbfbtaswejoy.supabase.co/**',route);pg=ctx.new_page();pg.on('pageerror',lambda e:errors.append(str(e)));pg.goto('http://127.0.0.1:8804',wait_until='networkidle');pg.locator('#customerFeedback').click();pg.locator('.rating-options label').nth(4).click();comment='<img src=x onerror=alert(1)> Lovely food';pg.locator('#publicFeedbackForm textarea').fill(comment);pg.locator('#sendMenuFeedback').click();pg.wait_for_function("document.querySelector('#menuFeedbackStatus').textContent.includes('Thank you')");assert inbox[0]['comment']==comment;assert inbox[0]['rating']==5;pg.locator('#closeMenuFeedback').click()
 owner=ctx.new_page();owner.goto('http://127.0.0.1:8804/staff',wait_until='networkidle');owner.locator('#ownerMode').click();owner.locator('[name=user]').fill('owner@example.com');owner.locator('[name=password]').fill('password-example');owner.locator('#loginForm button.primary').click();owner.wait_for_selector('.dashboard-metrics');owner.locator('#toggleSidebar').click();owner.locator('[data-tab=feedback]').click();owner.wait_for_selector('.record');assert comment in owner.locator('.record').inner_text();assert 'customer menu' in owner.locator('.record').inner_text();assert owner.locator('.record img').count()==0
 # Failed writes must show a failure and allow a retry, never a success.
 failure=503;pg.locator('#customerFeedback').click();pg.locator('.rating-options label').nth(3).click();pg.locator('#sendMenuFeedback').click();pg.wait_for_function("document.querySelector('#menuFeedbackStatus').textContent.includes('Could not send')");assert pg.locator('#sendMenuFeedback').is_enabled();assert len(inbox)==1
 failure=0;pg.locator('#sendMenuFeedback').click();pg.wait_for_function("document.querySelector('#menuFeedbackStatus').textContent.includes('Thank you')");assert len(inbox)==2;owner.locator('#refresh').click();owner.wait_for_function("document.querySelectorAll('.record').length===2")
 for width in [360,768,1440]:
  pg.set_viewport_size({'width':width,'height':900});assert pg.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
 assert not errors,errors;b.close();print('Customer feedback persists to owner inbox; origin label/escaping, failure/retry, refresh and responsive dialog pass with shared mocked transport.')
