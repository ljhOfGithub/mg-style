import{settleState,headerState,highlightState,sceneAt,captionAt}from'./motion.mjs';
import{applyState}from'./components.mjs';
/** Pure time addressing; keep the previous Hyperframes renderAt rounding exactly. */
export const frameAtTime=(t,config)=>Math.max(0,Math.min(config.frames-1,Math.round(t*config.fps)));
/** root owns this DOM only; the same updater is used by Hyperframes and Hypit. */
export function createFrameRenderer(config,root,{events=[]}={}){
 const lookup=new Map([...root.querySelectorAll('[data-event]')].map(el=>[el.dataset.event,el]));
 function renderFrame(frame){const f=Math.max(0,Math.min(config.frames-1,Math.round(frame))),current=sceneAt(f,config);
  for(const s of config.scenes){const host=root.querySelector('#scene-'+s.index);if(!host)continue;host.style.display=s===current?'block':'none';if(s!==current)continue;
   root.querySelector('.paper').style.setProperty('--accent',s.header.accent);const header=host.querySelector('.header');
   if(header){applyState(header,headerState(f,s));const h=s.headerEvent||events.find(e=>e.id==='s'+String(s.index).padStart(2,'0')+'-header');header.querySelector('mark').style.setProperty('--bar',100*highlightState(f,h)+'%');}
   for(const e of s.components){const el=lookup.get(e.id);if(el)applyState(el,settleState(f,e));}
  }
  for(const[key,m]of Object.entries(config.media||{})){const el=root.querySelector('[data-media-key="'+key+'"]');if(el)el.style.visibility=f>=m.first&&f<m.end?'visible':'hidden';}
  const text=captionAt(f/config.fps,config),cap=root.querySelector('#caption');if(cap){const top=current?.captionTop;if(top!==undefined)cap.style.top=top+'px';else if(cap.style.getPropertyValue('top'))cap.style.removeProperty('top');cap.textContent=text;cap.style.display=text?'block':'none';}return f;
 }
 const renderAt=t=>renderFrame(frameAtTime(t,config));return{renderAt,renderFrame};
}
