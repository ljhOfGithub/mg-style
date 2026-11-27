/** Pure absolute-frame state, adapted from the observed four-phase source windows.
 * No accumulated deltas; forward/backward seeking has the same result.
 */
export const clamp=x=>Math.max(0,Math.min(1,x));
export const lerp=(a,b,t)=>a+(b-a)*t;
export function keyed(frame,keys){if(frame<=keys[0][0])return keys[0][1];for(let i=1;i<keys.length;i++)if(frame<=keys[i][0]){const[a,x]=keys[i-1],[b,y]=keys[i];return lerp(x,y,clamp((frame-a)/(b-a)));}return keys.at(-1)[1];}
export function settleState(frame,event){const a=event.anchors,first=a.first,mid=a.middle,clear=a.clear;if(frame<first)return {opacity:0,x:0,y:0,scale:1,blur:0};if(event.kind==='sticker')return {opacity:clamp((frame-first)/(clear-first)),x:0,y:keyed(frame,[[first,20],[mid,-7],[clear+8,0]]),scale:1,blur:0};const media=event.kind==='phone',world=event.kind==='world',p=keyed(frame,[[first,0],[mid,.56],[clear,1]]),q=1-(1-p)**2;return {opacity:keyed(frame,[[first,.025],[mid,.66],[clear,1]]),x:media||world?lerp(18,0,q):0,y:lerp(media||world?9:15,0,q),scale:media||world?1:keyed(frame,[[first,.955],[mid,.982],[clear,1]]),blur:keyed(frame,[[first,2],[mid,.8],[clear,0]])};}
export function headerState(frame,scene){const start=scene.frames[0],p=clamp((frame-start-4)/12);return {opacity:p,x:0,y:12*(1-p),scale:1,blur:1.5*(1-p)};}
export function highlightState(frame,event){return clamp((frame-event.highlight[0])/(event.highlight[1]-event.highlight[0]));}
export function sceneAt(frame,config){return config.scenes.find(s=>frame>=s.frames[0]&&frame<s.frames[1])||null;}
export function captionAt(t,config){return(config.captions||[]).find(x=>t>=x.start&&t<x.end)?.text||'';}
export function validateConfig(c){if(c.fps!==30)throw Error('本来源时钟必须显式按30fps解释');if(!c.scenes.length||c.scenes[0].frames[0]!==0||c.scenes.at(-1).frames[1]!==c.frames)throw Error('整片时间线端点缺失');for(let i=0;i<c.scenes.length;i++){const s=c.scenes[i];if(s.frames[1]<=s.frames[0]||(i&&s.frames[0]!==c.scenes[i-1].frames[1]))throw Error('镜头时窗不连续');for(const e of s.components){if(e.anchors.first<s.frames[0]||e.anchors.clear>=s.frames[1])throw Error('组件入场越过本镜时窗');if(e.rect.length!==4||e.rect[2]<=e.rect[0]||e.rect[3]<=e.rect[1])throw Error('组件边界无效');}}return true;}
