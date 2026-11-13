import * as T from 'three';
// The supplied photograph is UV-projected onto the stone only. The aperture is a real hole.
export function createFacade(parent,ready){
 const group=new T.Group();group.name='ANQA reference facade — real open portal';parent.add(group);
 let sideMap;const texture=new T.TextureLoader().load(window.FACADE_ORIGINAL,()=>{if(sideMap)sideMap.needsUpdate=true;ready()});texture.colorSpace=T.SRGBColorSpace;texture.anisotropy=8;
 const front=new T.MeshBasicMaterial({map:texture,side:T.DoubleSide});
 sideMap=texture.clone();sideMap.needsUpdate=true;sideMap.repeat.set(.075,.38);sideMap.offset.set(.015,.35);
 const side=new T.MeshStandardMaterial({map:sideMap,color:0xe6d4bd,roughness:.83});
 const outline=new T.Shape();outline.moveTo(-4.59,-.12);outline.lineTo(-2.72,-.12);outline.lineTo(-2.72,2.77);outline.quadraticCurveTo(-2.72,3.25,-2.24,3.25);outline.lineTo(2.24,3.25);outline.quadraticCurveTo(2.72,3.25,2.72,2.77);outline.lineTo(2.72,-.12);outline.lineTo(4.59,-.12);outline.lineTo(4.59,5.08);outline.lineTo(-4.59,5.08);outline.closePath();
 const geo=new T.ExtrudeGeometry(outline,{depth:.40,bevelEnabled:false,curveSegments:48});
 const pos=geo.attributes.position,uv=geo.attributes.uv,norm=geo.attributes.normal;
 for(let i=0;i<pos.count;i++){
  if(norm.getZ(i)>.9)uv.setXY(i,(836+pos.getX(i)*990/5.44)/1672,1-(778-pos.getY(i)*498/3.25)/941);
  else uv.setXY(i,pos.getZ(i)*2,pos.getY(i)*.25);
 }
 geo.clearGroups();let start=0,lastMaterial=norm.getZ(0)>.9?0:1;for(let i=3;i<=pos.count;i+=3){const material=i<pos.count?(norm.getZ(i)>.9?0:1):-1;if(material!==lastMaterial){geo.addGroup(start,i-start,lastMaterial);start=i;lastMaterial=material}}
 const portal=new T.Mesh(geo,[front,side]);portal.position.z=4.83;portal.name='Stone facade with through-opening';group.add(portal);
 // Soft illuminated reveal has genuine depth; the photographic cap supplies the reference stone and sign.
 const archPoints=[];for(let i=0;i<=24;i++){let t=i/24*Math.PI/2;archPoints.push(new T.Vector3(2.72-.48+.48*Math.cos(t),2.77+.48*Math.sin(t),4.845))}
 archPoints.unshift(new T.Vector3(2.72,.02,4.845));archPoints.push(new T.Vector3(-2.24,3.25,4.845));
 for(let i=1;i<=24;i++){let t=Math.PI/2+i/24*Math.PI/2;archPoints.push(new T.Vector3(-2.24+.48*Math.cos(t),2.77+.48*Math.sin(t),4.845))}archPoints.push(new T.Vector3(-2.72,.02,4.845));
 const line=new T.CurvePath();for(let i=1;i<archPoints.length;i++)line.add(new T.LineCurve3(archPoints[i-1],archPoints[i]));
 const led=new T.Mesh(new T.TubeGeometry(line,128,.006,8,false),new T.MeshBasicMaterial({color:0xffd39a,toneMapped:false}));led.name='Recessed portal light';group.add(led);
 return group;
}
