"""Bridge Qt API differences using only the bindings exported by Krita."""

from krita import *

# Newer bindings scope enums by type; older PyQt5 versions expose them directly.
AlignmentFlag = getattr(Qt, "AlignmentFlag", Qt)
TextFormat = getattr(Qt, "TextFormat", Qt)
KeyboardModifier = getattr(Qt, "KeyboardModifier", Qt)
MouseButton = getattr(Qt, "MouseButton", Qt)
Key = getattr(Qt, "Key", Qt)
EventType = getattr(QEvent, "Type", QEvent)
PixelMetric = getattr(QStyle, "PixelMetric", QStyle)


def enum_value(value):
    """Convert both PyQt5 integer enums and PyQt6 Python enums to integers."""
    return int(getattr(value, "value", value))


def key_event_sequence(event):
    """Build a key sequence without mixing Qt6 flags with integer key codes."""
    modifier_keys = {
        enum_value(Key.Key_Shift): KeyboardModifier.ShiftModifier,
        enum_value(Key.Key_Control): KeyboardModifier.ControlModifier,
        enum_value(Key.Key_Alt): KeyboardModifier.AltModifier,
        enum_value(Key.Key_Meta): KeyboardModifier.MetaModifier,
    }
    key = enum_value(event.key())
    if key in modifier_keys:
        # A released modifier may already be absent from event.modifiers().
        combined = enum_value(modifier_keys[key])
    else:
        combined = enum_value(event.modifiers()) | key
    return QKeySequence(combined)


def mouse_event_position(event):
    """Return widget-local coordinates as QPointF on either Qt version."""
    if hasattr(event, "position"):
        return event.position()
    return QPointF(event.pos())


def mouse_move_event(widget, global_position):
    """Supply explicit local/global coordinates for Qt5 and Qt6 constructors."""
    return QMouseEvent(
        EventType.MouseMove,
        QPointF(widget.mapFromGlobal(global_position)),
        QPointF(global_position),
        MouseButton.NoButton,
        MouseButton.NoButton,
        KeyboardModifier.NoModifier,
    )


def is_opengl_widget(widget):
    """Recognize canvas widgets even if Krita does not export QOpenGLWidget."""
    # QOpenGLWidget moved from QtWidgets to QtOpenGLWidgets in Qt6. Querying
    # the Qt meta-object avoids importing a second binding or Qt library.
    return widget is not None and widget.inherits("QOpenGLWidget")


def exec_dialog(dialog):
    """Run dialogs with exec(), falling back to older PyQt5's exec_()."""
    execute = getattr(dialog, "exec", None)
    if execute is None:
        execute = dialog.exec_
    return execute()
