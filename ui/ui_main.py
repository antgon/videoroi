# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(712, 460)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.graphicsView = GraphicsLayoutWidget(self.centralwidget)
        self.graphicsView.setObjectName(_fromUtf8("graphicsView"))
        self.verticalLayout_3.addWidget(self.graphicsView)
        self.scrollbar = QtGui.QScrollBar(self.centralwidget)
        self.scrollbar.setOrientation(QtCore.Qt.Horizontal)
        self.scrollbar.setObjectName(_fromUtf8("scrollbar"))
        self.verticalLayout_3.addWidget(self.scrollbar)
        self.horizontalLayout.addLayout(self.verticalLayout_3)
        self.verticalLayout_4 = QtGui.QVBoxLayout()
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.open_video_button = QtGui.QPushButton(self.centralwidget)
        self.open_video_button.setObjectName(_fromUtf8("open_video_button"))
        self.verticalLayout_4.addWidget(self.open_video_button)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_4.addItem(spacerItem)
        self.autoLevel_button = QtGui.QRadioButton(self.centralwidget)
        self.autoLevel_button.setChecked(True)
        self.autoLevel_button.setObjectName(_fromUtf8("autoLevel_button"))
        self.verticalLayout_4.addWidget(self.autoLevel_button)
        self.roi_box = QtGui.QGroupBox(self.centralwidget)
        self.roi_box.setObjectName(_fromUtf8("roi_box"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.roi_box)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.add_roi_button = QtGui.QPushButton(self.roi_box)
        self.add_roi_button.setObjectName(_fromUtf8("add_roi_button"))
        self.verticalLayout_2.addWidget(self.add_roi_button)
        self.clear_roi_button = QtGui.QPushButton(self.roi_box)
        self.clear_roi_button.setObjectName(_fromUtf8("clear_roi_button"))
        self.verticalLayout_2.addWidget(self.clear_roi_button)
        self.verticalLayout_4.addWidget(self.roi_box)
        self.fluorescence_box = QtGui.QGroupBox(self.centralwidget)
        self.fluorescence_box.setObjectName(_fromUtf8("fluorescence_box"))
        self.verticalLayout = QtGui.QVBoxLayout(self.fluorescence_box)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.measure_button = QtGui.QPushButton(self.fluorescence_box)
        self.measure_button.setObjectName(_fromUtf8("measure_button"))
        self.verticalLayout.addWidget(self.measure_button)
        self.plot_button = QtGui.QPushButton(self.fluorescence_box)
        self.plot_button.setObjectName(_fromUtf8("plot_button"))
        self.verticalLayout.addWidget(self.plot_button)
        self.save_button = QtGui.QPushButton(self.fluorescence_box)
        self.save_button.setObjectName(_fromUtf8("save_button"))
        self.verticalLayout.addWidget(self.save_button)
        self.verticalLayout_4.addWidget(self.fluorescence_box)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_4.addItem(spacerItem1)
        self.quit_button = QtGui.QPushButton(self.centralwidget)
        self.quit_button.setObjectName(_fromUtf8("quit_button"))
        self.verticalLayout_4.addWidget(self.quit_button)
        self.horizontalLayout.addLayout(self.verticalLayout_4)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "Video ROI", None))
        self.open_video_button.setText(_translate("MainWindow", "&Open", None))
        self.open_video_button.setShortcut(_translate("MainWindow", "Ctrl+O", None))
        self.autoLevel_button.setText(_translate("MainWindow", "Auto level", None))
        self.roi_box.setTitle(_translate("MainWindow", "ROIs", None))
        self.add_roi_button.setText(_translate("MainWindow", "Add", None))
        self.clear_roi_button.setText(_translate("MainWindow", "Clear", None))
        self.fluorescence_box.setTitle(_translate("MainWindow", "Fluorescence", None))
        self.measure_button.setText(_translate("MainWindow", "Measure", None))
        self.plot_button.setText(_translate("MainWindow", "Plot", None))
        self.save_button.setText(_translate("MainWindow", "Save", None))
        self.quit_button.setText(_translate("MainWindow", "&Quit", None))
        self.quit_button.setShortcut(_translate("MainWindow", "Ctrl+Q", None))

from pyqtgraph import GraphicsLayoutWidget
