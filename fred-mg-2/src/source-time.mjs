// Hypit VisualMediaElement.sourceTime：实际案例全部源帧以1倍播放，禁止为适配旁白拉伸。
export function sourceTimeMap(sourceFrames,start,end,targetFrames,headHold=0){
 for(const v of[sourceFrames,start,end,targetFrames,headHold])if(!Number.isSafeInteger(v))throw Error('源与目标时窗须为整数帧');
 if(sourceFrames<1||start<0||end<=start||end>sourceFrames||headHold<0)throw Error('源时窗越界');
 const run=end-start;if(targetFrames<headHold+run)throw Error('目标太短，不能压缩或丢弃真实案例');
 const piece=(a,z,source,rate)=>({target:{startFrame:a,endFrameExclusive:z},sourceAtStart:{numerator:source,denominator:1},rate:{numerator:rate,denominator:1}}),pieces=[];
 if(headHold)pieces.push(piece(0,headHold,start,0));
 pieces.push(piece(headHold,headHold+run,start,1));
 if(targetFrames>headHold+run)pieces.push(piece(headHold+run,targetFrames,end-1,0));
 return{sourceFrameRate:{numerator:30,denominator:1},sourceFrameCount:sourceFrames,pieces};
}
