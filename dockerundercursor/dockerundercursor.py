from krita import Krita, Extension
from PyQt5 import QtWidgets
from .dockertogglemanager import DockerToggleManager
from .settingpanel import SettingPanel
import xml.etree.cElementTree as ET


class DockerUnderCursor(Extension):

    def __init__(self, parent):
        super().__init__(parent)

    def setup(self):
        pass

    def createActions(self, window):
        # create menu
        action_menu = window.createAction("DUC menu", "DUC menu", "tools/scripts")
        menu = QtWidgets.QMenu("DUC menu", window.qwindow())
        action_menu.setMenu(menu)

        # dynamic create docker toggle actions
        self.createDockerToggleActions(window)

        # create display setting panel action
        action_2 = window.createAction("settingpanel", "DUC setting panel","tools/scripts")
        action_2.triggered.connect(self.getSettingPanel)

        action_3 = window.createAction("pindocker", "DUC pin docker","tools/scripts")
        action_3.triggered.connect(self.pinDocker)

    def getSettingPanel(self):
        setting = SettingPanel()
        setting.exec()

    def createDockerToggleActions(self, window):
        tree = ET.parse(SettingPanel.file)
        root = tree.getroot()
        n = window.qwindow().objectName()

        for v in root.findall(".//Action/text"):
            toggler = DockerToggleManager(v.text)
            action = window.createAction("duc_{0}".format(v.text), "","tools/scripts/DUC menu")
            action.triggered.connect(toggler.toggleDockerStatus)
            toggler.action = action

    def pinDocker(self):
        for d in DockerToggleManager.LIST:
            if d.selfIsParent() and d.widget.isFloating():
                if d.pinned == False:
                    d.pin()
                else:
                    d.cancelPin()
                break

    def clearPinStatus(self):
        pass

    def savePinStatus(self):
        pass

    def loadPinStatus(self):
        pass

Krita.instance().addExtension(DockerUnderCursor(Krita.instance()))