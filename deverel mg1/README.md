# deverel mg1

可复用的 MG 动效组件库，基于已经交付的 Google AI Pro MG 提取工程 v3-r1 整理。包含38个SVG绘图组件（15个分层组件、23个基础兼容组件），另有1个媒体适配器和4个状态计算入口。组件按帧计算状态，可单独调用或组合进自己的视频。

## 开始使用

在本文件所在目录执行，需要本机Node.js：

```bash
npm test
npm run build
npm run build:notebook
npm run build:ring
npm run verify
```

默认构建双额度卡，生成`.build/flow-reuse/index.html`；四卡和呼吸环分别在`.build/notebook-reuse`、`.build/pulsing-ring-reuse`。构建不需要安装npm依赖，GSAP和字体随包提供。实际渲染使用本机已安装的Hyperframes插件，本次既有示例由CLI 0.9.99实渲。

## 先看三个换内容示例

| 示例 | 内容与可改参数 | 配置 | 视频 |
|---|---|---|---|
| 双额度卡，4.5秒 | 120/2400点；两组独立入场、计数曲线和卡片位置 | [配置](examples/flow-reuse.json) | [播放](previews/flow-reuse.mp4) |
| 四卡计数，5秒 | 6/800/120/30；四组数字与说明分别出现 | [配置](examples/notebook-reuse.json) | [播放](previews/notebook-reuse.mp4) |
| 轻呼吸环，4秒 | 24小时；灰环、弧线与文字整组轻呼吸，缺口朝向固定 | [配置](examples/pulsing-ring-reuse.json) | [播放](previews/pulsing-ring-reuse.mp4) |

修改JSON中的`component.props`即可换文字、目标值、配色、位置和动作时窗。`ats`和增长曲线的时间单位为帧，示例采用30fps；`duration`在工程根层为秒，在组件props里通常为入场帧数。更长文本需要同时调整文字区域，不能靠裁切掩盖重叠。

## 单独调用组件

```js
import {refinedRegistry} from './src/refined-components.mjs';
const markup = refinedRegistry.independentMetrics(props, frame, theme);
```

将返回的SVG标记放入自己的画面，用Hyperframes时间线提供`frame`。更换目标数值不必重写增长函数；新视频需要按自己的口播和镜头重新设置时窗。

完整入口见[组件目录](components/catalog.json)、[分层组件接口](组件接口.md)和[基础组件接口](基础组件接口.md)。`src/scene.mjs`保留组合入口，`src/browser.mjs`把状态接入GSAP时间线；旧基础组件用于兼容，独立数字增长、弱态强调和交棒请优先使用分层组件。

## 公开范围与验证

只包含可公开的代码、许可依赖、通用配置和三个无原声的组件预览。参考原片、原声、第三方真实UI裁片及本机路径均不发布。示例不需要原片播放器；媒体适配器由使用者接入自己有权使用的媒体，不把窗口包装当作软件实际演示。

三个视频沿用已经完成实渲、完整解码及半秒/末帧OCR的既有文件，本轮没有重新生成或改画面。配置与源码对应的哈希和覆盖范围见[验证记录](verification/previews.json)。原内容工程的45项回归不改名冒充公开包测试；本包另外运行不依赖私有媒体的组件行为测试、三个示例构建和仓库检查。源码构建、技术检查、精确复刻和用户认可分别记录。

Notebook波形包络、部分入场曲线、环几何和材质仍是重建近似。自动审片器是可选工具，本库不自动安装、调用或强制启用。素材和代码许可见[来源与许可](NOTICE.md)。
