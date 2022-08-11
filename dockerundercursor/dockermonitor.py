from PyQt5.QtCore import QObject, QEvent

class  DockerMonitor(QObject):
    
    def __init__(self,obj):
        super().__init__()
        self.dtm = obj

    def eventFilter(self, obj, event):
        if self.dtm.float:
            #Leaves docker event.
            if event.type() == QEvent.Leave:
                self.dtm.dockerReturn()
                return True
            #Block cursor shape toggle.
            elif event.type() == QEvent.MouseMove:
                if event.pos().x() <= 1 or event.pos().x() >= obj.size().width() - 1:
                    return True
                elif event.pos().y() <= 1 or event.pos().y() >= obj.size().height() - 1:
                    return True
        return False