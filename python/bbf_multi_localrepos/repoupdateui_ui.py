# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'repoupdateui.ui'
#
# Created: Thu Feb 25 14:56:12 2016
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_RepoUpdateUi(object):
    def setupUi(self, RepoUpdateUi):
        RepoUpdateUi.setObjectName("RepoUpdateUi")
        RepoUpdateUi.resize(378, 224)
        self.centralwidget = QtGui.QWidget(RepoUpdateUi)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.textEdit = QtGui.QTextEdit(self.centralwidget)
        self.textEdit.setObjectName("textEdit")
        self.verticalLayout.addWidget(self.textEdit)
        self.progressBar = QtGui.QProgressBar(self.centralwidget)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setTextVisible(False)
        self.progressBar.setObjectName("progressBar")
        self.verticalLayout.addWidget(self.progressBar)
        RepoUpdateUi.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(RepoUpdateUi)
        self.statusbar.setObjectName("statusbar")
        RepoUpdateUi.setStatusBar(self.statusbar)

        self.retranslateUi(RepoUpdateUi)
        QtCore.QMetaObject.connectSlotsByName(RepoUpdateUi)

    def retranslateUi(self, RepoUpdateUi):
        RepoUpdateUi.setWindowTitle(QtGui.QApplication.translate("RepoUpdateUi", "Repo Updates", None, QtGui.QApplication.UnicodeUTF8))

