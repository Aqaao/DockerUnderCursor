from krita import Krita
from PyQt5.QtGui import QCursor, QMouseEvent
from PyQt5.QtWidgets import QWidget, QOpenGLWidget, QApplication
from PyQt5.QtCore import QCoreApplication, QEvent, Qt, QPointF, QPoint

class DockerToggle():

    TRACEMOUSE = Krita.instance().readSetting("DockerUnderCursor", "TraceMousePosition","False")
    CLAMPPOSITION = Krita.instance().readSetting("DockerUnderCursor", "ClampPosition","False")

    def __init__(self,name):
        self.name = name
        self.weiget = None
        self.hidden = False
        self.top = False
        self.mousepos = None

    def targetPotion(self,pos):
        if self.mousepos:
            return QPoint(pos.x()-self.mousepos.x(),pos.y()-self.mousepos.y())
        return QPoint(pos.x()-self.weiget.width()/2,pos.y()-self.weiget.height()/2)

    def setToFloating(self):
        if self.weiget.visibleRegion().isEmpty():
            self.top = False
        else:
            self.top = True
        self.hidden = False
        self.weiget.setFloating(True)
        self.moveDocker()

    def setToDocked(self):
        self.weiget.setFloating(False)
        if self.top:
            self.weiget.raise_()

    def setToShow(self):
        self.hidden = True
        if not self.weiget.isFloating():
            self.weiget.setFloating(True)
        self.moveDocker()
        self.weiget.show()

    def setToHidden(self):
        self.weiget.hide()

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
            self.mousepos = self.weiget.mapFromGlobal(pos)
        else:
            self.mousepos = None

    def checkParent(self,obj):
        pobj = obj.parent()
        if pobj == self.weiget:
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
        elif rpos.x() > window.width() - self.weiget.width():
            rpos.setX(window.width() - self.weiget.width())
        if rpos.y() < 0:
            rpos.setY(0)
        elif rpos.y() > window.height() - self.weiget.height():
            rpos.setY(window.height() - self.weiget.height())
        return window.mapToGlobal(rpos)

    def moveDocker(self):
        dockerpos = self.targetPotion(QCursor.pos())
        if self.CLAMPPOSITION == "True":
            self.weiget.move(self.checkPosition(dockerpos))
        else:
            self.weiget.move(dockerpos)
        
    def toggleDockerStatus(self):
        if not self.weiget:
            self.weiget = Krita.instance().activeWindow().qwindow().findChild(QWidget,self.name)

        if self.weiget.isHidden():
            self.setToShow()
        elif self.weiget.isFloating():
            if self.TRACEMOUSE == "True":
                self.trackeCursorPosition()
            if self.hidden == 0:
                self.setToDocked()
            else:
                self.setToHidden()
            self.sendMoveEvent()#refresh position of cursor outline, preventing offset
        else:#If docked.
            self.setToFloating()