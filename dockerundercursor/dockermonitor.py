from PyQt5.QtCore import QObject, QEvent
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore
from . import qt_event
class  DockerMonitor(QObject):

    def __init__(self,obj):
        super().__init__()
        self.docker_manager = obj
        self.mouse_pressed = False
        self.auto_conceal = False

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            self.mouse_pressed = True
        if event.type() == QEvent.MouseButtonRelease:
            self.mouse_pressed = False
        # if self.docker_manager.name == "KisLayerBox" and self.docker_manager.widget == obj:
        #     QtCore.qDebug(qt_event.event_lookup.get(str(event.type())))
        if self.auto_conceal:
            if self.docker_manager.widget == obj and obj.isFloating() and not self.mouse_pressed:
                #Leaves docker event.
                if event.type() == QEvent.Leave:
                    wobj = QApplication.widgetAt(QCursor.pos())
                    if not wobj or not self.docker_manager.checkParent(wobj):
                        if self.docker_manager.pinned:
                            if self.docker_manager.leave:
                                self.docker_manager.transformPosition()
                            else:
                                return False
                        else:
                            self.docker_manager.dockerReturn()
                #Block cursor shape toggle.
                elif event.type() == QEvent.MouseMove:
                    if event.pos().x() <= 1 or event.pos().x() >= obj.size().width() - 1:
                        return True
                    elif event.pos().y() <= 1 or event.pos().y() >= obj.size().height() - 1:
                        return True
        return False