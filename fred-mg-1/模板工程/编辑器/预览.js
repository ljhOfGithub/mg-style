/* 仅由本地编辑器注入。Hyperframes渲染入口不加载此播放器。 */
(()=>{
const duration=Number(document.querySelector('#root').dataset.duration);let t=0,playing=false,last=0,lastSeek=-1;
const media=[...document.querySelectorAll('video,audio')],clips=[...document.querySelectorAll('.clip[data-start]')];
function frameReady(){const active=media.filter(m=>m.dataset.trackIndex!=='0'&&t>=Number(m.dataset.start)&&t<Number(m.dataset.start)+Number(m.dataset.duration));if(active.every(m=>m.readyState>=2&&!m.seeking&&Math.abs(m.currentTime-Math.min(t-Number(m.dataset.start),Math.max(0,m.duration-.04)))<.08))parent.postMessage({type:'mg-frame-ready',time:t},location.origin)}
function seek(value,continuous=false){
 t=Math.max(0,Math.min(duration-1/30,value));window.__timelines.main.seek(t,false);
 for(const e of clips){const s=Number(e.dataset.start),d=Number(e.dataset.duration),active=t>=s&&t<s+d;e.style.visibility=active?'visible':'hidden'}
 for(const m of media){
  const s=Number(m.dataset.start),d=Number(m.dataset.duration),active=t>=s&&t<s+d;m.muted=true;
  if(active){let target=t-s;if(Number.isFinite(m.duration))target=Math.min(target,Math.max(0,m.duration-.04));
   if(Math.abs(m.currentTime-target)>(continuous?.25:.03)||m.readyState<1){try{m.currentTime=target}catch{}}
   if(playing&&m.paused)m.play().catch(()=>{});if(!playing&&!m.paused)m.pause();
  }else if(!m.paused)m.pause();
 }
 parent.postMessage({type:'mg-time',time:t,duration},location.origin);frameReady()
}
window.addEventListener('message',e=>{if(e.origin!==location.origin)return;
 if(e.data.type==='mg-seek'){playing=false;seek(e.data.time)}
 if(e.data.type==='mg-play'){playing=!playing;last=0;if(!playing)media.forEach(m=>m.pause());parent.postMessage({type:'mg-playing',playing},location.origin)}
});
function tick(now){if(playing){if(last){const next=t+(now-last)/1000;if(next>=duration){playing=false;parent.postMessage({type:'mg-playing',playing:false},location.origin)}else seek(next,true)}last=now}requestAnimationFrame(tick)}
for(const m of media){m.addEventListener('loadedmetadata',()=>{const start=Number(m.dataset.start);if(t>=start&&t<start+Number(m.dataset.duration)){m.currentTime=Math.min(t-start,Math.max(0,m.duration-.04))}frameReady()});m.addEventListener('loadeddata',()=>frameReady());m.addEventListener('seeked',()=>frameReady())}
document.fonts.ready.then(()=>{seek(0);parent.postMessage({type:'mg-ready'},location.origin)});requestAnimationFrame(tick);
})();
