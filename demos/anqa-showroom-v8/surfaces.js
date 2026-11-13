import * as T from 'three';
import {skipIndoorAreaLights} from './lighting-utils.js';
export function createSurfaceLibrary(invalidate){
 const tasks=[],loader=new T.TextureLoader(),textures={};
 function load(name,color=false){let done;tasks.push(new Promise(r=>done=r));const tex=loader.load(window.SURFACES[name],()=>{done();invalidate()});tex.wrapS=tex.wrapT=T.RepeatWrapping;tex.anisotropy=8;if(color)tex.colorSpace=T.SRGBColorSpace;textures[name]=tex;return tex}
 const pine=load('pine-color.png',true),teak=load('teak-color.jpg',true),teakNormal=load('teak-normal.jpg'),teakRough=load('teak-rough.jpg');
 const facade=load('facade-color.png',true),floor=load('floor-color.png',true),light=load('architecture-irradiance.jpg',true);light.channel=1;light.flipY=false;light.wrapS=light.wrapT=T.ClampToEdgeWrapping;
 const grain=new Uint8Array(128*128*4);let seed=18;for(let i=0;i<128*128;i++){seed=(seed*1664525+1013904223)>>>0;const v=230+(seed>>>28);grain[i*4]=grain[i*4+1]=grain[i*4+2]=v;grain[i*4+3]=255}const powder=new T.DataTexture(grain,128,128,T.RGBAFormat);powder.wrapS=powder.wrapT=T.RepeatWrapping;powder.repeat.set(8,8);powder.needsUpdate=true;
 const cache=new Map();
 function get(name,baked=false){const key=name+'|'+baked;if(cache.has(key))return cache.get(key);let m;
  if(name.includes('glow'))m=new T.MeshBasicMaterial({color:0xfff1da,toneMapped:false});
  else if(name==='PineWall')m=new T.MeshStandardMaterial({name:'Natural beige pine walls',color:0xf4f1e9,map:pine,bumpMap:pine,bumpScale:.004,roughness:.84,metalness:0,envMapIntensity:.18});
  else if(name==='TeakSurface')m=new T.MeshStandardMaterial({name:'Warm teak furniture',color:new T.Color().setRGB(.88,.68,.45),map:teak,normalMap:teakNormal,normalScale:new T.Vector2(.4,.4),roughnessMap:teakRough,roughness:.90,metalness:0,envMapIntensity:.22});
  else if(name==='FacadeTravertine')m=new T.MeshStandardMaterial({name:'Original vein-cut travertine facade',map:facade,bumpMap:facade,bumpScale:.009,color:0xf0eae1,roughness:.8,envMapIntensity:.2});
  else if(name==='FloorStone')m=new T.MeshStandardMaterial({name:'Pitted limestone floor',map:floor,bumpMap:floor,bumpScale:.012,color:0xf2eee6,roughness:.78,envMapIntensity:.15});
  else if(name==='BlackSteel'||name==='Bronze')m=new T.MeshStandardMaterial({name:'Matte black powder-coated steel',color:0x252626,bumpMap:powder,bumpScale:.0008,roughnessMap:powder,roughness:.98,metalness:.10,envMapIntensity:.10});
  else m=new T.MeshStandardMaterial({color:name==='Upholstery'?0xbbae96:name==='GreigeCeiling'?0xa49e94:0x211e19,roughness:.95,envMapIntensity:.1});
  if(baked&&!m.isMeshBasicMaterial){m.lightMap=light;m.lightMapIntensity=1}
  if(!m.isMeshBasicMaterial){m.onBeforeCompile=shader=>{skipIndoorAreaLights(shader);if(name==='TeakSurface')shader.fragmentShader=shader.fragmentShader.replace('#include <roughnessmap_fragment>','#include <roughnessmap_fragment>\nroughnessFactor=max(roughnessFactor,.65);');if(baked)shader.fragmentShader=shader.fragmentShader.replace('#include <lights_fragment_end>','#include <lights_fragment_end>\nreflectedLight.directDiffuse=vec3(0.0);reflectedLight.directSpecular=vec3(0.0);')};m.customProgramCacheKey=()=>name+'-pine-teak-fast-irradiance-'+baked}
  m.userData.surface=name;m.userData.baked=baked;cache.set(key,m);return m;
 }
 return {get,textures,ready:Promise.all(tasks)};
}
