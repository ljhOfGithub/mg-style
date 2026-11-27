import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {registry} from '../src/components.mjs';
import {refinedRegistry,pulsingRing,countState,activeState,stagedState} from '../src/refined-components.mjs';
import {pulseRingState} from '../src/gap-ring.mjs';
import {renderScene} from '../src/scene.mjs';
import {renderRefinedComponent} from '../src/refined-scenes.mjs';

const read=path=>JSON.parse(fs.readFileSync(new URL(path,import.meta.url)));
const curves=read('../src/measured-curves.json');
const examples=['flow-reuse','notebook-reuse','pulsing-ring-reuse'];

for(const name of examples){
 const config=read('../examples/'+name+'.json');
 test(name+'：完整时长逐帧求值并可倒序重算',()=>{
  const frames=Math.round(config.duration*config.fps),seen=[];
  for(let f=0;f<frames;f++){
   const state=renderScene(config,f/config.fps,curves);
   assert.equal(state.frame,f);assert.equal(state.scene,'component');
   assert.equal(typeof state.markup,'string');assert(!/NaN|undefined/.test(state.markup));
   seen.push(state.markup);
  }
  for(let f=frames-1;f>=0;f--)assert.equal(renderScene(config,f/config.fps,curves).markup,seen[f]);
 });
 test(name+'：通用示例不读取原片媒体',()=>{
  assert.deepEqual(config.media,[]);assert(config.component);
  assert.equal(typeof refinedRegistry[config.component.type],'function');
 });
}

test('轻呼吸组件的命名导出与登记入口一致，防止运行时漏导出',()=>{
 assert.equal(pulsingRing,refinedRegistry.pulsingRing);
 const config=read('../examples/pulsing-ring-reuse.json');
 assert(renderRefinedComponent(config.component,50,config.background).includes('24 小时'));
});
test('组件目录每一项都指向可调用绘图入口，不混入媒体和状态计算',()=>{
 const catalog=read('../components/catalog.json');const ids=new Set();
 for(const item of catalog.components){assert(!ids.has(item.id));ids.add(item.id);assert.equal(typeof(item.family==='基础兼容'?registry:refinedRegistry)[item.id],'function');}
 assert(!ids.has('countState'));assert(!ids.has('mediaWindow'));assert.equal(ids.size,38);
});
test('换目标数字时保持计数相位，且前后保持端点',()=>{
 const points=[[10,0],[20,50],[30,100]];
 assert.deepEqual(countState(20,points,240),{value:120,progress:.5});
 assert.equal(countState(0,points,240).value,0);assert.equal(countState(40,points,240).value,240);
 assert.equal(countState(20,points).value,50);
});
test('两张计数卡分别入场，不会提前显示后一张文字',()=>{
 const c=read('../examples/flow-reuse.json');
 const early=renderScene(c,17/30,curves).markup;
 assert(early.includes(c.component.props.items[0].label));assert(!early.includes(c.component.props.items[1].label));
 assert(renderScene(c,35/30,curves).markup.includes(c.component.props.items[1].label));
});
test('文字参数转义后写入SVG，不执行注入标记',()=>{
 const c=read('../examples/flow-reuse.json');c.component.props.items[0].label='<script>bad()</script>';
 const html=renderScene(c,2,curves).markup;assert(!html.includes('<script>'));assert(html.includes('&lt;script&gt;'));
});
test('呼吸有启用时窗，灰底、弧线和文字同组缩放，朝向固定',()=>{
 const c=read('../examples/pulsing-ring-reuse.json'),p=c.component.props,b=p.breathing;
 assert.equal(pulseRingState(p,b.startFrame-1).scale,1);assert.equal(pulseRingState(p,b.endFrame).scale,1);
 assert(Math.abs(pulseRingState(p,b.startFrame+b.periodFrames/4).scale-(1+b.amplitude))<1e-10);
 assert(Math.abs(pulseRingState(p,b.startFrame+3*b.periodFrames/4).scale-(1-b.amplitude))<1e-10);
 const html=pulsingRing(p,40,c.background);for(const layer of['track','arc','labels'])assert(html.includes('data-ring-layer="'+layer+'"'));
 assert.equal((html.match(/rotate\(/g)||[]).length,1);assert(html.includes('rotate(-90)'));
});
test('分行出现与当前强调分别求值，强调前返回空状态',()=>{
 assert.equal(activeState(5,[10,20]),-1);assert.equal(activeState(15,[10,20]),0);
 const state=stagedState(15,[10,20],10);assert(state[0].alpha>0);assert.equal(state[1].alpha,0);
});
test('绘图入口拒绝未知名称和纯数值状态函数',()=>{
 const c=read('../examples/flow-reuse.json');
 assert.throws(()=>renderRefinedComponent({type:'unknown',props:{}},20,c.background),/未知/);
 assert.throws(()=>renderRefinedComponent({type:'countState',props:{}},20,c.background));
});
