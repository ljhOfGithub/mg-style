import *as C from'./components.mjs';
export const frameAtTime=(time,fps=30)=>Math.floor(time*fps+1e-4);
export function sceneAt(c,time){const frame=Math.min(frameAtTime(time,c.fps),c.scenes.at(-1).endFrame-1);let index=c.scenes.findIndex(s=>frame>=s.startFrame&&frame<s.endFrame);if(index<0)index=c.scenes.length-1;return{frame,index,scene:{...c.scenes[index],index,total:c.scenes.length}}}
export function renderScene(c,time){const{frame:f,scene:s}=sceneAt(c,time),a=s.accent,t=c.timings,k=c.content,start=s.startFrame;const bg=C.paperBackground({accent:a,theme:c.theme});let body=C.chapterHeader(s,f,c.theme),overlay='',blur=0;
 switch(s.id){
 case'intro':body+=C.mediaCard({x:298,y:244,w:602,h:354,media:c.media.product,accent:a,a:C.alpha(f,start+t.introCards[2],10)})+C.introSummary(k.intro,f,start+t.introCards[0],a)+C.introProcess(k.intro,f,start+t.introCards[1],a);break;
 case'pain':body+=C.problemCards(k.pain,f,start,t.painCards,a,t.alphaCurves?.pain)+C.painSummary({items:k.painSummary,frame:f,at:start+(t.painSummary??45),accent:a,curve:t.alphaCurves?.painSummary});break;
 case'team':body+=C.mediaCard({x:78,y:298,w:484,h:301,media:c.media.market,accent:a,a:C.alpha(f,start+t.teamMedia,10)})+C.stepCards(k.teamSteps,f,start,t.teamSteps,a,{curves:t.alphaCurves?.team});break;
 case'deliverables':{body+=C.overviewGallery(k.deliverables,c.media,f,start,t.deliverableCards,a);const st=C.galleryState(f,t.focusTransitions);blur=st.focus*7;overlay=C.focusFrame({labels:k.deliverables,media:c.media,state:st,accent:a});break;}
 case'controls':body+=C.controlCards(k.controls,k.controlPlane,f,start,t.controls,a,t.alphaCurves?.controls);break;
 case'collaboration':body+=C.mediaCard({x:78,y:298,w:464,h:226,media:c.media.collaboration,accent:a,a:C.alpha(f,start+t.collaboration[0],10,t.alphaCurves?.collaborationMedia),label:'技能创建器 · 官方界面'})+C.knowledgeChain(k.knowledgeChain,f,start+(t.knowledgeChainAt??t.collaboration[1]),a,t.alphaCurves?.collaborationMedia)+C.stepCards(k.collaboration,f,start,t.collaboration.slice(1),a,{x:566,y:298,w:335,h:90,gap:18,numberBox:true});break;
 case'open-source':body+=C.mediaCard({x:78,y:298,w:537,h:222,media:c.media.chart,accent:a,a:C.alpha(f,start+t.openSource[0],10),label:'STAR HISTORY'})+C.signalCards(k.signals,f,start,t.openSource.slice(1,4),a,t.alphaCurves?.signal)+C.codeStrip({command:k.installCommand,result:k.installResult,frame:f,at:start+t.openSource[4],accent:a});break;
 case'audiences':body+=C.audienceCards(k.audiences,f,start,t.audiences,a,t.alphaCurves?.audiences);break;
 case'conclusion':body+=C.conclusionPanel(k.conclusion,c.media,f,start,t.conclusion,a);overlay=C.ctaSticker(k.cta,f,t.ctaAt,t.ctaY,a);break;
 }
 const cue=c.captions.find(x=>time>=x.start&&time<x.end);const footer=C.tx(78,681,c.footer,10,'#30343d',650),captions=C.captionBox(cue?.text??'');
 return {frame:f,scene:s.id,markup:`<defs><filter id="background-blur" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="${blur}"/></filter></defs>`+`<g${blur>0?' data-layout-allow-overlap data-layout-ignore filter="url(#background-blur)"':''}>${bg}${body}${footer}</g>`+overlay+captions};}
