"""Run with DUC_QT_API=PyQt5 or PyQt6, in separate Python processes.

Uses real Qt widgets/events and a stub for Krita's application-specific API.
"""

import importlib
import os
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from types import ModuleType
from unittest.mock import Mock, patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
QT_API = os.environ.get("DUC_QT_API", "PyQt5")
if QT_API not in ("PyQt5", "PyQt6"):
    raise ValueError("DUC_QT_API must be PyQt5 or PyQt6")

QtCore = importlib.import_module(QT_API + ".QtCore")
QtGui = importlib.import_module(QT_API + ".QtGui")
QtWidgets = importlib.import_module(QT_API + ".QtWidgets")
APP = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class KritaStub:
    def __init__(self):
        self.resource_directory = ""
        self.settings = {}
        self.registered_actions = {}
        self.docker_widgets = []
        self.extensions = []

    def readSetting(self, group, key, default):
        if (group, key) == ("", "ResourceDirectory"):
            return self.resource_directory
        return self.settings.get((group, key), default)

    def writeSetting(self, group, key, value):
        self.settings[group, key] = value

    def action(self, name):
        return self.registered_actions.get(name)

    def dockers(self):
        return self.docker_widgets

    def addExtension(self, extension):
        self.extensions.append(extension)


API = KritaStub()
krita_stub = ModuleType("krita")
for module in (QtCore, QtGui, QtWidgets):
    for name in dir(module):
        # Exercise the case where Krita does not re-export QOpenGLWidget.
        if not name.startswith("_") and name != "QOpenGLWidget":
            setattr(krita_stub, name, getattr(module, name))
krita_stub.Krita = type("Krita", (), {"instance": staticmethod(lambda: API)})
krita_stub.Extension = type("Extension", (), {"__init__": lambda self, parent: None})
sys.modules["krita"] = krita_stub

# Import the complete plugin, including extension registration and event filters.
compat = importlib.import_module("dockerundercursor.qt_compat")
settings_module = importlib.import_module("dockerundercursor.setting_panel")
hold_module = importlib.import_module("dockerundercursor.action_hold_filter")
auto_hide_module = importlib.import_module("dockerundercursor.docker_auto_hide_filter")
visibility_module = importlib.import_module(
    "dockerundercursor.docker_visibility_toggler"
)


class QtCompatibilityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=os.environ.get("DUC_TEST_TEMP"))
        API.resource_directory = self.temp.name
        API.settings.clear()
        API.registered_actions.clear()
        for action_id in ("settingpanel", "pindocker", "togglecanvasmode"):
            API.registered_actions[action_id] = getattr(krita_stub, "QAction")()
        API.docker_widgets = [QtWidgets.QDockWidget("Palette")]
        API.docker_widgets[0].setObjectName("PaletteDocker")
        visibility_module.DockerVisibilityToggler.instances.clear()
        self.widgets = []

    def tearDown(self):
        hold_module.action_hold_filter._key_released = True
        hold_module.action_hold_filter._action = None
        for widget in self.widgets + API.docker_widgets:
            widget.close()
        self.temp.cleanup()

    def test_settings_open_edit_save_and_check_registration(self):
        panel = settings_module.SettingPanel()
        self.widgets.append(panel)
        panel.show()
        self.assertTrue(panel.isVisible())
        self.assertFalse(panel.restart_warning.isHidden())
        self.assertIn("click Save", panel.restart_warning.text())
        option = panel.docker_layout.itemAt(0).layout()
        self.assertEqual(option.itemAt(1).widget().text(), "PaletteDocker")
        self.assertEqual(option.itemAt(0).alignment(), compat.AlignmentFlag.AlignLeft)

        panel.docker_checkboxes[0].setChecked(True)
        panel.trace_checkbox.setChecked(True)
        self.assertTrue(panel.windowTitle().endswith(" *"))
        panel.save_button.click()
        self.assertEqual(panel.windowTitle(), panel.WINDOW_TITLE)
        self.assertTrue(panel.isVisible())
        self.assertFalse(panel.restart_warning.isHidden())
        self.assertIn("Restart Krita", panel.restart_warning.text())
        self.assertEqual(
            panel.action_file(),
            Path(self.temp.name) / "actions" / "dockerundercursor.action",
        )
        action = ET.parse(panel.action_file()).find(
            panel.DOCKER_ACTIONS_PATH + "/Action"
        )
        self.assertEqual(action.attrib["name"], "duc_PaletteDocker")
        self.assertEqual(
            API.settings["DockerUnderCursor", "TraceMousePosition"], "True"
        )

        API.registered_actions["duc_PaletteDocker"] = (
            QtGui.QAction() if QT_API == "PyQt6" else QtWidgets.QAction()
        )
        panel._update_restart_warning()
        self.assertTrue(panel.restart_warning.isHidden())

    def test_saving_docker_selection_preserves_general_actions(self):
        panel = settings_module.SettingPanel()
        self.widgets.append(panel)
        for enabled in (True, False, True):
            panel.docker_checkboxes[0].setChecked(enabled)
            panel._save_settings()
            root = ET.parse(panel.action_file()).getroot()
            self.assertEqual(root.attrib["name"], "Scripts")
            self.assertTrue(
                all(
                    category.get("category") == "Scripts"
                    for category in root.findall("Actions")
                )
            )
            general = root.find("./Actions[text='Docker Under Cursor / General']")
            self.assertEqual(
                {action.get("name") for action in general.findall("Action")},
                {"settingpanel", "pindocker", "togglecanvasmode"},
            )
            self.assertEqual(
                general.findtext("./Action[@name='pindocker']/shortcut"), "Ctrl+`"
            )
            dynamic = root.findall(panel.DOCKER_ACTIONS_PATH + "/Action")
            self.assertEqual(len(dynamic), 1 if enabled else 0)
            ids = [action.get("name") for action in root.findall(".//Action")]
            self.assertEqual(len(ids), len(set(ids)))

    def test_legacy_actions_move_to_dockers_category(self):
        panel_type = settings_module.SettingPanel
        path = panel_type.action_file()
        path.parent.mkdir()
        path.write_text(
            '<ActionCollection version="2" name="Scripts">'
            '<Actions category="Scripts"><text>Docker Under Cursor</text>'
            '<Action name="duc_PaletteDocker"><text>Palette</text>'
            "<shortcut>Ctrl+P</shortcut></Action></Actions></ActionCollection>",
            encoding="utf-8",
        )
        tree = panel_type.read_action_tree()
        self.assertEqual(tree.getroot().get("name"), "Scripts")
        self.assertEqual(
            tree.findtext(panel_type.DOCKER_ACTIONS_PATH + "/text"),
            "Docker Under Cursor / Dockers",
        )
        action = tree.find(panel_type.DOCKER_ACTIONS_PATH + "/Action")
        self.assertEqual(action.get("name"), "duc_PaletteDocker")
        self.assertEqual(action.findtext("shortcut"), "Ctrl+P")
        self.assertEqual(action.findtext("text"), "Palette")
        self.assertEqual(
            len(
                tree.findall(".//Actions[text='Docker Under Cursor / General']/Action")
            ),
            3,
        )
        # Reading migrates the structure in memory; files change only on Save.
        self.assertEqual(ET.parse(path).getroot().get("name"), "Scripts")

    def test_nested_template_exports_every_action_for_krita(self):
        panel_type = settings_module.SettingPanel
        # Retain coverage for legacy nested templates now that the bundled
        # template uses the flat format understood by Krita.
        source = ET.parse(panel_type.ACTION_TEMPLATE).getroot()
        nested_root = ET.Element(source.tag, dict(source.attrib))
        parent = ET.SubElement(nested_root, "Actions", {"category": "Scripts"})
        ET.SubElement(parent, "text").text = "Docker Under Cursor"
        for category in source.findall("Actions"):
            category.find("text").text = category.findtext("text").rsplit(" / ", 1)[-1]
            parent.append(category)
        template = Path(self.temp.name) / "template" / "dockerundercursor.action"
        template.parent.mkdir()
        ET.ElementTree(nested_root).write(template, encoding="UTF-8")
        template_patch = patch.object(panel_type, "ACTION_TEMPLATE", template)
        template_patch.start()
        self.addCleanup(template_patch.stop)
        original_template = panel_type.ACTION_TEMPLATE.read_bytes()
        panel = panel_type()
        self.widgets.append(panel)
        panel.docker_checkboxes[0].setChecked(True)
        panel._save_settings()

        root = ET.parse(panel.action_file()).getroot()
        self.assertEqual(root.get("name"), "Scripts")
        # Krita's native parser only reads these two direct-child levels.
        native_ids = {action.get("name") for action in root.findall("./Actions/Action")}
        self.assertEqual(
            native_ids,
            {"settingpanel", "pindocker", "togglecanvasmode", "duc_PaletteDocker"},
        )
        self.assertEqual(root.findall("./Actions/Actions"), [])
        self.assertEqual(
            [category.findtext("text") for category in root.findall("Actions")],
            ["Docker Under Cursor / General", "Docker Under Cursor / Dockers"],
        )
        self.assertEqual(panel_type.ACTION_TEMPLATE.read_bytes(), original_template)

        # Legacy nested templates and generated files resolve to the same group.
        restored = panel_type.read_action_tree()
        self.assertEqual(
            restored.find(panel_type.DOCKER_ACTIONS_PATH + "/Action").get("name"),
            "duc_PaletteDocker",
        )

    def test_already_nested_saved_actions_are_preserved(self):
        panel_type = settings_module.SettingPanel
        tree = ET.parse(panel_type.ACTION_TEMPLATE)
        actions = tree.find(panel_type.DOCKER_ACTIONS_PATH)
        action = ET.SubElement(actions, "Action", {"name": "duc_PaletteDocker"})
        ET.SubElement(action, "text").text = "Palette"
        ET.SubElement(action, "shortcut").text = "Alt+P"
        root = tree.getroot()
        nested = ET.Element("Actions", {"category": "Scripts"})
        ET.SubElement(nested, "text").text = "Docker Under Cursor"
        for category in root.findall("Actions"):
            root.remove(category)
            category.find("text").text = category.findtext("text").rsplit(" / ", 1)[-1]
            nested.append(category)
        root.append(nested)
        path = panel_type.action_file()
        path.parent.mkdir()
        tree.write(path, encoding="UTF-8")

        restored = panel_type.read_action_tree()
        saved = restored.findall(panel_type.DOCKER_ACTIONS_PATH + "/Action")
        self.assertEqual(len(saved), 1)
        self.assertEqual(saved[0].get("name"), "duc_PaletteDocker")
        self.assertEqual(saved[0].findtext("shortcut"), "Alt+P")

    def test_only_dynamic_actions_create_docker_togglers_without_menu_entries(self):
        panel = settings_module.SettingPanel()
        self.widgets.append(panel)
        panel.docker_checkboxes[0].setChecked(True)
        panel._save_settings()
        extension_module = importlib.import_module(
            "dockerundercursor.docker_under_cursor"
        )
        window = Mock()
        with patch.object(extension_module, "DockerVisibilityToggler") as factory:
            extension_module.DockerUnderCursor(API)._create_docker_toggle_actions(
                window
            )
            factory.assert_called_once_with("PaletteDocker")
            window.createAction.assert_called_once_with("duc_PaletteDocker", "", "")
            window.createAction.return_value.triggered.connect.assert_called_once_with(
                factory.return_value.trigger
            )

    def test_key_sequences_with_modifiers(self):
        sequence_format = getattr(
            QtGui.QKeySequence, "SequenceFormat", QtGui.QKeySequence
        )
        cases = (
            (compat.Key.Key_K, compat.KeyboardModifier.NoModifier, "K"),
            (compat.Key.Key_K, compat.KeyboardModifier.ControlModifier, "Ctrl+K"),
            (compat.Key.Key_Left, compat.KeyboardModifier.AltModifier, "Alt+Left"),
            (
                compat.Key.Key_K,
                compat.KeyboardModifier.ControlModifier
                | compat.KeyboardModifier.ShiftModifier,
                "Ctrl+Shift+K",
            ),
        )
        for key, modifiers, expected in cases:
            with self.subTest(expected=expected):
                event = QtGui.QKeyEvent(
                    compat.EventType.KeyRelease, compat.enum_value(key), modifiers
                )
                sequence = compat.key_event_sequence(event)
                self.assertEqual(
                    sequence.toString(sequence_format.PortableText), expected
                )

    def test_modifier_release_matches_assigned_shortcut(self):
        monitor = hold_module.ActionHoldFilter()
        action_type = getattr(krita_stub, "QAction")
        monitor._action = action_type()
        for key, shortcut in (
            (compat.Key.Key_Control, "Ctrl+K"),
            (compat.Key.Key_Shift, "Shift+K"),
            (compat.Key.Key_Alt, "Alt+K"),
            (compat.Key.Key_Meta, "Meta+K"),
        ):
            with self.subTest(shortcut=shortcut):
                monitor._action.setShortcut(QtGui.QKeySequence(shortcut))
                event = QtGui.QKeyEvent(
                    compat.EventType.KeyRelease,
                    compat.enum_value(key),
                    compat.KeyboardModifier.NoModifier,
                )
                self.assertTrue(monitor._match_shortcuts(event))

    def test_shortcut_can_be_triggered_again_after_key_release(self):
        monitor = hold_module.action_hold_filter
        toggler = Mock()
        toggler.action = getattr(krita_stub, "QAction")()
        toggler.action.setShortcut(QtGui.QKeySequence("K"))
        target = QtWidgets.QWidget()
        self.widgets.append(target)
        event = QtGui.QKeyEvent(
            compat.EventType.KeyRelease,
            compat.enum_value(compat.Key.Key_K),
            compat.KeyboardModifier.NoModifier,
        )
        monitor.action_key_pressed(toggler)
        APP.sendEvent(target, event)
        monitor.action_key_pressed(toggler)
        self.assertEqual(toggler.toggle_docker_status.call_count, 2)

    def test_long_hold_returns_docker_on_release(self):
        monitor = hold_module.ActionHoldFilter()
        toggler = Mock()
        toggler.action = getattr(krita_stub, "QAction")()
        toggler.action.setShortcut(QtGui.QKeySequence("Ctrl+K"))
        target = QtWidgets.QWidget()
        self.widgets.append(target)
        with patch.object(hold_module, "monotonic", side_effect=[1.0, 2.0]):
            monitor.action_key_pressed(toggler)
            event = QtGui.QKeyEvent(
                compat.EventType.KeyRelease,
                compat.enum_value(compat.Key.Key_K),
                compat.KeyboardModifier.ControlModifier,
            )
            monitor.eventFilter(target, event)
        self.assertEqual(toggler.toggle_docker_status.call_count, 2)

    def test_mouse_event_coordinates_and_edge_filter(self):
        widget = QtWidgets.QDockWidget()
        widget.resize(200, 200)
        widget.setFloating(True)
        self.widgets.append(widget)
        local = QtCore.QPoint(0, 40)
        event = compat.mouse_move_event(widget, widget.mapToGlobal(local))
        self.assertEqual(compat.mouse_event_position(event), QtCore.QPointF(local))
        toggler = Mock(widget=widget)
        monitor = auto_hide_module.DockerAutoHideFilter(toggler)
        monitor.auto_conceal = True
        self.assertTrue(monitor.eventFilter(widget, event))
        interior = compat.mouse_move_event(
            widget, widget.mapToGlobal(QtCore.QPoint(40, 40))
        )
        self.assertFalse(monitor.eventFilter(widget, interior))
        toggler.is_cursor_in_docker.return_value = False
        toggler.pinned = False
        monitor.eventFilter(widget, QtCore.QEvent(compat.EventType.Leave))
        toggler.restore_docker.assert_called_once_with()

    def test_opengl_widget_without_krita_export(self):
        module = importlib.import_module(
            QT_API + (".QtOpenGLWidgets" if QT_API == "PyQt6" else ".QtWidgets")
        )
        widget = module.QOpenGLWidget()
        self.widgets.append(widget)
        self.assertFalse(hasattr(krita_stub, "QOpenGLWidget"))
        self.assertTrue(compat.is_opengl_widget(widget))
        self.assertFalse(compat.is_opengl_widget(API.docker_widgets[0]))
        self.assertFalse(compat.is_opengl_widget(None))

    def test_dialog_execution_and_legacy_fallbacks(self):
        dialog = QtWidgets.QDialog()
        self.widgets.append(dialog)
        QtCore.QTimer.singleShot(0, dialog.accept)
        result = compat.exec_dialog(dialog)
        codes = getattr(QtWidgets.QDialog, "DialogCode", QtWidgets.QDialog)
        self.assertEqual(result, compat.enum_value(codes.Accepted))

        class LegacyDialog:
            def exec_(self):
                return 42

        class LegacyMouseEvent:
            def pos(self):
                return QtCore.QPoint(2, 3)

        self.assertEqual(compat.exec_dialog(LegacyDialog()), 42)
        self.assertEqual(
            compat.mouse_event_position(LegacyMouseEvent()), QtCore.QPointF(2, 3)
        )
        self.assertEqual(compat.enum_value(7), 7)


if __name__ == "__main__":
    print(f"Testing {QT_API} / Qt {QtCore.qVersion()}")
    unittest.main(verbosity=2)
