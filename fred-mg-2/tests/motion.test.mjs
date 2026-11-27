import test from'node:test';import assert from'node:assert/strict';import{valueAt,stateAt,sceneAt,validate}from'../src/motion.mjs';
test('键轨在前后端点保持状态，计数不会重新从零开始',()=>{const keys=[[10,4],[20,11],[30,6]];assert.equal(valueAt(keys,0),4);assert.equal(valueAt(keys,15),7.5);assert.equal(valueAt(keys,35),6);});
test('阶跃切换只在目标帧生效',()=>{const keys=[[0,0],[10,1,'step']];assert.equal(valueAt(keys,9),0);assert.equal(valueAt(keys,10),1);});
test('父子对象可独立控制，不把所有效果转成统一入场',()=>{const n={tracks:{x:[[0,60],[10,0]],alpha:[[0,1],[20,.2]]}};assert.equal(stateAt(n,5).x,30);assert.equal(stateAt(n,5).alpha,.8);});
test('相邻镜头端点属于新场，尾帧不越界',()=>{const ss=[{from:0,to:10},{from:10,to:20}];assert.equal(sceneAt(ss,10),ss[1]);assert.equal(sceneAt(ss,20),undefined);});
test('全片缺口与重复对象会被拒绝',()=>{const c={fps:30,frames:20,scenes:[{from:0,to:10,nodes:[{id:'a'}]},{from:11,to:20,nodes:[]}]};assert.throws(()=>validate(c),/缺口/);c.scenes[1].from=10;c.scenes[1].nodes=[{id:'a'}];assert.throws(()=>validate(c),/重复/);});
