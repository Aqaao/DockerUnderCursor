# Changelog

## 2.0 — 2026-09-15

> [!WARNING]
> **旧版本的快捷键可能失效。** 本版本更改了动作定义文件的位置与结构、快捷键分类和动作名称，升级后原有的快捷键可能不再生效。请重新为面板分配快捷键，然后重启 Krita。
>
> **Existing shortcuts may stop working.** This release changes the action
> definition file location and structure, the shortcut categories, and action
> names. After upgrading, reassign your shortcuts and restart Krita.


### Added / 新增

- 同时兼容 Qt5 与 Qt6 的 Krita 版本（新增兼容层，集中处理枚举、快捷键、鼠标事件和对话框差异）。
  Support for both Qt5- and Qt6-based Krita builds through a compatibility layer for enums, shortcuts, mouse events, and dialogs.
- 设置面板中，每个 Docker 勾选项下方以灰色小字显示其实际内部 ID。
  The settings panel now shows each docker's internal ID in small gray text below its checkbox.
- 设置面板新增 **Close** 按钮；点击 **Save** 后窗口保持打开，方便查看提示信息。
  Added a **Close** button. **Save** no longer closes the panel so the warning message stays visible.
- 设置面板顶部新增黄色提示：首次使用时提示选择 Docker 并保存；已启用面板的动作尚未注册时提示重启 Krita。
  A yellow message at the top of the settings panel prompts first-time setup and warns to restart Krita when enabled dockers' actions are not registered yet.
- 未保存更改时，窗口标题显示 `*`。
  The window title shows `*` when there are unsaved changes.
- 启动时若 action 文件与设置中的面板选择不一致，会按设置重新生成 action 文件以保持一致。
  On startup, the action file is regenerated to match the settings when the two differ.

### Changed / 变更

- 版本号更新至 **2.0**。
  Version bumped to **2.0**.
- 两个动作定义文件（`dockerundercursor.action`、`ducshotcuts.action`）合并为单个 `dockerundercursor.action`。
  The two action definition files were merged into a single `dockerundercursor.action`.
- 生成的 action 文件改存到 Krita 资源目录下的 `actions/`，不再写入插件目录。
  The generated action file is now saved under the `actions/` folder of Krita's resource directory instead of the plugin directory.
- 快捷键分类调整为 **Docker Under Cursor / General**（固定动作）和 **Docker Under Cursor / Dockers**（动态面板动作）。
  Shortcut categories are now **Docker Under Cursor / General** and **Docker Under Cursor / Dockers**.
- 菜单项与动作名称更新，例如 `DUC Settings panel` → `DUC Settings`、`DUC only canvas mode` → `DUC Toggle Canvas-Only Mode`、`DUC pin docker` → `DUC Pin/Unpin Docker`。
  Updated menu and action names, such as `DUC Settings panel` → `DUC Settings` and `DUC only canvas mode` → `DUC Toggle Canvas-Only Mode`.
- 面板勾选项左对齐。
  Docker options are now left-aligned.

### Fixed / 修复

- 修复切换画布模式时把固定位置当作函数调用的问题。
  Fixed the pinned position being called as a function in canvas-only mode.
- 修复初始化时删除不可用面板可能跳过后续面板的问题。
  Fixed unavailable dockers being removed while skipping later entries during setup.
- 修复打开设置面板时，已注册动作与设置选择不一致却不显示重启提示的问题。
  Fixed the restart warning not appearing at panel open when registered actions differed from the enabled dockers.

### Removed / 移除

- 从顶部菜单移除 **DUC Toggle Canvas-Only Mode**（仍可在快捷键中绑定）。
  Removed **DUC Toggle Canvas-Only Mode** from the top menu (it remains available for shortcut assignment).
- 删除 `ducshotcuts.action`（已合并）。
  Removed `ducshotcuts.action` (merged).
