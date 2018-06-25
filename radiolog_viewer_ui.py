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
        radiolog_viewer.resize(956, 880)
        radiolog_viewer.setStyleSheet("")
        self.gridLayoutWidget = QtWidgets.QWidget(radiolog_viewer)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(218, 102, 597, 689))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(2)
        self.gridLayout.setObjectName("gridLayout")
        self.widget = QtWidgets.QWidget(radiolog_viewer)
        self.widget.setGeometry(QtCore.QRect(219, 4, 214, 46))
        self.widget.setObjectName("widget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.groupBox = QtWidgets.QGroupBox(self.widget)
        self.groupBox.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setMaximumSize(QtCore.QSize(16777215, 40))
        self.groupBox.setTitle("")
        self.groupBox.setFlat(False)
        self.groupBox.setCheckable(False)
        self.groupBox.setObjectName("groupBox")
        self.rescanButton = QtWidgets.QPushButton(self.groupBox)
        self.rescanButton.setGeometry(QtCore.QRect(169, 1, 36, 36))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.rescanButton.sizePolicy().hasHeightForWidth())
        self.rescanButton.setSizePolicy(sizePolicy)
        self.rescanButton.setMaximumSize(QtCore.QSize(36, 36))
        self.rescanButton.setBaseSize(QtCore.QSize(36, 36))
        self.rescanButton.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/radiolog_viewer_ui/reload-icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.rescanButton.setIcon(icon)
        self.rescanButton.setIconSize(QtCore.QSize(30, 30))
        self.rescanButton.setObjectName("rescanButton")
        self.optionsButton = QtWidgets.QToolButton(self.groupBox)
        self.optionsButton.setGeometry(QtCore.QRect(124, 1, 37, 36))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.optionsButton.sizePolicy().hasHeightForWidth())
        self.optionsButton.setSizePolicy(sizePolicy)
        self.optionsButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.optionsButton.setToolTip("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/radiolog_viewer_ui/options_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.optionsButton.setIcon(icon1)
        self.optionsButton.setIconSize(QtCore.QSize(30, 30))
        self.optionsButton.setObjectName("optionsButton")
        self.clock = QtWidgets.QLCDNumber(self.groupBox)
        self.clock.setGeometry(QtCore.QRect(5, 0, 115, 36))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.clock.sizePolicy().hasHeightForWidth())
        self.clock.setSizePolicy(sizePolicy)
        self.clock.setMinimumSize(QtCore.QSize(115, 36))
        self.clock.setMaximumSize(QtCore.QSize(16777215, 36))
        self.clock.setObjectName("clock")
        self.horizontalLayout.addWidget(self.groupBox)
        self.groupBox.raise_()
        self.gridLayoutWidget.raise_()

        self.retranslateUi(radiolog_viewer)
        self.rescanButton.clicked.connect(radiolog_viewer.rescan)
        QtCore.QMetaObject.connectSlotsByName(radiolog_viewer)

    def retranslateUi(self, radiolog_viewer):
        _translate = QtCore.QCoreApplication.translate
        radiolog_viewer.setWindowTitle(_translate("radiolog_viewer", "Radiolog Viewer"))
        self.optionsButton.setShortcut(_translate("radiolog_viewer", "F2"))

import radiolog_viewer_rc
