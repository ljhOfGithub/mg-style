# houzi mg2

原视频抖音来源：[《让AI把内容创作、分发和变现串起来》](https://www.douyin.com/video/7677862342813617444)。来源身份与权利边界见[风格元数据](风格.json)。

纸格底、黑线框、彩色投影与短回位组成的MG组件库。11个组件族支持分开替换文字、颜色、品牌、角色、媒体与入场帧；包含九章通用配置和4个独立预览。组件族、绘制函数、状态方法和实例分别计数，不相加。

## 快速开始

在本目录执行，需要Node.js，不必安装npm依赖：

```bash
npm test
npm run build
npm run build:card
npm run build:loop
npm run build:sticker
npm run build:outro
npm run verify
```

默认构建[九章通用配置](examples/neutral.json)到`.build/neutral`，85.633秒、1440×1080、30fps。其余命令各生成4秒独立HTML。构建与实际视频渲染分开；HTML可交给已安装的Hyperframes插件渲染，包内4个预览已实际渲染。本库使用固定1440×1080布局，换画幅需同步几何和CSS。

## 示例与入口

|示例|配置|实际预览|
|---|---|---|
|短回位卡片|[参数](examples/card.json)|[播放](previews/card.mp4)|
|机器人四平台闭环|[参数](examples/loop.json)|[播放](previews/loop.mp4)|
|中性收藏贴纸|[参数](examples/sticker.json)|[播放](previews/sticker.mp4)|
|拍摄、制作、发布与增长流水线|[参数](examples/outro.json)|[播放](previews/outro.mp4)|

完整接口见[组件接口](组件接口.md)，组件族见[机器目录](components/catalog.json)。九章配置只生成通用画面，不含真实软件媒体；媒体框为空槽，不代表实际操作演示。

```js
import {componentHtml} from './src/components.mjs';
import {settleState} from './src/motion.mjs';
const item = {
  id:'my-loop', renderer:'robot-loop', kind:'world',
  brand:'资料流', diagramLabels:['收集','整理','核对','交付'],
  rect:[1715,420,2880,1435],
  anchors:{absent:14,first:15,middle:23,clear:32}
};
const markup = componentHtml(item);
const state = settleState(23,item);
```

这里返回HTML与确定的当前帧状态；调用者把状态应用到对应元素。更完整的运行时使用createFrameRenderer，支持逆向跳帧。actorSrc默认不附角色，填写自己的真实资源路径后使用。

## Hypit与Hyperframes

纯DOM状态可由Hypit的局部整数帧加章节起点后调用renderFrame；Hyperframes入口使用renderAt秒数定位。参考复刻的主体、真实媒体和Run/Build由具体Hypit工程建立。本公开库提供组件和HTML构建，不假装附带任意视频可直接执行的Hypit运行环境。无参考的新作、局部组件和本页独立示例使用Hyperframes。

## 公开范围与验证

公开内容只含可复用代码、许可依赖、通用配置、无声预览与测试。包内无完整参考片、原声音轨、私人角色、真实UI裁片、账户信息或私人操作历史。[验证记录](verification/previews.json)绑定每条预览SHA及半秒/末帧OCR。公开测试独立覆盖参数和时钟行为，不沿用其他工程的私有测试数量。

机器人、人物、材质、软边和中间曲线是代码重建近似；技术检查与OCR不等于精确视觉复刻。自动审片器为可选工具，本库不默认安装或运行。代码与字体、GSAP许可分开保留，见[来源与许可](NOTICE.md)。
