from time import time
from typing import TYPE_CHECKING

from krita import *

if TYPE_CHECKING:
    from .docker_visibility_toggler import DockerVisibilityToggler


class ActionHoldFilter(QMdiArea):
    def __init__(self) -> None:
        super().__init__()
        self._callback = lambda: qDebug("no action")
        self._action = None
        self._key_released = True
        self._last_press_time = time()

    def action_key_pressed(self, toggler: "DockerVisibilityToggler") -> None:
        if self._key_released:
            self._callback = toggler.toggleDockerStatus
            self._action = toggler.action
            self._last_press_time = time()
            self._key_released = False
            self._trigger_action()

    def _trigger_action(self) -> None:
        self._callback()

    def _long_key_release(self) -> None:
        self._trigger_action()

    def _match_shortcuts(self, event: QKeyEvent) -> bool:
        if self._action:
            match event.key():
                case Qt.Key_Shift:
                    released_key = QKeySequence(Qt.ShiftModifier).toString()
                case Qt.Key_Control:
                    released_key = QKeySequence(Qt.ControlModifier).toString()
                case Qt.Key_Alt:
                    released_key = QKeySequence(Qt.AltModifier).toString()
                case _:
                    released_key = QKeySequence(
                        event.modifiers() | event.key()).toString()
            for s in self._action.shortcuts():
                shortcut_key = s.toString()
                if released_key in shortcut_key or shortcut_key in released_key:
                    return True
        return False

    def eventFilter(self, obj: QWidget, event: QEvent) -> bool:
        if event.type() == QEvent.KeyRelease:
            if (not event.isAutoRepeat() and not self._key_released and self._match_shortcuts(event)):
                self._key_released = True
                if time() - self._last_press_time > 0.3:
                    self._long_key_release()
        return False


actionHoldFilter = ActionHoldFilter()
