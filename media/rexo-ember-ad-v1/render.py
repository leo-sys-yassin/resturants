from pathlib import Path
import json,math,functools,subprocess
from PIL import Image,ImageDraw
import numpy as np
import render_v2 as v
R=Path(__file__).resolve().parent;A=R/'assets';O=R/'delivery';O.mkdir(exist_ok=True)
W,H,FPS,DURATION=1080,1920,30,53
C='#ece6d8';D='#101516';G='#35564f';GREEN='#1f7a68';B='#cbb5a0';ORANGE='#fa5116'
E=v.E;put=v.put;text=v.text;disk=v.disk;rr=v.rr
SC=[(0,4,'hook'),(4,7,'question'),(7,10,'rexo'),(10,16,'demo'),(16,22,'categories'),(22,25,'details'),(25,30,'options'),(30,35,'cart'),(35,39,'language'),(39,43,'identity'),(43,47,'hospitality'),(47,53,'end')]
TAPS=json.loads((A/'tap-coordinates.json').read_text())
@functools.lru_cache(100)
def asset(n):return Image.open(A/n).convert('RGBA')
@functools.lru_cache(100)
def sized(n,w,box=None):
 im=asset(n)
 if box:im=im.crop(box)
 return im.resize((w,round(im.height*w/im.width)),Image.Resampling.LANCZOS)
def title(im,tx,y,u,col=C,size=105,delay=0):
 q=E((u-delay)/.4);text(im,tx,540,y+40*(1-q),size,col,alpha=q,maxwidth=910)
def photo(im,n,x,y,w,u=1):put(im,sized(n,w),x,y+85*(1-E(u/.6)),alpha=E(u/.4))
def shot(im,n,w,cx,cy,box=None):put(im,sized(n,w,box),cx,cy)
def tap(im,key,box,w,cx,cy,u):
 if u<0 or u>.6:return
 p=TAPS[key];x=(p['x']+p['width']/2)*2;y=(p['y']+p['height']/2)*2
 l,t,r,b=box;s=w/(r-l);x=cx-w/2+(x-l)*s;y=cy-(b-t)*s/2+(y-t)*s
 over=Image.new('RGBA',(W,H));d=ImageDraw.Draw(over);q=u/.6;radius=16+45*q
 d.ellipse((x-radius,y-radius,x+radius,y+radius),outline=(63,198,174,round(240*(1-q))),width=7);im.alpha_composite(over)
