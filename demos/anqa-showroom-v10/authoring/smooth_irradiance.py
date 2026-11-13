# Smooth residual Monte Carlo variance in irradiance only; PBR textures remain untouched.
from pathlib import Path
from PIL import Image
import numpy as np
r=Path(__file__).resolve().parents[1];p=r/'assets/architecture-irradiance.jpg'
x=np.asarray(Image.open(p)).astype('float32')/255
x=np.where(x<=.04045,x/12.92,((x+.055)/1.055)**2.4)
sigma=2.25;radius=7;k=np.exp(-np.arange(-radius,radius+1,dtype='float32')**2/(2*sigma*sigma));k/=k.sum()
for axis in [0,1]:
 pad=[(0,0),(0,0),(0,0)];pad[axis]=(radius,radius);source=np.pad(x,pad,mode='edge');out=np.zeros_like(x)
 for i,w in enumerate(k):
  sl=[slice(None)]*3;sl[axis]=slice(i,i+x.shape[axis]);out+=source[tuple(sl)]*w
 x=out
x=np.where(x<=.0031308,x*12.92,1.055*np.maximum(x,0)**(1/2.4)-.055)
Image.fromarray(np.uint8(np.clip(x,0,1)*255)).save(p,quality=96)
print('Residual irradiance variance smoothed in linear space; material textures unchanged')
