from krita import Krita
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QWidget

class DockerToggle():

    def __init__(self,name):
        self.name = name
        self.weiget = None
        self.hidden = False
        self.top = False

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
        self.weiget.show()
        self.weiget.move(*self.targetPotion())

    def setToHidden(self):
        self.weiget.hide()
    
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
        else:#If docked.
            self.setToFloating()