from pathlib import Path
import json, math, subprocess, functools
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
ROOT=Path(__file__).resolve().parent
A=ROOT/'assets'; O=ROOT/'delivery';O.mkdir(exist_ok=True)
W,H,FPS=1080,1920,30
DURATION=57.626122;N=math.ceil(DURATION*FPS)
CREAM='#f8f4ee';INK='#222426';GOLD='#d9962f';CORAL='#e0625a'
# Speech-derived phrase intervals; normalized recognition spelling and brand names.
cues=[(0,2.12,'زبونك بيعيش تجربة مكانك'),(2.12,4.12,'من أول ما يفتح المنيو'),(4.12,5.6,'بس إذا كل تعديل سعر'),(5.6,6.7,'بده طباعة جديدة'),(6.7,7.92,'وكل صنف جديد'),(7.92,9.3,'بده منيو جديد'),(9.3,10.22,'لإيمتى؟'),(10.22,12.36,'وحتى لو المنيو تبعك إلكتروني'),(12.36,13.72,'إذا أصنافه مخربطة'),(13.72,15.06,'وصوره مو واضحة'),(15.06,16.16,'وصعب تتصفحه'),(16.16,17.42,'رح يضيّع الزبون'),(17.42,18.86,'بدل ما يساعده يختار'),(18.86,19.96,'مع Rexo'),(19.96,21.3,'منحوّل التصفح'),(21.3,23,'لتجربة بتفتح النفس'),(23,25.3,'تصميم بيشبه هوية مكانك'),(25.3,26.94,'صور بتبرز أصنافك'),(26.94,28.16,'وحركة ناعمة'),(28.16,30.1,'بتعطي كل تفصيل حقه'),(30.1,31.82,'زبونك بيتنقّل بين الأقسام'),(31.82,32.48,'بسهولة'),(32.48,33.98,'بيشوف الأصناف بوضوح'),(33.98,34.84,'وبكبسة'),(34.84,36.8,'اختياره بينتقل للسلة'),(36.8,38.24,'بيراجع اختياراته'),(38.24,39.42,'بيعدّل الكمية'),(39.42,40.58,'وبيشوف المجموع'),(40.58,41.7,'وبكبسة تانية'),(41.7,43.02,'بيبدّل بين العربي'),(43.02,44.06,'والإنجليزي'),(44.06,45.2,'وهذا VELORA'),(45.2,47.18,'نموذج لمنيو كافيه صمّمناه'),(47.18,49.2,'ليجمع الذوق والحركة'),(49.2,50.44,'وسهولة الاستخدام'),(50.44,52.62,'إنت اهتم بالطعم والضيافة'),(52.62,54.44,'وخلّي أول انطباع علينا'),(54.44,55.32,'Rexo'),(55.32,57.626122,'منيو يليق بمكانك')]
json.dump({'dimensions':[W,H],'fps':FPS,'audio_speed':1,'style':'Warm editorial product motion: cream, charcoal, gold; Cairo and Montserrat; decelerating reveals; authentic supplied menu imagery.','cues':cues,'listening_review':'not_performed','transcript_note':'ASR normalized for spelling and context; not audited by listening.'},open(O/'timeline.json','w'),ensure_ascii=False,indent=2)
def stamp(t):
 ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
(O/'Rexo_Velora_AR.srt').write_text('\n\n'.join(f'{i+1}\n{stamp(s)} --> {stamp(e)}\n{x}' for i,(s,e,x) in enumerate(cues)),encoding='utf8')
def ease(x):return 1-(1-max(0,min(1,x)))**3
@functools.lru_cache(None)
def font(size,latin=False):
 f=ImageFont.truetype(str(A/('Montserrat.ttf' if latin else 'Cairo.ttf')),size)
 try:f.set_variation_by_axes([750 if latin else 720])
 except:pass
 return f
@functools.lru_cache(None)
def txt(s,size=70,color=INK,latin=False,maxwidth=870):
 f=font(size,latin);d=ImageDraw.Draw(Image.new('RGBA',(1,1)))
 while d.textbbox((0,0),s,font=f)[2]>maxwidth and size>32:size-=2;f=font(size,latin)
 bb=d.textbbox((0,0),s,font=f,stroke_width=0);im=Image.new('RGBA',(bb[2]-bb[0]+12,bb[3]-bb[1]+12));ImageDraw.Draw(im).text((6-bb[0],6-bb[1]),s,font=f,fill=color)
 return im
@functools.lru_cache(None)
def asset(n):return Image.open(A/n).convert('RGBA')
def put(im,obj,cx,cy,scale=1,angle=0,opacity=1):
 if scale<=0:return
 if scale!=1:obj=obj.resize((max(1,round(obj.width*scale)),max(1,round(obj.height*scale))),Image.Resampling.LANCZOS)
 if angle:obj=obj.rotate(angle,Image.Resampling.BICUBIC,expand=True)
 if opacity<1:obj=obj.copy();obj.putalpha(obj.getchannel('A').point(lambda x:round(x*opacity)))
 im.alpha_composite(obj,(round(cx-obj.width/2),round(cy-obj.height/2)))
