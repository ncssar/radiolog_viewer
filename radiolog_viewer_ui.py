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
        radiolog_viewer.resize(422, 752)
        radiolog_viewer.setStyleSheet("")
        self.verticalLayout = QtWidgets.QVBoxLayout(radiolog_viewer)
        self.verticalLayout.setContentsMargins(-1, 0, -1, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtWidgets.QGroupBox(radiolog_viewer)
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.groupBox)
        self.horizontalLayout_2.setContentsMargins(-1, 0, -1, 0)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtWidgets.QSpacerItem(365, 41, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.clock = QtWidgets.QLCDNumber(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.clock.sizePolicy().hasHeightForWidth())
        self.clock.setSizePolicy(sizePolicy)
        self.clock.setMinimumSize(QtCore.QSize(115, 36))
        self.clock.setMaximumSize(QtCore.QSize(16777215, 36))
        self.clock.setObjectName("clock")
        self.horizontalLayout_2.addWidget(self.clock)
        self.optionsButton = QtWidgets.QToolButton(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.optionsButton.sizePolicy().hasHeightForWidth())
        self.optionsButton.setSizePolicy(sizePolicy)
        self.optionsButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.optionsButton.setToolTip("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/radiolog_viewer_ui/options_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.optionsButton.setIcon(icon)
        self.optionsButton.setIconSize(QtCore.QSize(30, 30))
        self.optionsButton.setObjectName("optionsButton")
        self.horizontalLayout_2.addWidget(self.optionsButton)
        self.rescanButton = QtWidgets.QPushButton(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.rescanButton.sizePolicy().hasHeightForWidth())
        self.rescanButton.setSizePolicy(sizePolicy)
        self.rescanButton.setMaximumSize(QtCore.QSize(36, 36))
        self.rescanButton.setBaseSize(QtCore.QSize(36, 36))
        self.rescanButton.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/radiolog_viewer_ui/reload-icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.rescanButton.setIcon(icon1)
        self.rescanButton.setIconSize(QtCore.QSize(30, 30))
        self.rescanButton.setObjectName("rescanButton")
        self.horizontalLayout_2.addWidget(self.rescanButton)
        self.verticalLayout.addWidget(self.groupBox)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setHorizontalSpacing(2)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout.addLayout(self.gridLayout)
        self.verticalLayout.setStretch(0, 1)

        self.retranslateUi(radiolog_viewer)
        self.rescanButton.clicked.connect(radiolog_viewer.rescan)
        QtCore.QMetaObject.connectSlotsByName(radiolog_viewer)

    def retranslateUi(self, radiolog_viewer):
        _translate = QtCore.QCoreApplication.translate
        radiolog_viewer.setWindowTitle(_translate("radiolog_viewer", "Radiolog Viewer"))
        self.optionsButton.setShortcut(_translate("radiolog_viewer", "F2"))

import radiolog_viewer_rc
