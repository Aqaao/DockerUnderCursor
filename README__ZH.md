# Docker Under Cursor

## 语言

- 中文
- [English](/README.md)

## 介绍

Docker Under Cursor 是一款 [Krita](https://krita.org/) 插件，实现了一键让任何 Krita 内部面板浮动显示到鼠标位置，可以让你享受到不用移动数位笔就能随意操作的便利。支持插件面板，例如 [Pigment.O](https://github.com/EyeOdin/Pigment.O) 调色板。

## 预览

![This is an image](https://github.com/Aqaao/DockerUnderCursor/blob/main/IMAGE/Preview.gif)

## 安装

1. 点击本页面上方的 Code，然后点击 Download ZIP。
2. 打开 Krita，在上方菜单中点击 **工具 \- 脚本 \- 从文件导入 Python 插件**，选中你下载好的压缩文件，点击打开。
3. 在弹窗中选择**是**，然后**重启 Krita** 即安装完成。

## 使用

第一次使用插件需要手动启用各个面板的可用性。点击上方菜单中 **工具 \- 脚本 \- DUC Settings panel** 调出配置面板。勾选上你需要的面板，点击 **Save**，然后再次**重启 Krita**。此时打开**配置 Krita**窗口，在**键盘快捷键**中找到 **Scripts - Docker Under Cursor** ，就可以看到你启用的面板项，因为某些原因（懒）这里没有中文，不知道面板叫啥名请看下面的对照表。为面板显示设置一个快捷键后就可以使用了。

当面板固定在窗口中时，按切换键会让面板浮动并出现到鼠标位置，再次按下会让面板重新固定。如果**不想让面板固定**在窗口上，**请在面板浮动时关闭面板**，这样当你按下切换键时面板会出现在鼠标下，再次按下时面板会直接隐藏。

## 已知问题

- 某些带有滚动条的面板（色板、笔刷预设等）在固定窗口上时，在多次进行浮动显示操作后，固定面板的高度会变小。这时请在面板浮动时手动拖拽面板到固定状态，这样再进行切换就正常了。

## Dockers名称对照表

Docker名称|面板标题
|-|-|
|AnimationCurvesDocker|动画曲线|
|ArrangeDocker|矢量图形排列控制|
|ArtisticColorSelector|美术拾色器|
|ChannelDocker|通道|
|ColorSelectorNg|多功能拾色器|
|CompositionDocker|图层显示方案|
|DigitalMixer|颜色比例混合器|
|GamutMask|色域蒙版|
|GridDocker|网格与参考线|
|HistogramDocker|直方图|
|History (历史)|撤销历史|
|KisLayerBox|图层|
|LogDocker|日志查看器|
|LutDocker|LUT 色彩管理|
|OnionSkinsDocker|绘图纸外观|
|OverviewDocker|导航器 = 总览图|
|PaletteDocker|色板|
|PatternDocker|图案|
|PresetDocker|笔刷预设|
|PresetHistory|笔刷预设历史|
|RecorderDocker|录像工具|
|SmallColorSelector|小型拾色器|
|Snapshot|图像版本快照|
|SpecificColorSelector|量化拾色器|
|StoryboardDocker|分镜头脚本|
|SvgSymbolCollectionDocker|SVG 矢量图形库|
|TasksetDocker|操作流程|
|TimelineDocker|动画时间轴|
|ToolBox|工具箱|
|TouchDocker|触摸屏辅助按钮|
|comics_project_manager_docker|漫画项目管理|
|lastdocumentsdocker|最近图像列表|
|quick_settings_docker|笔刷常用数值一键切换面板|
|sharedtooldocker|工具选项|