from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import math,functools,subprocess,json,io
import numpy as np
import cairosvg
R=Path(__file__).resolve().parent;A=R/'assets';O=R/'delivery';O.mkdir(exist_ok=True)
W,H,FPS=1080,1920,30
C='#f4f0e8';G='#35584f';D='#082e2c';B='#cfb89f';T='#67b7a4';M='#9b947e';INK='#173c36'
scenes=[
(0,4,'idea','فكرتك تستاهل','حضور رقمي يليق فيها'),
(4,8,'brand','من الفكرة','للإطلاق'),
(8,14,'web','مواقع إلكترونية','تعرّف الناس على شغلك'),
(14,19,'app','تطبيقات موبايل','خدماتك أقرب لزبونك'),
(19,25,'custom','برمجيات مخصّصة','على مقاس مشروعك'),
(25,31,'order','أنظمة طلبات وإدارة','ترتيب أوضح. متابعة أسهل.'),
(31,37,'ai','ذكاء اصطناعي وأتمتة','وقت أقل للمهام المتكرّرة'),
(37,43,'connect','حلول بتشتغل مع بعض','ربط الأنظمة وتبادل البيانات'),
(43,48,'difference','شو بيميّز طريقتنا؟','نبدأ من احتياج مشروعك'),
(48,54,'journey','فريق واحد','من فكرتك لمنتجك الرقمي'),
(54,60,'close','جاهز تبدأ؟','احكيلنا عن فكرتك')]
json.dump({'width':W,'height':H,'fps':FPS,'duration':60,'audio':'none','timing':'provisional silent editorial pacing; re-time to supplied narration later','style':'Editorial modular motion inspired by brand pixel geometry. Forest green, beige, ivory, subtle teal. Cairo/Montserrat.','palette':{'forest':G,'deep':D,'beige':B,'ivory':C,'teal':T},'scenes':scenes,'claims':'Service categories and concept-to-launch proposition supplied in Instagram screenshots. Benefits qualitative; no competitor ranking, quantified results or guarantees.','logo':'Reference-based extraction prepared with image generation; original references remain authoritative.'},open(O/'timeline.json','w'),ensure_ascii=False,indent=2)
def clamp(x):return max(0,min(1,x))
def ease(x):return 1-(1-clamp(x))**3
def smooth(x):x=clamp(x);return x*x*(3-2*x)
def mix(a,b,x):return a+(b-a)*x
@functools.lru_cache(None)
def font(size,latin=False):
 f=ImageFont.truetype(str(A/('Montserrat.ttf' if latin else 'Cairo.ttf')),size)
 try:f.set_variation_by_axes([700 if latin else 750])
 except:pass
 return f
@functools.lru_cache(None)
def label(s,size=70,col=INK,latin=False,maxwidth=880):
 d=ImageDraw.Draw(Image.new('RGBA',(1,1)));f=font(size,latin);bb=d.textbbox((0,0),s,font=f)
 while bb[2]-bb[0]>maxwidth:
  size-=2;f=font(size,latin);bb=d.textbbox((0,0),s,font=f)
 im=Image.new('RGBA',(bb[2]-bb[0]+16,bb[3]-bb[1]+16));ImageDraw.Draw(im).text((8-bb[0],8-bb[1]),s,font=f,fill=col);return im
@functools.lru_cache(None)
def icon(n,size=100,col=G):
 s=(A/(n+'.svg')).read_text().replace('currentColor',col)
 return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=s.encode(),output_width=size,output_height=size))).convert('RGBA')
@functools.lru_cache(None)
def logo(size):
 im=Image.open(A/'brand-symbol.png').convert('RGBA');im=im.crop(im.getbbox());return im.resize((size,round(size*im.height/im.width)),Image.Resampling.LANCZOS)
def put(im,ob,x,y,scale=1,alpha=1,angle=0):
 if alpha<=0 or scale<=0:return
 if scale!=1:ob=ob.resize((max(1,round(ob.width*scale)),max(1,round(ob.height*scale))),Image.Resampling.BICUBIC)
 if angle:ob=ob.rotate(angle,Image.Resampling.BICUBIC,expand=True)
 if alpha<1:ob=ob.copy();ob.putalpha(ob.getchannel('A').point(lambda a:round(a*alpha)))
 im.alpha_composite(ob,(round(x-ob.width/2),round(y-ob.height/2)))
