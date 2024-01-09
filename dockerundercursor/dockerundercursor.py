from krita import Krita, Extension
from PyQt5.QtWidgets import QWidget
from .dockertogglemanager import DockerToggleManager
from .settingpanel import SettingPanel
from .dockermonitor import DockerMonitor
import xml.etree.cElementTree as ET


class DockerUnderCursor(Extension):

    def __init__(self, parent):
        super().__init__(parent)

    def setup(self):
        pass

    def createActions(self, window):
        # dynamic create docker toggle actions
        self.createDockerToggleActions(window)

        # create display setting panel action
        action_1 = window.createAction("settingpanel", "DUC setting panel","tools/scripts")
        action_1.triggered.connect(self.getSettingPanel)

        # create fix docker action
        action_2 = window.createAction("pindocker", "","")
        action_2.triggered.connect(self.pinDocker)

        # create toggle view mode action
        action_3 = window.createAction("togglecanvasmode", "DUC only canvas mode","tools/scripts")
        action_3.triggered.connect(self.toggleCancasMode)
        
        Krita.instance().notifier().windowCreated.connect(self.finalSetup)
        # Krita.instance().notifier().applicationClosing.connect(self.savePinStatus)

    def getSettingPanel(self):
        setting = SettingPanel()
        setting.exec()

    def createDockerToggleActions(self, window):
        tree = ET.parse(SettingPanel.file)
        root = tree.getroot()
        #n = window.qwindow().objectName()

        for v in root.findall(".//Action/text"):
            toggler = DockerToggleManager(v.text)
            action = window.createAction("duc_{0}".format(v.text),"","")
            action.triggered.connect(toggler.toggleDockerStatus)
            toggler.action = action

    def pinDocker(self):
        for d in DockerToggleManager.LIST:
            if d.selfIsParent()[0]:
                if d.pinned == False:
                    d.pin()
                else:
                    d.cancelPin()
                break

    def toggleCancasMode(self):
        for d in DockerToggleManager.LIST:
            if d.pinned:
                if d.leave:
                    DockerToggleManager.PINDOCKERS[d] = d.pin_position()
                else:
                    DockerToggleManager.PINDOCKERS[d] = d.widget.pos()
        Krita.instance().action('view_show_canvas_only').trigger()

    def recoveryPinStatus(self):
        for d,pos in DockerToggleManager.PINDOCKERS.items():
            d.widget.setFloating(True)
            d.widget.show()
            d.widget.move(pos)
            d.pin()
        DockerToggleManager.PINDOCKERS = {}

    # def savePinStatus(self):
    #     for d in DockerToggleManager.LIST:
    #         if d.pinned:
    #             Krita.instance().writeSetting("DockerUnderCursor_pin", d.name, "1")
    #         else:
    #             Krita.instance().writeSetting("DockerUnderCursor_pin", d.name, "0")

    def finalSetup(self):
        for d in DockerToggleManager.LIST:
            d.widget = Krita.instance().activeWindow().qwindow().findChild(QWidget,d.name)
            if d.widget:
                d.monitor = DockerMonitor(d) 
                d.widget.installEventFilter(d.monitor)
                d.setAutoConceal()
                d.widget.visibilityChanged.connect(d.resetPin)
                if d.widget.isFloating():
                    d.widget.titleBarWidget().children()[2].setChecked(False)
                # if Krita.instance().readSetting("DockerUnderCursor_pin", d.name, "0") == "1":
                #     d.pin()
            else:
                DockerToggleManager.LIST.remove(d)
                d.action.triggered.disconnect(d.toggleDockerStatus)
                Krita.instance().writeSetting("DockerUnderCursor", d.name, "0")
        
        Krita.instance().action('view_show_canvas_only').triggered.connect(self.recoveryPinStatus)
        Krita.instance().notifier().windowCreated.disconnect(self.finalSetup)

Krita.instance().addExtension(DockerUnderCursor(Krita.instance()))