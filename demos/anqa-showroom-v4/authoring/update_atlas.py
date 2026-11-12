from PIL import Image
from pathlib import Path
import numpy as np
W=Path(__file__).resolve().parent/'work';A=Path(__file__).resolve().parents[1]/'assets'
with (W/'light-denoised.pfm').open('rb') as f:
 assert f.readline().strip()==b'PF';w,h=map(int,f.readline().split());scale=float(f.readline());x=np.flipud(np.fromfile(f,'<f4').reshape(h,w,3))
x=np.maximum(x,0);x=np.where(x<=.0031308,x*12.92,1.055*x**(1/2.4)-.055)
# Calibrate the architectural palette toward neutral limestone and soft walnut.
luma=x@np.array([.2126,.7152,.0722]);x=luma[:,:,None]+(x-luma[:,:,None])*.70
Image.fromarray(np.uint8(np.clip(x,0,1)*255)).save(A/'architecture-light.jpg',quality=95)
