"""Manage a docker's floating position, visibility, and pinned state."""

from krita import *

from .action_hold_filter import action_hold_filter


class DockerVisibilityToggler:
    """Remember the state needed to return a docker after a shortcut toggle."""

    # Krita persists settings as strings; retain the existing keys and values.
    trace_mouse = Krita.instance().readSetting(
        "DockerUnderCursor", "TraceMousePosition", "False"
    )
    clamp_position = Krita.instance().readSetting(
        "DockerUnderCursor", "ClampPosition", "False"
    )
    auto_conceal = Krita.instance().readSetting(
        "DockerUnderCursor", "AutoConceal", "False"
    )

    instances: list["DockerVisibilityToggler"] = []
    pinned_positions = {}

    def __init__(self, name):
        self.name = name
        self.window_name = None
        self.widget: QDockWidget | None = None
        # Remember whether the docker was hidden or was the active dock tab.
        self.was_hidden = True
        self.was_top = False
        self.cursor_offset = None
        self.auto_hide_filter = None
        self.action = None
        self.pinned = False
        self.away_from_pin = False
        self.pin_position = None
        self.instances.append(self)

    def trigger(self):
        action_hold_filter.action_key_pressed(self)

    def toggle_docker_status(self):
        """Show at the cursor, restore the docker, or move a pinned docker."""
        # Actions may become available before window setup has found the widget.
        if not self.widget:
            self.widget = (
                Krita.instance()
                .activeWindow()
                .qwindow()
                .findChild(QDockWidget, self.name)
            )
            if not self.widget:
                return
        if self.widget.isHidden():
            self.widget.unsetCursor()  # Avoid retaining the resize cursor.
            self.was_hidden = True
            if not self.widget.isFloating():
                self.widget.setFloating(True)
            self._move_docker()
            self.widget.show()
            self.widget.activateWindow()
        elif self.widget.isFloating():
            if self.pinned:
                self.toggle_pin_position()
            else:
                self.restore_docker()
        else:
            self.widget.unsetCursor()
            self.was_top = not self.widget.visibleRegion().isEmpty()
            self.widget.setFloating(True)
            self.widget.activateWindow()
            self._move_docker()
            self.was_hidden = False

    def _move_docker(self):
        cursor_position = QCursor.pos()
        if self.cursor_offset:
            docker_position = cursor_position - self.cursor_offset
        else:
            docker_position = QPoint(
                int(cursor_position.x() - self.widget.width() / 2),
                int(cursor_position.y() - self.widget.height() / 2),
            )
        if self.clamp_position == "True":
            self.widget.move(self._get_safe_position(docker_position))
        else:
            self.widget.move(docker_position)

    def toggle_pin_position(self):
        """Move between the saved pin position and the cursor position."""
        if self.away_from_pin:
            if self.trace_mouse == "True":
                self._record_cursor_position()
            self.widget.move(self.pin_position)
            self.widget.setWindowTitle(self.widget.windowTitle()[:-1])
            self.away_from_pin = False
            self._send_leave_event()
            self._send_move_event()
        else:
            self.widget.unsetCursor()
            self.away_from_pin = True
            self.pin_position = self.widget.pos()
            self._move_docker()
            self.widget.setWindowTitle(self.widget.windowTitle() + "*")

    def restore_docker(self):
        """Restore the docker's previous visibility and active-tab state."""
        if self.trace_mouse == "True":
            self._record_cursor_position()
        if self.was_hidden:
            self.widget.hide()
        else:
            self.widget.setFloating(False)
            if self.was_top:
                self.widget.raise_()
        self._send_leave_event()
        self._send_move_event()

    def update_auto_hide(self):
        if self.auto_hide_filter:
            self.auto_hide_filter.auto_conceal = self.auto_conceal == "True"

    def _send_move_event(self):
        """Refresh the canvas brush outline without moving the physical cursor."""
        cursor_position = QCursor.pos()
        widget = QApplication.widgetAt(cursor_position)
        if widget is not None and widget.__class__ == QOpenGLWidget:
            local_position = QPointF(widget.mapFromGlobal(cursor_position))
            move_event = QMouseEvent(
                QEvent.MouseMove,
                local_position,
                Qt.MouseButton.NoButton,
                Qt.MouseButton.NoButton,
                Qt.KeyboardModifier.NoModifier,
            )
            QCoreApplication.postEvent(widget, move_event)

    def _send_leave_event(self):
        if self.is_cursor_in_docker():
            QCoreApplication.postEvent(self.widget, QEvent(QEvent.Leave))

    def _record_cursor_position(self):
        # Auto-hide happens outside the docker; preserve the previous offset
        # in that case, and clear it only when auto-hide is disabled.
        if self.is_cursor_in_docker():
            self.cursor_offset = self.widget.mapFromGlobal(QCursor.pos())
        elif self.auto_conceal != "True":
            self.cursor_offset = None

    def is_cursor_in_docker(self):
        if not self.widget or not self.widget.isVisible():
            return False
        cursor_position = self.widget.mapFromGlobal(QCursor.pos())
        geometry = QWidget.geometry(self.widget)
        geometry.moveTo(0, 0)
        return geometry.contains(cursor_position)

    def _get_safe_position(self, docker_position) -> QPoint:
        """Clamp a global position using the main window's local coordinates."""
        window = Krita.instance().activeWindow().qwindow()
        relative_position = window.mapFromGlobal(docker_position)
        if relative_position.x() < 0:
            relative_position.setX(0)
        elif relative_position.x() > window.width() - self.widget.width():
            relative_position.setX(window.width() - self.widget.width())
        if relative_position.y() < 0:
            relative_position.setY(0)
        elif relative_position.y() > window.height() - self.widget.height():
            relative_position.setY(window.height() - self.widget.height())
        return window.mapToGlobal(relative_position)

    def pin(self):
        if self.widget.isFloating() and not self.widget.isHidden():
            self.pinned = True
            self.widget.setWindowTitle(self.widget.windowTitle() + "(pin)")
            self.pin_position = self.widget.pos()

    def cancel_pin(self):
        self.pinned = False
        # The title ends in '(pin)*' while away, and '(pin)' at the pin position.
        if self.away_from_pin:
            self.widget.setWindowTitle(self.widget.windowTitle()[:-6])
            self.away_from_pin = False
        else:
            self.widget.setWindowTitle(self.widget.windowTitle()[:-5])

    def reset_pin(self):
        if self.pinned:
            self.cancel_pin()
