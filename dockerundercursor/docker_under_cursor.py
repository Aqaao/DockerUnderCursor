from copy import copy
import xml.etree.cElementTree as ET

from krita import *

from dockerundercursor.action_hold_filter import ActionHoldFilter
from dockerundercursor.docker_visibility_toggler import DockerVisibilityToggler
from dockerundercursor.setting_panel import SettingPanel
from dockerundercursor.docker_auto_hide_filter import DockerAutoHideFilter


class DockerUnderCursor(Extension):

    def __init__(self, parent):
        super().__init__(parent)

    def setup(self):
        pass

    def createActions(self, window):
        # dynamic create docker toggle actions
        self._create_docker_toggle_actions(window)

        # create display setting panel action
        action_1 = window.createAction(
            "settingpanel", "DUC setting panel", "tools/scripts"
        )
        action_1.triggered.connect(self._open_setting_panel)

        # create fix docker action
        action_2 = window.createAction("pindocker", "", "")
        action_2.triggered.connect(self._pin_docker)

        # create toggle view mode action
        action_3 = window.createAction(
            "togglecanvasmode", "DUC only canvas mode", "tools/scripts"
        )
        action_3.triggered.connect(self._toggle_canvas_mode)

        Krita.instance().notifier().windowCreated.connect(self._final_setup)

    def _open_setting_panel(self):
        setting = SettingPanel()
        setting.exec()

    def _create_docker_toggle_actions(self, window):
        tree = ET.parse(SettingPanel.file)
        root = tree.getroot()
        # n = window.qwindow().objectName()

        for v in root.findall(".//Action/text"):
            toggler = DockerVisibilityToggler(v.text)
            action: QAction = window.createAction("duc_{0}".format(v.text), "", "")
            action.triggered.connect(toggler.trigger)
            toggler.action = action

    def _pin_docker(self):
        for d in DockerVisibilityToggler.INSTANCES:
            if d.selfIsParent()[0]:
                if d.pinned == False:
                    d.pin()
                else:
                    d.cancel_pin()
                break

    def _toggle_canvas_mode(self):
        for d in DockerVisibilityToggler.INSTANCES:
            if d.pinned:
                if d.leave:
                    DockerVisibilityToggler.PINDOCKERS[d] = d.pin_position()
                else:
                    DockerVisibilityToggler.PINDOCKERS[d] = d.widget.pos()
        Krita.instance().action("view_show_canvas_only").trigger()

    def _recovery_pin_status(self):
        for d, pos in DockerVisibilityToggler.PINDOCKERS.items():
            d.widget.setFloating(True)
            d.widget.show()
            d.widget.move(pos)
            d.pin()
        DockerVisibilityToggler.PINDOCKERS = {}

    def _final_setup(self):
        for d in DockerVisibilityToggler.INSTANCES:
            if not d.window:
                qwin = Krita.instance().activeWindow().qwindow()
                d.window = qwin.objectName()
                d.widget = qwin.findChild(QWidget, d.name)
                if d.widget:
                    d.monitor = DockerAutoHideFilter(d)
                    d.widget.installEventFilter(d.monitor)
                    d.update_auto_hide()
                    d.widget.visibilityChanged.connect(d.reset_pin)
                    if d.widget.isFloating():
                        # reset docker lock status
                        lock_icon = Krita.instance().icon("docker_lock_b")
                        for i in d.widget.titleBarWidget().children():
                            if (
                                i.__class__ == QAbstractButton
                                and i.icon().cacheKey() == lock_icon.cacheKey()
                            ):
                                i.setChecked(False)
                else:
                    DockerVisibilityToggler.INSTANCES.remove(d)
                    d.action.triggered.disconnect(d.trigger)
                    Krita.instance().writeSetting("DockerUnderCursor", d.name, "0")

        Krita.instance().action("view_show_canvas_only").triggered.connect(
            self._recovery_pin_status
        )
        Krita.instance().notifier().windowCreated.disconnect(self._final_setup)


Krita.instance().addExtension(DockerUnderCursor(Krita.instance()))
