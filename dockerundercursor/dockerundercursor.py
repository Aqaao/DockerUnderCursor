from copy import copy
import xml.etree.cElementTree as ET

from krita import *

from dockerundercursor.ActionKeyFilter import ActionHoldFilter
from dockerundercursor.DockerVisibilityToggler import DockerVisibilityToggler
from dockerundercursor.SettingPanel import SettingPanel
from dockerundercursor.DockerAutoHideFilter import DockerAutoHideFilter


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

    def getSettingPanel(self):
        setting = SettingPanel()
        setting.exec()

    def createDockerToggleActions(self, window):
        tree = ET.parse(SettingPanel.file)
        root = tree.getroot()
        #n = window.qwindow().objectName()

        for v in root.findall(".//Action/text"):
            toggler = DockerVisibilityToggler(v.text)
            action:QAction = window.createAction("duc_{0}".format(v.text),"","")
            action.triggered.connect(toggler.trigger)
            toggler.action = action

    def pinDocker(self):
        for d in DockerVisibilityToggler.LIST:
            if d.selfIsParent()[0]:
                if d.pinned == False:
                    d.pin()
                else:
                    d.cancelPin()
                break

    def toggleCancasMode(self):
        for d in DockerVisibilityToggler.LIST:
            if d.pinned:
                if d.leave:
                    DockerVisibilityToggler.PINDOCKERS[d] = d.pin_position()
                else:
                    DockerVisibilityToggler.PINDOCKERS[d] = d.widget.pos()
        Krita.instance().action('view_show_canvas_only').trigger()

    def recoveryPinStatus(self):
        for d,pos in DockerVisibilityToggler.PINDOCKERS.items():
            d.widget.setFloating(True)
            d.widget.show()
            d.widget.move(pos)
            d.pin()
        DockerVisibilityToggler.PINDOCKERS = {}

    def finalSetup(self):
        for d in DockerVisibilityToggler.LIST:
            if not d.window:
                qwin = Krita.instance().activeWindow().qwindow()
                d.window = qwin.objectName()
                d.widget = qwin.findChild(QWidget,d.name)
                if d.widget:
                    d.monitor = DockerAutoHideFilter(d) 
                    d.widget.installEventFilter(d.monitor)
                    d.setAutoConceal()
                    d.widget.visibilityChanged.connect(d.resetPin)
                    if d.widget.isFloating():
                        #reset docker lock status
                        for i in d.widget.titleBarWidget().children():
                            if i.__class__ == QAbstractButton and i.toolTip() == "Lock Docker":
                                i.setChecked(False)
                else:
                    DockerVisibilityToggler.LIST.remove(d)
                    d.action.triggered.disconnect(d.toggleDockerStatus)
                    Krita.instance().writeSetting("DockerUnderCursor", d.name, "0")
        
        Krita.instance().action('view_show_canvas_only').triggered.connect(self.recoveryPinStatus)
        Krita.instance().notifier().windowCreated.disconnect(self.finalSetup)

Krita.instance().addExtension(DockerUnderCursor(Krita.instance()))