def text(im,s,x,y,size=70,col=INK,latin=False,alpha=1,maxwidth=880):put(im,label(s,size,col,latin,maxwidth),x,y,alpha=alpha)
def rr(im,box,fill,r=26,outline=None,width=2):ImageDraw.Draw(im).rounded_rectangle(tuple(round(x) for x in box),radius=r,fill=fill,outline=outline,width=width)
def line(im,p,col=T,w=6):ImageDraw.Draw(im).line(p,fill=col,width=w,joint='curve')
def disk(im,x,y,r,col):ImageDraw.Draw(im).ellipse((x-r,y-r,x+r,y+r),fill=col)
def check(im,x,y,size=60,col=G):put(im,icon('check',size,col),x,y)
def header(im,u,title,sub,dark=False):
 col=C if dark else INK
 text(im,title,540,405+35*(1-ease(u/.5)),88,col,alpha=ease(u/.35))
 text(im,sub,540,535+25*(1-ease((u-.25)/.55)),48,B if dark else G,alpha=ease((u-.25)/.35))
@functools.lru_cache(None)
def background(dark):
 col=D if dark else C;im=Image.new('RGBA',(W,H),col)
 # Subtle large-radius tonal field, no decorative data or particles.
 if dark:
  ar=np.zeros((H,W,4),dtype=np.uint8);yy,xx=np.ogrid[:H,:W];v=np.exp(-((xx-540)**2+(yy-1050)**2)/(2*520**2));ar[:,:,0]=50;ar[:,:,1]=107;ar[:,:,2]=92;ar[:,:,3]=(v*45).astype('uint8');im.alpha_composite(Image.fromarray(ar))
 return im

