import{clamp,lerp,sceneAt,stateAt}from'./motion.mjs';
// 所有变化来自配置键轨。静态底色不添加漂移、扫光或装饰循环。
export function createRenderer(canvas,config,images={}){
 const x=canvas.getContext('2d'),W=config.width,H=config.height,C={bg:'#14140e',ink:'#f7f5eb',gold:'#dfb85f',weak:'#848277',green:'#82cba1',red:'#db6e6a',...config.palette};
 canvas.width=W;canvas.height=H;
 function box(b,fill,stroke,r=5,lw=1){x.beginPath();x.roundRect(...b,r);if(fill){x.fillStyle=fill;x.fill();}if(stroke){x.lineWidth=lw;x.strokeStyle=stroke;x.stroke();}}
 function text(t,b,n={}){
  const rows=String(t).split('\n'),lineHeight=n.lineHeight??1.35,size=Math.min(n.size??32,b[3]/(1+(rows.length-1)*lineHeight)),weight=n.weight??700,family=n.font==='display'?'FredDisplay':n.font==='mono'?'monospace':'FredSC';
  x.font=`${weight} ${size}px ${family},sans-serif`;x.fillStyle=n.color??C.ink;x.textAlign=n.align??'left';x.textBaseline='top';
  const xx=n.align==='center'?b[0]+b[2]/2:n.align==='right'?b[0]+b[2]:b[0];
  rows.forEach((v,i)=>{x.font=`${weight} ${size}px ${family},sans-serif`;const width=x.measureText(v).width;if(width>b[2])x.font=`${weight} ${size*b[2]/width}px ${family},sans-serif`;x.fillText(v,xx,b[1]+i*size*lineHeight);});
 }
 function image(n,b,f){
  const key=(n.frames??[]).filter(v=>f>=v.at).at(-1)?.media??n.media,im=images[key];
  if(!im){box(b,'#25251c','#5b523b',5);text(n.placeholder??'真实案例媒体', [b[0]+12,b[1]+b[3]/2-20,b[2]-24,60],{size:24,color:C.weak,align:'center'});return;}
  x.save();x.beginPath();x.roundRect(...b,n.radius??4);x.clip();
  const crop=n.crop??[0,0,im.width,im.height],scale=n.fit==='cover'?Math.max(b[2]/crop[2],b[3]/crop[3]):Math.min(b[2]/crop[2],b[3]/crop[3]);
  const dw=crop[2]*scale,dh=crop[3]*scale,ox=b[0]+(b[2]-dw)/2,oy=b[1]+(b[3]-dh)/2;
  if(n.back!=='transparent'){x.fillStyle=n.back??'#11120f';x.fillRect(...b);}x.drawImage(im,...crop,ox,oy,dw,dh);x.restore();
 }
 function node(n,f){
  const variant=(n.variants??[]).filter(v=>f>=v.at).at(-1);if(variant)n={...n,...variant};
  if(f<(n.from??-Infinity)||f>=(n.to??Infinity))return;
  const v=stateAt(n,f);let b=[...(n.bounds??[0,0,W,H])];if(n.tracks?.width)b[2]=v.width;if(n.tracks?.height)b[3]=v.height;if(v.alpha<=0)return;
  x.save();x.globalAlpha*=clamp(v.alpha);x.translate(v.x,v.y);const cx=b[0]+b[2]/2,cy=b[1]+b[3]/2;x.translate(cx,cy);x.rotate(v.rotate*Math.PI/180);x.transform(v.scale,0,Math.tan(v.skew*Math.PI/180),v.scale,0,0);x.translate(-cx,-cy);
  if(v.reveal<1){x.beginPath();x.rect(b[0],b[1],Math.max(0,b[2]*v.reveal),b[3]);x.clip();}
  if(n.kind==='rect')box(b,n.fill===undefined?'#211e13':n.fill,n.stroke,n.radius,n.lineWidth);
  else if(n.kind==='image')image(n,b,f);
  else if(n.kind==='preview'){const cv=document.createElement('canvas');const rr=createRenderer(cv,{...config,captions:[]},images);rr.renderFrame(n.frame??682);const crop=W>H?[90,140,W-180,H-330]:[30,320,W-60,950];x.drawImage(cv,...crop,...b);}
  else if(n.kind==='text')text(n.text,b,n);
  else if(n.kind==='counter')text((n.prefix??'')+Math.round((n.value??0)*v.count).toLocaleString('en-US')+(n.suffix??''),b,n);
  else if(n.kind==='type'){const count=Math.floor(String(n.text).length*v.count);text(String(n.text).slice(0,count)+(n.cursor&&v.count<1?'▌':''),b,n);}
  else if(n.kind==='line'){x.beginPath();x.strokeStyle=n.color??C.gold;x.lineWidth=n.lineWidth??3;x.moveTo(b[0],b[1]);x.lineTo(b[0]+b[2]*v.count,b[1]+b[3]*v.count);x.stroke();}
  else if(n.kind==='bar')box([b[0],b[1],Math.max(0,b[2]*v.count),b[3]],n.fill??C.gold,null,n.radius??2);
  else if(n.kind==='gradient'){const g=x.createLinearGradient(0,b[1],0,b[1]+b[3]);(n.stops??[[0,'#14140e00'],[1,C.bg]]).forEach(([k,c])=>g.addColorStop(k,c));x.fillStyle=g;x.fillRect(...b);}
  for(const child of n.children??[])node(child,f);
  x.restore();
 }
 function background(){x.fillStyle=C.bg;x.fillRect(0,0,W,H);if(config.vignette!==false){const g=x.createRadialGradient(W*.5,H*.45,0,W*.5,H*.45,Math.max(W,H)*.65);g.addColorStop(0,'#69602a0d');g.addColorStop(1,'#00000055');x.fillStyle=g;x.fillRect(0,0,W,H);}}
 function caption(f){const c=(config.captions??[]).find(c=>f>=c.from&&f<c.to);if(!c)return;const b=sceneAt(config.scenes,f)?.captionBounds??config.captionBounds??[W*.06,H*.72,W*.88,H*.09];text(c.text,b,{size:config.captionSize??42,align:'center',weight:900});}
 return{renderFrame(f){if(!Number.isInteger(f))throw Error('只接受整数帧');x.clearRect(0,0,W,H);background();const s=sceneAt(config.scenes,f);if(s)for(const n of s.nodes??[])node(n,f);caption(f);},drawNode:node};
}
