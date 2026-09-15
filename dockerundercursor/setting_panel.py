"""Configure enabled dockers and persist positioning preferences."""

import xml.etree.ElementTree as ET
from pathlib import Path

from krita import *

from .docker_visibility_toggler import DockerVisibilityToggler


class SettingPanel(QDialog):
    """Save docker action definitions for Krita to load at the next startup."""

    ACTION_TEMPLATE = Path(__file__).resolve().with_name("dockerundercursor.action")
    WINDOW_TITLE = "Docker Under Cursor Settings"

    @classmethod
    def action_file(cls):
        """Resolve Krita's resource directory rather than the plugin directory."""
        resource_directory = Krita.instance().readSetting("", "ResourceDirectory", "")
        return Path(resource_directory) / "actions" / cls.ACTION_TEMPLATE.name

    @classmethod
    def read_action_tree(cls):
        action_file = cls.action_file()
        # Use the bundled collection on first save, including legacy selections
        # previously written to the plugin directory.
        return ET.parse(action_file if action_file.is_file() else cls.ACTION_TEMPLATE)

    def __init__(self):
        super().__init__()

        self.restart_warning = QLabel(
            "Restart Krita to make all selected docker actions available."
        )
        self.restart_warning.setStyleSheet("color: #e6b800;")
        self.restart_warning.setWordWrap(True)

        self.docker_layout = QVBoxLayout()
        self.docker_layout.setAlignment(Qt.AlignTop)
        self.docker_checkboxes = []
        self.dockers = Krita.instance().dockers()
        self._add_docker_checkboxes()

        self.docker_group = QGroupBox()
        self.docker_group.setStyleSheet("QGroupBox {border:none}")
        self.docker_group.setLayout(self.docker_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.docker_group)

        self.trace_checkbox = QCheckBox("Remember cursor position within the docker")
        self.trace_checkbox.setToolTip(
            "If disabled, the docker is centered on the cursor."
        )
        self.trace_checkbox.setChecked(self._read_preference("TraceMousePosition"))

        self.clamp_checkbox = QCheckBox("Keep floating dockers inside the main window")
        self.clamp_checkbox.setToolTip(
            "If disabled, the docker may extend beyond the main window."
        )
        self.clamp_checkbox.setChecked(self._read_preference("ClampPosition"))

        self.auto_conceal_checkbox = QCheckBox("Restore dockers when the cursor leaves")
        self.auto_conceal_checkbox.setToolTip(
            "Automatically hide the docker, dock it again, or return it to its "
            "pinned position when the cursor leaves."
        )
        self.auto_conceal_checkbox.setChecked(self._read_preference("AutoConceal"))

        for checkbox in (
            self.trace_checkbox,
            self.clamp_checkbox,
            self.auto_conceal_checkbox,
        ):
            checkbox.stateChanged.connect(self._mark_dirty)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self._save_settings)

        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.restart_warning)
        self.main_layout.addWidget(self.scroll_area)
        self.main_layout.addWidget(self.trace_checkbox)
        self.main_layout.addWidget(self.clamp_checkbox)
        self.main_layout.addWidget(self.auto_conceal_checkbox)
        self.main_layout.addWidget(self.save_button)

        self.setLayout(self.main_layout)
        self.resize(380, 800)
        self.setWindowTitle(self.WINDOW_TITLE)
        self._update_restart_warning()

    def _mark_dirty(self):
        self.setWindowTitle(self.WINDOW_TITLE + " *")

    def _update_restart_warning(self):
        """Prompt for initial setup or missing registrations of saved actions."""
        action_file = self.action_file()
        if not action_file.is_file():
            self.restart_warning.setText(
                "Select the dockers you want to use, then click Save."
            )
            self.restart_warning.setVisible(True)
            return

        root = ET.parse(action_file).getroot()
        restart_required = any(
            Krita.instance().action(action.attrib["name"]) is None
            for action in root.findall(".//Action")
        )
        self.restart_warning.setText(
            "Restart Krita to make all selected docker actions available."
        )
        self.restart_warning.setVisible(restart_required)

    def _read_preference(self, key):
        return Krita.instance().readSetting("DockerUnderCursor", key, "False") == "True"

    def _add_docker_checkboxes(self):
        for docker in self.dockers:
            checkbox = QCheckBox(docker.windowTitle())
            checkbox.setChecked(self._read_docker_status(docker.objectName()))
            checkbox.stateChanged.connect(self._mark_dirty)
            self.docker_checkboxes.append(checkbox)

            docker_id = QLabel(docker.objectName())
            docker_id.setTextFormat(Qt.PlainText)
            docker_id.setAlignment(Qt.AlignLeft)
            docker_id.setStyleSheet("color: gray;")
            font = docker_id.font()
            font.setPointSizeF(max(1.0, font.pointSizeF() * 0.85))
            docker_id.setFont(font)
            # Align the ID with the checkbox text, after the check indicator.
            docker_id.setIndent(
                checkbox.style().pixelMetric(QStyle.PM_IndicatorWidth)
                + checkbox.style().pixelMetric(QStyle.PM_CheckBoxLabelSpacing)
            )

            option_layout = QVBoxLayout()
            option_layout.setSpacing(2)
            option_layout.addWidget(checkbox, alignment=Qt.AlignLeft)
            option_layout.addWidget(docker_id, alignment=Qt.AlignLeft)
            self.docker_layout.addLayout(option_layout)

    def _save_settings(self):
        tree = self.read_action_tree()
        actions = tree.getroot()[0]
        # Preserve the collection metadata while replacing enabled docker actions.
        for action in actions.findall("Action"):
            actions.remove(action)
        self._save_docker_actions(actions)
        ET.indent(tree, space="    ")
        action_file = self.action_file()
        action_file.parent.mkdir(parents=True, exist_ok=True)
        tree.write(
            action_file,
            encoding="UTF-8",
            xml_declaration=True,
            short_empty_elements=False,
        )

        for docker, checkbox in zip(self.dockers, self.docker_checkboxes):
            enabled = checkbox.isChecked()
            Krita.instance().writeSetting(
                "DockerUnderCursor", docker.objectName(), "1" if enabled else "0"
            )

        preferences = (
            ("TraceMousePosition", "trace_mouse", self.trace_checkbox),
            ("ClampPosition", "clamp_position", self.clamp_checkbox),
            ("AutoConceal", "auto_conceal", self.auto_conceal_checkbox),
        )
        for key, attribute, checkbox in preferences:
            value = str(checkbox.isChecked())
            Krita.instance().writeSetting("DockerUnderCursor", key, value)
            setattr(DockerVisibilityToggler, attribute, value)

        # Preferences apply immediately; new shortcuts require a Krita restart.
        for toggler in DockerVisibilityToggler.instances:
            toggler.cursor_offset = None
            toggler.update_auto_hide()
        self.setWindowTitle(self.WINDOW_TITLE)
        self._update_restart_warning()

    def _save_docker_actions(self, actions):
        for docker, checkbox in zip(self.dockers, self.docker_checkboxes):
            enabled = checkbox.isChecked()
            if enabled:
                self._write_action(actions, docker.objectName())

    def _read_docker_status(self, name):
        return Krita.instance().readSetting("DockerUnderCursor", name, "0") == "1"

    def _write_action(self, actions, docker_name):
        action = ET.SubElement(
            actions, "Action", {"name": "duc_{}".format(docker_name)}
        )
        ET.SubElement(action, "text").text = docker_name
        ET.SubElement(action, "shortcut").text = "none"
