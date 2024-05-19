from krita import *

from . import qt_event
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .docker_visibility_toggler import DockerVisibilityToggler


class DockerAutoHideFilter(QObject):

    def __init__(self, obj):
        super().__init__()
        self.docker_manager: "DockerVisibilityToggler" = obj
        self.mouse_pressed = False
        self.auto_conceal = False

    def eventFilter(self, obj, event):
        if self.auto_conceal:
            if event.type() == QEvent.MouseButtonPress:
                self.mouse_pressed = True
            if event.type() == QEvent.MouseButtonRelease:
                self.mouse_pressed = False
            if self.docker_manager.widget == obj and obj.isFloating() and not self.mouse_pressed:
                # Leaves docker event.
                if event.type() == QEvent.Leave:
                    if not self.docker_manager.is_cursor_in_docker():
                        if self.docker_manager.pinned:
                            if self.docker_manager.leave:
                                self.docker_manager.translocation()
                            else:
                                return False
                        else:
                            self.docker_manager.docker_return()
                # Block cursor shape toggle.
                elif event.type() == QEvent.MouseMove:
                    if event.pos().x() <= 1 or event.pos().x() >= obj.size().width() - 1:
                        return True
                    elif event.pos().y() <= 1 or event.pos().y() >= obj.size().height() - 1:
                        return True
        return False
