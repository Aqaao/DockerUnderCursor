# Docker Under Cursor

## Language

- [中文](/README__ZH.md)
- English

## Overview

DockerUnderCursor is a plugin of [Krita](https://krita.org/), it can make any docker float and display in the mouse position with keyboard shotcuts. Support Plugin Panel, E.g [Pigment.O](https://github.com/EyeOdin/Pigment.O).

## Preview

![This is an image](https://github.com/Aqaao/DockerUnderCursor/blob/main/IMAGE/Preview.gif)

## Log

- 2022.8.2 relese
- 2022.8.5 update:
  - work better in show canvas only mode.
  - now position of cursor outline will refresh after floating docker back mainwindow.
- 2022.8.5 once more update:
  - fix the cursor outline refresh not working in multi-view
  - fix bug that docker flicker when it displayed from hidden
- 2022.8.8 update:
  - add function remember mouse position relative to docker.you can enable it in setting panel.![This is an image](https://github.com/Aqaao/DockerUnderCursor/blob/main/IMAGE/NewFunction.gif)
- 2022.8.9 update：
  - add function limit position of docker, keeping docker from leaving the main window.you can enable it in setting panel

## Install

1. Click **Code** at the top of this page，then click **Download ZIP** in pop-up menu。
2. Open Krita, click in order the top menu bar **Tools \- Scripts \- Import Python Plugin from File**, find zip file you downloaded，click open。
3. Select **Yes** in pop-up window，then **restart Krita**.

## How it works

If it's the first time you use the plugin, you won't find anything in the keyboard shortcuts configuration, you need to enable in settings。Click in order in the top menu bar **Tools \- Scripts \- DUC Settings panel** open setting dialog。Select the docker you need，and click **Save**，then **restart Krita**。Right now, open **configure Krita**，in **keyboard shortcuts** find **Scripts - Docker Under Cursor** ，you can see the items you have enabled, set a shortcut key for it!

## Known issues

- Some dockers with scroll bars(E.g Palette), the height of docker becomes smaller after switching the display multiple times.You need to drag the docker in the floating state to get it to attach and docked to the main window, and then it's normal.
  
