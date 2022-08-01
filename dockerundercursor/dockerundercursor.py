from krita import Krita, Extension
from PyQt5 import QtWidgets
from .dockertoggle import DockerToggle
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

    def getSettingPanel(self):
        setting = SettingPanel()
        setting.exec()

    def createDockerToggleActions(self, window):
        tree = ET.parse(SettingPanel.file)
        root = tree.getroot()

        for i,v in enumerate(root.findall(".//Action/text")):
            setattr(self, "action_{0}".format(i), DockerToggle(v.text))
            window.createAction("duc_{0}".format(v.text), "","tools/scripts/DUC menu").triggered.connect(getattr(self, "action_{0}".format(i)).toggleDockerStatus)


Krita.instance().addExtension(DockerUnderCursor(Krita.instance()))