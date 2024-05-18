from time import time

from krita import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .DockerVisibilityToggler import DockerVisibilityToggler

class ActionHoldFilter(QMdiArea):
    def __init__(self) -> None:
        super().__init__()
        self._callback = lambda:qDebug("no action")
        self._action = None
        self._key_released = True
        self._last_press_time = time()
    
    def actionKeyPressed(self,toggler:"DockerVisibilityToggler") -> None:
        if self._key_released:
            self._callback = toggler.toggleDockerStatus
            self._action = toggler.action
            self._last_press_time = time()
            self._key_released = False
            self.triggerAction()
        
    def triggerAction(self) -> None:
        self._callback()

    def longKeyRelease(self) -> None:
        self.triggerAction()
    
    def matchShortcuts(self,event:QKeyEvent) -> bool:
        if self._action:
            if event.key() in (Qt.Key_Shift,Qt.Key_Control,Qt.Key_Alt):
                released_key = QKeySequence(event.modifiers()).toString()
            else:
                released_key = QKeySequence(event.modifiers() | event.key()).toString()
            for s in self._action.shortcuts():
                shortcut_key = s.toString()
                if released_key in shortcut_key or shortcut_key in released_key:
                    return True
        return False
    
    def eventFilter(self, obj:QWidget, event:QEvent) -> bool:
        if event.type() == QEvent.KeyRelease:
            if (not event.isAutoRepeat() and not self._key_released and self.matchShortcuts(event)):
                self._key_released = True
                if time() - self._last_press_time > 0.3:
                    self.longKeyRelease()
        return False

actionHoldFilter = ActionHoldFilter()