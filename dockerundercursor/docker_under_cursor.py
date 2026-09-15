"""Register Krita actions and connect them to the window's dock widgets."""

from krita import *

from .docker_auto_hide_filter import DockerAutoHideFilter
from .docker_visibility_toggler import DockerVisibilityToggler
from .qt_compat import exec_dialog
from .setting_panel import SettingPanel


class DockerUnderCursor(Extension):
    """Expose per-docker shortcuts, pinning, and plugin settings."""

    def setup(self):
        """Defer initialization until Krita creates a window and its actions."""

    def createActions(self, window):
        """Implement Krita's action-registration callback."""
        self._create_docker_toggle_actions(window)

        settings_action = window.createAction(
            "settingpanel", "DUC Settings", "tools/scripts"
        )
        settings_action.triggered.connect(self._open_setting_panel)

        pin_action = window.createAction("pindocker", "DUC Pin/Unpin Docker", "")
        pin_action.triggered.connect(self._pin_docker)

        # No menu location: the action stays available for shortcut assignment.
        canvas_mode_action = window.createAction(
            "togglecanvasmode", "DUC Toggle Canvas-Only Mode", ""
        )
        canvas_mode_action.triggered.connect(self._toggle_canvas_mode)

        Krita.instance().notifier().windowCreated.connect(self._final_setup)

    def _open_setting_panel(self):
        settings = SettingPanel()
        exec_dialog(settings)

    def _create_docker_toggle_actions(self, window):
        tree = SettingPanel.read_action_tree()
        for definition in tree.findall(SettingPanel.DOCKER_ACTIONS_PATH + "/Action"):
            action_id = definition.get("name", "")
            if not action_id.startswith(SettingPanel.DOCKER_ACTION_PREFIX):
                continue
            docker_name = action_id[len(SettingPanel.DOCKER_ACTION_PREFIX) :]
            toggler = DockerVisibilityToggler(docker_name)
            action = window.createAction(action_id, "", "")
            action.triggered.connect(toggler.trigger)
            toggler.action = action

    def _pin_docker(self):
        for toggler in DockerVisibilityToggler.instances:
            if toggler.is_cursor_in_docker():
                if toggler.pinned:
                    toggler.cancel_pin()
                else:
                    toggler.pin()
                break

    def _toggle_canvas_mode(self):
        # Canvas-only mode changes visibility and clears pin state. Keep the
        # original pinned positions so the triggered callback can restore them.
        for toggler in DockerVisibilityToggler.instances:
            if toggler.pinned:
                position = (
                    toggler.pin_position
                    if toggler.away_from_pin
                    else toggler.widget.pos()
                )
                DockerVisibilityToggler.pinned_positions[toggler] = position
        Krita.instance().action("view_show_canvas_only").trigger()

    def _restore_pin_status(self):
        for toggler, position in DockerVisibilityToggler.pinned_positions.items():
            toggler.widget.setFloating(True)
            toggler.widget.show()
            toggler.widget.move(position)
            toggler.pin()
        DockerVisibilityToggler.pinned_positions.clear()

    def _final_setup(self):
        # Regenerate the file when its docker selection differs from settings.
        SettingPanel.sync_action_file()

        # Iterate over a copy: unavailable dockers are removed from the registry.
        for toggler in DockerVisibilityToggler.instances[:]:
            if not toggler.window_name:
                window = Krita.instance().activeWindow().qwindow()
                toggler.window_name = window.objectName()
                toggler.widget = window.findChild(QDockWidget, toggler.name)
                if toggler.widget:
                    toggler.auto_hide_filter = DockerAutoHideFilter(toggler)
                    toggler.widget.installEventFilter(toggler.auto_hide_filter)
                    toggler.update_auto_hide()
                    toggler.widget.visibilityChanged.connect(toggler.reset_pin)
                    if toggler.widget.isFloating():
                        # Unlock floating dockers restored by Krita's workspace.
                        lock_icon = Krita.instance().icon("docker_lock_b")
                        for button in toggler.widget.titleBarWidget().children():
                            if (
                                button.__class__ == QAbstractButton
                                and button.icon().cacheKey() == lock_icon.cacheKey()
                            ):
                                button.setChecked(False)
                else:
                    DockerVisibilityToggler.instances.remove(toggler)
                    toggler.action.triggered.disconnect(toggler.trigger)
                    Krita.instance().writeSetting(
                        "DockerUnderCursor", toggler.name, "0"
                    )

        Krita.instance().action("view_show_canvas_only").triggered.connect(
            self._restore_pin_status
        )
        Krita.instance().notifier().windowCreated.disconnect(self._final_setup)


Krita.instance().addExtension(DockerUnderCursor(Krita.instance()))
