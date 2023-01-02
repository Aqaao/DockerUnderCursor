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
