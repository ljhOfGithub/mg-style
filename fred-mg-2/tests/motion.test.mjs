import test from'node:test';import assert from'node:assert/strict';import{valueAt,stateAt,sceneAt,validate}from'../src/motion.mjs';
import fs from'node:fs';import{sourceTimeMap}from'../src/source-time.mjs';
const example=JSON.parse(fs.readFileSync(new URL('../examples/source-timeline.json',import.meta.url))),scene=id=>example.scenes.find(s=>s.id===id);
const walk=ns=>ns.flatMap(n=>[n,...walk(n.children??[])]);
test('键轨在前后端点保持状态，计数不会重新从零开始',()=>{const keys=[[10,4],[20,11],[30,6]];assert.equal(valueAt(keys,0),4);assert.equal(valueAt(keys,15),7.5);assert.equal(valueAt(keys,35),6);});
test('阶跃切换只在目标帧生效',()=>{const keys=[[0,0],[10,1,'step']];assert.equal(valueAt(keys,9),0);assert.equal(valueAt(keys,10),1);});
test('父子对象可独立控制，不把所有效果转成统一入场',()=>{const n={tracks:{x:[[0,60],[10,0]],alpha:[[0,1],[20,.2]]}};assert.equal(stateAt(n,5).x,30);assert.equal(stateAt(n,5).alpha,.8);});
test('相邻镜头端点属于新场，尾帧不越界',()=>{const ss=[{from:0,to:10},{from:10,to:20}];assert.equal(sceneAt(ss,10),ss[1]);assert.equal(sceneAt(ss,20),undefined);});
test('全片缺口与重复对象会被拒绝',()=>{const c={fps:30,frames:20,scenes:[{from:0,to:10,nodes:[{id:'a'}]},{from:11,to:20,nodes:[]}]};assert.throws(()=>validate(c),/缺口/);c.scenes[1].from=10;c.scenes[1].nodes=[{id:'a'}];assert.throws(()=>validate(c),/重复/);});
test('第二段出现时纸张已跳到完整承载高度，不重现黑字越纸',()=>{
 const nodes=walk(scene('context-paper').nodes),paper=nodes.find(n=>n.id==='context-paper-paper'),paragraph=nodes.find(n=>n.id==='context-paper-paragraph1');
 for(const frame of[4627,4632,4635]){const bottom=paper.bounds[1]+valueAt(paper.tracks.height,frame);assert.equal(valueAt(paper.tracks.height,frame),581);for(const n of walk(paragraph.children).filter(n=>n.kind==='text'))assert.ok(n.bounds[1]+n.bounds[3]<=bottom,n.id);}
 assert.equal(valueAt(paper.tracks.height,4660),792);
});
test('压缩条从满宽收至五分之一，左锚保持且不反向增长',()=>{
 const n=walk(scene('context-compress').nodes).find(n=>n.id==='context-compress-compression-fill');assert.equal(n.bounds[0],80);assert.equal(valueAt(n.tracks.width,4497),694);assert.equal(valueAt(n.tracks.width,4522),139);for(let f=4498;f<=4522;f++)assert.ok(valueAt(n.tracks.width,f)<=valueAt(n.tracks.width,f-1));
});
test('Handy只有18条实际波形，多出的旧对象保持不可见',()=>{const ns=scene('handy-input').nodes.filter(n=>/wave\d+$/.test(n.id));assert.equal(ns.filter(n=>stateAt(n,3830).alpha>0).length,18);assert.equal(ns.filter(n=>stateAt(n,3714).alpha>0).length,0);});
test('原速案例所有源帧完整使用，目标太短直接拒绝',()=>{
 const m=sourceTimeMap(7872,2080,2320,300,20);assert.deepEqual(m.pieces.map(p=>p.rate.numerator),[0,1,0]);assert.deepEqual(m.pieces[1].target,{startFrame:20,endFrameExclusive:260});assert.equal(m.pieces[1].sourceAtStart.numerator,2080);assert.equal(m.pieces[2].sourceAtStart.numerator,2319);assert.throws(()=>sourceTimeMap(7872,2080,2320,239),/太短/);assert.throws(()=>sourceTimeMap(7872,7800,7900,200),/越界/);
});