def frame(t):
 s,e,k=next(row for row in SC if row[0]<=t<row[1]);u=t-s
 im=Image.new('RGBA',(W,H),C if k in ['hook','identity'] else GREEN if k in ['rexo','end'] else D)
 if k=='hook':
  title(im,'زبونك بيختار',350,u,G,96)
  title(im,'بعينه.',575,u,G,180,.25)
  disk(im,540,1160,445,'#dcd7c9');photo(im,'cheesemeal.webp',540,1160,1030,u)
  title(im,'قبل أول لقمة.',1670,u,D,80,.8)
 elif k=='question':
  title(im,'منيو مطعمك…',620,u,C,115)
  title(im,'بيعطي أطباقك',890,u,C,116,.2)
  title(im,'حقّها؟',1160,u,B,190,.5)
 elif k=='rexo':
  disk(im,540,760,290,C);v.assembling(im,u,540,760,490)
  title(im,'REXO',1190,u,C,145,.25)
  title(im,'تجربة بتفتح النفس.',1430,u,C,73,.5)
 elif k=='demo':
  ix=round(59*max(0,min(1,(u-1)/3.5)))
  shot(im,f'scroll/{ix:03d}.jpg',1080,540,960)
  if u<2.5:
   q=1-E((u-2)/.5);rr(im,(210,1570,870,1740),(16,21,22,255),30);text(im,'EMBER',540,1618,59,C,True,alpha=q);text(im,'نموذج منيو من تصميمنا',540,1695,38,B,alpha=q)
 elif k=='categories':
  second=u>=3;local=u-3 if second else u;n='shakes.png' if second else 'burgers.png'
  title(im,'للمشروبات.' if second else 'من البرغر…',300,local,C,112)
  box=(0,170,864,1420);shot(im,n,910,540+60*(1-E(local/.4)),1095,box)
 elif k=='details':
  title(im,'تفاصيل الطبق.',300,u,C,112)
  shot(im,'details.png',940,540,1070,(0,230,864,1285))
 elif k=='options':
  title(im,'اختيار على ذوقه.',300,u,C,102)
  box=(0,580,864,1536);name='options-before.png' if u<2 else 'options-selected.png'
  shot(im,name,940,540,1110,box);tap(im,'cheese',box,940,540,1110,u-2);tap(im,'add',box,940,540,1110,u-4.4)
 elif k=='cart':
  title(im,'الكميات والمجموع.',300,u,C,101)
  box=(0,450,864,1350);name='cart-one.png' if u<1.8 else 'cart-two.png'
  shot(im,name,970,540,1050,box);tap(im,'plus',box,970,540,1050,u-1.8)
 elif k=='language':
  text(im,'عربي',755,245,100,C,alpha=E(u/.4));text(im,'English',340,245,85,C,True,alpha=E(u/.4));disk(im,555,245,6,B)
  box=(0,0,864,1536);name='language-ar.png' if u<1.7 else 'language-en.png'
  shot(im,name,800,540,1110,box);tap(im,'language',box,800,540,1110,u-1.7)
 elif k=='identity':
  title(im,'هوية مطعمك.',360,u,G,110)
  title(im,'بكل تفصيل.',550,u,G,102,.2)
  photo(im,'crispy.webp',540,1120,1000,u)
  for j,col in enumerate([D,ORANGE,C]):disk(im,420+120*j,1600,36,col)
 elif k=='hospitality':
  if u<2:
   title(im,'إنت اهتم',680,u,C,110);title(im,'بالطعم والضيافة.',940,u,B,112,.2)
  else:
   title(im,'أول انطباع…',680,u-2,C,115);title(im,'علينا.',960,u-2,B,190,.2)
 elif k=='end':
  disk(im,540,730,270,C);put(im,v.mark('full',450),540,730)
  text(im,'REXO',540,1110,145,C,True)
  title(im,'منيو يليق بمطعمك.',1320,u,C,88)
  if u>.8:
   q=E((u-.8)/.4);rr(im,(220,1515,860,1645),C,65);text(im,'@rexo.web',540,1580,58,G,True,alpha=q)
 return im.convert('RGB')

def render():
 out=O/'Rexo_EMBER_Ad_Silent_v1.mp4'
 p=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','30','-i','-','-an','-c:v','libx264','-crf','19','-preset','fast','-threads','3','-pix_fmt','yuv420p','-movflags','+faststart',str(out)],stdin=subprocess.PIPE)
 last_key=None;raw=None
 for i in range(DURATION*FPS):
  t=i/FPS;s,e,k=next(row for row in SC if row[0]<=t<row[1]);u=t-s
  key=round(t,4)
  # Cache resolved still holds; animated events and captured scroll remain fully timed.
  holds={'hook':1.3,'question':1.0,'rexo':2.2,'details':.5,'identity':.6,'end':1.3}
  if k in holds and u>holds[k]:key=s+holds[k]
  if k=='categories' and u%3>.5:key=s+(3 if u>=3 else 0)+.5
  if k=='options' and .5<u<2:key=s+.5
  if k=='options' and 2.65<u<4.4:key=s+2.65
  if k=='cart' and .5<u<1.8:key=s+.5
  if k=='cart' and u>2.45:key=s+2.45
  if k=='language' and .5<u<1.7:key=s+.5
  if k=='language' and u>2.35:key=s+2.35
  if k=='hospitality' and .7<u<2:key=s+.7
  if k=='hospitality' and u>2.7:key=s+2.7
  if key!=last_key:raw=frame(key).tobytes();last_key=key
  p.stdin.write(raw)
  if i%300==0:print(f'{i}/{DURATION*FPS}',flush=True)
 p.stdin.close();assert p.wait()==0
if __name__=='__main__':
 import sys
 if '--preview' in sys.argv:
  times=[2,5.5,9.5,11,14.5,17.5,20.5,23.5,28,33,38,41,46,51]
  sheet=Image.new('RGB',(5*216,3*384),C)
  for i,t in enumerate(times):
   f=frame(t);f.save(O/f'frame-{t}.jpg');sheet.paste(f.resize((216,384)),((i%5)*216,(i//5)*384))
  sheet.save(O/'Storyboard.jpg')
 else:render()
