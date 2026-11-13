import * as T from 'three';
import {skipIndoorAreaLights} from './lighting-utils.js';
export function createSurfaceLibrary(invalidate){
 const tasks=[],loader=new T.TextureLoader(),textures={};
 function load(name,color=false){let done;tasks.push(new Promise(r=>done=r));const tex=loader.load(window.SURFACES[name],()=>{done();invalidate()});tex.wrapS=tex.wrapT=T.RepeatWrapping;tex.anisotropy=16;if(color)tex.colorSpace=T.SRGBColorSpace;textures[name]=tex;return tex}
 const plaster=load('plaster-color.jpg',true),plasterNormal=load('plaster-normal.jpg'),plasterRough=load('plaster-rough.jpg'),walnut=load('walnut-color.jpg',true),walnutNormal=load('walnut-normal.jpg'),walnutRough=load('walnut-rough.jpg');
 const facade=load('facade-color.png',true),floor=load('floor-color.png',true),light=load('architecture-irradiance.jpg',true);light.channel=1;light.flipY=false;light.wrapS=light.wrapT=T.ClampToEdgeWrapping;
 const grain=new Uint8Array(128*128*4);let seed=18;for(let i=0;i<128*128;i++){seed=(seed*1664525+1013904223)>>>0;const v=230+(seed>>>28);grain[i*4]=grain[i*4+1]=grain[i*4+2]=v;grain[i*4+3]=255}const powder=new T.DataTexture(grain,128,128,T.RGBAFormat);powder.wrapS=powder.wrapT=T.RepeatWrapping;powder.repeat.set(8,8);powder.needsUpdate=true;
 const cache=new Map();
 function get(name,baked=false){const key=name+'|'+baked;if(cache.has(key))return cache.get(key);let m;
  if(name.includes('glow'))m=new T.MeshBasicMaterial({color:name==='WarmLED_Diffuser_glow'?0xffd4a3:0xfff1da,toneMapped:false});
  else if(name==='WarmPlaster')m=new T.MeshStandardMaterial({name:'Warm beige fine plaster',color:0xcfb295,map:plaster,normalMap:plasterNormal,normalScale:new T.Vector2(.12,.12),roughnessMap:plasterRough,roughness:.94,metalness:0,envMapIntensity:.18});
  else if(name==='WalnutSurface')m=new T.MeshStandardMaterial({name:'Natural walnut satin furniture',color:0xffffff,map:walnut,normalMap:walnutNormal,normalScale:new T.Vector2(.36,.36),roughnessMap:walnutRough,roughness:.80,metalness:0,envMapIntensity:.22});
  else if(name==='FacadeTravertine')m=new T.MeshStandardMaterial({name:'Original vein-cut travertine facade',map:facade,bumpMap:facade,bumpScale:.009,color:0xebd7bc,roughness:.8,envMapIntensity:.2});
  else if(name==='FloorStone')m=new T.MeshStandardMaterial({name:'Pitted limestone floor',map:floor,bumpMap:floor,bumpScale:.003,color:0xd8cfc3,roughness:.78,envMapIntensity:.15});
  else if(name==='BlackSteel'||name==='Bronze')m=new T.MeshStandardMaterial({name:'Matte black powder-coated steel',color:0x1e1e1e,bumpMap:powder,bumpScale:.0008,roughnessMap:powder,roughness:.98,metalness:.10,envMapIntensity:.10});
  else m=new T.MeshStandardMaterial({color:name==='Upholstery'?0xbbae96:name==='GreigeCeiling'?0xa49e94:0x211e19,roughness:.95,envMapIntensity:.1});
  if(baked&&!m.isMeshBasicMaterial){m.lightMap=light;m.lightMapIntensity=1}
  if(!m.isMeshBasicMaterial){m.onBeforeCompile=shader=>{skipIndoorAreaLights(shader);if(name==='WalnutSurface')shader.fragmentShader=shader.fragmentShader.replace('#include <roughnessmap_fragment>','#include <roughnessmap_fragment>\nroughnessFactor=max(roughnessFactor,.58);');if(baked)shader.fragmentShader=shader.fragmentShader.replace('#include <lights_fragment_end>','#include <lights_fragment_end>\nreflectedLight.directDiffuse=vec3(0.0);reflectedLight.directSpecular=vec3(0.0);')
 if(name==='WalnutSurface'&&baked){
  shader.vertexShader=shader.vertexShader.replace('#include <common>','#include <common>\nvarying vec3 vFurnitureLightPosition;').replace('#include <project_vertex>','#include <project_vertex>\nvFurnitureLightPosition=(modelMatrix*vec4(transformed,1.0)).xyz;');
  shader.fragmentShader=shader.fragmentShader.replace('#include <common>',`#include <common>
 varying vec3 vFurnitureLightPosition;
 float furnitureLED(vec3 p,vec3 n,vec3 a,vec3 b){vec3 ab=b-a;vec3 q=a+ab*clamp(dot(p-a,ab)/dot(ab,ab),0.0,1.0);vec3 l=q-p;float d2=dot(l,l);return .030*(.20+.80*max(dot(n,normalize(l)),0.0))/(.008+d2);}
 `);
  shader.fragmentShader=shader.fragmentShader.replace('reflectedLight.directSpecular=vec3(0.0);',`reflectedLight.directSpecular=vec3(0.0);
 vec3 fp=vFurnitureLightPosition;
 if(abs(fp.x)<.785&&abs(fp.z-.75)<.58&&fp.y>.14&&fp.y<.683){
  vec3 wn=inverseTransformDirection(normal,viewMatrix);
  float e=furnitureLED(fp,wn,vec3(-.80,.670,.21),vec3(-.80,.670,1.29))+furnitureLED(fp,wn,vec3(.80,.670,.21),vec3(.80,.670,1.29))+furnitureLED(fp,wn,vec3(-.79,.670,.19),vec3(.79,.670,.19))+furnitureLED(fp,wn,vec3(-.79,.670,1.31),vec3(.79,.670,1.31));
  reflectedLight.indirectDiffuse+=vec3(1.0,.695,.431)*min(e,2.0)*BRDF_Lambert(material.diffuseColor);
 }
 `);
 }
 };m.customProgramCacheKey=()=>name+'-walnut-plaster-led-irradiance-'+baked}
  m.userData.surface=name;m.userData.baked=baked;cache.set(key,m);return m;
 }
 function mapPhysical(mesh){
  const g=mesh.geometry,p=g.attributes.position,n=g.attributes.normal,uv=g.attributes.uv;if(!uv||!n)return;mesh.updateWorldMatrix(true,false);const v=new T.Vector3(),normal=new T.Vector3(),nm=new T.Matrix3().getNormalMatrix(mesh.matrixWorld);
  for(let i=0;i<p.count;i++){v.fromBufferAttribute(p,i).applyMatrix4(mesh.matrixWorld);normal.fromBufferAttribute(n,i).applyMatrix3(nm);if(Math.abs(normal.y)>.7)uv.setXY(i,v.x/1.2,v.z/1.2);else if(Math.abs(normal.x)>.7)uv.setXY(i,v.z/1.2,v.y/2.4);else uv.setXY(i,v.x/1.2,v.y/2.4)}uv.needsUpdate=true;
 }
 return {get,textures,mapPhysical,ready:Promise.all(tasks)};
}
