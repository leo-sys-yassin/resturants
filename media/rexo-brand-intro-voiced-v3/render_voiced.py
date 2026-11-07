from pathlib import Path
import json,math,subprocess,functools
import numpy as np
from PIL import Image,ImageDraw
import render_v2 as v
R=Path(__file__).resolve().parent;O=R/'delivery';O.mkdir(exist_ok=True)
AUDIO=R/'voice.mp3'
raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(AUDIO),'-f','f32le','-ac','1','-ar','16000','-'])
SOURCE_DURATION=len(raw)/4/16000;N=math.ceil(SOURCE_DURATION*30);DURATION=N/30
SC=[(0,3.08,'idea'),(3.08,4.94,'who'),(4.94,8.34,'chat'),(8.34,13.12,'chaos'),(13.12,16.5,'brand'),(16.5,20.28,'web'),(20.28,23.34,'custom'),(23.34,28.7,'order'),(28.7,35.06,'ai'),(35.06,39.14,'connect'),(39.14,45.74,'why'),(45.74,49.84,'process'),(49.84,DURATION,'end')]
OLD={k:(s,e) for s,e,k in v.SC}
E=v.E;text=v.text;rr=v.rr;put=v.put;title=v.title

def interp(x,knots):return float(np.interp(x,[a for a,b in knots],[b for a,b in knots]))
def frame(t):
 s,e,k=next(x for x in SC if x[0]<=t<x[1]);u=t-s
 if k=='chat':
  im=Image.new('RGBA',(1080,1920),v.D);title(im,'شو بدك لمشروعك؟',400,94,v.C,u)
  items=[(5.26,'موقع للمشروع.','globe'),(5.8,'وتطبيق موبايل.','smartphone'),(6.92,'وبوت يساعد الزباين.','bot')]
  for j,(cue,tx,ic) in enumerate(items):
   q=E((t-cue)/.22)
   if q<=0:continue
   cx=580 if j%2==0 else 480;cy=790+j*250+25*(1-q)
   rr(im,(cx-390,cy-88,cx+390,cy+88),v.TEAL if j==1 else '#242b2b',40)
   text(im,tx,cx-35,cy,54,v.D if j==1 else v.C,alpha=q,maxwidth=610)
   put(im,v.b.icon(ic,53,v.D if j==1 else v.TEAL),cx+320,cy,alpha=q)
  return im.convert('RGB')
 if k=='chaos':
  im=Image.new('RGBA',(1080,1920),v.D)
  for cue,tx,y,col in [(8.88,'كل جزء عند جهة.',530,v.C),(10.5,'متابعة أكتر.',800,v.C),(11.58,'والفكرة وحدة.',1150,v.TEAL)]:
   q=E((t-cue)/.22);text(im,tx,540,y+25*(1-q),115,col,alpha=q)
  return im.convert('RGB')
 if k=='end':
  im=Image.new('RGBA',(1080,1920),v.GREEN);v.disk(im,540,1050,175,v.C);put(im,v.mark('full',285),540,1050)
  if t<52.6:text(im,'REXO',540,1290,90,v.C,True)
  if t>=50.56:title(im,'رؤيتك.',450,174,v.C,t-50.56)
  if t>=51.58:title(im,'وتقنيتنا.',705,171,v.B,t-51.58)
  if t>=52.6:title(im,'احكيلنا عن فكرتك',1390,79,v.C,t-52.6)
  if t>=54.48:v.pill(im,'@rexo.web',1585,v.C,v.G)
  return im.convert('RGB')
 old_s,old_e=OLD[k]
 if k=='why':local=interp(u,[(0,0),(1.52,.65),(2.9,1.9),(4.38,3.15),(6.6,5.99)])
 elif k=='process':local=interp(u,[(0,.5),(1.14,1.9),(2.10,2.8),(3,3.7),(4.1,4.99)])
 elif k=='ai':local=interp(u,[(0,0),(2.88,2.8),(4.7,3.4),(6.36,5.99)])
 elif k=='brand':local=interp(u,[(0,0),(.36,.8),(1.42,1.3),(2.24,1.65),(3.38,4.99)])
 else:local=u/(e-s)*(old_e-old_s)
 return v.frame(min(old_e-1/1000,old_s+local))

@functools.lru_cache(3)
def pixels(t):return frame(t).tobytes()
def render():
 picture=O/'picture.mp4';out=O/'Rexo_Brand_Intro_Voiced_v3.mp4'
 p=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','30','-i','-','-an','-c:v','libx264','-preset','ultrafast','-crf','19','-threads','3','-pix_fmt','yuv420p',str(picture)],stdin=subprocess.PIPE)
 for i in range(N):
  t=i/30
  # Stable holds are deliberate and local to artwork. Speech remains the original recording.
  if 7.4<t<8.34:t=7.4
  if 12.1<t<13.12:t=12.1
  if t>55:t=55
  p.stdin.write(pixels(t))
  if i%180==0:print(f'{i}/{N}',flush=True)
 p.stdin.close();assert p.wait()==0
 subprocess.run(['ffmpeg','-y','-v','error','-i',str(picture),'-i',str(AUDIO),'-map','0:v:0','-map','1:a:0','-c:v','copy','-af',f'loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000,apad=whole_dur={DURATION}','-c:a','aac','-b:a','192k','-movflags','+faststart',str(out)],check=True)
 json.dump({'duration':DURATION,'original_audio_duration':SOURCE_DURATION,'fps':30,'dimensions':[1080,1920],'audio_playback_rate':1.0,'audio_processing':'loudness normalization only; no music','scenes':SC,'alignment':'automatic word alignment; key brand and service cues mapped to original recording','listening_review':'not_performed'},open(O/'timeline.json','w'),ensure_ascii=False,indent=2)
if __name__=='__main__':
 import sys
 if '--preview' in sys.argv:
  sheet=Image.new('RGB',(5*270,3*480),v.C)
  for j,t in enumerate([2,4.5,7.6,12.2,15.8,19.5,22.8,27,34.5,38.6,44.7,49.2,56]):
   im=frame(t);im.save(O/f'frame-{t}.jpg');sheet.paste(im.resize((270,480)),((j%5)*270,(j//5)*480))
  sheet.save(O/'Storyboard_voiced.jpg')
 else:render()
