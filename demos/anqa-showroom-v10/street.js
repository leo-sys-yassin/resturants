import * as T from 'three';
import {skipIndoorAreaLights} from './lighting-utils.js';
// Far architecture is photographic; the near pavement, curbs and road provide parallax.
export function createStreet(parent,invalidate){
 const root=new T.Group();root.name='Street outside the boutique';parent.add(root);
 let done;const ready=new Promise(r=>done=r);const image=new T.TextureLoader().load(window.SURFACES['street.png'],()=>{done();invalidate()});image.colorSpace=T.SRGBColorSpace;image.wrapS=T.RepeatWrapping;image.repeat.x=3;image.anisotropy=4;
 const pano=new T.Mesh(new T.CylinderGeometry(20,20,8.4,96,1,true,-Math.PI/2,Math.PI),new T.MeshBasicMaterial({map:image,side:T.BackSide,toneMapped:false,transparent:true,depthWrite:false}));pano.material.onBeforeCompile=s=>{s.fragmentShader=s.fragmentShader.replace('#include <opaque_fragment>','diffuseColor.a*=1.0-smoothstep(.92,1.0,vMapUv.y);\n#include <opaque_fragment>')};pano.renderOrder=-20;pano.position.set(0,3.75,1);pano.name='Opposite shops and trees';root.add(pano);
 const n=256,noise=new Uint8Array(n*n*4);let seed=8417;for(let i=0;i<n*n;i++){seed=(seed*1664525+1013904223)>>>0;const c=105+(seed>>>26);noise[i*4]=noise[i*4+1]=noise[i*4+2]=c;noise[i*4+3]=255}const asphalt=new T.DataTexture(noise,n,n,T.RGBAFormat);asphalt.wrapS=asphalt.wrapT=T.RepeatWrapping;asphalt.repeat.set(24,3);asphalt.needsUpdate=true;
 const road=new T.Mesh(new T.PlaneGeometry(60,6.5),new T.MeshStandardMaterial({color:0x57595a,map:asphalt,bumpMap:asphalt,bumpScale:.002,roughness:1,metalness:0}));road.rotation.x=-Math.PI/2;road.position.set(0,-.135,12.45);road.name='Asphalt road';root.add(road);
 const curb=new T.InstancedMesh(new T.BoxGeometry(60,.12,.18),new T.MeshStandardMaterial({color:0xb3ada3,roughness:.92}),2),matrix=new T.Matrix4();for(let i=0;i<2;i++){matrix.makeTranslation(0,-.074,i?15.78:9.12);curb.setMatrixAt(i,matrix)}curb.name='Street curbs';root.add(curb);
 const walk=new T.Mesh(new T.PlaneGeometry(60,5.2),new T.MeshStandardMaterial({color:0xbeb7aa,roughness:.9}));walk.rotation.x=-Math.PI/2;walk.position.set(0,-.014,18.4);walk.name='Opposite pavement';root.add(walk);
 const dashes=new T.InstancedMesh(new T.BoxGeometry(1.2,.002,.075),new T.MeshStandardMaterial({color:0xd5d2c7,roughness:1}),15);for(let i=0;i<15;i++){matrix.makeTranslation(-28+i*4,-.132,12.45);dashes.setMatrixAt(i,matrix)}root.add(dashes);
 root.traverse(m=>{if(m.isMesh&&m.material.isMeshStandardMaterial){m.material.onBeforeCompile=skipIndoorAreaLights;m.material.customProgramCacheKey=()=> 'street-daylight-v8'}});
 return {root,ready};
}
