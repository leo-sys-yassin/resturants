import json,time
from playwright.sync_api import sync_playwright
R='1f4996a9-3b3f-4ec1-baff-54df3f35bc65'
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);ctx=b.new_context(viewport={'width':390,'height':844},locale='en-US');calls={};role='owner';failure=False;errors=[]
 def route(r):
  global role
  path=r.request.url.split('?')[0].split('/')[-1];calls[path]=calls.get(path,0)+1;status=200;data={}
  if path=='token':role='owner';data={'access_token':'owner-test'}
  elif path=='login':role='waiter';data={'access_token':'waiter-test','restaurantId':R}
  elif path=='bootstrap':data={'state':{'role':role,'userId':role,'tables':[],'sessions':[],'waiters':[]},'catalog':{'config':{'name':'أمبر','nameEn':'EMBER'},'products':[],'groups':[]},'profile':{'role':role,'name':'Owner' if role=='owner' else 'Ali','username':role,'day':'2026-11-04','timezone':'Asia/Damascus','closedTables':4,'closedValueUSD':28,'openTables':0,'viewsToday':10,'series':[],'staff':[]}}
  elif path=='feedback':
   if failure:status=503
   data=[{'source':'menu','rating':5,'comment':'Private owner feedback','created_at':'2026-11-04T14:00:00Z'}]
  elif path in ('history','history-summary'):data=[]
  r.fulfill(status=status,content_type='application/json',body=json.dumps(data))
 ctx.route('https://sewhqpwncbfbtaswejoy.supabase.co/**',route)
 ctx.add_init_script("const originalFetch=window.fetch;window.fetch=(...a)=>String(a[0]).includes('/functions/v1/')&&(!a[1]?.method||a[1].method==='GET')?new Promise(r=>setTimeout(r,900)).then(()=>originalFetch(...a)):originalFetch(...a)")
 pg=ctx.new_page();pg.on('pageerror',lambda e:errors.append(str(e)));pg.goto('http://127.0.0.1:8804/staff',wait_until='networkidle');pg.locator('#ownerMode').click();pg.locator('[name=user]').fill('owner@example.com');pg.locator('[name=password]').fill('owner-password');pg.locator('#loginForm button.primary').click();pg.wait_for_selector('.dashboard-metrics');assert calls.get('bootstrap')==1;assert calls.get('state',0)==0;assert calls.get('catalog',0)==0;assert pg.locator('[data-tab=profile]').count()==0
 def select(tab):
  pg.locator('#toggleSidebar').click();pg.locator('[data-tab='+tab+']').click()
 select('feedback');pg.wait_for_selector('.record');timings=[]
 for _ in range(3):
  pg.locator('#toggleSidebar').click();start=time.perf_counter();pg.locator('[data-tab=overview]').click();pg.wait_for_selector('.dashboard-metrics');timings.append((time.perf_counter()-start)*1000)
  pg.locator('#toggleSidebar').click();start=time.perf_counter();pg.locator('[data-tab=feedback]').click();pg.wait_for_selector('.record');timings.append((time.perf_counter()-start)*1000)
 assert max(timings)<400,timings;assert calls.get('profile',0)==0,calls
 # Revalidation must leave cached content visible when the network fails.
 failure=True;pg.evaluate("const clock=Date.now;Date.now=()=>clock()+4000");select('overview');select('feedback');assert 'Private owner feedback' in pg.locator('#content').inner_text();pg.wait_for_function("document.querySelector('#notice').textContent.includes('last available data')");assert pg.locator('.record').count()==1
 # An older response cannot repopulate private state after logout/new account.
 failure=False;select('overview');select('feedback');pg.locator('#toggleSidebar').click();pg.locator('#logout').click();pg.locator('[name=user]').fill('ali');pg.locator('[name=password]').fill('waiter-password');pg.locator('#loginForm button.primary').click();pg.wait_for_selector('[data-tab=tables]');pg.wait_for_timeout(1100);assert pg.locator('[data-tab=feedback]').count()==0;assert 'Private owner feedback' not in pg.locator('#workspace').inner_text();assert pg.locator('[data-tab=profile]').count()==0
 assert not errors,errors;print('900 ms delayed network: cached navigation ms=',[round(n) for n in timings],'; requests=',calls,'; stale-data error and logout isolation pass');b.close()
