import * as T from 'three';
export function createSurfaceLibrary(invalidate){
 const tasks=[],loader=new T.TextureLoader(),textures={};
 function load(name,color=false){let done;tasks.push(new Promise(r=>done=r));const tex=loader.load(window.SURFACES[name],()=>{done();invalidate()});tex.wrapS=tex.wrapT=T.RepeatWrapping;tex.anisotropy=8;if(color)tex.colorSpace=T.SRGBColorSpace;textures[name]=tex;return tex}
 const oak=load('oak-color.jpg',true),oakNormal=load('oak-normal.jpg'),oakRough=load('oak-rough.jpg');
 const facade=load('facade-color.png',true),floor=load('floor-color.png',true),cabinet=load('cabinet-color.jpg',true),cabinetNormal=load('cabinet-normal.jpg'),cabinetRough=load('cabinet-rough.jpg');
 const light=load('architecture-irradiance.jpg',true);light.channel=1;light.flipY=false;light.wrapS=light.wrapT=T.ClampToEdgeWrapping;
 const cache=new Map();
 function get(name,baked=false){const key=name+'|'+baked;if(cache.has(key))return cache.get(key);let m;
  if(name.includes('glow'))m=new T.MeshBasicMaterial({color:0xffd6a0,toneMapped:false});
  else if(name.startsWith('Oak'))m=new T.MeshStandardMaterial({name:'Dark oak — detailed veneer',color:new T.Color().setRGB(.38,.29,.20),map:oak,normalMap:oakNormal,normalScale:new T.Vector2(1.10,1.10),roughnessMap:oakRough,roughness:.67,metalness:0,envMapIntensity:.35});
  else if(name==='FacadeTravertine')m=new T.MeshStandardMaterial({name:'Original vein-cut travertine facade',map:facade,bumpMap:facade,bumpScale:.009,color:0xf0eae1,roughness:.77,envMapIntensity:.35});
  else if(name==='FloorStone')m=new T.MeshPhysicalMaterial({name:'Pitted limestone floor',map:floor,bumpMap:floor,bumpScale:.016,color:new T.Color().setRGB(1.05,1.05,1.00),roughness:.66,clearcoat:.10,clearcoatRoughness:.4,envMapIntensity:.3});
  else if(name==='CabinetStone')m=new T.MeshPhysicalMaterial({name:'Smooth cream stone boards and cabinets',map:cabinet,normalMap:cabinetNormal,normalScale:new T.Vector2(.16,.16),roughnessMap:cabinetRough,color:new T.Color().setRGB(1.5,1.4,1.2),roughness:.8,clearcoat:.12,envMapIntensity:.3});
  else if(name==='BlackSteel')m=new T.MeshStandardMaterial({color:0x24231f,metalness:.72,roughness:.36,envMapIntensity:.6});
  else if(name==='Bronze')m=new T.MeshStandardMaterial({color:0x4b4032,metalness:.85,roughness:.27,envMapIntensity:.7});
  else m=new T.MeshStandardMaterial({color:name==='Upholstery'?0xbbae96:name==='WhiteCeiling'?0xbab0a0:0x211d18,roughness:.85,envMapIntensity:.2});
  if(baked&&!m.isMeshBasicMaterial){m.lightMap=light;m.lightMapIntensity=1}
  if(!m.isMeshBasicMaterial){m.onBeforeCompile=shader=>{if(name.startsWith('Oak')||name==='CabinetStone')shader.fragmentShader=shader.fragmentShader.replace('#include <roughnessmap_fragment>','#include <roughnessmap_fragment>\nroughnessFactor=max(roughnessFactor,'+(name.startsWith('Oak')?'.70':'.50')+');');if(baked)shader.fragmentShader=shader.fragmentShader.replace('#include <lights_fragment_end>','#include <lights_fragment_end>\nreflectedLight.directDiffuse=vec3(0.0);')};m.customProgramCacheKey=()=>name+'-irradiance-v3-'+baked}
  m.userData.surface=name;m.userData.baked=baked;cache.set(key,m);return m;
 }
 return {get,textures,ready:Promise.all(tasks)};
}
