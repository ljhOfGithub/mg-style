# mg style

可复用的 MG（动态图形）风格集合。每个风格独立放在根目录的一个子文件夹中，包含自己的源码、配置、素材、编辑器、预览、使用说明和 Skill。

## 风格目录

| 风格 | 内容 | 入口 | 原视频抖音来源 |
|---|---|---|---|
| fred mg 1 | 黑白紫工作流风格，23个独立参数组件、148项动作事件、单组件预览与本地编辑器 | [打开风格文件夹](fred-mg-1/) · [使用说明](fred-mg-1/README.md) | [原视频](https://www.douyin.com/video/7711624059825491263) |
| nana mg1 | 深蓝青紫讲解风格，15个独立参数组件、30段原示例、单组件预览与构建 | [打开风格文件夹](nana-mg-1/) · [使用说明](nana-mg-1/README.md) | [原视频](https://www.douyin.com/video/7667501595546180473) |
| deverel mg1 | 38个绘图组件，双卡、四卡和轻呼吸环独立示例 | [打开风格文件夹](<deverel mg1/>) · [使用说明](<deverel mg1/README.md>) | [原视频](https://www.douyin.com/video/7709865794791918848) |
| houzi mg 1 | 20个暖纸格与章节卡组件，4个换内容预览 | [打开风格文件夹](<houzi mg 1/>) · [使用说明](<houzi mg 1/README.md>) | [原视频](https://www.douyin.com/video/7707492692657327400) |
| houzi mg2 | 11个纸格、闭环、流水线与卡片组件族，4个独立预览 | [打开风格文件夹](<houzi mg2/>) · [使用说明](<houzi mg2/README.md>) | [原视频](https://www.douyin.com/video/7677862342813617444) |
| fred mg2 | 暖金黑底榜单风格，43场原时序组件、96项来源事件，已按专用Python审片修订 | [打开风格文件夹](fred-mg-2/) · [使用说明](fred-mg-2/README.md) | [原视频](https://www.douyin.com/video/7712675882543975689) |

## 添加新风格

1. 在根目录新建风格文件夹，例如 `my-next-style/`，专属文件均放在其中。
2. 在`风格.json`的`reference_source`登记原视频抖音正式链接、作品号和核实依据，并在`README.md`展示该链接；根目录`index.json`同步`reference_url`。来源链接不代表第三方素材可再分发。
3. 在该文件夹提供 `README.md`、`风格.json`、模板工程与来源许可；风格 Skill、测试和预览图也放在同一文件夹。
4. 在根目录[index.json](index.json)登记相对根目录的路径，并在上方风格目录添加入口。
5. 运行 `python tools/verify_repository.py` 核对配置、默认构建、基线文件与文档链接。

当前 [fred mg 1 的完整安装、编辑与导出命令](fred-mg-1/README.md)以仓库根目录为执行目录。公开素材使用通用占位内容，个人媒体另存。

## 通用文件

根目录只保留集合目录、仓库约定、通用校验工具与[许可说明](NOTICE.md)。各风格使用自己的相对资源路径，新增风格不需要改动已有风格。

目录统一使用英文命名，旧路径对应见[目录迁移说明](docs/directory-migration.md)。文档正文仍使用简体中文。
