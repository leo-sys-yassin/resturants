from pathlib import Path
import json,math,functools,subprocess,io
from PIL import Image,ImageDraw
import cairosvg
import base as b
R=Path(__file__).resolve().parent;O=R/'delivery';A=R/'assets';O.mkdir(exist_ok=True)
C='#ece6d8';D='#101516';G='#35564f';GREEN='#1f7a68';B='#cbb5a0';TEAL='#3fc6ae';INK='#151b19'
b.C=C;b.D=D;b.G=G;b.INK=INK;b.B=B
E=b.ease;S=b.smooth;put=b.put;text=b.text;rr=b.rr;line=b.line;disk=b.disk
SC=[(0,4,'idea'),(4,7,'who'),(7,14,'chat'),(14,17,'chaos'),(17,22,'brand'),(22,28,'web'),(28,33,'custom'),(33,38,'order'),(38,44,'ai'),(44,49,'connect'),(49,55,'why'),(55,60,'process'),(60,66,'end')]
LG=json.loads((R/'logo-paths.json').read_text())
@functools.lru_cache(None)
def mark(part='full',size=500):
 pieces=[('bk','#35564f'),('up','#46675f'),('lo','#cbb5a0')];paths=[]
 for name,col in pieces:
  if part in ['full',name]:paths.append(f'<path fill="{col}" d="{LG[name]}"/>')
 for j,(col,path) in enumerate(LG['sq']):
  if part in ['full',str(j)]:paths.append(f'<path fill="{col}" d="{path}"/>')
 svg='<svg xmlns="http://www.w3.org/2000/svg" width="900" height="800" viewBox="80 80 900 800">'+''.join(paths)+'</svg>'
 return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(),output_width=size,output_height=round(size*8/9)))).convert('RGBA')
def assembling(im,u,x=540,y=850,size=510):
 for j in range(6):
  e=E((u-.08*j)/.85);put(im,mark(str(j),size),x-180*(1-e),y+(j-2)*60*(1-e),alpha=e)
 for j,k in enumerate(['bk','up','lo']):
  e=E((u-.5-j*.23)/.8);put(im,mark(k,size),x-70*(1-e),y+(-90 if k=='up' else 90 if k=='lo' else 0)*(1-e),alpha=e)
def title(im,s,y=420,size=108,col=INK,u=1,delay=0):text(im,s,540,y+32*(1-E((u-delay)/.5)),size,col,alpha=E((u-delay)/.35))
def grid(im,col):
 d=ImageDraw.Draw(im)
 for x in [180,540,900]:d.line((x,0,x,1920),fill=col,width=1)
def pill(im,s,y=1500,bg=G,fg=C):
 rr(im,(200,y-65,880,y+65),bg,65);text(im,s,540,y,52,fg)
def service(t,u,key):
 mp={'web':8,'custom':19,'order':25,'ai':31,'connect':37}
 # Preserve the original explanatory animations, with the new campaign typography.
 im=b.frame(mp[key]+min(u,5.9 if key in ['web','ai'] else 4.9)).convert('RGBA')
 dark=key=='ai';bg=D if dark else C;fg=C if dark else INK
 im.paste(b.background(dark).crop((0,0,1080,675)),(0,0))
 heads={'web':('موقعك. تطبيقك.','خدماتك أقرب لزبونك'), 'custom':('حل بيشبه شغلك','برمجيات على مقاس مشروعك'),'order':('طلباتك منظّمة','من الاختيار للمتابعة'),'ai':('ذكاء ضمن الحل','بوتات وأتمتة المهام'),'connect':('كلها بتشتغل سوا','أنظمة مترابطة وبيانات أوضح')}
 h,s=heads[key];title(im,h,410,105,fg,u);title(im,s,555,53,B if dark else GREEN,u,.3)
 # Selective brand accent, appears only once the headline is readable.
 q=E((u-.6)/.6);line(im,[(430,650),(430+int(220*q),650)],B if dark else GREEN,6)
 return im

