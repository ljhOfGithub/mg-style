# nana mg1

新增[15个独立动效组件](components/README.md)与[单独预览目录](components/预览.html)，无需加载61秒整片时间线。原整片工程继续保留。

深蓝青紫的知识讲解 MG 模板。15类模块组合为30段、61.27秒的完整示例，采用Hyperframes实际编排和渲染。文案、媒体、卡片尺寸、主体位置与进退场时窗均可替换。

[查看通用示例](previews/通用示例.mp4) · [打开配置编辑器](编辑器.html) · [编辑配置](template/配置.json) · [来源与许可](来源与许可.md)

## 构建与预览

以下命令从仓库根目录执行。配置编辑器须经HTTP打开：在仓库根目录运行`python -m http.server 8788`，再访问`http://127.0.0.1:8788/nana-mg-1/编辑器.html`。

普通构建只用Python标准库；本地已经安装Hyperframes时，用自己的实际启动器调用固定的0.9.97版本。

```sh
python nana-mg-1/template/构建.py
python nana-mg-1/template/scripts/测试模板.py
npx hyperframes@0.9.97 preview nana-mg-1/模板工程
npx hyperframes@0.9.97 render nana-mg-1/模板工程 --quality delivery -o nana-mg1.mp4
```

## 换成自己的内容

在配置的`templates`修改模块通用字段，在`chapter_presets`修改六个章节预设，在`shots`按镜头ID覆盖。`scenes`定义完整时间线。`media`使用工程`assets/`内的相对路径。

- `summary_rect`：摘要卡左、上、宽、高。
- `media_rect`：每块媒体的左、上、宽、高。
- `slot_options`：媒体完整显示的位置、背景、圆角与边框。
- `presenter`：主体素材与矩形，不让媒体盖住关键面部。
- `page_peel`：镜像背面卷页的起点、时长与缓动；`exit`独立控制摘要、媒体和底层页退场。
- `summary_track`与`line_duration`：固定轨道和增长填充的时序。

第12段展示“编辑媒体卷出→底层资料显露→摘要和资料共同溶出”，第22段展示“摘要和完整资料页共同溶出”。两者不混成同一种退场。

## 模块

居中标题、媒体窗翻出、六宫格、文档与内层预览叠窗、编号章节卡、五卡展开、摘要与媒体、节点流程、媒体分区、悬浮媒体、三步故事板、大字强调、两次描勾、五步生产链、章节导航。

## 公开范围与检查

本目录的媒体是可编辑通用图形，不是软件实录、第三方案例或个人实测。参考片、自有个人角色和音轨均不随公开库分发。卷页使用斜切正面和镜像倾斜背面重建，不宣称物理曲面或原始关键帧一致。

修改后运行模块测试与仓库验证。通用示例经过实际Hyperframes渲染和半秒OCR，记录见[验证记录](验证记录.md)。技术检查与审美、用户认可分别记录。
