# Docker Under Cursor

## Language

- [中文](/README__ZH.md)
- English

## Overview

DockerUnderCursor is a plugin of [Krita](https://krita.org/), it can make any docker float and display in the mouse position with keyboard shotcuts. Support Plugin Panel, E.g [Pigment.O](https://github.com/EyeOdin/Pigment.O).

## Features

- You can set a shortcut key for each docker to switch between floating and hidden(docked).
- You can fix the floating docker on the screen so that you can use shortcuts to move the docker between the cursor position and the fixed position. Press the dedicated shortcut key(Default Ctrl+`) on the floating docker you want to fix, and it is fixed.
- In addition you can set three optional functions.
  - Remember position of cursor relative to docker when docker was last hidden.
  - Keep floating docker inside the main window.
  - Auto-hide docker after cursor leaves docker.

## Preview

Quick show docker
![Preview](https://github.com/Aqaao/DockerUnderCursor/blob/main/IMAGE/Preview.gif)
Remember position of cursor relative to docker
![RememberRelativePosition](https://github.com/Aqaao/DockerUnderCursor/blob/main/IMAGE/RememberRelativePosition.gif)
Keep floating docker inside the main window
![KeepInMainwindow](https://github.com/Aqaao/DockerUnderCursor/blob/main/IMAGE/KeepInMainwindow.gif)
Fix docker.
![FixedFloattingDocker](https://github.com/Aqaao/DockerUnderCursor/blob/main/IMAGE/FixedFloattingDocker.gif)

## Install

1. Click **Code** at the top of this page，then click **Download ZIP** in pop-up menu。
2. Open Krita, click in order the top menu bar **Tools \- Scripts \- Import Python Plugin from File**, find zip file you downloaded，click open。
3. Select **Yes** in pop-up window，then **restart Krita**.

## Useage

If it's the first time you use the plugin, you won't find anything in the keyboard shortcuts configuration, you need to enable in settings。Click in order in the top menu bar **Tools \- Scripts \- DUC Settings panel** open setting dialog。Select the docker you need，and click **Save**，then **restart Krita**。Right now, open **configure Krita**，in **keyboard shortcuts** find **Scripts - Docker Under Cursor** ，you can see the items you have enabled, set a shortcut key for it!

## Known issues

- Some dockers with scroll bars(E.g Palette), the height of docker becomes smaller after switching the display multiple times.You need to drag the docker in the floating state to get it to attach and docked to the main window, and then it's normal.
  
## Log

- 2022.8.2 relese
- 2022.8.5 update:
  - work better in show canvas only mode.
  - now position of cursor outline will refresh after floating docker back mainwindow.
- 2022.8.5 once more update:
  - fix the cursor outline refresh not working in multi-view
  - fix bug that docker flicker when it displayed from hidden
- 2022.8.8 update:
  - add function remember mouse position relative to docker.you can enable it in setting panel. 
  - [Function preview](https://github.com/Aqaao/DockerUnderCursor/blob/main/IMAGE/NewFunction.gif)
- 2022.8.9 update：
  - add function limit position of docker, keeping docker from leaving the main window.you can enable it in setting panel
- 2022.8.9 one more update:
  - fix bug in multi-window mode only the newly opened window works properly.
  - optimized a bit code
- 2022.8.11 update：
  - add function, docker can auto-hide when mouse leaves the floating docker. 
  - [Function preview](https://github.com/Aqaao/DockerUnderCursor/blob/main/IMAGE/auto-hide.gif)
  - improved, optional options can take effect immediately after saving the settings, even without restarting krita
  - fix bug the moment docker is displayed cursor shape will change to size-cursor。
- 2022.8.11 fix：
  - fix bug hidden docker cant enable.
- 2022.8.13 fix：
  - fix bug，cant drag floating docker back mainwindow when enable docekr auto-hide.
- 2022.8.18 fix:
  - fix bug, add two lines of accidentally deleted code, it causes cursor flicker from normal-cursor to size-cursor.
- 2022.10.28 fix:
  - fix: block some error
  - fix: in docker auto-hide mode, open popup menu of floating docker causes docker to hide.
- 2022.12.3 update:
  - fix some error
  - add new function that fix docker.
