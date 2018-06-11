# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'radiolog_viewer.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_radiolog_viewer(object):
    def setupUi(self, radiolog_viewer):
        radiolog_viewer.setObjectName("radiolog_viewer")
        radiolog_viewer.resize(1456, 880)
        self.gridLayout = QtWidgets.QGridLayout(radiolog_viewer)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(radiolog_viewer)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.watchedDirField = QtWidgets.QLineEdit(radiolog_viewer)
        self.watchedDirField.setObjectName("watchedDirField")
        self.gridLayout.addWidget(self.watchedDirField, 0, 1, 1, 1)
        self.rescanButton = QtWidgets.QPushButton(radiolog_viewer)
        self.rescanButton.setObjectName("rescanButton")
        self.gridLayout.addWidget(self.rescanButton, 1, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(radiolog_viewer)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.watchedFileField = QtWidgets.QLineEdit(radiolog_viewer)
        self.watchedFileField.setObjectName("watchedFileField")
        self.gridLayout.addWidget(self.watchedFileField, 2, 1, 1, 1)
        self.mdi = QtWidgets.QMdiArea(radiolog_viewer)
        self.mdi.setObjectName("mdi")
        self.gridLayout.addWidget(self.mdi, 4, 0, 1, 2)
        self.logField = QtWidgets.QTextEdit(radiolog_viewer)
        self.logField.setObjectName("logField")
        self.gridLayout.addWidget(self.logField, 3, 0, 1, 2)

        self.retranslateUi(radiolog_viewer)
        self.rescanButton.clicked.connect(radiolog_viewer.rescan)
        QtCore.QMetaObject.connectSlotsByName(radiolog_viewer)

    def retranslateUi(self, radiolog_viewer):
        _translate = QtCore.QCoreApplication.translate
        radiolog_viewer.setWindowTitle(_translate("radiolog_viewer", "Dialog"))
        self.label.setText(_translate("radiolog_viewer", "Watched Dir"))
        self.rescanButton.setText(_translate("radiolog_viewer", "Re-scan"))
        self.label_2.setText(_translate("radiolog_viewer", "Watched File"))

