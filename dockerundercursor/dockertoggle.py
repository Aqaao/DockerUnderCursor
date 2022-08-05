from krita import Krita
from PyQt5.QtGui import QCursor, QMouseEvent
from PyQt5.QtWidgets import QWidget, QOpenGLWidget, QApplication
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
        self.weiget.move(*self.targetPotion())
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