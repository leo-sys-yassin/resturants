/* Stable entry point. Every visit resolves the current manifest; asset URLs are content hashes. */
(async()=>{
 try {
  const response=await fetch('version.json',{cache:'no-store'});if(!response.ok)throw new Error('manifest '+response.status);const version=await response.json();window.ANQA_WEB_VERSION=version.version;
  if(version.body){const oldPoster=document.getElementById('loadingFacade');const posterHTML=oldPoster?oldPoster.outerHTML:'';document.body.innerHTML=posterHTML+version.body;}if(version.title)document.title=version.title;
  const poster=document.querySelector('#loadingFacade img');if(poster)poster.src=version.surfaces['new-facade.png'];
  const style=new Promise((resolve,reject)=>{const link=document.createElement('link');link.rel='stylesheet';link.href=version.style;link.onload=resolve;link.onerror=reject;document.head.append(link)});
  window.SURFACES=version.surfaces;window.CATALOG=version.catalog;window.IMAGES=version.images;window.MODELS={};window.PBR={};
  async function binary(path){const r=await fetch(path,{cache:'force-cache'});if(!r.ok)throw new Error('asset '+r.status);const blob=await r.blob();return new Promise((resolve,reject)=>{const reader=new FileReader();reader.onload=()=>resolve(reader.result.slice(reader.result.indexOf(',')+1));reader.onerror=reject;reader.readAsDataURL(blob)})}
  await Promise.all([style,binary(version.architecture).then(v=>window.ARCHITECTURE=v),binary(version.hdr).then(v=>window.PBR['exterior.hdr']=v),...Object.entries(version.models).map(([id,path])=>binary(path).then(v=>window.MODELS[id]=v))]);
  const script=document.createElement('script');script.src=version.script;script.onerror=()=>{const label=document.querySelector('#loadingFacade span');if(label)label.textContent='تعذّر تحميل الجولة. حدّث الصفحة للمحاولة مجددًا.'};document.body.append(script);
 } catch(error){console.error('ANQA load failed',error);const label=document.querySelector('#loadingFacade span');if(label)label.textContent='تعذّر تحميل الجولة. تحقق من الاتصال وحدّث الصفحة.'}
})();