def text(im,s,y,size=70,color=INK,latin=False,x=540,maxwidth=870):put(im,txt(s,size,color,latin,maxwidth),x,y)
@functools.lru_cache(None)
def panel(n,width=650):
 ob=asset(n);ob=ob.resize((width,round(ob.height*width/ob.width)),Image.Resampling.LANCZOS);m=Image.new('L',ob.size);ImageDraw.Draw(m).rounded_rectangle((0,0,ob.width-1,ob.height-1),radius=30,fill=255);ob.putalpha(m)
 # A screenshot plane, no fabricated device casing.
 sh=Image.new('RGBA',(ob.width+100,ob.height+100));ImageDraw.Draw(sh).rounded_rectangle((50,57,ob.width+50,ob.height+57),radius=30,fill=(0,0,0,55));sh=sh.filter(ImageFilter.GaussianBlur(22));sh.alpha_composite(ob,(50,50));return sh
@functools.lru_cache(None)
def crop(n,box,width):
 im=asset(n).crop(box);return im.resize((width,round(im.height*width/im.width)),Image.Resampling.LANCZOS)
def product(im,n,cx,cy,width,angle=0):
 ob=asset(n+'.webp');put(im,ob,cx,cy,width/ob.width,angle)
def circle(im,x,y,r,col):ImageDraw.Draw(im).ellipse((x-r,y-r,x+r,y+r),fill=col)
def scene(t):
 if t<4.12:return 0,0
 if t<9.3:return 1,4.12
 if t<10.22:return 2,9.3
 if t<18.86:return 3,10.22
 if t<23:return 4,18.86
 if t<25.3:return 5,23
 if t<30.1:return 6,25.3
 if t<33.98:return 7,30.1
 if t<36.8:return 8,33.98
 if t<40.58:return 9,36.8
 if t<44.06:return 10,40.58
 if t<50.44:return 11,44.06
 if t<54.44:return 12,50.44
 return 13,54.44
# Reusable conceptual graphic: successive editions of a price list, not a product screenshot.
@functools.lru_cache(None)
def edition(label):
 im=Image.new('RGBA',(550,690),CREAM);d=ImageDraw.Draw(im);d.rectangle((0,0,550,14),fill=CORAL)
 text(im,'MENU',100,58,INK,True,x=275);text(im,label,210,45,CORAL,x=275,maxwidth=480)
 for j,w in enumerate([320,240,300,200]):d.line((80,325+j*70,80+w,325+j*70),fill='#c6bfb5',width=12)
 return im

