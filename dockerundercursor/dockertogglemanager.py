from krita import Krita
from PyQt5.QtGui import QCursor, QMouseEvent
from PyQt5.QtWidgets import QWidget, QOpenGLWidget, QApplication
from PyQt5.QtCore import QCoreApplication, QEvent, Qt, QPointF, QPoint
from .dockermonitor import DockerMonitor

class DockerToggleManager():

    TRACEMOUSE = Krita.instance().readSetting("DockerUnderCursor", "TraceMousePosition","False")
    CLAMPPOSITION = Krita.instance().readSetting("DockerUnderCursor", "ClampPosition","False")
    AUTOCONCEAL = Krita.instance().readSetting("DockerUnderCursor", "AutoConceal","False")

    LIST = []

    def __init__(self,name):
        self.name = name
        self.widget = None
        self.hidden = False
        self.top = False
        self.mousepos = None
        self.monitor = None
        self.float = False
        Krita.instance().notifier().windowCreated.connect(self.finalSetup)
        self.LIST.append(self)

    def finalSetup(self):
        self.widget =Krita.instance().activeWindow().qwindow().findChild(QWidget,self.name)
        self.monitor = DockerMonitor(self)
        self.setMonitor()

    def setMonitor(self):
        if self.AUTOCONCEAL == "True":
            self.widget.installEventFilter(self.monitor)
        if self.AUTOCONCEAL == "False":
            self.widget.removeEventFilter(self.monitor)

    def targetPotion(self,pos):
        if self.mousepos:
            return QPoint(pos.x()-self.mousepos.x(),pos.y()-self.mousepos.y())
        return QPoint(pos.x()-self.widget.width()/2,pos.y()-self.widget.height()/2)

    def setToFloating(self):
        if self.widget.visibleRegion().isEmpty():
            self.top = False
        else:
            self.top = True
        self.hidden = False
        self.widget.setFloating(True)
        self.moveDocker()

    def setToDocked(self):
        self.widget.setFloating(False)
        if self.top:
            self.widget.raise_()

    def setToShow(self):
        self.hidden = True
        if not self.widget.isFloating():
            self.widget.setFloating(True)
        self.moveDocker()
        self.widget.show()

    def setToHidden(self):
        self.widget.hide()

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
    
    def trackeCursorPosition(self):
        pos = QCursor.pos()
        wobj = QApplication.widgetAt(pos)
        if wobj != None and self.checkParent(wobj):
            self.mousepos = self.widget.mapFromGlobal(pos)
        elif self.AUTOCONCEAL == "True":
            return
        else:
            self.mousepos = None

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
        dockerpos = self.targetPotion(QCursor.pos())
        if self.CLAMPPOSITION == "True":
            self.widget.move(self.checkPosition(dockerpos))
        else:
            self.widget.move(dockerpos)
    
    #The method is core.
    def toggleDockerStatus(self):
        if self.widget.isFloating():
            self.dockerReturn()
        else:
            self.dockerDisplay()

    def dockerReturn(self):
        if self.TRACEMOUSE == "True":
            self.trackeCursorPosition()
        if self.hidden == 0:
            self.setToDocked()
        else:
            self.setToHidden()
        #refresh position of cursor outline, preventing offset
        self.sendMoveEvent()

        self.float = False

    def dockerDisplay(self):
        #Prevent cursor shape flicker
        self.widget.unsetCursor()

        if self.widget.isHidden():
            self.setToShow()
        #If docked.
        else:
            self.setToFloating()
        self.float = True