def frame(t):
 st,en,k=next(s for s in SC if s[0]<=t<s[1]);u=t-st
 bg=GREEN if k in ['who','brand','end'] else D if k in ['chat','chaos','why'] else C
 im=Image.new('RGBA',(1080,1920),bg)
 if k=='idea':
  grid(im,'#ddd8cd');title(im,'عندك فكرة',410,138,INK,u);title(im,'مشروع؟',610,174,GREEN,u,.25)
  title(im,'وجاهز تبدأ؟',820,94,INK,u,.65)
  b.web_ui(im,540,1320,830,530,u)
  if u>2.3:
   e=E((u-2.3)/.4);badge=Image.new('RGBA',(270,270));b.disk(badge,135,135,125,C);ImageDraw.Draw(badge).ellipse((12,12,258,258),outline=GREEN,width=8);text(badge,'LIVE',135,125,61,GREEN,True);put(im,badge,835,1280,.8+.2*e,alpha=e,angle=-12)
 elif k=='who':
  title(im,'طيب…',420,65,C,u);title(im,'مين رح',750,185,C,u,.15);title(im,'ينفّذ؟',1050,200,B,u,.4)
  # The pending idea is represented as an incomplete set of roles, not a fake progress statistic.
  for j,n in enumerate(['globe','smartphone','bot']):
   q=E((u-.7-j*.25)/.5);rr(im,(210+j*235,1370+40*(1-q),400+j*235,1560+40*(1-q)),G,35);put(im,b.icon(n,92,C),305+j*235,1465+40*(1-q),alpha=q)
 elif k=='chat':
  title(im,'ولما تتوزّع الفكرة…',340,70,C,u)
  msgs=[('بدي موقع للمشروع.',False),('بدك مطوّر ويب.',True),('وتطبيق موبايل كمان.',False),('بدك مطوّر تطبيقات.',True),('وبوت للزباين؟',False),('وكمان ربط بين الأنظمة.',True)]
  for j,(tx,ans) in enumerate(msgs):
   delay=.5+j*.9;e=E((u-delay)/.4)
   if e==0:continue
   w=760 if not ans else 700;cx=600 if not ans else 460;y=580+j*176+25*(1-e)
   rr(im,(cx-w/2,y-67,cx+w/2,y+67),TEAL if ans else '#242b2b',37)
   text(im,tx,cx,y,46,D if ans else C,alpha=e,maxwidth=w-60)
 elif k=='chaos':
  title(im,'جهات أكتر.',510,125,C,u)
  title(im,'متابعة أكتر.',750,125,C,u,.3)
  title(im,'والفكرة وحدة.',1110,135,TEAL,u,.7)
  q=E((u-1.5)/.6);line(im,[(260,1260),(260+int(560*q),1260)],B,8)
 elif k=='brand':
  disk(im,540,800,315,C);assembling(im,u,540,800,515)
  title(im,'REXO',1210,172,C,u,.85)
  title(im,'شريك واحد',1435,104,C,u,1.3)
  title(im,'لحلولك الرقمية',1580,84,B,u,1.65)
 elif k in ['web','custom','order','ai','connect']:
  im=service(t,u,k)
 elif k=='why':
  title(im,'شو بيميّز طريقتنا؟',410,97,C,u)
  items=[('sliders-horizontal','حل على مقاس شغلك'),('layers','خدمات مترابطة'),('check','من الفكرة للإطلاق')]
  for j,(n,tx) in enumerate(items):
   e=E((u-.65-j*1.25)/.6);y=820+j*255
   rr(im,(120+75*(1-e),y-85,960+75*(1-e),y+85),'#202a29',35)
   put(im,b.icon(n,77,TEAL),850+75*(1-e),y,alpha=e)
   text(im,tx,480+75*(1-e),y,62,C,alpha=e,maxwidth=620)
  title(im,'من احتياجك… بنبدأ.',1670,44,B,u,4.25)
 elif k=='process':
  title(im,'من الفكرة',430,131,INK,u);title(im,'للإطلاق',620,151,GREEN,u,.25)
  xs=[870,650,430,210];words=['فكرة','تصميم','تطوير','إطلاق'];q=b.clamp((u-1)/2.7)
  line(im,[(210,1080),(870,1080)],'#c4c7ba',7);line(im,[(870,1080),(870-660*q,1080)],GREEN,9)
  for j,(x,tx) in enumerate(zip(xs,words)):
   on=q>=j/3;disk(im,x,1080,33,GREEN if on else '#c4c7ba')
   if on:put(im,b.icon('check',38,C),x,1080)
   text(im,tx,x,1210,47,G,maxwidth=200)
  title(im,'فريق واحد. رؤية واضحة.',1510,65,INK,u,3.4)
 elif k=='end':
  title(im,'رؤيتك.',480,174,C,u)
  title(im,'وتقنيتنا.',735,171,B,u,.3)
  disk(im,540,1100,165,C);put(im,mark('full',260),540,1100)
  title(im,'احكيلنا عن فكرتك',1390,79,C,u,.8)
  pill(im,'@rexo.web',1585,C,G)
 # Consistent 0.3s wipe at the three narrative chapter changes only.
 if k in ['brand','web','end'] and u<.32:
  x=round(1080*E(u/.32));ImageDraw.Draw(im).rectangle((x,0,1080,1920),fill=B)
 return im.convert('RGB')

def sample(t):
 st,en,k=next(s for s in SC if s[0]<=t<s[1]);holds={'idea':3.4,'who':2.0,'chat':6,'chaos':2.2,'brand':2.8,'web':4.6,'custom':3.8,'order':4.6,'ai':4.8,'connect':4.6,'why':5,'process':4.4,'end':2}
 return st+min(t-st,holds[k])
@functools.lru_cache(3)
def pixels(t):return frame(t).tobytes()
def render():
 p=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','30','-i','-','-an','-c:v','libx264','-preset','ultrafast','-crf','19','-threads','3','-pix_fmt','yuv420p','-movflags','+faststart',str(O/'Rexo_Motion_Merged_v2.mp4')],stdin=subprocess.PIPE)
 for i in range(1980):
  p.stdin.write(pixels(sample(i/30)))
  if i%180==0:print(f'{i}/1980',flush=True)
 p.stdin.close();assert p.wait()==0
if __name__=='__main__':
 import sys
 if '--preview' in sys.argv:
  ts=[3,6,13,16,20.5,26.5,31.5,37,42.7,48.4,54,59.3,64]
  sheet=Image.new('RGB',(5*270,3*480),C)
  for j,t in enumerate(ts):
   im=frame(t);im.save(O/f'frame-{t}.jpg');sheet.paste(im.resize((270,480)),((j%5)*270,(j//5)*480))
  sheet.save(O/'Storyboard_v2.jpg')
 else:render()
