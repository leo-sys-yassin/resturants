import * as T from 'three';
import {RoundedBoxGeometry} from 'three/addons/geometries/RoundedBoxGeometry.js';
export function installInteriorLabels(parent,entrance,surfaces,invalidate){
 const items=[];
 function text(value,x,y,z,w,h,rot=0,font='Cormorant',color='#ecd08a',kind='category'){
  const c=document.createElement('canvas');c.width=1536;c.height=Math.ceil(1536*h/w);const ctx=c.getContext('2d');let fs=c.height*.74;ctx.font=`${fs}px ${font}`;while(ctx.measureText(value).width>1430){fs*=.96;ctx.font=`${fs}px ${font}`}ctx.textAlign='center';ctx.textBaseline='middle';ctx.lineWidth=1.2;ctx.strokeStyle='#4d371c';ctx.strokeText(value,c.width/2,c.height/2);ctx.fillStyle=color;ctx.fillText(value,c.width/2,c.height/2);
  const map=new T.CanvasTexture(c);map.colorSpace=T.SRGBColorSpace;const m=new T.Mesh(new T.PlaneGeometry(w,h),new T.MeshBasicMaterial({map,transparent:true,depthWrite:false,side:T.DoubleSide}));m.position.set(x,y,z);m.rotation.y=rot;m.name='Gold '+value;m.userData.label=value;m.userData.labelKind=kind;parent.add(m);items.push(m);return m;
 }
 const backing=new T.Mesh(new RoundedBoxGeometry(1.60,1.24,.028,2,.012),surfaces.get('TeakSurface'));backing.position.set(-1.99,2.05,-2.78);backing.name='Teak backing behind interior gold brand';parent.add(backing);
 const gold=new T.MeshStandardMaterial({color:0xe2b85c,metalness:.40,roughness:.52,emissive:0x90651f,emissiveIntensity:.28,envMapIntensity:.8});const sign=entrance.sign.clone(true);sign.scale.multiplyScalar(1.28/2.22);sign.position.set(-1.99,2.13,-2.74);sign.traverse(m=>{if(m.isMesh)m.material=gold});sign.name='Interior gold ANQA lettering';parent.add(sign);
 const ready=document.fonts.ready.then(()=>{
  text('أناقة',-1.99,1.80,-2.73,.76,.24,0,'Amiri','#f0d085','brand');text('THE ATELIER',-1.99,1.53,-2.73,1.08,.105,0,'Cormorant','#e4c277','brand');
  text('THE NEXT CHAPTER',0,1.96,-2.60,1.3,.13,0,'Cormorant','#d3b16b','door');text('COMING SOON',0,1.72,-2.60,.74,.08,0,'Cormorant','#cba45b','door');
  for(let k=0;k<3;k++){const z=-1.85+k*1.85,plate=new T.Mesh(new RoundedBoxGeometry(.018,.20,1.50,2,.005),surfaces.get('TeakSurface'));plate.position.set(-2.582,3.075,z);plate.name='Teak footwear header';parent.add(plate);text('FOOTWEAR',-2.570,3.075,z,1.15,.13,Math.PI/2);}
  for(const [a,b,value] of [[-2.55,.25,'KNITWEAR'],[.50,3.20,'ESSENTIALS'],[3.25,4.20,'SOON']]){
   const width=Math.min(1.4,b-a-.12),plate=new T.Mesh(new T.BoxGeometry(.025,.16,width),surfaces.get('TeakSurface'));plate.position.set(2.435,3.145,(a+b)/2);plate.name='Teak stand top label plate';parent.add(plate);text(value,2.418,3.145,(a+b)/2,width-.08,.115,-Math.PI/2);
  }
  const accessories=new T.Mesh(new RoundedBoxGeometry(1.55,.20,.025,2,.005),surfaces.get('TeakSurface'));accessories.position.set(2.04,3.08,-2.77);accessories.name='Teak accessories header';parent.add(accessories);text('ACCESSORIES',2.04,3.08,-2.751,1.35,.12);invalidate();return items;
 });
 return {items,ready,sign};
}
