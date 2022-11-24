from PyQt5.QtCore import QObject, QEvent
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QApplication

class  DockerMonitor(QObject):
    
    def __init__(self,obj):
        super().__init__()
        self.dockermanager = obj
        self.mousepressed = False

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            self.mousepressed = True
        if event.type() == QEvent.MouseButtonRelease:
            self.mousepressed = False
        # if event.type() == QEvent.Move and self.dockermanager.pinned and not self.dockermanager.leave:
        #     self.dockermanager.position = self.dockermanager.widget.pos()
        if self.dockermanager.widget == obj and obj.isFloating() and not self.mousepressed:
            #Leaves docker event.
            if event.type() == QEvent.Leave:
                wobj = QApplication.widgetAt(QCursor.pos())
                if not wobj or not self.dockermanager.checkParent(wobj):
                    if self.dockermanager.pinned:
                        if self.dockermanager.leave:
                            self.dockermanager.transformPosition()
                        else:
                            return False
                    else:
                        self.dockermanager.dockerReturn()
            #Block cursor shape toggle.
            elif event.type() == QEvent.MouseMove:
                if event.pos().x() <= 1 or event.pos().x() >= obj.size().width() - 1:
                    return True
                elif event.pos().y() <= 1 or event.pos().y() >= obj.size().height() - 1:
                    return True
        return False