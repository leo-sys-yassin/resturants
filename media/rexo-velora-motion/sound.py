import wave,math
import numpy as np
from pathlib import Path
ROOT=Path(__file__).resolve().parent
R=48000;D=1729/30;n=round(D*R);y=np.zeros(n,dtype=np.float64);rng=np.random.default_rng(2026)
# Original restrained warm keyboard bed, composed for this edit.
chords=[[130.81,164.81,196.00],[110,130.81,164.81],[87.31,130.81,174.61],[98,146.83,196]]
for i,start in enumerate(np.arange(0,D,2.5)):
 for j,f in enumerate(chords[(i//2)%4]):
  st=start+j*.32;ix=int(st*R);tt=np.arange(min(int(2.8*R),n-ix))/R
  if len(tt)==0:continue
  env=(1-np.exp(-tt*45))*np.exp(-tt*2.1)
  sig=(np.sin(2*np.pi*f*tt)+.22*np.sin(2*np.pi*f*2*tt)+.09*np.sin(2*np.pi*f*3*tt))*env*.012
  y[ix:ix+len(sig)]+=sig
for st in [4.12,18.86,23,30.1,33.98,40.58,44.06,54.44]:
 ix=int(st*R);tt=np.arange(int(.24*R))/R;v=rng.normal(0,1,len(tt));v=np.convolve(v,np.ones(20)/20,mode='same');v*=np.sin(np.pi*tt/.24)**2*.017;y[ix:ix+len(v)]+=v
y*=np.minimum(np.arange(n)/R/1.5,1)*np.minimum((n-np.arange(n))/R/1.7,1)
with wave.open(str(ROOT/'delivery/music.wav'),'wb') as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(R);f.writeframes((np.clip(y,-1,1)*32767).astype('<i2').tobytes())
