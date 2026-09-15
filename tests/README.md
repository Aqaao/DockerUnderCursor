# Qt compatibility checks

`test_qt_compat.py` imports the complete plugin using real Qt widgets and events,
with a stub for Krita's application-specific API. Run each binding in a separate
process to avoid loading Qt5 and Qt6 together.

From the repository root, use [uv](https://docs.astral.sh/uv/) in PowerShell:

```powershell
$env:DUC_QT_API = "PyQt5"
uv run --isolated --with PyQt5 python tests/test_qt_compat.py

$env:DUC_QT_API = "PyQt6"
uv run --isolated --with PyQt6 python tests/test_qt_compat.py
```

The tests use Qt's offscreen platform by default. They cover settings creation
and saving, action-registration prompts, key combinations and modifier release,
short and long shortcut presses, mouse coordinates and auto-hide filtering,
OpenGL widget recognition, and dialog execution.

The compatibility helpers in `dockerundercursor/qt_compat.py` use Qt classes
exported by Krita. The test harness deliberately omits `QOpenGLWidget` from those
exports to verify that canvas detection does not depend on its Python module.

These checks do not replace testing inside Krita. In both Qt5- and Qt6-based
builds, verify shortcut assignment after restarting, floating and docking,
pinning, canvas-only mode, and brush-outline updates on the actual canvas.