def web_ui(im,x,y,w,h,u,compact=False):
 rr(im,(x-w/2,y-h/2,x+w/2,y+h/2),'#ffffff',30)
 top=y-h/2
 rr(im,(x-w/2+25,top+23,x+w/2-25,top+80),C,17)
 for j in range(3):disk(im,x-w/2+47+j*21,top+51,5,[G,B,M][j])
 put(im,icon('globe',31,G),x+w/2-52,top+52)
 text(im,'مشروعك',x,top+145,46,G)
 # One hero panel and its related services reflow between breakpoints.
 e=ease((u-.4)/.65)
 bw=w-60;rr(im,(x-bw/2,top+192,x+bw/2,top+192+int(160*e)),G,20)
 if e>.7:text(im,'خدماتك بوضوح',x,top+270,38,C,alpha=(e-.7)/.3,maxwidth=w-85)
 gap=15;cols=1 if compact else 3;cw=(w-60-gap*(cols-1))/cols
 for j in range(3):
  ee=ease((u-.8-j*.13)/.5)
  bx=x-w/2+30+(j%cols)*(cw+gap);by=top+380+(j//cols)*110
  rr(im,(bx,by+30*(1-ee),bx+cw,by+85+30*(1-ee)),C,14)
  put(im,icon(['layers','shopping-bag','send'][j],32,G),bx+cw/2,by+42+30*(1-ee),alpha=ee)

def frame(t):
 start,end,key,title,sub=next(s for s in scenes if s[0]<=t<s[1]);u=t-start
 dark=key in ['idea','brand','app','ai','difference','close'];im=background(dark).copy();d=ImageDraw.Draw(im)
 if key=='idea':
  text(im,title,540,440,108,C,alpha=ease(u/.4));text(im,sub,540,600,68,B,alpha=ease((u-.35)/.4))
  # Pixel modules converge to a disciplined digital composition.
  pts=[(-270,-160,150,G),(70,-205,200,B),(-130,100,190,T),(220,120,130,G),(-300,300,90,B),(210,345,75,M)]
  for j,(dx,dy,sz,col) in enumerate(pts):
   q=ease((u-.15-j*.08)/1.0);x=540+dx*(1.5-.5*q);y=1100+dy+100*(1-q)
   rr(im,(x-sz*q/2,y-sz*q/2,x+sz*q/2,y+sz*q/2),col,round(max(1,sz*.18)))
  if u>2:
   q=ease((u-2)/.7);line(im,[(250,1540),(250+int(580*q),1540)],B,4)
 elif key=='brand':
  put(im,logo(500),540,830+70*(1-ease(u/.7)),alpha=ease(u/.5))
  text(im,'Rexo',540,1190,160,C,True,alpha=ease((u-.25)/.5))
  text(im,'WEB & DIGITAL',540,1310,37,B,True,alpha=ease((u-.4)/.5))
  text(im,'من الفكرة للإطلاق',540,1510,57,C,alpha=ease((u-.65)/.5))
 elif key=='web':
  header(im,u,title,sub)
  q=smooth((u-2.6)/.85);w=mix(860,470,q);h=mix(640,830,q)
  web_ui(im,540,1120,w,h,u,compact=q>.5)
  text(im,'تجربة مناسبة لكل شاشة',540,1660,42,G,alpha=ease((u-3.4)/.4))
 elif key=='app':
  header(im,u,title,sub,True)
  # Application interface, independent of fabricated physical phone hardware.
  q=ease(u/.55);rr(im,(260,710+60*(1-q),820,1510+60*(1-q)),C,45)
  put(im,icon('smartphone',64,G),540,790)
  text(im,'كل شي بمكانه',540,900,49,G)
  for j,word in enumerate(['تصفّح','اختار','تواصل']):
   e=ease((u-.6-j*.6)/.5);cy=1040+j*150
   rr(im,(315,cy-53,765,cy+53),G if j==min(2,int(max(0,u-1)/.9)) else '#e5e7df',22)
   col=C if j==min(2,int(max(0,u-1)/.9)) else G
   text(im,word,540,cy+20*(1-e),48,col,alpha=e)
  text(im,'خطوات واضحة لزبونك',540,1660,42,B,alpha=ease((u-2.7)/.5))
 elif key=='custom':
  header(im,u,title,sub)
  # Modules move into the footprint of a system: customization rather than stats.
  rr(im,(165,780,915,1410),None,34,outline='#b8c9c0',width=3)
  put(im,icon('code-xml',100,G),540,880)
  modules=[(215,990,300,160,'شغلك'),(535,990,330,160,'احتياجك'),(215,1170,650,170,'نظامك')]
  for j,(x,y,w,h,tx) in enumerate(modules):
   e=ease((u-.5-j*.55)/.7);dx=(-300 if j%2==0 else 300)*(1-e)
   rr(im,(x+dx,y,x+w+dx,y+h),[G,B,G][j],23)
   text(im,tx,x+w/2+dx,y+h/2,53,C if j!=1 else INK,alpha=e,maxwidth=w-30)
  text(im,'نطوّر الحل حول احتياجك',540,1590,46,G,alpha=ease((u-2.8)/.5))
 elif key=='order':
  header(im,u,title,sub)
  # Illustrative order moving through explicit stages; no sales numbers.
  st=min(2,int(max(0,u-.8)/1.25));xs=[820,540,260]
  for j in range(2):
   q=ease((u-1.7-j*1.25)/.6);line(im,[(xs[j]-75,930),(mix(xs[j]-75,xs[j+1]+75,q),930)],G if j<st else '#cbd4cd',7)
  for j,tx in enumerate(['اختيار','طلب','متابعة']):
   disk(im,xs[j],930,69,G if j<=st else '#dce2da');put(im,icon(['shopping-bag','send','check'][j],60,C if j<=st else G),xs[j],930)
   text(im,tx,xs[j],1055,41,G,maxwidth=220)
  q=ease((u-.6)/.5);rr(im,(225,1170+65*(1-q),855,1430+65*(1-q)),'#ffffff',28)
  text(im,'الطلب',730,1235,42,G)
  text(im,['تم الاختيار','جاهز للإرسال','قيد المتابعة'][st],540,1350,56,G)
  text(im,'منيو رقمي • طلبات • إدارة',540,1610,40,G,alpha=ease((u-3)/.5))
 elif key=='ai':
  header(im,u,title,sub,True)
  # Repetitive task enters one automation and exits as organized output.
  put(im,icon('bot',135,B),540,1000)
  for j,tx in enumerate(['رسالة','مهمة','بيانات']):
   e=ease((u-.6-j*.2)/.6);y=790+j*190
   rr(im,(115-120*(1-e),y-50,355-120*(1-e),y+50),G,20)
   text(im,tx,235-120*(1-e),y,38,C,maxwidth=210,alpha=e)
  for j in range(3):
   q=ease((u-1.5-j*.35)/.65);line(im,[(365,790+j*190),(mix(365,455,q),1000)],T,5)
  q=ease((u-2.4)/.6);line(im,[(630,1000),(630+int(110*q),1000)],B,6)
  if u>2.8:
   rr(im,(755,880,965,1120),C,25);check(im,860,960,70,G);text(im,'منظّم',860,1060,37,G,maxwidth=185)
  text(im,'خلّي وقتك للأهم',540,1450,73,C,alpha=ease((u-3.4)/.5))
 elif key=='connect':
  header(im,u,title,sub)
  coords=[(290,900),(790,900),(290,1330),(790,1330)];names=['globe','shopping-bag','database','bot']
  q=ease((u-.8)/1.0)
  for j,((x,y),n) in enumerate(zip(coords,names)):
   # Link forms toward the shared hub, then a token reaches it.
   e=ease((u-.6-j*.25)/.8);line(im,[(x,y),(mix(x,540,e),mix(y,1115,e))],G,6)
   rr(im,(x-85,y-85,x+85,y+85),G if j%2 else B,28);put(im,icon(n,84,C if j%2 else G),x,y)
  rr(im,(435,1010,645,1220),C,35,outline=G,width=4);put(im,icon('workflow',100,G),540,1115)
  if u>2.1:
   p=clamp((u-2.1)/1.2)
   for x,y in coords:disk(im,mix(x,540,p),mix(y,1115,p),11,T)
  text(im,'شغل مترابط… متابعة أوضح',540,1570,48,G,alpha=ease((u-3.2)/.5))
 elif key=='difference':
  header(im,u,title,sub,True)
  # One proposition per beat; no unsupported comparisons with named competitors.
  phase=0 if u<2.5 else 1
  tx='حل حسب احتياجك' if phase==0 else 'خدمات مترابطة'
  put(im,icon('sliders-horizontal' if phase==0 else 'layers',180,B),540,990)
  text(im,tx,540,1260,81,C,alpha=ease(((u if phase==0 else u-2.5)-.15)/.4))
  text(im,'فكرة واحدة. تنفيذ متكامل.',540,1480,45,B,alpha=ease((u-3.2)/.4))
 elif key=='journey':
  header(im,u,title,sub)
  positions=[770,960,1150,1340];labels=['فهم الفكرة','تصميم التجربة','تطوير الحل','الإطلاق'];progress=clamp((u-.7)/3.7)
  line(im,[(790,770),(790,1340)],'#d1d9d1',7);line(im,[(790,770),(790,mix(770,1340,progress))],G,9)
  for j,(y,tx) in enumerate(zip(positions,labels)):
   active=progress>=j/3;e=ease((u-.5-j*.9)/.45)
   disk(im,790,y,32,G if active else '#d1d9d1')
   if active:check(im,790,y,37,C)
   text(im,tx,470+30*(1-e),y,55,G,alpha=e,maxwidth=450)
  text(im,'من أول خطوة… لحد الإطلاق',540,1590,44,G,alpha=ease((u-4.1)/.5))
 elif key=='close':
  # Brand on a light field preserves the reference symbol's green and beige.
  im=background(False).copy()
  put(im,logo(330),540,640+40*(1-ease(u/.6)),alpha=ease(u/.4))
  text(im,'Rexo',540,955,151,G,True,alpha=ease((u-.2)/.4))
  text(im,'WEB & DIGITAL',540,1080,34,G,True)
  text(im,'احكيلنا عن فكرتك',540,1270,75,G,alpha=ease((u-.7)/.5))
  rr(im,(265,1430,815,1560),G,65)
  text(im,'@rexo.web',540,1495,54,C,True)
  text(im,'تواصل معنا برسالة',540,1660,37,G)
 # Small deliberate geometric wipe only at major act boundaries.
 if key in ['brand','difference','close'] and u<.3:
  q=ease(u/.3);x=round(mix(0,1080,q));d=ImageDraw.Draw(im);d.rectangle((x,0,1080,H),fill=B)
 return im.convert('RGB')

# Freeze only settled graphic states. All local animations finish before these thresholds.
def sample_time(t):
 st,en,k,_,_=next(s for s in scenes if s[0]<=t<s[1]);u=t-st
 holds={'idea':2.85,'brand':1.4,'web':4.2,'app':3.5,'custom':3.5,'order':4.5,'ai':4.2,'connect':4.0,'difference':4.0,'journey':4.9,'close':1.5}
 return st+min(u,holds[k])
@functools.lru_cache(3)
def pixels(t):return frame(t).tobytes()
def render():
 out=O/'Rexo_Brand_Intro_Silent_v1.mp4'
 p=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','30','-i','-','-an','-c:v','libx264','-preset','ultrafast','-crf','19','-threads','3','-pix_fmt','yuv420p','-movflags','+faststart','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709',str(out)],stdin=subprocess.PIPE)
 for i in range(1800):
  p.stdin.write(pixels(sample_time(i/30)))
  if i%150==0:print(f'{i}/1800',flush=True)
 p.stdin.close();assert p.wait()==0
if __name__=='__main__':
 import sys
 if '--preview' in sys.argv:
  sheet=Image.new('RGB',(5*270,3*480),C)
  for j,t in enumerate([2,6,10,12.5,16.5,22,29.5,35.5,41,45,47,52.8,58]):
   im=frame(t);im.save(O/f'frame-{t}.jpg');sheet.paste(im.resize((270,480)),((j%5)*270,(j//5)*480))
  sheet.save(O/'Storyboard.jpg')
 else:render()
