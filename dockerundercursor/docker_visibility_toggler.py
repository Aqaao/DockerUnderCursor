from krita import *

from .action_hold_filter import actionHoldFilter


class DockerVisibilityToggler:

    TRACEMOUSE = Krita.instance().readSetting(
        "DockerUnderCursor", "TraceMousePosition", "False"
    )
    CLAMPPOSITION = Krita.instance().readSetting(
        "DockerUnderCursor", "ClampPosition", "False"
    )
    AUTOCONCEAL = Krita.instance().readSetting(
        "DockerUnderCursor", "AutoConceal", "False"
    )

    INSTANCES: list["DockerVisibilityToggler"] = []
    PINDOCKERS = {}

    def __init__(self, name):
        self.name = name
        self.window = None
        self.widget: DockWidget = None
        self.hidden = True
        self.top = False
        self.mousepos = None
        self.monitor = None
        self.action = None
        self.pinned = False
        self.leave = False
        self.pin_position = None
        self.INSTANCES.append(self)

    def trigger(self):
        actionHoldFilter.action_key_pressed(self)

    # The method is core.
    def toggleDockerStatus(self):
        if not self.widget:  # idk why need this check
            self.widget = (
                Krita.instance().activeWindow().qwindow().findChild(QWidget, self.name)
            )
            if not self.widget:
                return
        if self.widget.isHidden():
            self.widget.unsetCursor()  # avoid cursor flicker
            self.hidden = True
            if not self.widget.isFloating():
                self.widget.setFloating(True)
            self._move_docker()
            self.widget.show()
            self.widget.activateWindow()
        elif self.widget.isFloating():
            if self.pinned:
                self.translocation()
            else:
                self.docker_return()
        else:  # If docked.
            self.widget.unsetCursor()
            if self.widget.visibleRegion().isEmpty():
                self.top = False
            else:
                self.top = True
            self.widget.setFloating(True)
            self.widget.activateWindow()
            self._move_docker()
            self.hidden = False

    def _move_docker(self):
        pos = QCursor.pos()
        if self.mousepos:
            dockerpos = QPoint(
                int(pos.x() - self.mousepos.x()), int(pos.y() - self.mousepos.y())
            )
        else:
            dockerpos = QPoint(
                int(pos.x() - self.widget.width() / 2),
                int(pos.y() - self.widget.height() / 2),
            )
        if self.CLAMPPOSITION == "True":
            self.widget.move(self._get_safe_position(dockerpos))
        else:
            self.widget.move(dockerpos)

    def translocation(self):
        if self.leave:
            if self.TRACEMOUSE == "True":
                self._record_cursor_pos()
            self.widget.move(self.pin_position)
            self.widget.setWindowTitle(self.widget.windowTitle()[0:-1])
            self.leave = False
            self._send_leave_event()
            self._send_move_event()
        else:
            self.widget.unsetCursor()
            self.leave = True
            self.pin_position = self.widget.pos()
            self._move_docker()
            self.widget.setWindowTitle(self.widget.windowTitle() + "*")

    def docker_return(self):
        if self.TRACEMOUSE == "True":
            self._record_cursor_pos()
        if self.hidden:
            self.widget.hide()
        else:
            self.widget.setFloating(False)
            if self.top:
                self.widget.raise_()
        self._send_leave_event()
        self._send_move_event()  # refresh position of cursor outline

    def update_auto_hide(self):
        if self.monitor:
            if self.AUTOCONCEAL == "True":
                self.monitor.auto_conceal = True
            elif self.AUTOCONCEAL == "False":
                self.monitor.auto_conceal = False

    def _send_move_event(self):
        pos_0 = QCursor.pos()
        wobj = QApplication.widgetAt(pos_0)
        if wobj != None and wobj.__class__ == QOpenGLWidget:
            event = QEvent.MouseMove
            button = Qt.MouseButton.NoButton
            key = Qt.KeyboardModifier.NoModifier
            pos_1 = wobj.mapFromGlobal(pos_0)
            pos = QPointF(pos_1)

            moveevent = QMouseEvent(event, pos, button, button, key)
            QCoreApplication.postEvent(wobj, moveevent)

    def _send_leave_event(self):
        if self.is_cursor_in_docker():
            QCoreApplication.postEvent(self.widget, QEvent(QEvent.Leave))

    def _record_cursor_pos(self):
        if self.is_cursor_in_docker():
            self.mousepos = self.widget.mapFromGlobal(QCursor.pos())
        elif self.AUTOCONCEAL == "True":
            return
        else:
            self.mousepos = None

    def is_cursor_in_docker(self):
        if not self.widget.isVisible():
            return False
        pos = self.widget.mapFromGlobal(QCursor.pos())
        geometry = self.widget.geometry()
        geometry.moveTo(0, 0)
        if geometry.contains(pos):
            return True
        return False

    def _get_safe_position(self, dockerpos) -> QPoint:
        window = Krita.instance().activeWindow().qwindow()
        rpos = window.mapFromGlobal(dockerpos)
        if rpos.x() < 0:
            rpos.setX(0)
        elif rpos.x() > window.width() - self.widget.width():
            rpos.setX(window.width() - self.widget.width())
        if rpos.y() < 0:
            rpos.setY(0)
        elif rpos.y() > window.height() - self.widget.height():
            rpos.setY(window.height() - self.widget.height())
        return window.mapToGlobal(rpos)

    def pin(self):
        if self.widget.isFloating() and not self.widget.isHidden():
            self.pinned = True
            self.widget.setWindowTitle(self.widget.windowTitle() + "(pin)")
            self.pin_position = self.widget.pos()
            qDebug(f"pin {self.name}")

    def cancel_pin(self):
        self.pinned = False
        if self.leave == True:
            self.widget.setWindowTitle(self.widget.windowTitle()[:-6])
            self.leave = False
        else:
            self.widget.setWindowTitle(self.widget.windowTitle()[:-5])
        qDebug(f"unpin {self.name}")

    def reset_pin(self):
        if self.pinned:
            self.cancel_pin()
