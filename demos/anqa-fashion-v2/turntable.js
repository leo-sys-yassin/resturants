/* ANQA multi-angle sequence renderer. Dense frames are prepared at build time;
   canvas draws one frame only, never stacks silhouettes or mirrors a front view. */
(()=>{
 const pool=new Map();
 function load(src){if(!pool.has(src)){const img=new Image();const promise=new Promise((resolve,reject)=>{img.onload=()=>resolve(img);img.onerror=reject});img.src=src;pool.set(src,{img,promise});}return pool.get(src).promise;}
 class Turntable{
  constructor(canvas){this.canvas=canvas;this.ctx=canvas.getContext('2d',{alpha:true});this.image=null;this.key='';this.frame=-1;this.ready=false;this.ticket=0;this.total=96;this.cols=8;this.width=384;this.height=512;}
  async set(sequence,poster){const key=sequence?.atlas||poster;if(key===this.key)return;this.key=key;this.ready=false;this.frame=-1;const ticket=++this.ticket;this.canvas.dataset.ready='false';this.canvas.dataset.asset=sequence?.id||'poster';
   if(poster){try{const im=await load(poster);if(ticket!==this.ticket)return;this.ctx.clearRect(0,0,this.canvas.width,this.canvas.height);this.ctx.drawImage(im,0,0,this.canvas.width,this.canvas.height);}catch{}}
   if(!sequence)return;
   try{const image=await load(sequence.atlas);if(ticket!==this.ticket)return;this.image=image;this.total=sequence.frames;this.cols=sequence.columns;this.width=sequence.width;this.height=sequence.height;this.ready=true;this.canvas.dataset.ready='true';this.frame=-1;this.draw(0);}catch{this.canvas.dataset.ready='failed';}
  }
  draw(degrees){if(!this.ready)return;const angle=((degrees%360)+360)%360;const frame=Math.round(angle/360*this.total)%this.total;if(frame===this.frame)return;this.frame=frame;const x=frame%this.cols*this.width,y=Math.floor(frame/this.cols)*this.height;this.ctx.clearRect(0,0,this.canvas.width,this.canvas.height);this.ctx.drawImage(this.image,x,y,this.width,this.height,0,0,this.canvas.width,this.canvas.height);this.canvas.dataset.frame=frame;this.canvas.dataset.angle=angle.toFixed(2);}
 }
 window.ANQATurntable=Turntable;
})();
