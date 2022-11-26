from krita import Krita
from PyQt5.QtGui import QCursor, QMouseEvent
from PyQt5.QtWidgets import QWidget, QOpenGLWidget, QApplication
from PyQt5.QtCore import QCoreApplication, QEvent, Qt, QPointF, QPoint
from PyQt5 import QtCore
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
        self.action = None
        self.pinned = False
        self.leave = False
        self.pin_position = None
        self.pin_status = {
            "canvas_only_mode":None,
            "normal_mode":None}
        Krita.instance().notifier().windowCreated.connect(self.finalSetup)
        self.LIST.append(self)

    def finalSetup(self):
        self.widget = Krita.instance().activeWindow().qwindow().findChild(QWidget,self.name)
        if self.widget:
            self.monitor = DockerMonitor(self)
            self.widget.installEventFilter(self.monitor)
            self.setAutoConceal()
        else:
            self.action.triggered.disconnect(self.toggleDockerStatus)
        self.widget.visibilityChanged.connect(self.hideDocker)
        # self.widget.topLevelChanged.connect(self.dockDocker)
        Krita.instance().notifier().windowCreated.disconnect(self.finalSetup)
        Krita.instance().action('view_show_canvas_only').triggered.connect(self.restorePin)
        Krita.instance().action('view_show_canvas_only').triggered.connect(self.checkPinException,type=Qt.DirectConnection)
        #self.loadPinStatus()


    def setAutoConceal(self):
        if self.AUTOCONCEAL == "True":
            self.monitor.auto_conceal = True
        elif self.AUTOCONCEAL == "False":
            self.monitor.auto_conceal = False

    def targetPotion(self,pos):
        if self.mousepos:
            return QPoint(pos.x()-self.mousepos.x(),pos.y()-self.mousepos.y())
        return QPoint(pos.x()-self.widget.width()/2,pos.y()-self.widget.height()/2)

    def setToFloating(self):
        self.widget.unsetCursor()
        if self.widget.visibleRegion().isEmpty():
            self.top = False
        else:
            self.top = True
        self.widget.setFloating(True)
        self.moveDocker()
        self.hidden = False

    def setToDocked(self):
        self.widget.setFloating(False)
        if self.top:
            self.widget.raise_()

    def setToShow(self):
        #avoid cursor flicker
        self.widget.unsetCursor()
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
    
    def sendLeaveEvent(self):
        pos_0 = QCursor.pos()
        wobj = QApplication.widgetAt(pos_0)
        if self.checkParent(wobj):
            QCoreApplication.postEvent(wobj, QEvent(QEvent.Leave))

    def trackeCursorPosition(self):
        pos = QCursor.pos()
        wobj = QApplication.widgetAt(pos)
        if wobj != None and self.checkParent(wobj):
            self.mousepos = self.widget.mapFromGlobal(pos)
        elif self.AUTOCONCEAL == "True":
            return
        else:
            self.mousepos = None

    def selfIsParent(self):
        pos = QCursor.pos()
        wobj = QApplication.widgetAt(pos)
        if wobj != None and self.checkParent(wobj):
            return True
        else:
            return False

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
        if self.widget.isHidden():
            self.setToShow()
        elif self.widget.isFloating():
            if self.pinned:
                self.transformPosition()
            else:
                self.dockerReturn()
        else:#If docked.
            self.setToFloating()

    def dockerReturn(self):
        self.sendLeaveEvent()
        if self.TRACEMOUSE == "True":
            self.trackeCursorPosition()
        if self.hidden:
            self.setToHidden()
        else:
            self.setToDocked()
        #refresh position of cursor outline, preventing offset
        self.sendMoveEvent()

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
            self.moveDocker()
            self.widget.setWindowTitle(self.widget.windowTitle()+"*")

    def pin(self, record_status=True):
        if self.widget.isFloating() and not self.widget.isHidden():
            self.pinned = True
            self.widget.setWindowTitle(self.widget.windowTitle()+"(pin)")
            self.pin_position = self.widget.pos()
            if record_status:
                self.savePinStatus(clear=False)
        else:
            self.savePinStatus(clear=True)

    def cancelPin(self,clear_status=True):
        self.pinned = False
        if self.leave == True:
            self.widget.setWindowTitle(self.widget.windowTitle()[:-6])
            self.leave = False
        else:
            self.widget.setWindowTitle(self.widget.windowTitle()[:-5])

        if clear_status:
            self.savePinStatus(clear=True)

    def savePinStatus(self,clear):
        if Krita.instance().action('view_show_canvas_only').isChecked():
            if clear:
                self.pin_status["canvas_only_mode"] = None
            else:
                self.pin_status["canvas_only_mode"] = self.widget.pos()
        else:
            if clear:
                self.pin_status["normal_mode"] = None
            else:
                self.pin_status["normal_mode"] = self.widget.pos()
    
    def hideDocker(self,visible):
        if visible and self.pinned:
            self.cancelPin(False)
    
    def restorePin(self):
        #---DEBUG---#Application.activeWindow().activeView().showFloatingMessage("mode switch.",Application.icon('warning'),1000,1)
        if self.pin_status["canvas_only_mode"] and Krita.instance().action('view_show_canvas_only').isChecked():
            self.widget.show()
            self.widget.setFloating(True)
            self.widget.move(self.pin_status["canvas_only_mode"])
            self.pin(False)
        if self.pin_status["normal_mode"] and not Krita.instance().action('view_show_canvas_only').isChecked():
            self.widget.move(self.pin_status["normal_mode"])
            self.pin(False)

    def checkPinException(self):
        if not self.pinned and self.pin_status:
            self.savePinStatus(clear=True)