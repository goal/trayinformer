#!/usr/bin/env python
#encoding=utf-8

import sip
sip.setapi('QVariant', 2)

from PyQt4 import QtCore, QtGui


class Window(QtGui.QDialog):
    def __init__(self):
        super(Window, self).__init__()

        self.createMessageGroupBox()

        self.createActions()
        self.createTrayIcon()

        self.showMessageButton.clicked.connect(self.addInformEvent)
        self.trayIcon.messageClicked.connect(self.messageClicked)
        self.trayIcon.activated.connect(self.iconActivated)

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(self.messageGroupBox)
        self.setLayout(mainLayout)

        self.trayIcon.show()

        self.setWindowTitle("Systray")
        self.resize(400, 300)
        
        self.trayIcon.setVisible(1)
        
        self.informEvents = {}
        self.informId = 0
        
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.heartBeat)
        timer.start(1000)
        
        
    def setVisible(self, visible):
        super(Window, self).setVisible(visible)

    def closeEvent(self, event):
        if self.trayIcon.isVisible():
            QtGui.QMessageBox.information(self, "Systray",
                    "The program will keep running in the system tray. To "
                    "terminate the program, choose <b>Quit</b> in the "
                    "context menu of the system tray entry.")
            self.hide()
            event.ignore()

    def iconActivated(self, reason):
        if reason == QtGui.QSystemTrayIcon.MiddleClick:
            self.showMessage()

    def messageClicked(self):
        pass

    def createMessageGroupBox(self):
        self.messageGroupBox = QtGui.QGroupBox("Balloon Message")

        self.timeLeftLabel = QtGui.QLabel("Mins:")

        self.timeLeftSpinBox = QtGui.QSpinBox()
        self.timeLeftSpinBox.setRange(1, 2880)
        self.timeLeftSpinBox.setSuffix(" m")
        self.timeLeftSpinBox.setValue(30)

        titleLabel = QtGui.QLabel("Title:")

        self.titleEdit = QtGui.QLineEdit("Cannot connect to network")

        bodyLabel = QtGui.QLabel("Body:")

        self.bodyEdit = QtGui.QTextEdit()
        self.bodyEdit.setPlainText("提示消息")

        self.showMessageButton = QtGui.QPushButton("添加定时提醒")
        self.showMessageButton.setDefault(True)

        messageLayout = QtGui.QGridLayout()
        messageLayout.addWidget(self.timeLeftLabel, 1, 0)
        messageLayout.addWidget(self.timeLeftSpinBox, 1, 1)
        messageLayout.addWidget(titleLabel, 2, 0)
        messageLayout.addWidget(self.titleEdit, 2, 1, 1, 4)
        messageLayout.addWidget(bodyLabel, 3, 0)
        messageLayout.addWidget(self.bodyEdit, 3, 1, 2, 4)
        messageLayout.addWidget(self.showMessageButton, 5, 4)
        messageLayout.setColumnStretch(3, 1)
        messageLayout.setRowStretch(4, 1)
        self.messageGroupBox.setLayout(messageLayout)

    def createActions(self):
        self.quitAction = QtGui.QAction("&Quit", self,
                triggered=QtGui.qApp.quit)

    def createTrayIcon(self):
        self.trayIconMenu = QtGui.QMenu(self)
        self.trayIconMenu.addAction(self.quitAction)

        self.trayIcon = QtGui.QSystemTrayIcon(self)
        self.trayIcon.setContextMenu(self.trayIconMenu)
        
        icon = QtGui.QIcon("./clock.svg")
        self.trayIcon.setIcon(icon)
        self.setWindowIcon(icon)
        self.trayIcon.setToolTip("Clock")
         
    def addInformEvent(self):
        title = self.titleEdit.text()
        text = self.bodyEdit.toPlainText()
        mins = self.timeLeftSpinBox.value()
        secs = mins * 60 * 1000
        
        if not (title and text and secs):
            QtGui.QMessageBox.information(self, "Error", "title, text and time cannot be null!")
            return

        self.informId += 1
        self.informEvents[self.informId] = {"title": title, "text": text, "time": secs}
        
        QtGui.QMessageBox.information(self, "添加成功", "将于 %d 分钟后提醒" % mins)
    
    def heartBeat(self):
        toRmKeys = []
        canInform = 1
        for _id in self.informEvents:
            info = self.informEvents[_id]
            info["time"] -= 1000
            if info["time"] <= 0:
                if not canInform: continue
                toRmKeys.append(_id)
                icon = QtGui.QSystemTrayIcon.MessageIcon(1)
                self.trayIcon.showMessage(info["title"], info["text"], icon, 5)
                canInform = 0
        
        for _id in toRmKeys:
            del self.informEvents[_id]
        

if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)

    if not QtGui.QSystemTrayIcon.isSystemTrayAvailable():
        QtGui.QMessageBox.critical(None, "Systray",
                "I couldn't detect any system tray on this system.")
        sys.exit(1)

    QtGui.QApplication.setQuitOnLastWindowClosed(False)

    window = Window()
    window.show()
    sys.exit(app.exec_())
