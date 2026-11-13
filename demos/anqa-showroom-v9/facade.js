import * as T from 'three';
import {skipIndoorAreaLights} from './lighting-utils.js';
import {SVGLoader} from 'three/addons/loaders/SVGLoader.js';
import {signSVG} from './sign-paths.js';
export function createFacade(parent,surfaces,ready){
 const group=new T.Group();group.name='ANQA solid facade and rigid entrance';parent.add(group);const doors=[];
 const stone=surfaces.get('FacadeTravertine').clone();stone.name='Original travertine exterior stone';stone.onBeforeCompile=skipIndoorAreaLights;stone.customProgramCacheKey=()=> 'stone-daylight-v8';stone.roughness=.78;stone.bumpScale=.012;
 const oak=surfaces.get('WarmPlaster');const metal=surfaces.get('BlackSteel');
 const glass=new T.MeshPhysicalMaterial({name:'Clear architectural glazing',color:0xdbe1d8,transparent:true,opacity:.035,roughness:.025,metalness:0,clearcoat:1,clearcoatRoughness:.025,envMapIntensity:1.5,depthWrite:false,side:T.DoubleSide});glass.forceSinglePass=true;glass.onBeforeCompile=skipIndoorAreaLights;glass.customProgramCacheKey=()=> 'glazing-daylight-v8';
 function box(w,h,d,x,y,z,mat=metal,p=group){const m=new T.Mesh(new T.BoxGeometry(w,h,d),mat);m.position.set(x,y,z);p.add(m);return m}
 function cyl(a,b,r=.012,mat=metal,p=group){const v=new T.Vector3(...b).sub(new T.Vector3(...a));const m=new T.Mesh(new T.CylinderGeometry(r,r,v.length(),20),mat);m.position.fromArray(a).addScaledVector(v,.5);m.quaternion.setFromUnitVectors(new T.Vector3(0,1,0),v.normalize());p.add(m);return m}
 function uShape(outerWidth,outerTop,innerWidth,innerTop,r){const s=new T.Shape();s.moveTo(-outerWidth,-.12);s.lineTo(-innerWidth,-.12);s.lineTo(-innerWidth,innerTop-r);s.quadraticCurveTo(-innerWidth,innerTop,-innerWidth+r,innerTop);s.lineTo(innerWidth-r,innerTop);s.quadraticCurveTo(innerWidth,innerTop,innerWidth,innerTop-r);s.lineTo(innerWidth,-.12);s.lineTo(outerWidth,-.12);s.lineTo(outerWidth,outerTop);s.lineTo(-outerWidth,outerTop);s.closePath();return s}
 const stoneGeo=new T.ExtrudeGeometry(uShape(20,10,3.12,3.65,.68),{depth:.18,steps:1,bevelEnabled:true,bevelSize:.008,bevelThickness:.008,bevelSegments:2,curveSegments:40});
 const uv=stoneGeo.attributes.uv,pos=stoneGeo.attributes.position,n=stoneGeo.attributes.normal;
 for(let i=0;i<pos.count;i++){if(Math.abs(n.getZ(i))>.7)uv.setXY(i,pos.getX(i)/2.4,pos.getY(i)/2.4);else uv.setXY(i,pos.getY(i)/2.4,pos.getZ(i)/2.4)}
 // Opaque front/back faces share two contiguous batches, not one draw per bevel segment.
 const frontFaces=[],backFaces=[];for(let i=0;i<pos.count;i+=3)(n.getZ(i)<-.7?backFaces:frontFaces).push(i,i+1,i+2);stoneGeo.setIndex([...frontFaces,...backFaces]);stoneGeo.clearGroups();stoneGeo.addGroup(0,frontFaces.length,0);stoneGeo.addGroup(frontFaces.length,backFaces.length,1);
 const facade=new T.Mesh(stoneGeo,[stone,oak]);facade.name='Stone stops outside the arch';facade.position.z=5.04;group.add(facade);
 // The recessed, rounded stone surround retains the reference entrance's carved depth.
 function rimPoints(x,top,r,z){const pts=[],v=(a,b)=>new T.Vector3(a,b,z);for(let i=0;i<=24;i++)pts.push(v(-x,.02+(top-r-.02)*i/24));for(let i=1;i<=20;i++){const t=i/20,a=(1-t)*(1-t),b=2*(1-t)*t,c=t*t;pts.push(v(a*(-x)+b*(-x)+c*(-x+r),a*(top-r)+b*top+c*top))}for(let i=1;i<=32;i++)pts.push(v(-x+r+(2*x-2*r)*i/32,top));for(let i=1;i<=20;i++){const t=i/20,a=(1-t)*(1-t),b=2*(1-t)*t,c=t*t;pts.push(v(a*(x-r)+b*x+c*x,a*top+b*top+c*(top-r)))}for(let i=1;i<=24;i++)pts.push(v(x,(top-r)*(1-i/24)+.02*i/24));return pts}
 const outer=rimPoints(3.12,3.65,.68,5.224),inner=rimPoints(2.72,3.25,.48,5.05),vs=[],uvs=[],indices=[];
 for(let i=0;i<outer.length;i++){for(const p of [outer[i],inner[i]]){vs.push(p.x,p.y,p.z);uvs.push(p.x/2.4,p.y/2.4)}if(i<outer.length-1){const a=i*2;indices.push(a,a+1,a+2,a+1,a+3,a+2)}}
 const rg=new T.BufferGeometry();rg.setAttribute('position',new T.Float32BufferAttribute(vs,3));rg.setAttribute('uv',new T.Float32BufferAttribute(uvs,2));rg.setIndex(indices);rg.computeVertexNormals();const rim=new T.Mesh(rg,stone);rim.name='Carved stone arch surround';group.add(rim);

 const liningGeo=new T.ExtrudeGeometry(uShape(3.02,3.40,2.68,3.21,.45),{depth:.16,bevelEnabled:false,curveSegments:40});
 const lpos=liningGeo.attributes.position,luv=liningGeo.attributes.uv;for(let i=0;i<lpos.count;i++)luv.setXY(i,Math.abs(lpos.getX(i))>2.35?lpos.getY(i)/2.4:lpos.getX(i)/1.2,Math.abs(lpos.getX(i))>2.35?lpos.getX(i)/.3:lpos.getY(i)/.4);
 const lining=new T.Mesh(liningGeo,surfaces.get('WalnutSurface'));lining.name='Walnut interior entrance trim';lining.position.z=4.88;group.add(lining);surfaces.mapPhysical(lining);
 function archPath(x,top,r,z){const p=new T.CurvePath();const v=(a,b)=>new T.Vector3(a,b,z);p.add(new T.LineCurve3(v(-x,.02),v(-x,top-r)));p.add(new T.QuadraticBezierCurve3(v(-x,top-r),v(-x,top),v(-x+r,top)));p.add(new T.LineCurve3(v(-x+r,top),v(x-r,top)));p.add(new T.QuadraticBezierCurve3(v(x-r,top),v(x,top),v(x,top-r)));p.add(new T.LineCurve3(v(x,top-r),v(x,.02)));return p}
 const border=new T.Mesh(new T.TubeGeometry(archPath(2.67,3.20,.45,4.995),160,.018,12,false),metal);border.name='Continuous fixed arched frame';group.add(border);
 const ledMat=new T.MeshBasicMaterial({color:0xffd79d,toneMapped:false});const light=new T.Mesh(new T.TubeGeometry(archPath(3.04,3.57,.64,5.196),160,.008,8,false),ledMat);light.name='Warm continuous portal backlight';group.add(light);
 box(5.34,.042,.055,0,2.68,4.995);box(5.34,.028,.050,0,.025,4.995);
 for(const side of [-1,1]){
  box(.032,3.18,.055,side*1.4,1.61,4.995);
  box(1.225,2.615,.009,side*2.035,1.345,4.997,glass);
  const pivot=new T.Group();pivot.position.set(side*1.4,0,4.995);pivot.name=side<0?'Left rigid door hinge':'Right rigid door hinge';group.add(pivot);doors.push({pivot,side});const cx=-side*.709;
  const leaf=box(1.326,2.570,.009,cx,1.330,0,glass,pivot);leaf.name='Rigid flat door glazing';
  for(const x of [-side*.033,-side*1.385])box(.028,2.61,.046,x,1.345,0,metal,pivot);
  for(const y of [.054,2.636])box(1.38,.028,.046,cx,y,0,metal,pivot);
  const handleX=-side*1.235;for(const z of [-.055,.055]){cyl([handleX,.92,z],[handleX,1.72,z],.012,metal,pivot);for(const y of [1.0,1.64])cyl([handleX,y,0],[handleX,y,z],.008,metal,pivot)}
  for(const y of [.30,1.35,2.40])cyl([0,y-.05,0],[0,y+.05,0],.022,metal,pivot);
 }
 box(.026,.50,.055,0,2.94,4.995);
 const topShape=new T.Shape();topShape.moveTo(-2.65,2.704);topShape.lineTo(-2.65,2.75);topShape.quadraticCurveTo(-2.65,3.182,-2.22,3.182);topShape.lineTo(2.22,3.182);topShape.quadraticCurveTo(2.65,3.182,2.65,2.75);topShape.lineTo(2.65,2.704);topShape.closePath();
 const top=new T.Mesh(new T.ShapeGeometry(topShape,40),glass);top.name='Visible fixed upper glazing';top.position.z=4.997;group.add(top);
 // A faint sky reflection distinguishes clear transom glass from an empty opening.
 const reflection=glass.clone();reflection.opacity=.02;reflection.onBeforeCompile=skipIndoorAreaLights;reflection.customProgramCacheKey=()=> 'transom-daylight-v8';reflection.color.setHex(0xdbe8f3);const refl=new T.Mesh(new T.ShapeGeometry(topShape,40),reflection);refl.position.z=5.002;group.add(refl);
 const black=new T.MeshStandardMaterial({name:'Black backlit lettering',color:0x090908,roughness:.30,metalness:.45});
 const paths=new SVGLoader().parse(signSVG).paths;const letters=new T.Group();for(const p of paths)for(const shape of SVGLoader.createShapes(p)){const geo=new T.ExtrudeGeometry(shape,{depth:18,bevelEnabled:true,bevelSize:1.5,bevelThickness:1.5,bevelSegments:2,curveSegments:12});const m=new T.Mesh(geo,black);letters.add(m)}
 const bounds=new T.Box3().setFromObject(letters),size=bounds.getSize(new T.Vector3()),center=bounds.getCenter(new T.Vector3());for(const m of letters.children)m.position.sub(center);const scale=2.22/size.x;letters.scale.set(scale,-scale,scale);letters.position.set(0,4.32,5.265);letters.name='ANQA black three dimensional sign';group.add(letters);
 function label(text,y,width,height,font,glow=false){const c=document.createElement('canvas');c.width=1536;c.height=Math.round(1536*height/width);const ctx=c.getContext('2d');ctx.textAlign='center';ctx.textBaseline='middle';ctx.direction='rtl';ctx.font=`${c.height*.65}px ${font}`;if(glow){const g=ctx.createRadialGradient(c.width/2,c.height/2,0,c.width/2,c.height/2,c.width*.49);g.addColorStop(0,'#ffdda780');g.addColorStop(.5,'#ffd39738');g.addColorStop(1,'#ffd39700');ctx.fillStyle=g;ctx.fillRect(0,0,c.width,c.height)}else{ctx.fillStyle='#080807';ctx.fillText(text,c.width/2,c.height/2);}const map=new T.CanvasTexture(c);map.colorSpace=T.SRGBColorSpace;const mat=new T.MeshBasicMaterial({map,transparent:true,depthWrite:false,toneMapped:false});const m=new T.Mesh(new T.PlaneGeometry(width,height),mat);m.position.set(0,y,glow?5.242:5.282);group.add(m);return m}
 document.fonts.ready.then(()=>{label('ANQA',4.32,2.75,.88,'Cormorant',true);label('أناقة',3.86,.98,.42,'Amiri');label('أناقة',3.86,1.1,.45,'Amiri',true);ready()});
 return {group,doors,topGlass:top,lining,stone:facade,sign:letters};
}
