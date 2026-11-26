# fred mg 1 独立组件

23个原场景已拆为23个独立组件。每个组件有自己的模板、文字字段、数据、媒体插槽和动作事件；导出后只有一个场景，起点为0，不读取151秒整片配置，也不复制其他22个模板。

[打开组件预览](preview.html) · [参数目录](catalog.json) · [验证记录](validation.json) · [返回风格首页](../README.md)

## 构建与渲染

在仓库根目录执行，需要Python 3.10以上、`beautifulsoup4`与FFmpeg/ffprobe；实际渲染另需Node.js及已安装的Hyperframes Codex插件：

```sh
python3 -m pip install -r fred-mg-1/template/requirements.txt
python3 fred-mg-1/components/build.py --component 04-chapter-flip --output .build/my-chapter
```

使用自己的配置：

```sh
python3 fred-mg-1/components/build.py --config config.json --media-root ./my-media --output .build/my-clip
```

`--media-root`只解析这次指定的替换素材；未改的素材仍从组件包读取。素材使用根目录内的相对路径，不能写绝对路径或越界。图片槽接收PNG/JPEG/WebP/SVG，视频槽接收MP4/WebM/MOV；不能互相替代。

导出后的`config.json`是这个单场工程的实际配置，直接修改它再运行工程自己的`build.py`即可重建。`spec.json`只是导出时的简洁参数快照；要重新应用这种规格及媒体校验，使用本组件库的构建命令，不会在导出工程中静默读取它。

独立导出包括`index.html`、`compositions/component.html`、一个`modules/*.tpl`、`config.json`、`spec.json`、重建入口、样式、动作运行库、字体与实际使用的媒体。导出素材使用独立副本；改动导出文件不会污染源包或其他工程。

```sh
# 不依赖原库重建这个工程
python3 .build/my-clip/build.py
# 用已安装的Hyperframes检查与渲染
node "$HOME/.agents/skills/hyperframes/scripts/plugin-cli.mjs" --cli-version 0.9.97 check .build/my-clip --json
node "$HOME/.agents/skills/hyperframes/scripts/plugin-cli.mjs" --cli-version 0.9.97 render .build/my-clip --fps 30 --quality looks --output my-clip.mp4
```

本地预览页面：在仓库根目录运行`python3 -m http.server 8000`，用系统Chrome打开`http://127.0.0.1:8000/fred-mg-1/components/preview.html`。页面展示已渲染样例；修改JSON后导出，重新构建和渲染才能更新视频。

## 参数格式

```json
{
  "format": "fred-component@1",
  "component": "04-chapter-flip",
  "duration": 3.8,
  "data": {"chapter": {"number": "08", "title": "资料整理"}}
}
```

- `component`使用[目录](catalog.json)的英文ID。最小配置只需`format`和`component`。
- `duration`从该组件的默认完整时长至30秒，按1/30秒对齐。不会用整体变速压缩主要动作；延长主要增加阅读停留，章节退场随新总长移动，入场速度不变。媒体保持到外层完整退场结束，六格队列的媒体不会提前移除。视频素材还须足够覆盖原速时窗及源偏移，不冻结、循环或变速补齐。
- `content`只接受当前组件目录中的`fields`。每项有`max_length`，超长或未知字段直接报错，不自动截字。动态数字、提示词和章节不混进普通文字槽。
- `data`只接受当前组件的`data_fields`及实际消费的子字段：翻牌章节使用`number/title`，分组章节使用`number/groups`；开场预算只使用`human`，账本还可改AI标签与条宽。章节标题最多8字，分组章节每组最多6字、两组共最多9字。提示词、摘要、末卡和独立状态文字分别填写，不会被另一层绑定静默盖掉。
- `media`使用目录登记的`media-01`等插槽。每槽标明`image/video`，可从加长方案查看替换图片例子。
- `theme`支持已有四个六位十六进制颜色字段。`motions`使用预设中的事件ID，只接受`at/duration`。视频墙绑定和带`knots`变化节点的动作时长不可通过普通覆盖修改，必须保留其完整状态变化；错误覆盖会被拒绝。

## 组件清单

清单按原场景顺序排列。五种章节是不同动作，不把它们合并成同一种淡入。

| ID | 用途 | 默认秒数 | 动作类型 |
|---|---|---|---|
| `01-opening-wall` | 开场 | 6.000 | counter, draw, fade, mask, move, wordFall |
| `02-contrast` | 反差 | 4.000 | bar, fade, style |
| `03-workflow` | 流程 | 7.800 | fade |
| `04-chapter-flip` | 章节01 | 1.800 | fade, flip, move, state |
| `05-prompt-input` | 输入 | 11.600 | move, state, style, typing |
| `06-script-summary` | 写稿 | 5.600 | fade, move, style |
| `07-chapter-reveal` | 章节02 | 1.800 | fade |
| `08-preparation` | 准备零分钟 | 7.000 | bar, state, style |
| `09-media-wave` | 素材 | 10.167 | fade, wavefill |
| `10-chapter-fade` | 章节03 | 1.633 | fade, style |
| `11-cloud-budget` | 云端预算 | 6.000 | fade, tiles |
| `12-render-queue` | 渲染 | 8.600 | bar, counter, fade, state, style |
| `13-background-work` | 后台工作 | 4.000 | bar, fade |
| `14-chapter-zoom` | 章节04 | 1.800 | fade, giant, move, state |
| `15-review` | 审片 | 12.400 | fade, state, style |
| `16-revision` | 返修 | 7.900 | fade, state |
| `17-chapter-slide` | 章节05 | 1.900 | move |
| `18-publishing` | 发布 | 14.300 | fade, state, style |
| `19-budget-ledger` | 账本 | 10.300 | bar, counter, fade, state, style |
| `20-parallel-progress` | 并行 | 9.300 | bar, fade, move, state |
| `21-duration-comparison` | 对比 | 11.600 | bar, fade |
| `22-value-summary` | 价值 | 10.100 | bar, fade, style |
| `23-ending-type` | 末卡 | 2.867 | wordFall |

## 来源、媒体与验证边界

动作源码从mg-style提交`9c34106367df7cb996bbcf4f724012fc51d45175`的fred mg 1模板拆分；每个组件的原场景时窗见目录。沿用`mg-styles-15/01-flat-vector`固定版本`3164c24e188899fd79b155124cfa7eefc7a906e9`的时间原语与MIT许可。字体、GSAP和媒体的许可分别保留，详见[来源说明](../NOTICE.md)。没有宣称原作者工程或逐像素复刻。

验证分别使用默认和加长方案。带普通文字字段的组件替换文案，带数据绑定的组件替换对应数据，有图片槽的组件另测横图、竖图或方图；动态视频原速保留。长版是参数测试，不冒充用户的原素材复现。

开场、分层媒体、翻牌、波形、六槽队列、四路进度重置和末卡字符归位均保留原动作结构。跨场景背景作为组件自己的依赖，保留`data-media-start`源偏移；独立组件不会把背景从0秒重播。翻牌半面和发布前占位说明标记了明确的有意遮挡，未将其他遮挡一概豁免。

机器检查、完整解码、半秒及末帧OCR、独立实际图复核与用户认可分别记录。只保证已验证的有限文案、比例与时长组合，不把预览成功写成任意输入保证。
