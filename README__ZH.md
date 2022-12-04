# Docker Under Cursor

## 语言

- 中文
- [English](/README.md)

## 介绍

Docker Under Cursor 是一款 [Krita](https://krita.org/) 插件，实现了一键让任何 Krita 内部面板浮动显示到鼠标位置，可以让你享受到不用移动数位笔就能随意操作的便利。支持插件面板，例如 [Pigment.O](https://github.com/EyeOdin/Pigment.O) 调色板。

## 功能

- 可以为每一个面板设置一个切换显示/隐藏的快捷键。如果面板停靠在主窗口或者被隐藏，按下切换键面板将出现在鼠标下方。如果面板位于鼠标下方，按下切换键面板将根据之前的状态隐藏或者停靠。
- 你可以将悬浮的面板固定，按下快捷键（默认是 ctrl + ~）后将鼠标位置的浮动面板固定，这样按下面板的切换键就可以让浮动面板从固定时的位置移动到鼠标下。
- 设置面板内有三个可选设置
  - **[Remember mouse position relative to docker]**
    可以选择记住上次隐藏面板时鼠标的相对位置，否则鼠标位于面板中心。
  - **[Keep docker inside the main window]**
    保持悬浮面板位于主窗口内，防止面板出现在屏幕边缘被遮挡。
  - **[Auto conceal docker after mouse leaves]**
    鼠标离开悬浮面板后面板将会自动隐藏。

## 预览

快速调出面板
![Preview](https://github.com/Aqaao/DockerUnderCursor/blob/main/IMAGE/Preview.gif)
记住鼠标相对于面板的位置
![RememberRelativePosition](https://github.com/Aqaao/DockerUnderCursor/blob/main/IMAGE/RememberRelativePosition.gif)
保持面板位于主窗口内
![KeepInMainwindow](https://github.com/Aqaao/DockerUnderCursor/blob/main/IMAGE/KeepInMainwindow.gif)
固定浮动面板
![FixedFloattingDocker](https://github.com/Aqaao/DockerUnderCursor/blob/main/IMAGE/FixedFloattingDocker.gif)

## 安装

1. 点击主页面上方的 Code，然后点击 Download ZIP。
2. 打开 Krita，在上方菜单中点击 **工具 \- 脚本 \- 从文件导入 Python 插件**，选中你下载好的压缩文件，点击打开。
3. 在弹窗中选择**是**，然后**重启 Krita** 即安装完成。

## 使用

第一次使用插件需要手动启用各个面板的可用性。点击上方菜单中 **工具 \- 脚本 \- DUC Settings panel** 调出配置面板。勾选上你需要的面板，点击 **Save**，然后再次**重启 Krita**。此时打开**配置 Krita**窗口，在**键盘快捷键**中找到 **Scripts - Docker Under Cursor** ，就可以看到你启用的面板项，因为某些原因（懒）这里没有中文，不知道面板叫啥名请看下面的对照表。为面板显示设置一个快捷键后就可以使用了。

## 已知问题

- 某些带有滚动条的面板（色板、笔刷预设等）固定窗口上时，在多次进行浮动显示操作后，固定面板的高度会变小。这时请在面板浮动时手动拖拽面板到固定状态，这样再进行切换就正常了。

## 更新日志

- 2022.8.2 发布
- 2022.8.5 更新:
  - 面板切换在面板隐藏模式下可以正常使用了（享受沉浸式绘画）.
  - 将浮动面板切换回到主窗口后，光标的轮廓将会刷新，防止了鼠标位置和轮廓位置分离的bug。
- 2022.8.5 再次更新：
  - 修复了光标轮廓无法在多视图中刷新的bug
  - 修复了面板从隐藏状态中显示时会闪烁的bug
- 2022.8.8 更新:
  - 添加功能，可以记住鼠标相对于面板的位置了。你可以在设置面板选择启用它。[功能演示](https://github.com/Aqaao/DockerUnderCursor/blob/main/IMAGE/NewFunction.gif)
- 2022.8.9 更新：
  - 添加功能，限制面板位置，让面板无法离开主窗口，防止被遮挡。你可以在设置面板选择启用它。
- 2022.8.9 再次更新：
  - 修复了在多窗口模式下只有新打开的窗口可以正常运行的bug
  - 优化代码
- 2022.8.11 更新：
  - 添加功能，鼠标离开浮动面板后面板自动隐藏。在设置面板内启用[功能演示](https://github.com/Aqaao/DockerUnderCursor/blob/main/IMAGE/auto-hide.gif)
  - 优化，三个可选选项现在可以在保存设置后立即生效，即使不重启krita
  - 修复了面板浮动显示时会有一瞬间光标变成缩放形状的bug。
- 2022.8.11 修复：
  - 修复了隐藏面板不能显示的bug。
- 2022.8.13 修复：
  - 修复了开启面板自动隐藏后无法拖拽面板回到主窗口的bug
- 2022.8.18 修复：
  - 添加两行不小心删掉的代码，防止光标在正常形状和缩放形状之间闪烁
- 2022.10.28 修复：
  - 屏蔽了一些报错
  - 修复了在悬浮面板自动隐藏的状态下打开面板的弹出菜单会导致面板消失的bug
- 2022.12.3 更新：
  - 修复了一些错误
  - 添加了固定面板的功能

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
