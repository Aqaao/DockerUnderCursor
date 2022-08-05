from krita import Krita
from PyQt5.QtGui import QCursor, QMouseEvent
from PyQt5.QtWidgets import QWidget, QOpenGLWidget
from PyQt5.QtCore import QCoreApplication, QEvent, Qt, QPointF

class DockerToggle():

    def __init__(self,name):
        self.name = name
        self.weiget = None
        self.hidden = False
        self.top = False
        self.wobj = None

    def targetPotion(self):
        pos = QCursor.pos()
        return (pos.x()-self.weiget.width()/2,pos.y()-self.weiget.height()/2)

    def setToFloating(self):
        if self.weiget.pos().y() > 0:#If weiget is not top tab, you will get a negative number coordinate.
            self.top = True
        else:
            self.top = False
        self.hidden = False
        self.weiget.setFloating(True)
        self.weiget.move(*self.targetPotion())

    def setToDocked(self):
        self.weiget.setFloating(False)
        if self.top:
            self.weiget.raise_()

    def setToShow(self):
        self.hidden = True
        if not self.weiget.isFloating():
            self.weiget.setFloating(True)
        self.weiget.show()
        self.weiget.move(*self.targetPotion())

    def setToHidden(self):
        self.weiget.hide()

    def sendMoveEvent(self):
        if not self.wobj:
            qwin = Krita.instance().activeWindow().qwindow()
            pobj = qwin.findChild(QWidget,'view_0')
            self.wobj = pobj.findChild(QOpenGLWidget)
        event = QEvent.MouseMove
        button = Qt.MouseButton.NoButton
        key = Qt.KeyboardModifier.NoModifier
        pos_0 = QCursor.pos()
        pos_1 = self.wobj.mapFromGlobal(pos_0)
        pos = QPointF(pos_1)

        moveevent = QMouseEvent(event, pos, button, button, key)
        QCoreApplication.postEvent(self.wobj, moveevent)
    
    def toggleDockerStatus(self):
        if not self.weiget:
            self.weiget = Krita.instance().activeWindow().qwindow().findChild(QWidget,self.name)

        if self.weiget.isHidden():
            self.setToShow()
        elif self.weiget.isFloating():
            if self.hidden == 0:
                self.setToDocked()
            else:
                self.setToHidden()
            self.sendMoveEvent()
        else:#If docked.
            self.setToFloating()