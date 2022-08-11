from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QCheckBox, QGroupBox, QScrollArea, QFrame
from PyQt5.QtCore import Qt
from os import path
from .dockertogglemanager import DockerToggleManager
from krita import Krita
import xml.etree.ElementTree as ET

class SettingPanel(QDialog):

    file = path.dirname(path.realpath(__file__)) + '/dockerundercursor.action'

    def __init__(self):
        super().__init__()

        # some QCheckBoxs ———→ QVBoxLayout_1 ———→ QGroupBox ———→ QScrollArea ———→ QVBoxLayout_2 ———→ SettingPanel(QDialog)
        #                                                        savebutton ————↗  ↗  ↑
        #                                                              tracecheckbox    |
        #                                                                        QCheckBox
        
        self.layout_1 = QVBoxLayout()
        self.dockerlist = Krita.instance().dockers()
        self.addCheckBox()

        self.groupbox = QGroupBox()
        self.groupbox.setStyleSheet("QGroupBox {border:none}")
        self.groupbox.setLayout(self.layout_1)

        self.scrollarea = QScrollArea()
        self.scrollarea.setAlignment(Qt.AlignHCenter)
        self.scrollarea.setFrameShape(QFrame.NoFrame)
        self.scrollarea.setWidget(self.groupbox)


        self.savebutton = QPushButton("Save")
        self.savebutton.clicked.connect(self.handleSaveButton)

        self.tracecheckbox = QCheckBox("Remember mouse position relative to docker")
        self.tracecheckbox.setToolTip("If false, the center point of docker will appear at mouse position")
        if Krita.instance().readSetting("DockerUnderCursor", "TraceMousePosition","False") == "True":
            self.tracecheckbox.setChecked(True)

        self.clampcheckbox = QCheckBox("Keep docker inside the main window")
        self.clampcheckbox.setToolTip("If false, the docker can appear anywhere on screen, may be obscured")
        if Krita.instance().readSetting("DockerUnderCursor", "ClampPosition","False") == "True":
            self.clampcheckbox.setChecked(True)

        self.autoconcealcheckbox = QCheckBox("Auto conceal docker after mouse leaves")
        self.autoconcealcheckbox.setToolTip("If false, you need to press shortcut key again to hide docker")
        if Krita.instance().readSetting("DockerUnderCursor", "AutoConceal","False") == "True":
            self.autoconcealcheckbox.setChecked(True)

        self.layout_2 = QVBoxLayout()
        self.layout_2.addWidget(self.scrollarea)
        self.layout_2.addWidget(self.savebutton)
        self.layout_2.addWidget(self.tracecheckbox)
        self.layout_2.addWidget(self.clampcheckbox)
        self.layout_2.addWidget(self.autoconcealcheckbox)

        self.setLayout(self.layout_2)
        self.resize(380, 800)
        self.setWindowTitle("Settings (change docker list need restart krita)")

    def addCheckBox(self):
        for i,v in enumerate(self.dockerlist):
            self.layout_1.addWidget(QCheckBox(v.windowTitle()))
            self.layout_1.itemAt(i).widget().setChecked(self.readSetting(v.objectName()))
    
    def handleSaveButton(self):
        self.tree = ET.parse(self.file)
        self.root = self.tree.getroot()
        self.removeAction()
        self.save()
        #ET.indent(self.tree,"    ") #At least python3.9 ,but krita is 3.8 now.
        self.tree.write(self.file, encoding='UTF-8', xml_declaration=True, short_empty_elements=False)
        Krita.instance().writeSetting("DockerUnderCursor", "TraceMousePosition", str(self.tracecheckbox.isChecked()))
        DockerToggleManager.TRACEMOUSE = str(self.tracecheckbox.isChecked())
        Krita.instance().writeSetting("DockerUnderCursor", "ClampPosition", str(self.clampcheckbox.isChecked()))
        DockerToggleManager.CLAMPPOSITION = str(self.clampcheckbox.isChecked())
        Krita.instance().writeSetting("DockerUnderCursor", "AutoConceal", str(self.autoconcealcheckbox.isChecked()))
        DockerToggleManager.AUTOCONCEAL = str(self.autoconcealcheckbox.isChecked())
        for v in DockerToggleManager.LIST:
            v.mousepos = None
            v.setMonitor()
        self.close()

    def save(self):
        for i,v in enumerate(self.dockerlist):
            if  self.layout_1.itemAt(i).widget().isChecked():
                self.writeSetting(v.objectName(), "1")
                self.writeAction(v.objectName())
            else:
                self.writeSetting(v.objectName(), "0")

    def readSetting(self, name):
        if Krita.instance().readSetting("DockerUnderCursor", name,"0") == "1":
            return True
        else:
            return False

    def writeSetting(self, name, status):
        Krita.instance().writeSetting("DockerUnderCursor", name, status)

    def writeSetting(self, name, status):
        Krita.instance().writeSetting("DockerUnderCursor", name, status)

    def removeAction(self):
        for v in self.root[0].findall("Action"):
            self.root[0].remove(v)

    def writeAction(self, actionname):
        element = ET.SubElement(self.root[0],"Action",{"name":"duc_{0}".format(actionname)})
        ET.SubElement(element,"text").text = actionname
        ET.SubElement(element,"shortcut").text = "none"