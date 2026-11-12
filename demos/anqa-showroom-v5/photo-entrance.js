// The user's original photograph is never repainted. Only the central aperture
// reveals an inpainted clean plate; the two transparent leaves are separate DOM objects.
export function createPhotoEntrance(go){
 const el=document.createElement('section');el.id='photoEntrance';el.setAttribute('aria-label','واجهة أناقة الأصلية والبابان المتحركان');
 el.innerHTML=`<div class="photo-stage"><img class="facade-original" alt="واجهة متجر أناقة بالحجر والإنارة الدافئة" draggable="false"><div class="aperture-clean"><img alt="" draggable="false"></div><div class="photo-leaf left-leaf"><i class="glass-reflection"></i><i class="pull-handle"></i></div><div class="photo-leaf right-leaf"><i class="glass-reflection"></i><i class="pull-handle"></i></div></div><div class="entrance-controls"><span id="entranceHint">مرّر لفتح البابين</span><div><button id="openPhotoDoors">افتح البابين <span>↗</span></button><button id="closePhotoDoors" hidden>أغلق البابين</button><button id="enterPhotoStore">دخول المتجر <span>←</span></button></div></div>`;
 document.body.append(el);el.querySelector('.facade-original').src=window.FACADE_ORIGINAL;el.querySelector('.aperture-clean img').src=window.FACADE_CLEAN;
 const stage=el.querySelector('.photo-stage'),left=el.querySelector('.left-leaf'),right=el.querySelector('.right-leaf'),patch=el.querySelector('.aperture-clean'),hint=el.querySelector('#entranceHint'),openButton=el.querySelector('#openPhotoDoors'),closeButton=el.querySelector('#closePhotoDoors'),enter=el.querySelector('#enterPhotoStore');
 const resize=()=>stage.style.perspective=(stage.clientWidth*1.25)+'px';new ResizeObserver(resize).observe(stage);resize();
 openButton.onclick=()=>go(.175);closeButton.onclick=()=>go(0);enter.onclick=()=>go(.28);
 const clamp=v=>Math.max(0,Math.min(1,v)),smooth=v=>{v=clamp(v);return v*v*(3-2*v)};
 let state={progress:0,open:0,visible:true};
 function update(progress){
  const returning=progress>.94;const visible=progress<.235||returning;
  el.hidden=!visible;if(!visible){state={progress,open:0,visible:false};return}
  const open=returning?0:smooth((progress-.012)/.15);
  // A fixed photograph; no orbit, zoom, pan, or background transform.
  el.style.opacity=returning?smooth((progress-.94)/.06):1-smooth((progress-.185)/.05);
  el.style.pointerEvents=progress>.2&&!returning?'none':'auto';
  const active=open>.00001;patch.style.visibility=active?'visible':'hidden';left.style.visibility=right.style.visibility=active?'visible':'hidden';
  left.style.transform=`rotateY(${open*82}deg)`;right.style.transform=`rotateY(${-open*82}deg)`;
  openButton.hidden=open>.97;closeButton.hidden=open<.97;enter.classList.toggle('ready',open>.97);hint.textContent=open>.97?'البابان مفتوحان — تابع إلى المتجر':'مرّر لفتح البابين';
  state={progress,open,visible:true};
 }
 update(0);return {update,element:el,get state(){return state}};
}
