const assert=require('node:assert/strict'),path=require('node:path');
const R=path.resolve(__dirname,'..'),{gsap}=require(path.join(R,'assets/vendor/gsap.min.js'));
require(path.join(R,'runtime/motions.js'));
const pill={opacity:1,x:0,y:0},bar={scaleX:1},letter={opacity:1,y:0};
const els={'[data-mg-id="pill"]':[pill],'[data-mg-id="bar"]':[bar],'[data-mg-id="letter"]':[letter]};
const stage={opacity:1,querySelectorAll:q=>els[q]||[]};global.document={getElementById:()=>stage};
const tl=RefMG.build(gsap,[{id:'test',domId:'test',start:0,end:5,visibleEnd:5,fadeIn:0,fadeOut:0,events:[
 {type:'fade',target:'#pill',at:1,duration:.2},
 {type:'move',target:'#pill',at:3,duration:.5,from:{y:0,opacity:1},to:{y:100,opacity:0}},
 {type:'bar',target:'#bar',at:1,duration:3,knots:[[0,.8],[1,1],[1.2,.5],[3,.9]],ease:'linear'},
 {type:'wordFall',target:'#letter',at:1,duration:.3,fromYs:[-60]}
]}]);
tl.seek(.5,false);assert.equal(pill.opacity,0,'未来退场不能提前显示胶囊');assert.equal(letter.opacity,0);assert.equal(bar.scaleX,.8);
tl.seek(1.3,false);assert.equal(pill.opacity,1);assert.equal(letter.y,0);
tl.seek(2,false);assert.equal(bar.scaleX,1);tl.seek(2.2,false);assert.equal(bar.scaleX,.5,'进度应确实回落');tl.seek(3.5,false);assert(pill.opacity<.01);
tl.seek(.5,false);assert.equal(pill.opacity,0,'倒退定位恢复初态');tl.kill();gsap.ticker.sleep();console.log('PASS earliest initial state, delayed exit, progress reset, character baseline and reverse seek');
