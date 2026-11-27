# 在 Hypit 中绑定真实案例

公开示例的图片槽是替换入口，没有原片媒体。实际复刻须把自己的原始完整素材先登记为资源，再用独立视频对象绑定源时窗；静帧示例不是连续视频证明。

本次私有工程实际使用43场独立编排、20个真实案例视频槽和独立原速旁白，完成真实 Run／Build／Result。新增MG图层由Hyperframes实际渲染，Hypit再将各场前景、原速案例和后景组合；不是把另一引擎整条成片放进单轨。

[sourceTimeMap](../src/source-time.mjs)返回Hypit `VisualMediaElement.sourceTime` 使用的整数帧关系：

```js
import {sourceTimeMap} from './src/source-time.mjs';
const mapping=sourceTimeMap(7872,2080,2320,300,20);
// 起帧读20帧；真实2080..2319全部以1倍播放；其余40帧是明确登记的末帧阅读。
const element={kind:'video',artifact:ownedVideoArtifact,muted:true,sourceTime:mapping};
```

实际对象还需要本场唯一的 `id`、`order`、父对象和 `style`，不能把这段省略样式的代码当作可独立执行工程。本例原始输入与模板时钟均为30fps；其他源帧率必须另外按实际时钟建立有理数映射，不能直接套用本例。源帧域使用左闭右开区间。目标太短时函数直接拒绝；不得暗中加速、循环或删掉真实操作。

本次验证的本地HTML渲染入口接受MP4及WebM视频资源，不接受`video/quicktime`。透明MG使用WebM；MOV可存档，不能直接提交给这个入口。原始文件、兼容编码与实际编排结果分别保留哈希和工具日志。

裁切区域使用源像素坐标；容器位置使用画布坐标。视频位于裁切容器内时，其位移须相对父对象计算。保持固定比例与位移，不能为了对齐错误核对区域而改素材。

声音只做音轨存在、完整解码及原速映射检查；不设置试听或用户批准停点。字幕使用实际新旁白定位的一套文本。完整实际成片及连续左右对比另作验收，源时序示例和自动候选分数不能替代它们。
