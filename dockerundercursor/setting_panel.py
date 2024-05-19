from os import path
import xml.etree.ElementTree as ET
from krita import *

from .docker_visibility_toggler import DockerVisibilityToggler


class SettingPanel(QDialog):

    file = path.dirname(path.realpath(__file__)) + '/dockerundercursor.action'

    def __init__(self):
        super().__init__()

        self.layout_1 = QVBoxLayout()
        self.dockerlist = Krita.instance().dockers()
        self._add_check_box()

        self.groupbox = QGroupBox()
        self.groupbox.setStyleSheet("QGroupBox {border:none}")
        self.groupbox.setLayout(self.layout_1)

        self.scrollarea = QScrollArea()
        self.scrollarea.setAlignment(Qt.AlignHCenter)
        # self.scrollarea.setFrameShape(QFrame.NoFrame)
        self.scrollarea.setWidget(self.groupbox)

        self.tracecheckbox = QCheckBox(
            "Remember mouse position relative to docker")
        self.tracecheckbox.setToolTip(
            "If false, the center point of docker will appear at mouse position")
        if Krita.instance().readSetting("DockerUnderCursor", "TraceMousePosition", "False") == "True":
            self.tracecheckbox.setChecked(True)

        self.clampcheckbox = QCheckBox("Keep docker inside the main window")
        self.clampcheckbox.setToolTip(
            "If false, the docker can appear anywhere on screen, may be obscured")
        if Krita.instance().readSetting("DockerUnderCursor", "ClampPosition", "False") == "True":
            self.clampcheckbox.setChecked(True)

        self.autoconcealcheckbox = QCheckBox(
            "Auto conceal docker after mouse leaves")
        self.autoconcealcheckbox.setToolTip(
            "If false, you need to press shortcut key again to hide docker")
        if Krita.instance().readSetting("DockerUnderCursor", "AutoConceal", "False") == "True":
            self.autoconcealcheckbox.setChecked(True)

        self.savebutton = QPushButton("Save")
        self.savebutton.clicked.connect(self._on_save_button_click)

        self.layout_2 = QVBoxLayout()
        self.layout_2.addWidget(self.scrollarea)
        self.layout_2.addWidget(self.tracecheckbox)
        self.layout_2.addWidget(self.clampcheckbox)
        self.layout_2.addWidget(self.autoconcealcheckbox)
        self.layout_2.addWidget(self.savebutton)

        self.setLayout(self.layout_2)
        self.resize(380, 800)
        self.setWindowTitle("Settings")

    def _add_check_box(self):
        for i, v in enumerate(self.dockerlist):
            self.layout_1.addWidget(QCheckBox(v.windowTitle()))
            self.layout_1.itemAt(i).widget().setChecked(
                self._read_docker_status(v.objectName()))

    def _on_save_button_click(self):
        self.tree = ET.parse(self.file)
        self.root = self.tree.getroot()
        self._remove_action()
        # ET.indent(self.tree,"    ") #At least python3.9
        self.save()
        self.tree.write(self.file, encoding='UTF-8',
                        xml_declaration=True, short_empty_elements=False)
        Krita.instance().writeSetting("DockerUnderCursor", "TraceMousePosition",
                                      str(self.tracecheckbox.isChecked()))
        DockerVisibilityToggler.TRACEMOUSE = str(
            self.tracecheckbox.isChecked())
        Krita.instance().writeSetting("DockerUnderCursor", "ClampPosition",
                                      str(self.clampcheckbox.isChecked()))
        DockerVisibilityToggler.CLAMPPOSITION = str(
            self.clampcheckbox.isChecked())
        Krita.instance().writeSetting("DockerUnderCursor", "AutoConceal",
                                      str(self.autoconcealcheckbox.isChecked()))
        DockerVisibilityToggler.AUTOCONCEAL = str(
            self.autoconcealcheckbox.isChecked())
        for v in DockerVisibilityToggler.INSTANCES:
            v.mousepos = None
            v.update_auto_hide()
        self.close()

    def save(self):
        for i, v in enumerate(self.dockerlist):
            if self.layout_1.itemAt(i).widget().isChecked():
                self._write_docker_status(v.objectName(), "1")
                self._write_action(v.objectName())
            else:
                self._write_docker_status(v.objectName(), "0")

    def _read_docker_status(self, name):
        if Krita.instance().readSetting("DockerUnderCursor", name, "0") == "1":
            return True
        else:
            return False

    def _write_docker_status(self, name, status):
        Krita.instance().writeSetting("DockerUnderCursor", name, status)

    def _remove_action(self):
        for v in self.root[0].findall("Action"):
            self.root[0].remove(v)

    def _write_action(self, actionname):
        element = ET.SubElement(self.root[0], "Action", {
                                "name": "duc_{0}".format(actionname)})
        ET.SubElement(element, "text").text = actionname
        ET.SubElement(element, "shortcut").text = "none"
