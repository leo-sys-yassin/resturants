from PIL import Image
import numpy as np
from pathlib import Path
W=Path(__file__).resolve().parent/'work';A=Path(__file__).resolve().parents[1]/'assets'
x=np.asarray(Image.open(A/'architecture-light.jpg')).astype('float32')/255
x=np.where(x<=.04045,x/12.92,((x+.055)/1.055)**2.4)
with (W/'light.pfm').open('wb') as f:
 f.write(f'PF\n{x.shape[1]} {x.shape[0]}\n-1.0\n'.encode());np.flipud(x).astype('<f4').tofile(f)
