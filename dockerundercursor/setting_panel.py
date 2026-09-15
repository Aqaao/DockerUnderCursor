"""Configure enabled dockers and persist positioning preferences."""

import xml.etree.ElementTree as ET
from copy import deepcopy
from pathlib import Path

from krita import *

from .docker_visibility_toggler import DockerVisibilityToggler
from .qt_compat import AlignmentFlag, PixelMetric, TextFormat


class SettingPanel(QDialog):
    """Save docker action definitions for Krita to load at the next startup."""

    ACTION_TEMPLATE = Path(__file__).resolve().with_name("dockerundercursor.action")
    DOCKER_ACTION_PREFIX = "duc_"
    # Krita groups actions by <text>; all categories use the Scripts attribute.
    DOCKER_ACTIONS_PATH = ".//Actions[text='Docker Under Cursor / Dockers']"
    WINDOW_TITLE = "Docker Under Cursor Settings"

    @classmethod
    def action_file(cls):
        """Resolve Krita's resource directory rather than the plugin directory."""
        resource_directory = Krita.instance().readSetting("", "ResourceDirectory", "")
        return Path(resource_directory) / "actions" / cls.ACTION_TEMPLATE.name

    @classmethod
    def read_action_tree(cls):
        """Combine the bundled categories with previously generated actions."""
        tree = cls.action_tree_for_krita(ET.parse(cls.ACTION_TEMPLATE))
        docker_actions = tree.find(cls.DOCKER_ACTIONS_PATH)
        if docker_actions is None:
            raise ValueError("The action template must contain a Dockers category.")
        action_file = cls.action_file()
        if action_file.is_file():
            # Older generated files placed every docker under Scripts. Read by
            # stable ID rather than display text or the old category structure.
            saved_root = ET.parse(action_file).getroot()
            for action in docker_actions.findall("Action"):
                docker_actions.remove(action)
            for action in saved_root.findall(".//Action"):
                if action.get("name", "").startswith(cls.DOCKER_ACTION_PREFIX):
                    docker_actions.append(action)
        return tree

    @staticmethod
    def action_tree_for_krita(tree):
        """Flatten nested template categories for Krita's action-file parser.

        Krita reads only Actions directly below ActionCollection and Action
        directly below each category. Keep the template hierarchy in category
        labels so nested definitions are not silently ignored at startup.
        """
        source_root = tree.getroot()
        root = ET.Element(source_root.tag, dict(source_root.attrib))

        def append_category(category, parent_labels):
            title = category.findtext("text") or category.get("category", "")
            labels = parent_labels + [title]
            children = category.findall("Actions")
            actions = category.findall("Action")
            if actions or not children:
                attributes = dict(category.attrib)
                attributes["category"] = "Scripts"
                flattened = ET.SubElement(root, "Actions", attributes)
                ET.SubElement(flattened, "text").text = " / ".join(labels)
                flattened.extend(deepcopy(action) for action in actions)
            for child in children:
                append_category(child, labels)

        for category in source_root.findall("Actions"):
            append_category(category, [])
        return ET.ElementTree(root)

    def __init__(self):
        super().__init__()

        self.restart_warning = QLabel(
            "Restart Krita to make all selected docker actions available."
        )
        self.restart_warning.setStyleSheet("color: #e6b800;")
        self.restart_warning.setWordWrap(True)

        self.docker_layout = QVBoxLayout()
        self.docker_layout.setAlignment(AlignmentFlag.AlignTop)
        self.docker_checkboxes = []
        self.dockers = Krita.instance().dockers()
        self._add_docker_checkboxes()

        self.docker_group = QGroupBox()
        self.docker_group.setStyleSheet("QGroupBox {border:none}")
        self.docker_group.setLayout(self.docker_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setAlignment(AlignmentFlag.AlignLeft | AlignmentFlag.AlignTop)
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
            checkbox.toggled.connect(self._mark_dirty)

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
            checkbox.toggled.connect(self._mark_dirty)
            self.docker_checkboxes.append(checkbox)

            docker_id = QLabel(docker.objectName())
            docker_id.setTextFormat(TextFormat.PlainText)
            docker_id.setAlignment(AlignmentFlag.AlignLeft)
            docker_id.setStyleSheet("color: gray;")
            font = docker_id.font()
            font.setPointSizeF(max(1.0, font.pointSizeF() * 0.85))
            docker_id.setFont(font)
            # Align the ID with the checkbox text, after the check indicator.
            docker_id.setIndent(
                checkbox.style().pixelMetric(PixelMetric.PM_IndicatorWidth)
                + checkbox.style().pixelMetric(PixelMetric.PM_CheckBoxLabelSpacing)
            )

            option_layout = QVBoxLayout()
            option_layout.setSpacing(2)
            option_layout.addWidget(checkbox, alignment=AlignmentFlag.AlignLeft)
            option_layout.addWidget(docker_id, alignment=AlignmentFlag.AlignLeft)
            self.docker_layout.addLayout(option_layout)

    def _save_settings(self):
        tree = self.read_action_tree()
        actions = tree.find(self.DOCKER_ACTIONS_PATH)
        # Only rebuild the Dockers category; keep General actions and defaults.
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
