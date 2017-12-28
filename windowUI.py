import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
import sys

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        #self.setupMainWindow()


    def setupMainWindow(self):
        self.setWindowTitle("main window")
        self.setMinimumSize(QtCore.QSize(900, 700))
        self.setMaximumSize(QtCore.QSize(1000, 2000))
        self.gridLayout = QtWidgets.QGridLayout(self)
# menu
        horizontalLayout_1 = QHBoxLayout()
        spacerItem = QSpacerItem(100, 100, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.shutterButton = QPushButton('shutter', self)
        self.AOTFButton = QPushButton('AOTF', self)
        self.GalvoButton = QPushButton('Galvo', self)
        self.StageButton = QPushButton('stage', self)
        horizontalLayout_1.addWidget(self.shutterButton)
        horizontalLayout_1.addItem(spacerItem)
        horizontalLayout_1.addWidget(self.AOTFButton)
        horizontalLayout_1.addItem(spacerItem)
        horizontalLayout_1.addWidget(self.GalvoButton)
        horizontalLayout_1.addItem(spacerItem)
        horizontalLayout_1.addWidget(self.StageButton)
        horizontalLayout_1.addItem(spacerItem)
        self.gridLayout.addLayout(horizontalLayout_1, 0, 0, 1, 4)

# handle live and record
# set up parameters
        parameter_box = QGroupBox("parameter box",self)
        verticalLayout_p = QVBoxLayout()
        horizontalLayout_p1 = QHBoxLayout()
        # 405 laser
        label_405 = QLabel("405 exposure(ms)", parameter_box)
        horizontalLayout_p1.addWidget(label_405)
        self.doublespinbox_405 = QDoubleSpinBox()
        self.doublespinbox_405.setMaximum(1000)
        self.doublespinbox_405.setMinimum(1)
        self.doublespinbox_405.setValue(200)
        horizontalLayout_p1.addWidget(self.doublespinbox_405)
# set frames number per cycle
        horizontalLayout_p2 = QHBoxLayout()
        label_frames = QLabel("frames per cycle", parameter_box)
        horizontalLayout_p2.addWidget(label_frames)
        self.frames_doublespinbox = QDoubleSpinBox()
        self.frames_doublespinbox.setMinimum(1)
        self.frames_doublespinbox.setMaximum(1000)
        self.frames_doublespinbox.setValue(50)
        horizontalLayout_p2.addWidget(self.frames_doublespinbox)
        # set cycles
        horizontalLayout_p3 = QHBoxLayout()
        label_cycles = QLabel("cycles,0=infinity", parameter_box)
        horizontalLayout_p3.addWidget(label_cycles)
        self.cycles_doublespinbox = QDoubleSpinBox()
        self.cycles_doublespinbox.setMinimum(0)
        self.cycles_doublespinbox.setMaximum(1000)
        self.cycles_doublespinbox.setValue(0)
        horizontalLayout_p3.addWidget(self.cycles_doublespinbox)
        # start camera button
        self.set_parameter = QPushButton("start camera", parameter_box)
        self.set_parameter.setCheckable(True)
        verticalLayout_p.addLayout(horizontalLayout_p1)
        verticalLayout_p.addLayout(horizontalLayout_p2)
        verticalLayout_p.addLayout(horizontalLayout_p3)
        horizontalLayout_p4 = QHBoxLayout()
        horizontalLayout_p4.addWidget(self.set_parameter)
        verticalLayout_p.addLayout(horizontalLayout_p4)
        parameter_box.setLayout(verticalLayout_p)
        self.gridLayout.addWidget(parameter_box,1,0,1,1)
# handle live
        liveGroupBox = QGroupBox("live box",self)
        verticalLayout_l = QVBoxLayout(liveGroupBox)
        # live button
        self.liveButton = QPushButton('live', self)
        horizontalLayout_l1=QHBoxLayout()
        horizontalLayout_l1.addWidget(self.liveButton)
        # autoscale button
        self.autoscalebutton = QPushButton("autoscale", liveGroupBox)
        horizontalLayout_l1.addWidget(self.autoscalebutton)
        verticalLayout_l.addLayout(horizontalLayout_l1)
        # ser live exposure time
        horizontalLayout_3 = QHBoxLayout(liveGroupBox)
        self.exp_t_label = QLabel('exps(ms)', self)
        horizontalLayout_3.addWidget(self.exp_t_label)
        self.exp_t_doublespinbox = QDoubleSpinBox(self)
        self.exp_t_doublespinbox.setDecimals(1)
        self.exp_t_doublespinbox.setMinimum(1)
        self.exp_t_doublespinbox.setMaximum(1000)
        self.exp_t_doublespinbox.setValue(50)
        horizontalLayout_3.addWidget(self.exp_t_doublespinbox)
        # set exposure time anytime by pushing exposurebutton
        self.exposurebutton = QPushButton('set', liveGroupBox)
        horizontalLayout_3.addWidget(self.exposurebutton)
        verticalLayout_l.addLayout(horizontalLayout_3)
        liveGroupBox.setLayout(verticalLayout_l)
        self.gridLayout.addWidget(liveGroupBox,2,0,1,1)
# handle record
        recordGroupBox = QGroupBox("record box",self)
        verticalLayout_r = QVBoxLayout(recordGroupBox)
        horizontalLayout_r1=QHBoxLayout()
        self.recordButton = QPushButton('record', self)
        horizontalLayout_r1.addWidget(self.recordButton)

        verticalLayout_r.addLayout(horizontalLayout_r1)
        # set record exposure time
        horizontalLayout_5 = QHBoxLayout(recordGroupBox)
        #horizontalLayout_5.addItem(spacerItem1)
        self.record_expo_label = QLabel('exposure(ms)', self)
        horizontalLayout_5.addWidget(self.record_expo_label)
        self.recor_exp_t_doublespinbox = QDoubleSpinBox(self)
        self.recor_exp_t_doublespinbox.setDecimals(1)
        self.recor_exp_t_doublespinbox.setValue(20)
        self.recor_exp_t_doublespinbox.setMinimum(1)
        self.recor_exp_t_doublespinbox.setMaximum(1000)
        horizontalLayout_5.addWidget(self.recor_exp_t_doublespinbox)
        #horizontalLayout_5.addItem(spacerItem1)
        verticalLayout_r.addLayout(horizontalLayout_5)
        #verticalLayout_r.addItem(spacerItem_r)
        # set file name
        horizontalLayout_7 = QHBoxLayout(recordGroupBox)
        #horizontalLayout_7.addItem(spacerItem1)
        self.name_label = QLabel('filename', recordGroupBox)
        horizontalLayout_7.addWidget(self.name_label)
        #horizontalLayout_7.addItem(spacerItem1)
        self.name_text = QLineEdit('movie_', recordGroupBox)
        horizontalLayout_7.addWidget(self.name_text)
        #horizontalLayout_7.addItem(spacerItem1)
        self.name_num = QDoubleSpinBox(recordGroupBox)
        self.name_num.setValue(1.0)
        self.name_num.setMaximum(1000)
        horizontalLayout_7.addWidget(self.name_num)
        #horizontalLayout_7.addItem(spacerItem1)
        verticalLayout_r.addLayout(horizontalLayout_7)
        recordGroupBox.setLayout(verticalLayout_r)
        self.gridLayout.addWidget(recordGroupBox,3,0,1,1)
        #self.gridLayout.addItem(spacerItem, 4, 0, 1, 1)
        # display image window
        self.livewindow = QLabel(self)
        self.livewindow.setScaledContents(True)
        # self.livewindow.resize(200, 200)
        data = np.ones((2048, 2048), dtype=np.uint8)
        pixmap = QtGui.QImage(data, 2048, 2048, QtGui.QImage.Format_Indexed8)
        pixmap = QtGui.QPixmap.fromImage(pixmap)
        self.livewindow.setPixmap(pixmap)

        self.gridLayout.addWidget(self.livewindow,1,1,3,3)

        horizontalLayout_8 = QHBoxLayout()
        # message label
        self.message_label = QLabel('message', self)
        horizontalLayout_8.addWidget(self.message_label)
        self.gridLayout.addLayout(horizontalLayout_8, 7, 0, 1, 3)

        self.liveButton.setCheckable(True)
        self.recordButton.setCheckable(True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    example = MainWindow()
    sys.exit(app.exec_())