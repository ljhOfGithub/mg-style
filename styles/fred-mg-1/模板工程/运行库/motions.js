/* 时间原语适配 mg-styles-15 01-flat-vector @3164c24e，MIT见项目许可。
 * 动作事件来自本地FredTalk参考片的可见状态，不声称作者使用本库。 */
(function(root){
'use strict';
const clamp=(x,a=0,b=1)=>Math.max(a,Math.min(b,x));
const lerp=(a,b,u)=>a+(b-a)*u;
const inv=(a,b,x)=>clamp((x-a)/(b-a));
const ease={linear:u=>u,inQ:u=>u*u,outQ:u=>1-(1-u)**2,inC:u=>u**3,outC:u=>1-(1-u)**3,inQt:u=>u**4,outQt:u=>1-(1-u)**4};
function countAt(t,knots){let value=knots[0][1];for(let i=1;i<knots.length;i++)if(t>=knots[i-1][0])value=lerp(knots[i-1][1],knots[i][1],inv(knots[i-1][0],knots[i][0],t));return value;}
function select(stage,selector){const local=selector.replace(/\[id([~|^$*]?=)/g,'[data-mg-id$1').replace(/#([\w\u3400-\u9fff-]+)/g,'[data-mg-id="$1"]');const elements=[...stage.querySelectorAll(local)];if(!elements.length)throw Error('MG目标不存在: '+stage.id+' '+selector);return elements;}
function apply(tl,stage,event,offset=0){
 const e=event,t=offset+e.at,d=e.duration===undefined?.2:e.duration;
 const els=select(stage,e.target);const curve=ease[e.ease||'outQ'];if(!curve)throw Error('未知缓动 '+e.ease);
 const tween=(from,to,at=t,duration=d)=>tl.fromTo(els,from,{...to,duration,ease:curve,stagger:e.stagger||0,immediateRender:false},at);
 switch(e.type){
 case 'fade':tween({opacity:e.from===undefined?0:e.from},{opacity:e.to===undefined?1:e.to});break;
 case 'move':tween(e.from||{x:0,y:0},e.to||{x:0,y:0});break;
 case 'mask':tween({clipPath:e.from||'inset(0 100% 0 0)'},{clipPath:e.to||'inset(0 0% 0 0)'});break;
 case 'state':tl.set(els,e.values,t);break;
 case 'style':tl.to(els,{...e.to,duration:d,ease:curve},t);break;
 case 'bar':if(e.knots){for(let i=1;i<e.knots.length;i++)tween({scaleX:e.knots[i-1][1]},{scaleX:e.knots[i][1]},t+e.knots[i-1][0],e.knots[i][0]-e.knots[i-1][0]);}else tween({scaleX:e.from===undefined?0:e.from},{scaleX:e.to===undefined?1:e.to});break;
 case 'draw':els.forEach(el=>{const length=el.getTotalLength?el.getTotalLength():1;if(el.removeAttribute)el.removeAttribute('pathLength');if(el.setAttribute)el.setAttribute('stroke-dasharray',length+' '+length);tl.fromTo(el,{strokeDashoffset:length*(e.from===undefined?1:e.from)},{strokeDashoffset:length*(e.to===undefined?0:e.to),duration:d,ease:curve,immediateRender:false},t);});break;
 case 'wordFall':els.forEach((el,i)=>tl.fromTo(el,{y:e.fromYs?e.fromYs[i%e.fromYs.length]:(e.fromY===undefined?-80:e.fromY),opacity:0},{y:0,opacity:1,duration:d,ease:curve,immediateRender:false},t+i*(e.stagger||0)));break;
 case 'counter':{
  const cursor={t:0};const knots=e.knots||[[0,e.from||0],[d,e.to||0]];
  tl.fromTo(cursor,{t:0},{t:d,duration:d,ease:'none',immediateRender:false,onUpdate:()=>{const value=countAt(cursor.t,knots);els.forEach(el=>el.textContent=(e.prefix||'')+(e.integer===false?value.toFixed(e.decimals||1):Math.round(value))+(e.suffix||''));}},t);break;
 }
 case 'typing':{
  const text=e.text===undefined?els[0].textContent:e.text,cursor={p:0};
  tl.fromTo(cursor,{p:0},{p:1,duration:d,ease:'none',immediateRender:false,onUpdate:()=>els.forEach(el=>el.textContent=text.slice(0,Math.floor(text.length*cursor.p)))},t);break;
 }
 case 'wavefill':{
  const bars=select(stage,e.bars),line=select(stage,e.line);
  tl.fromTo(line,{x:0},{x:e.distance,duration:d,ease:'none',immediateRender:false},t);
  bars.forEach((bar,i)=>{tl.fromTo(bar,{backgroundColor:e.gray||'#514956'},{backgroundColor:e.color||'#c6a4fa',duration:.08,ease:'none',immediateRender:false},t+i*d/bars.length);});break;
 }
 case 'flip':{
  const out=select(stage,e.out),incoming=select(stage,e.in);
  tl.fromTo(incoming,{rotationX:90},{rotationX:0,transformOrigin:'center center',duration:d/2,ease:ease.outQ,immediateRender:false},t+d/2);
  tl.fromTo(out,{rotationX:0},{rotationX:-90,transformOrigin:'center center',duration:d/2,ease:ease.inQ,immediateRender:false},t);break;
 }
 case 'giant':tween({scale:1},{scale:e.scale||9});break;
 case 'tiles':tween({opacity:1},{opacity:0});break;
 default:throw Error('未知MG动作 '+e.type);
 }
 return tl;
}
function initialise(tl,stage,events,offset){const seen=new Map();function first(elements,props){for(const el of elements){let keys=seen.get(el);if(!keys){keys=new Set();seen.set(el,keys);}const values={};for(const [key,value] of Object.entries(props))if(!keys.has(key)){keys.add(key);values[key]=value;}if(Object.keys(values).length)tl.set(el,values,offset);}}
 for(const e of [...events].sort((a,b)=>a.at-b.at)){const els=select(stage,e.target);switch(e.type){
 case 'fade':first(els,{opacity:e.from===undefined?0:e.from});break;
 case 'move':first(els,e.from||{x:0,y:0});break;
 case 'mask':first(els,{clipPath:e.from||'inset(0 100% 0 0)'});break;
 case 'bar':first(els,{scaleX:e.knots?e.knots[0][1]:(e.from===undefined?0:e.from)});break;
 case 'wordFall':els.forEach((el,i)=>first([el],{y:e.fromYs?e.fromYs[i%e.fromYs.length]:(e.fromY===undefined?-80:e.fromY),opacity:0}));break;
 case 'tiles':first(els,{opacity:1});break;
 case 'flip':first(select(stage,e.in),{rotationX:90});first(select(stage,e.out),{rotationX:0});break;
 case 'typing':first(els,{textContent:''});break;
 case 'counter':first(els,{textContent:String(e.knots?e.knots[0][1]:(e.from||0))});break;
 case 'draw':els.forEach(el=>first([el],{strokeDashoffset:(el.getTotalLength?el.getTotalLength():1)*(e.from===undefined?1:e.from)}));break;
 case 'style':for(const el of els){let keys=seen.get(el);if(!keys){keys=new Set();seen.set(el,keys);}Object.keys(e.to).forEach(k=>keys.add(k));}break;
 }} }
function build(gsap,sceneSpecs){const tl=gsap.timeline({paused:true});for(const scene of sceneSpecs){const stage=document.getElementById(scene.domId);if(!stage)throw Error('缺场景 '+scene.id);
 tl.set(stage,{opacity:0},0);
 if(!scene.fadeIn)tl.set(stage,{opacity:1},scene.start);
 if(scene.fadeIn)tl.fromTo(stage,{opacity:0},{opacity:1,duration:scene.fadeIn,ease:ease.outQ},scene.start);
 if(scene.fadeOut)tl.to(stage,{opacity:0,duration:scene.fadeOut,ease:ease.outQ},scene.visibleEnd-scene.fadeOut);else tl.set(stage,{opacity:0},scene.visibleEnd);
 initialise(tl,stage,scene.events,scene.start);for(const event of scene.events)apply(tl,stage,event,scene.start);
 }
 return tl;}
root.RefMG={clamp,lerp,inv,ease,countAt,select,apply,build};
})(typeof window!=='undefined'?window:globalThis);
