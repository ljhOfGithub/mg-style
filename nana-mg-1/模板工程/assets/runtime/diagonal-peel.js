/* nana mg1: 正面斜切＋镜像倾斜背面；系数按参考动作归一化，未声称真实曲面模拟。 */
window.nanaPeel=function(front,back,width,height){
 const a=-.832,b=-.428,c=-.718,d=.832,k=-c/d;
 const knots=[[0,2.853,0,1],[.2,1.498,.464,.8],[.35,1.189,.369,.63],[.5,.880,.274,.25],[.65,.571,.178,0],[.8,.261,.083,0],[1,-.151,-.044,0]];
 function polygon(offset){
  const points=[[0,0],[width,0],[width,height],[0,height]],out=[];
  for(let i=0;i<points.length;i++){
   const x=points[i],y=points[(i+1)%points.length],dx=x[0]+k*x[1]-offset,dy=y[0]+k*y[1]-offset;
   if(dx<=0)out.push(x);
   if((dx<=0)!==(dy<=0)){const t=dx/(dx-dy);out.push([x[0]+(y[0]-x[0])*t,x[1]+(y[1]-x[1])*t]);}
  }
  return out.length>2?'polygon('+out.map(v=>v[0]+'px '+v[1]+'px').join(',')+')':'polygon(0px 0px,0px 0px,0px 0px)';
 }
 return function(p){
  p=Math.max(0,Math.min(1,p));let i=0;while(i<knots.length-2&&p>knots[i+1][0])i++;
  const x=knots[i],y=knots[i+1],t=(p-x[0])/(y[0]-x[0]);const tx=(x[1]+(y[1]-x[1])*t)*width,ty=(x[2]+(y[2]-x[2])*t)*height;
  front.style.clipPath=polygon(tx+a*width-c/d*(ty+b*width));
  back.style.clipPath='inset(0px 0px 0px '+((x[3]+(y[3]-x[3])*t)*width)+'px)';back.style.transformOrigin='0 0';back.style.transform='matrix('+[a,b,c,d,tx,ty].join(',')+')';
  back.style.opacity=p>0&&p<1?'1':'0';
 };
};
