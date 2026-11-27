# houzi mg 1

原视频抖音来源：[《一句话调动AI团队，Magic把结果直接交付》](https://www.douyin.com/video/7707492692657327400)。来源身份与权利边界见[风格元数据](风格.json)。

暖纸格、彩色影板与黑圆角框组成的可复用MG组件库。包含20个SVG绘图或组合入口、5种CLI演示入口和4个实际预览；两个入口数量不相加。文字、颜色、媒体、入场帧和透明度曲线可分开设置。

## 快速开始

在本目录执行，需要Node.js，不需要安装npm依赖：

```bash
npm test
npm run build
npm run build:steps
npm run build:focus
npm run build:summary
npm run verify
```

默认构建24秒通用工程到`.build/neutral/index.html`。其他输出依次为`.build/steps`、`.build/focus`和`.build/summary`。构建产生HTML；Hyperframes实际渲染需本机已安装对应插件。仓库提供的4个预览已由Hyperframes CLI 0.9.99实际渲染，本次发布不重新制作画面。

## 先看示例再换内容

|示例|配置|预览|
|---|---|---|
|24秒团队流程，4章|[整片配置](examples/neutral.json)|[播放](previews/neutral.mp4)|
|5秒步骤卡，逐卡建立|[步骤参数](examples/component-steps.json)|[播放](previews/steps.mp4)|
|8秒四结果聚焦，短融变与背景虚化|[聚焦参数](examples/component-focus.json)|[播放](previews/focus.mp4)|
|4秒总结链，短上移和轻缩放|[总结参数](examples/component-summary-v2.json)|[播放](previews/summary.mp4)|

改JSON中的文字、accent、ats、at、curve或transitions后重新构建。字号和卡片几何是独立参数，长文案仍需检查边界。默认媒体为空对象，显示源码绘制的中性示例；接自己的图片时提供media槽，不需要参考片。

## 单独调用与引擎边界

```js
import {registry} from './src/components.mjs';
const svg = registry.painSummary({
  items: ['收集资料','共享上下文','核对交付'],
  frame: 30, at: 15, accent: '#ff6863'
});
```

函数返回SVG字符串，按当前帧重算，不依赖前帧。20个入口含静态背景与图形基元，不等于20种独立特效。具体签名、相位单位和媒体格式见[组件接口](组件接口.md)与[机器目录](components/catalog.json)。

源码可接Hypit的整数localFrame：调用者用章节开始帧加localFrame求绝对帧，再传给组件；或将绝对帧除以fps后调用renderScene。完整Hypit Producer、Timeline、Run及素材需由具体项目建立，本公开包不假装包含任意时长可直接运行的Hypit工程。参考复刻应由Hypit承担主体编排；Hyperframes可提供局部代码动效。无参考的新作和独立演示可使用本包HTML构建入口。

## 公开范围与验证

仅发布通用组件、许可依赖、配置及无声预览。不含参考全片、原音轨、第三方UI裁片、个人路径或操作历史；不附原内容工程的私有测试数据。预览哈希、半秒/末帧OCR和覆盖见[验证记录](verification/previews.json)。本包另做公开行为测试、4种示例构建、文件SHA及仓库检查，不把原工程42项私有回归改名为公开测试。

短融变的混合权重、部分逐卡曲线、箭头分组、阴影和模糊核仍是重建近似。技术验证不等于精确复刻或全片审美认可。自动审片器为可选工具，本库不安装或默认调用。素材和代码分别遵守[来源与许可](NOTICE.md)。
