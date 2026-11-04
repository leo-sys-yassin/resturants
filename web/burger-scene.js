import * as THREE from './vendor/three.module.js';
import {GLTFLoader} from './vendor/GLTFLoader.js';
import {RoomEnvironment} from './vendor/RoomEnvironment.js';

const stage=document.getElementById('burgerStage'),button=document.getElementById('layersToggle'),canvas=document.getElementById('burgerCanvas'),reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
const names=[['top_bun','خبز بالسمسم','right',3.2],['tomato','شرائح الطماطم','left',2.4],['pickles','مخلّل الخيار','right',1.85],['cheese','جبنة شيدر','left',1.3],['beef','لحم بقري مشوي','right',.75],['lettuce','خس طازج','left',.1],['bottom_bun','قاعدة الخبز','right',-.35]];
let draw,renderer,scene,camera,root,parts=[],target=0,progress=0,pinned=false,visible=true,last=0,frame=0,rotation=.12,targetRotation=.12,pointerStart=null,hasMoved=false,dragging=false,ready=false;
const labels=document.getElementById('ingredientLabels'),lines=document.getElementById('ingredientLines');
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
function announce(){button.setAttribute('aria-pressed',String(pinned));button.querySelector('.button-text').textContent=pinned?'تجميع البرغر':'اكتشف المكونات';stage.classList.toggle('is-open',target>.5);}
function expand(value){target=value;stage.classList.toggle('is-open',value>.5);requestTick();}
function requestTick(){if(!frame&&visible&&!document.hidden&&ready)frame=requestAnimationFrame(draw)}
try{
 renderer=new THREE.WebGLRenderer({canvas,alpha:true,antialias:true,powerPreference:'low-power'});renderer.setPixelRatio(Math.min(devicePixelRatio,1.7));renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.1;
 scene=new THREE.Scene();camera=new THREE.PerspectiveCamera(32,1,.1,50);camera.position.set(0,1.6,10.3);camera.lookAt(0,0,0);
 const pmrem=new THREE.PMREMGenerator(renderer),env=new RoomEnvironment();scene.environment=pmrem.fromScene(env,.04).texture;env.dispose();pmrem.dispose();
 scene.add(new THREE.HemisphereLight(0xfff2dc,0x29231d,1.1));
 const key=new THREE.DirectionalLight(0xffecd3,2.5);key.position.set(-4,6,7);scene.add(key);
 const fill=new THREE.DirectionalLight(0xd7e3ff,1.0);fill.position.set(4,2,4);scene.add(fill);
 const rim=new THREE.DirectionalLight(0xffc184,1.7);rim.position.set(1,5,-4);scene.add(rim);
 const loader=new GLTFLoader();
 const url=window.EMBER_BURGER_MODEL||'assets/burger-3d.glb';
 loader.load(url,gltf=>{
  root=new THREE.Group();root.add(gltf.scene);scene.add(root);root.scale.setScalar(.72);root.position.y=-.85;
  gltf.scene.traverse(o=>{if(o.isMesh){o.frustumCulled=false;if(o.material){o.material.envMapIntensity=.65;o.material.metalness=0;}}});
  root.updateMatrixWorld(true);for(const [name,label,side,offset] of names){const object=gltf.scene.getObjectByName(name);if(!object)continue;const center=new THREE.Box3().setFromObject(object).getCenter(new THREE.Vector3());root.worldToLocal(center);const tag=document.createElement('span');tag.className='ingredient-tag '+side;tag.textContent=label;labels.appendChild(tag);const path=document.createElementNS('http://www.w3.org/2000/svg','path');lines.appendChild(path);parts.push({name,object,label,side,offset,base:object.position.clone(),center,tag,path});}
  ready=true;stage.classList.add('model-ready');stage.dataset.modelReady='true';document.getElementById('modelStatus').textContent='اسحب لتدوير البرغر · المس لاكتشاف المكونات';resize();requestTick();
 },undefined,error=>fallback(error));
 function resize(){const box=stage.getBoundingClientRect();renderer.setSize(box.width,box.height,false);camera.aspect=box.width/box.height;camera.updateProjectionMatrix();lines.setAttribute('viewBox',`0 0 ${box.width} ${box.height}`);requestTick()}
 new ResizeObserver(resize).observe(stage);
 new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;if(visible)requestTick();else if(frame){cancelAnimationFrame(frame);frame=0}},{threshold:.03}).observe(stage);
 document.addEventListener('visibilitychange',()=>{if(!document.hidden)requestTick();else if(frame){cancelAnimationFrame(frame);frame=0}});
 stage.addEventListener('pointerenter',event=>{if(event.pointerType==='mouse'){expand(1)}});
 stage.addEventListener('pointerleave',event=>{if(event.pointerType==='mouse'&&!pinned&&!dragging)expand(0)});
 canvas.addEventListener('pointerdown',event=>{pointerStart={x:event.clientX,y:event.clientY,rotation:targetRotation};hasMoved=false;dragging=true});
 canvas.addEventListener('pointermove',event=>{if(!pointerStart)return;const dx=event.clientX-pointerStart.x,dy=event.clientY-pointerStart.y;if(Math.abs(dx)>8&&Math.abs(dx)>Math.abs(dy)){hasMoved=true;canvas.setPointerCapture(event.pointerId);targetRotation=pointerStart.rotation+dx*.009;expand(1);requestTick()}});
 canvas.addEventListener('pointerup',event=>{if(!hasMoved&&pointerStart){pinned=!pinned;expand(pinned?1:0);announce()}pointerStart=null;dragging=false;if(canvas.hasPointerCapture(event.pointerId))canvas.releasePointerCapture(event.pointerId)});
 canvas.addEventListener('pointercancel',()=>{pointerStart=null;dragging=false});
 button.addEventListener('click',()=>{pinned=!pinned;expand(pinned?1:0);announce()});
 draw=function(time){frame=0;if(!ready||!visible||document.hidden)return;const dt=last?Math.min((time-last)/1000,.04):.016;last=time;const blend=reduced?1:1-Math.exp(-dt*8.5);progress+=(target-progress)*blend;rotation+=(targetRotation-rotation)*(reduced?1:1-Math.exp(-dt*8));if(Math.abs(progress-target)<.0005)progress=target;root.rotation.y=rotation;root.rotation.x=-.035;root.position.y=-.85-progress*.95;root.scale.setScalar(.72-progress*.035);
  for(const part of parts){part.object.position.copy(part.base);part.object.position.y+=part.offset*progress;}
  root.updateMatrixWorld(true);const box=stage.getBoundingClientRect();
  for(const part of parts){part.tag.style.opacity=String(clamp((progress-.4)*2,0,1));part.path.style.opacity=String(clamp((progress-.45)*1.8,0,1));const pos=part.center.clone();pos.y+=part.offset*progress;pos.x+=(part.side==='left'?-1:1)*1.15;root.localToWorld(pos);pos.project(camera);const x=(pos.x*.5+.5)*box.width,y=clamp((-pos.y*.5+.5)*box.height,26,box.height-24);part.tag.style.top=`${y-13}px`;const tagWidth=part.tag.offsetWidth;const endX=part.side==='left'?14+tagWidth:box.width-14-tagWidth;part.path.setAttribute('d',`M${x.toFixed(1)} ${y.toFixed(1)}L${endX.toFixed(1)} ${y.toFixed(1)}`);}
  renderer.render(scene,camera);stage.dataset.explosion=progress.toFixed(3);stage.dataset.rotation=rotation.toFixed(3);if(Math.abs(progress-target)>.0001||Math.abs(rotation-targetRotation)>.001)requestTick();
 }
 canvas.addEventListener('webglcontextlost',event=>{event.preventDefault();ready=false;fallback(new Error('context-lost'))});
}catch(error){fallback(error)}
function fallback(error){stage.classList.remove('model-ready');stage.classList.add('model-fallback');document.getElementById('modelStatus').textContent='عرض ثابت للبرغر · العرض ثلاثي الأبعاد غير متاح على هذا المتصفح';button.disabled=true;console.info('EMBER 3D fallback:',error?.message||'WebGL unavailable')}
