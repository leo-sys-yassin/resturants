from pathlib import Path
from PIL import Image
import numpy as np,subprocess
r=Path(__file__).resolve().parents[1];w=r/'authoring/work';a=r/'assets';p=a/'architecture-irradiance.jpg'
x=np.asarray(Image.open(p).resize((3072,3072),Image.Resampling.LANCZOS)).astype('float32')/255;x=np.where(x<=.04045,x/12.92,((x+.055)/1.055)**2.4)
with (w/'light.pfm').open('wb') as f:f.write(f'PF\n{x.shape[1]} {x.shape[0]}\n-1.0\n'.encode());np.flipud(x).astype('<f4').tofile(f)
subprocess.run(['/workspace/work/showroom-build/oidn-2.5.1.x86_64.linux/bin/oidnDenoise','--hdr',str(w/'light.pfm'),'-o',str(w/'light-denoised.pfm')],check=True)
with (w/'light-denoised.pfm').open('rb') as f:
 assert f.readline().strip()==b'PF';width,height=map(int,f.readline().split());f.readline();x=np.flipud(np.fromfile(f,'<f4').reshape(height,width,3))
x=np.maximum(x,0);x=np.where(x<=.0031308,x*12.92,1.055*x**(1/2.4)-.055);Image.fromarray(np.uint8(np.clip(x,0,1)*255)).save(p,quality=95)
