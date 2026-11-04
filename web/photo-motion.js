/* Whole ingredient assets extracted from the user-provided reference video. No WebGL, mesh or cropped assembled-photo bands. */
(()=>{
 'use strict';
 const section=document.getElementById('burgerScroll'),pin=section.querySelector('.burger-pin'),stage=document.getElementById('burgerStage'),images=document.getElementById('ingredientImages');
 const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
 const definitions=[["ref-top", "خبز بريوش وصوص", 360, 162.94, 200, "right"], ["ref-jalapeno", "هالبينو", 206, 373.65, 252, "left"], ["ref-cheese-one", "شيدر", 212, 539.25, 271, "right"], ["ref-beef-one", "لحم بقري مشوي", 202, 689.98, 294, "left"], ["ref-cheese-two", "شيدر مضاعف", 249, 864.07, 314, "right"], ["ref-beef-two", "طبقة لحم ثانية", 249, 1032.85, 338, "left"], ["ref-onions", "بصل مقرمش", 287, 1220.2, 367, "right"], ["ref-base", "خبز محمّص", 314, 1424.01, 406, "left"]];
 const proportions={"ref-top": [1.003796, 0.008104], "ref-base": [0.900292, -0.005673], "ref-jalapeno": [0.918936, 0.005673], "ref-cheese-one": [0.9255, -0.007293], "ref-cheese-two": [0.864478, -0.005673], "ref-beef-one": [0.895645, -0.004862], "ref-beef-two": [0.861323, -0.005673], "ref-onions": [0.82338, 0.0]};
 const parts=definitions.map(([id,label,height,sourceY,assembledY,side],i)=>{
  const img=document.createElement('img');img.src=window.EMBER_PHOTO_ASSETS?.[id]||`assets/burger-photo/${id}.webp`;img.alt='';img.width=1024;img.height=height;img.style.width='1024px';img.style.height=height+'px';img.className='whole-ingredient';img.dataset.ingredient=id;img.style.zIndex=String(10-i);img.fetchPriority=i===0?'high':'auto';img.decoding='async';images.appendChild(img);
  return {img,id,label,height,sourceY,assembledY,side,i,fit:proportions[id][0],offset:proportions[id][1]};
 });

 let progress=0,target=0,raf=0,w=0,h=0,visible=true,parallax=0,parallaxTarget=0,lastTime=0;
 const clamp=(x,a=0,b=1)=>Math.max(a,Math.min(b,x));
 function request(){if(!raf&&!document.hidden)raf=requestAnimationFrame(draw)}
 function resize(){w=stage.clientWidth;h=stage.clientHeight;request()}
 function draw(time){raf=0;if(document.hidden)return;const rect=stage.getBoundingClientRect(),documentTop=rect.top+scrollY,start=Math.max(0,documentTop-innerHeight*.50),distance=Math.max(80,Math.min(110,innerHeight*.13));const raw=clamp((scrollY-start)/distance);target=raw*raw*(3-2*raw);
  const dt=lastTime?Math.min((time-lastTime)/1000,.05):.016;lastTime=time;
  const follow=reduced||!visible?1:1-Math.exp(-dt*35);progress+=(target-progress)*follow;if(Math.abs(target-progress)<.0002)progress=target;
  parallax+=(parallaxTarget-parallax)*(reduced?1:.18);
  if(!w||!h){resize();return}
  const desktop=innerWidth>=1000,closedWidth=Math.min(w*.94,desktop?620:420),openWidth=Math.min(w*.90,(h-48)*1024/1690,desktop?480:390),artWidth=closedWidth+(openWidth-closedWidth)*progress;
  const center=h*.5;
  for(const part of parts){
   const closedY=(part.assembledY-300)*closedWidth/560,openY=(part.sourceY-768)*openWidth/1024;
   const y=center+closedY+(openY-closedY)*progress;
   const height=part.height*artWidth/1024*part.fit;
   const sway=-part.offset*artWidth*part.fit+(reduced?0:parallax*.8);const rotation=0;
   part.img.style.transform=`translate3d(calc(-50% + ${sway.toFixed(2)}px),${(y-height/2).toFixed(2)}px,0) rotate(${rotation.toFixed(2)}deg) scale(${(artWidth/1024*part.fit).toFixed(5)})`;part.img.style.transformOrigin='50% 0';

  }
  document.getElementById('scrollMeter').style.transform=`scaleX(${progress.toFixed(4)})`;
  document.getElementById('scrollProgressLabel').textContent=progress<.015?'اسحب للأعلى':`${Math.round(progress*100)}٪ من التفاصيل`;
  document.getElementById('layerStory').textContent=progress<.25?'تشيز برغر إمبر':progress<.75?'كل طبقة، نكهة.':'المكونات، على الأصول.';
stage.dataset.motionSource='compositor-layers';stage.style.setProperty('--explosion',progress.toFixed(4));stage.style.setProperty('--burger-drift',parallax.toFixed(3));stage.dataset.explosion=progress.toFixed(3);stage.dataset.photoReady='true';stage.dataset.flow='free-scroll';
  if(visible&&(Math.abs(progress-target)>.0001||Math.abs(parallax-parallaxTarget)>.02))request();
 }
 addEventListener('scroll',request,{passive:true});addEventListener('resize',resize,{passive:true});new ResizeObserver(resize).observe(stage);
 new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;request()},{rootMargin:'80px'}).observe(section);
 stage.addEventListener('pointermove',event=>{if(event.pointerType==='mouse'&&!reduced){const box=stage.getBoundingClientRect();parallaxTarget=clamp((event.clientX-box.left)/box.width,0,1)*2-1;request()}});
 stage.addEventListener('pointerleave',()=>{parallaxTarget=0;request()});
 document.addEventListener('visibilitychange',()=>{if(document.hidden&&raf){cancelAnimationFrame(raf);raf=0}else request()});
 document.fonts?.ready.then(resize);resize();
})();
