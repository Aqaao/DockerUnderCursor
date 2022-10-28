from PyQt5.QtCore import QObject, QEvent
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QApplication

class  DockerMonitor(QObject):
    
    def __init__(self,obj):
        super().__init__()
        self.dockermanager = obj

    def eventFilter(self, obj, event):
        if self.dockermanager.widget == obj and obj.isFloating():
            #Leaves docker event.
            if event.type() == QEvent.Leave:
                wobj = QApplication.widgetAt(QCursor.pos())
                if not self.dockermanager.checkParent(wobj):
                    self.dockermanager.dockerReturn()
                    return True
            #Block cursor shape toggle.
            elif event.type() == QEvent.MouseMove:
                if event.pos().x() <= 1 or event.pos().x() >= obj.size().width() - 1:
                    return True
                elif event.pos().y() <= 1 or event.pos().y() >= obj.size().height() - 1:
                    return True
        return False