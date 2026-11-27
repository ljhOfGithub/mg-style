// 归一化、插值与独立对象相位：改编自 mg-styles-15@3164c24 的 flat-vector 演示。
// 父子分组和整数帧键轨延续本库已验证的时间函数；不添加无来源的循环运动。
export const clamp=(x,a=0,b=1)=>Math.max(a,Math.min(b,x));
export const lerp=(a,b,u)=>a+(b-a)*u;
export const phase=(f,a,b)=>b<=a?+(f>=b):clamp((f-a)/(b-a));
export const ease=(u,name='linear')=>name==='out-cubic'?1-(1-u)**3:name==='in-out'?u*u*(3-2*u):u;
export function valueAt(keys,frame,fallback=0){
 if(!keys?.length)return fallback;
 if(frame<=keys[0][0])return keys[0][1];
 for(let i=1;i<keys.length;i++){const a=keys[i-1],b=keys[i];if(frame<=b[0])return b[2]==='step'?(frame<b[0]?a[1]:b[1]):lerp(a[1],b[1],ease(phase(frame,a[0],b[0]),b[2]));}
 return keys.at(-1)[1];
}
export const sceneAt=(scenes,f)=>scenes.find(s=>f>=s.from&&f<s.to);
export function stateAt(node,frame){
 const v={alpha:1,x:0,y:0,scale:1,rotate:0,skew:0,reveal:1,count:1};
 for(const [name,keys]of Object.entries(node.tracks??{}))v[name]=valueAt(keys,frame,v[name]??0);
 return v;
}
export function validate(config){
 if(config.fps!==30||!Number.isInteger(config.frames)||config.frames<1)throw Error('须为30fps与正整数帧数');
 if(!config.scenes.length||config.scenes[0].from!==0||config.scenes.at(-1).to!==config.frames)throw Error('缺少全片端点');
 const ids=new Set();
 function check(nodes,scene){for(const n of nodes){if(!n.id||ids.has(n.id))throw Error('对象ID缺失或重复');ids.add(n.id);if(n.from!==undefined&&(n.from<scene.from||n.from>=scene.to))throw Error('对象开始帧越出镜头 '+n.id);for(const keys of Object.values(n.tracks??{})){if(!Array.isArray(keys)||keys.some((k,i)=>!Number.isInteger(k[0])||(i&&k[0]<=keys[i-1][0])))throw Error('键轨帧须严格递增 '+n.id);}check(n.children??[],scene);}}
 config.scenes.forEach((s,i)=>{if(!Number.isInteger(s.from)||!Number.isInteger(s.to)||s.from>=s.to||(i&&s.from!==config.scenes[i-1].to))throw Error('镜头重叠或缺口');check(s.nodes??[],s);});
 return true;
}
