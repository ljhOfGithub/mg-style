const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
(async()=>{
 const messages=[],listeners={},frames=[];const video={dataset:{start:'0',duration:'5'},readyState:0,seeking:true,currentTime:0,duration:NaN,paused:true,style:{},addEventListener:(type,fn)=>listeners[type]=fn,pause(){},play(){return Promise.resolve()}};
 const handlers={};const root={dataset:{duration:'15'}};const context={document:{querySelector:()=>root,querySelectorAll:q=>q==='video,audio'?[video]:[video],fonts:{ready:Promise.resolve()}},window:{__timelines:{main:{seek(){}}},addEventListener:(type,fn)=>handlers[type]=fn},parent:{postMessage:m=>messages.push(m)},location:{origin:'http://local.test'},requestAnimationFrame:fn=>frames.push(fn),Math,Number};
 vm.createContext(context);vm.runInContext(fs.readFileSync(path.join(__dirname,'../模板工程/编辑器/预览.js'),'utf8'),context);await Promise.resolve();
 function paint(){const batch=frames.splice(0);batch.forEach(fn=>fn(0))}
 handlers.message({origin:'http://local.test',data:{type:'mg-seek',time:3}});paint();assert(!messages.some(m=>m.type==='mg-frame-ready'),'帧未加载时不能宣布画面就绪');
 video.duration=10;listeners.loadedmetadata();assert.equal(video.currentTime,3,'元数据加载后恢复所选时刻');video.readyState=2;video.seeking=false;listeners.seeked();paint();assert(messages.some(m=>m.type==='mg-frame-ready'&&m.time===3));
 console.log('PASS media readiness waits for decoded seeked frame and retries after metadata');
})().catch(e=>{console.error(e);process.exitCode=1});
