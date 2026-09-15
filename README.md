# Docker Under Cursor

[中文](README__ZH.md) | English

## Overview

Docker Under Cursor is a [Krita](https://krita.org/) plugin that brings dockers to the cursor with keyboard shortcuts. It also supports dockers provided by other plugins, such as [Pigment.O](https://github.com/EyeOdin/Pigment.O).

## Features

- Assign a shortcut to each enabled docker. Press it to show the docker at the cursor, then press it again to hide it or return it to its docked state.
- Customize the floating behavior with three options:
  - **Remember cursor position within the docker**: reuse the cursor's position within the docker, recorded when the docker was last restored or hidden. When disabled, the docker is centered on the cursor.
  - **Keep floating dockers inside the main window**: constrain the floating docker's position to the main window.
  - **Restore dockers when the cursor leaves**: automatically hide the docker, dock it again, or return it to its pinned position when the cursor leaves it.
- Pin a floating docker by hovering over it and pressing **Ctrl + backtick (\`)**. Its shortcut then moves it between the pinned position and the cursor. Press the pin shortcut again to unpin it.
- Preserve pinned dockers when toggling canvas-only mode by assigning **Tab** to **DUC Toggle Canvas-Only Mode**. Remove any conflicting Tab assignment first.

## Preview

### Show a docker at the cursor

![A docker displayed at the cursor](IMAGE/Preview.gif)

### Remember the cursor's relative position

![Remembering the cursor position within a docker](IMAGE/RememberRelativePosition.gif)

### Keep dockers inside the main window

![Constraining a floating docker to the main window](IMAGE/KeepInMainwindow.gif)

### Pin a floating docker

![Moving a docker between its pinned position and the cursor](IMAGE/FixedFloattingDocker.gif)

## Installation

1. On the repository page, select **Code → Download ZIP**.
2. In Krita, select **Tools → Scripts → Import Python Plugin from File** and open the downloaded ZIP file.
3. Confirm that you want to enable the plugin, then **restart Krita**.

If the plugin is not enabled, open **Configure Krita → Python Plugin Manager**, enable **Docker Under Cursor**, and restart Krita.

## Usage

1. Open **Tools → Scripts → DUC Settings**.
2. Select the dockers you want to control and click **Save**.
3. **Restart Krita** to load the selected docker actions.
4. Open **Configure Krita → Keyboard Shortcuts → Scripts → Docker Under Cursor** and assign a shortcut to each enabled docker.
5. Use those shortcuts to bring dockers to the cursor and restore their previous state.

Shortcut entries use Krita's internal docker IDs, which may differ from the titles shown in the interface. Pinning and canvas-only mode actions are listed under **Docker Under Cursor: Other Actions**.

Changes to the three behavior options take effect when you click **Save**. Changes to the selection of enabled dockers require a restart.

## Known issues

- Some dockers with scroll bars, such as Palette and Brush Presets, may shrink in height after being floated and docked repeatedly. To restore their size, float the docker and manually drag it back into the main window's docking area.

## Development

The plugin runs inside Krita and uses its `krita` module and PyQt bindings.

- `docker_under_cursor.py`: extension registration and action setup.
- `docker_visibility_toggler.py`: docker positioning, visibility, and pinning.
- `action_hold_filter.py` and `docker_auto_hide_filter.py`: shortcut and mouse event handling.
- `setting_panel.py`: settings dialog and generated action definitions.
- `qt_event.py`: event-name lookup for debugging.

From the repository root, run the following checks with [uv](https://docs.astral.sh/uv/):

```sh
uvx ruff check .
uvx ruff format --check .
python -m compileall -q dockerundercursor
```

Use `uvx ruff format .` to format the Python source. Formatting and lint rules are defined in `pyproject.toml`; editor defaults are in `.editorconfig`.

Use `snake_case` for internal methods and variables, `PascalCase` for classes, and `UPPER_SNAKE_CASE` for constants. Preserve Krita and Qt callback names such as `createActions` and `eventFilter`, as well as existing action IDs and persisted settings keys.

GUI behavior must be verified in Krita: enable dockers and restart, assign shortcuts, toggle docked and hidden dockers, exercise each behavior option, pin and unpin a docker, and toggle canvas-only mode with a pinned docker both at and away from its pinned position.
