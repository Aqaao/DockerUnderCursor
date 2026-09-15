"""Distinguish shortcut taps from press-and-hold interactions."""

from time import monotonic
from typing import TYPE_CHECKING

from krita import *

from .qt_compat import EventType, key_event_sequence

HOLD_THRESHOLD_SECONDS = 0.3

if TYPE_CHECKING:
    from .docker_visibility_toggler import DockerVisibilityToggler


class ActionHoldFilter(QMdiArea):
    """Toggle on press, then toggle back on release after a long hold."""

    def __init__(self) -> None:
        super().__init__()
        self._callback = lambda: qDebug("no action")
        self._action = None
        self._key_released = True
        self._last_press_time = monotonic()

    def action_key_pressed(self, toggler: "DockerVisibilityToggler") -> None:
        if self._key_released:
            self._callback = toggler.toggle_docker_status
            self._action = toggler.action
            self._last_press_time = monotonic()
            self._key_released = False
            self._trigger_action()

    def _trigger_action(self) -> None:
        self._callback()

    def _long_key_release(self) -> None:
        self._trigger_action()

    def _match_shortcuts(self, event: QKeyEvent) -> bool:
        if self._action:
            released_key = key_event_sequence(event).toString()
            if not released_key:
                return False
            for shortcut in self._action.shortcuts():
                shortcut_key = shortcut.toString()
                if released_key in shortcut_key or shortcut_key in released_key:
                    return True
        return False

    def eventFilter(self, obj: QWidget, event: QEvent) -> bool:
        # Docking destroys the floating QWindow. Handling its release event
        # could access a deleted Qt object, so only process widget events.
        if not isinstance(obj, QWindow):
            if event.type() == EventType.KeyRelease:
                if (
                    not event.isAutoRepeat()
                    and not self._key_released
                    and self._match_shortcuts(event)
                ):
                    self._key_released = True
                    self._action = None
                    if monotonic() - self._last_press_time > HOLD_THRESHOLD_SECONDS:
                        self._long_key_release()
        return False


action_hold_filter = ActionHoldFilter()
