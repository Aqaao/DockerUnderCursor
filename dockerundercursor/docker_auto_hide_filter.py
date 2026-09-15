"""Return floating dockers when the cursor leaves their bounds."""

from typing import TYPE_CHECKING

from krita import *

from .qt_compat import EventType, mouse_event_position

if TYPE_CHECKING:
    from .docker_visibility_toggler import DockerVisibilityToggler


class DockerAutoHideFilter(QObject):
    """Handle auto-hide while avoiding interference with mouse drags."""

    def __init__(self, toggler: "DockerVisibilityToggler"):
        super().__init__()
        self.toggler = toggler
        self.mouse_pressed = False
        self.auto_conceal = False

    def eventFilter(self, obj, event):
        """Implement Qt's event-filter callback for the managed docker."""
        if self.auto_conceal:
            if event.type() == EventType.MouseButtonPress:
                self.mouse_pressed = True
            if event.type() == EventType.MouseButtonRelease:
                self.mouse_pressed = False
            if (
                self.toggler.widget == obj
                and obj.isFloating()
                and not self.mouse_pressed
            ):
                if event.type() == EventType.Leave:
                    if not self.toggler.is_cursor_in_docker():
                        if self.toggler.pinned:
                            if self.toggler.away_from_pin:
                                self.toggler.toggle_pin_position()
                            else:
                                return False
                        else:
                            self.toggler.restore_docker()
                # Suppress resize-cursor changes at the floating docker's edge.
                elif event.type() == EventType.MouseMove:
                    position = mouse_event_position(event)
                    if position.x() <= 1 or position.x() >= obj.width() - 1:
                        return True
                    if position.y() <= 1 or position.y() >= obj.height() - 1:
                        return True
        return False
