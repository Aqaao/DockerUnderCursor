from krita import Krita
from PyQt5.QtGui import QCursor, QMouseEvent
from PyQt5.QtWidgets import QOpenGLWidget, QApplication
from PyQt5.QtCore import QCoreApplication, QEvent, Qt, QPointF, QPoint

class DockerToggleManager():

    TRACEMOUSE = Krita.instance().readSetting("DockerUnderCursor", "TraceMousePosition","False")
    CLAMPPOSITION = Krita.instance().readSetting("DockerUnderCursor", "ClampPosition","False")
    AUTOCONCEAL = Krita.instance().readSetting("DockerUnderCursor", "AutoConceal","False")

    LIST = []
    PINDOCKERS = {}

    def __init__(self,name):
        self.name = name
        self.widget = None
        self.hidden = True
        self.top = False
        self.mousepos = None
        self.monitor = None
        self.action = None
        self.pinned = False
        self.leave = False
        self.pin_position = None
        self.LIST.append(self)

    def setAutoConceal(self):
        if self.monitor:
            if self.AUTOCONCEAL == "True":
                self.monitor.auto_conceal = True
            elif self.AUTOCONCEAL == "False":
                self.monitor.auto_conceal = False

    def sendMoveEvent(self):
        pos_0 = QCursor.pos()
        wobj = QApplication.widgetAt(pos_0)
        if wobj != None and wobj.__class__ == QOpenGLWidget:
            event = QEvent.MouseMove
            button = Qt.MouseButton.NoButton
            key = Qt.KeyboardModifier.NoModifier
            pos_1 = wobj.mapFromGlobal(pos_0)
            pos = QPointF(pos_1)

            moveevent = QMouseEvent(event, pos, button, button, key)
            QCoreApplication.postEvent(wobj, moveevent)
    
    def sendLeaveEvent(self):
        reasult = self.selfIsParent()
        if reasult[0]:
            QCoreApplication.postEvent(reasult[2], QEvent(QEvent.Leave))

    def trackeCursorPosition(self):
        reasult = self.selfIsParent()
        if reasult[0]:
            self.mousepos = self.widget.mapFromGlobal(reasult[1])
        elif self.AUTOCONCEAL == "True":
            return
        else:
            self.mousepos = None

    def selfIsParent(self):
        pos = QCursor.pos()
        wobj = QApplication.widgetAt(pos)
        if wobj != None and self.checkParent(wobj):
            return True,pos,wobj
        else:
            return False,pos,wobj

    def checkParent(self,obj):
        pobj = obj.parent()
        if pobj == self.widget:
            return True
        elif pobj == None:
            return False
        else:
            return self.checkParent(pobj)

    def checkPosition(self,dockerpos):
        window = Krita.instance().activeWindow().qwindow()
        rpos = window.mapFromGlobal(dockerpos)
        if rpos.x() < 0:
            rpos.setX(0)
        elif rpos.x() > window.width() - self.widget.width():
            rpos.setX(window.width() - self.widget.width())
        if rpos.y() < 0:
            rpos.setY(0)
        elif rpos.y() > window.height() - self.widget.height():
            rpos.setY(window.height() - self.widget.height())
        return window.mapToGlobal(rpos)

    def moveDocker(self):
        pos = QCursor.pos()
        if self.mousepos:
            dockerpos = QPoint(int(pos.x()-self.mousepos.x()),int(pos.y()-self.mousepos.y()))
        else:
            dockerpos = QPoint(int(pos.x()-self.widget.width()/2),int(pos.y()-self.widget.height()/2))
        if self.CLAMPPOSITION == "True":
            self.widget.move(self.checkPosition(dockerpos))
        else:
            self.widget.move(dockerpos)
    
    #The method is core.
    def toggleDockerStatus(self):
        if self.widget.isHidden():
            self.widget.unsetCursor()#avoid cursor flicker
            self.hidden = True
            if not self.widget.isFloating():
                self.widget.setFloating(True)
            self.moveDocker()
            self.widget.show()
        elif self.widget.isFloating():
            if self.pinned:
                self.transformPosition()
            else:
                self.dockerReturn()
        else:#If docked.
            self.widget.unsetCursor()
            if self.widget.visibleRegion().isEmpty():
                self.top = False
            else:
                self.top = True
            self.widget.setFloating(True)
            self.moveDocker()
            self.hidden = False

    def dockerReturn(self):
        self.sendLeaveEvent()
        if self.TRACEMOUSE == "True":
            self.trackeCursorPosition()
        if self.hidden:
            self.widget.hide()
        else:
            self.widget.setFloating(False)
            if self.top:
                self.widget.raise_()
        self.sendMoveEvent() #refresh position of cursor outline, preventing offset

    def transformPosition(self):
        if self.leave:
            if self.TRACEMOUSE == "True":
                self.trackeCursorPosition()
            self.sendLeaveEvent()
            self.widget.move(self.pin_position)
            self.widget.setWindowTitle(self.widget.windowTitle()[0:-1])
            self.leave = False
            self.sendMoveEvent()
        else:
            self.widget.unsetCursor()
            self.leave = True
            self.pin_position = self.widget.pos()
            self.moveDocker()
            self.widget.setWindowTitle(self.widget.windowTitle()+"*")

    def pin(self):
        if self.widget.isFloating() and not self.widget.isHidden():
            self.pinned = True
            self.widget.setWindowTitle(self.widget.windowTitle()+"(pin)")
            self.pin_position = self.widget.pos()

    def cancelPin(self):
        self.pinned = False
        if self.leave == True:
            self.widget.setWindowTitle(self.widget.windowTitle()[:-6])
            self.leave = False
        else:
            self.widget.setWindowTitle(self.widget.windowTitle()[:-5])

    def resetPin(self):
        if self.pinned:
            self.cancelPin()