def frame(t):
 k,start=scene(t);u=t-start;e=ease(u/.6);dark=k in [0,2,4,6,12,13];im=Image.new('RGBA',(W,H),INK if dark else CREAM);d=ImageDraw.Draw(im)
 fg=CREAM if dark else INK
 # Product-led hook, anchored to the first spoken idea.
 if k==0:
  hero=crop('welcome.png',(0,0,860,880),1080);put(im,hero,540,1150,1.05-.04*min(u/4,1))
  text(im,'REXO',190,38,GOLD,True)
  d.line((460,1520,620,1520),fill=GOLD,width=5)
 elif k==1:
  for j in range(3):put(im,edition('تعديل السعر' if t<6.7 else 'صنف جديد'),540+(j-1)*65,1050+(j-1)*32+80*(1-e),.92,(j-1)*-9)
  text(im,'كل تحديث… نسخة جديدة',1510,43,CORAL)
 elif k==2:
  circle(im,540,950,400,GOLD);text(im,'لإيمتى؟',950,155,INK)
 elif k==3:
  # Illustrative disorder stays separate from VELORA evidence.
  labels=['أصناف مخربطة','صور مو واضحة','تصفّح صعب'];idx=0 if t<13.72 else 1 if t<15.06 else 2
  for j in range(3):
   col=CORAL if j==idx else '#d9d3c9'; y=870+j*180
   d.line((210,y,870,y),fill=col,width=3)
   text(im,labels[j],y+65,62,col)
  if t>=16.16:
   d.line((255,1530,825,1530),fill=CORAL,width=6)
 elif k==4:
  text(im,'REXO',820,190,CREAM,True)
  d.rectangle((180,950,180+int(720*e),960),fill=GOLD)
  product(im,'coffee-2',570,1300+70*(1-e),670,-5+5*e)
 elif k==5:
  put(im,panel('welcome.png',520),540,1110+100*(1-e),1,-4+4*e)
  for j,c in enumerate([INK,GOLD,CORAL]):circle(im,430+j*110,1710,27,c)
 elif k==6:
  circle(im,540,1090,400,'#303233')
  if t<26.94:
   product(im,'coffee-2',540,1100+80*(1-e),820)
  else:
   v=ease((t-26.94)/.7);product(im,'coffee-2',540-440*v,1130,820-420*v,-8*v)
   product(im,'frappe-0',880-240*v,1090+180*(1-v),380,v*5-5)
  text(im,'VELORA',1650,42,GOLD,True)
 elif k==7:
  n='coffee.png' if t<31.32 else 'iced.png' if t<32.48 else 'pastries.png'
  put(im,panel(n,650),540,1220,1)
 elif k==8:
  put(im,panel('coffee.png',650),540,1220)
  v=ease((u-.85)/1.15)
  # Magnified supplied product moves toward the visible basket.
  if u<2.2:product(im,'coffee-0',540+(250-540)*v,1000+(1750-1000)*v,440*(1-v)+55,v*15)
  circle(im,260,1720,55+35*(1-ease((u-1.8)/.5)),(217,150,47,70))
 elif k==9:
  n='cart-one.png' if t<38.24 else 'cart-two.png'
  # Focus the actual basket dialog at a mobile-readable scale.
  put(im,crop(n,(0,1020,860,1760),860),540,1110)
 elif k==10:
  n='coffee.png' if t<43.02 else 'coffee-en.png'
  put(im,panel(n,650),540,1250)
 elif k==11:
  text(im,'VELORA',695,100,INK,True)
  p=ease(u/.8)
  put(im,panel('iced.png',420),260-100*(1-p),1300,1,8)
  put(im,panel('pastries.png',420),820+100*(1-p),1300,1,-8)
  put(im,panel('welcome.png',480),540,1240+80*(1-p))
 elif k==12:
  circle(im,540,1120,400,'#303233');product(im,'coffee-2',470,1130,770)
  product(im,'frappe-0',840,1300,260,-8)
 elif k==13:
  text(im,'REXO',930,190,CREAM,True)
  d.rectangle((260,1080,820,1087),fill=GOLD)
  if t>55.32:text(im,'منيو يليق بمكانك',1190,72,CREAM)
  text(im,'خلّينا نصمّم منيو مكانك',1510,43,GOLD)
 # Single synchronized readable caption treatment, above the current graphic.
 active=next(((s,en,x) for s,en,x in cues if s<=t<en),None)
 if active and k not in [2,13]:
  s,en,x=active;size=76 if len(x)<23 else 65
  words=x.split();lines=[x]
  if txt(x,size,fg).width>845 and len(words)>4:lines=[' '.join(words[:len(words)//2]),' '.join(words[len(words)//2:])]
  # Correct stable grouping using actual font widths (no moving karaoke).
  for j,line in enumerate(lines):text(im,line,390+j*110+12*(1-ease((t-s)/.16)),size,fg,maxwidth=860)
 return im.convert('RGB')

def render_time(t):
 k,st=scene(t)
 cue=next((s for s,en,x in cues if s<=t<en),st)
 if t<st+.85 or t<cue+.18:return t
 if k==0:return t
 if k==6 and 26.94<t<27.8:return t
 if k==8 and t<36.4:return t
 special=31.32 if k==7 and t>=31.32 else st
 return max(st+.85,cue+.18,special+.01)
@functools.lru_cache(10)
def cached_frame(t):return frame(t).tobytes()
def render():
 cmd=['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','ultrafast','-crf','19','-threads','4','-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709',str(O/'picture.mp4')]
 p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
 for i in range(N):
  p.stdin.write(cached_frame(render_time(i/FPS)))
  if i%150==0:print(f'render {i}/{N}',flush=True)
 p.stdin.close();assert p.wait()==0
 # Original full narration, normalized only; pad less than one video frame.
 subprocess.run(['ffmpeg','-y','-v','error','-i',str(O/'picture.mp4'),'-i',str(ROOT/'voice.mp3'),'-map','0:v','-map','1:a','-c:v','copy','-af',f'loudnorm=I=-16:TP=-1.5:LRA=11,apad=whole_dur={N/FPS}','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',str(O/'Rexo_Velora_Motion_1080x1920.mp4')],check=True)
if __name__=='__main__':
 import sys
 if '--preview' in sys.argv:
  times=[1,5.5,9.7,14,20.8,24,27.9,31.5,35.2,38.8,43.5,46.5,52,56]
  sheet=Image.new('RGB',(7*270,2*480))
  for j,t in enumerate(times):
   im=frame(t);im.save(O/f'frame-{t}.jpg');sheet.paste(im.resize((270,480)),((j%7)*270,(j//7)*480))
  sheet.save(O/'contact.jpg')
 else:render()
