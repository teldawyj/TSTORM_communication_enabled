
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
import sys

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setupMainWindow()
        self.show()


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
#set camera mode
        cambox=QGroupBox('camera box',self)
        verticalLayout_c=QVBoxLayout(cambox)
        #trigger source
        horizontalLayout_c1=QHBoxLayout()
        label_source=QLabel('trigger source',cambox)
        self.source=QComboBox(cambox)
        self.source.addItems(['internal','external'])
        horizontalLayout_c1.addWidget(label_source)
        horizontalLayout_c1.addWidget(self.source)
        #trigger active
        horizontalLayout_c2=QHBoxLayout()
        label_active=QLabel('trigger active',cambox)
        self.active=QComboBox(cambox)
        self.active.addItems(['edge','synchronous'])
        horizontalLayout_c2.addWidget(label_active)
        horizontalLayout_c2.addWidget(self.active)
        #set button
        horizontalLayout_c3=QHBoxLayout()
        self.set_button=QPushButton('set',cambox)
        horizontalLayout_c3.addWidget(self.set_button)
        verticalLayout_c.addLayout(horizontalLayout_c1)
        verticalLayout_c.addLayout(horizontalLayout_c2)
        verticalLayout_c.addLayout(horizontalLayout_c3)

        cambox.setLayout(verticalLayout_c)
        self.gridLayout.addWidget(cambox)

# handle live
        liveGroupBox = QGroupBox("live box",self)
        verticalLayout_l = QVBoxLayout(liveGroupBox)
        #405
        horizontalLayout_l1=QHBoxLayout()
        horizontalLayout_l11 = QHBoxLayout()
        label_405_expo=QLabel("405_exposure",liveGroupBox)
        self._405_expo=QDoubleSpinBox(liveGroupBox)
        self._405_expo.setDecimals(0)
        self._405_expo.setMinimum(0)
        self._405_expo.setMaximum(2000)
        self._405_expo.setValue(100)
        horizontalLayout_l1.addWidget(label_405_expo)
        horizontalLayout_l1.addWidget(self._405_expo)
        # 647 and camera exposure
        horizontalLayout_l2=QHBoxLayout()
        horizontalLayout_l22 = QHBoxLayout()
        label_cam_expo=QLabel("cam_exposure",liveGroupBox)
        self.cam_expo=QDoubleSpinBox(liveGroupBox)
        self.cam_expo.setDecimals(0)
        self.cam_expo.setMinimum(5)
        self.cam_expo.setMaximum(1000)
        self.cam_expo.setValue(50)
        horizontalLayout_l2.addWidget(label_cam_expo)
        horizontalLayout_l2.addWidget(self.cam_expo)

        #frames and cycles
        horizontalLayout_l3=QHBoxLayout()
        horizontalLayout_l33 = QHBoxLayout()
        label_frames=QLabel("frames",liveGroupBox)
        self.frames=QDoubleSpinBox(liveGroupBox)
        self.frames.setDecimals(0)
        self.frames.setMinimum(1)
        self.frames.setMaximum(100)
        self.frames.setValue(10)
        label_cycles=QLabel("cycles",liveGroupBox)
        self.cycles=QDoubleSpinBox(liveGroupBox)
        self.cycles.setDecimals(0)
        self.cycles.setMinimum(0)
        self.cycles.setMaximum(1000)
        self.cycles.setValue(0)
        horizontalLayout_l3.addWidget(label_frames)
        horizontalLayout_l3.addWidget(self.frames)
        horizontalLayout_l33.addWidget(label_cycles)
        horizontalLayout_l33.addWidget(self.cycles)
        #live button and autoscale button
        horizontalLayout_l4=QHBoxLayout()
        self.liveButton = QPushButton('live', self)
        self.autoscalebutton = QPushButton("autoscale", liveGroupBox)
        horizontalLayout_l4.addWidget(self.liveButton)
        horizontalLayout_l4.addWidget(self.autoscalebutton)
        verticalLayout_l.addLayout(horizontalLayout_l1)
        verticalLayout_l.addLayout(horizontalLayout_l11)
        verticalLayout_l.addLayout(horizontalLayout_l2)
        verticalLayout_l.addLayout(horizontalLayout_l22)
        verticalLayout_l.addLayout(horizontalLayout_l3)
        verticalLayout_l.addLayout(horizontalLayout_l33)
        verticalLayout_l.addLayout(horizontalLayout_l4)

        liveGroupBox.setLayout(verticalLayout_l)
        self.gridLayout.addWidget(liveGroupBox,2,0,1,1)
# handle record
        recordGroupBox = QGroupBox("record box",self)
        verticalLayout_r = QVBoxLayout(recordGroupBox)
        # 405
        horizontalLayout_r1 = QHBoxLayout()
        label_405_expo = QLabel("405_expo", liveGroupBox)
        self.r_405_expo = QDoubleSpinBox(recordGroupBox)
        self.r_405_expo.setDecimals(0)
        self.r_405_expo.setMinimum(0)
        self.r_405_expo.setMaximum(2000)
        self.r_405_expo.setValue(100)

        horizontalLayout_r1.addWidget(label_405_expo)
        horizontalLayout_r1.addWidget(self.r_405_expo)
        # 647 and camera exposure
        horizontalLayout_r2 = QHBoxLayout()
        label_cam_expo = QLabel("cam_expo", recordGroupBox)
        self.rcam_expo = QDoubleSpinBox(recordGroupBox)
        self.rcam_expo.setDecimals(0)
        self.rcam_expo.setMinimum(5)
        self.rcam_expo.setMaximum(1000)
        self.rcam_expo.setValue(20)
        horizontalLayout_r2.addWidget(label_cam_expo)
        horizontalLayout_r2.addWidget(self.rcam_expo)

        # frames and cycles
        horizontalLayout_r3 = QHBoxLayout()
        label_frames = QLabel("frames", recordGroupBox)
        self.rframes = QDoubleSpinBox(recordGroupBox)
        self.rframes.setDecimals(0)
        self.rframes.setMinimum(1)
        self.rframes.setMaximum(100)
        self.rframes.setValue(10)
        label_cycles = QLabel("cycles", recordGroupBox)
        self.rcycles = QDoubleSpinBox(recordGroupBox)
        self.rcycles.setDecimals(0)
        self.rcycles.setMinimum(0)
        self.rcycles.setMaximum(1000)
        self.rcycles.setValue(20)
        horizontalLayout_r3.addWidget(label_frames)
        horizontalLayout_r3.addWidget(self.rframes)
        horizontalLayout_r3.addWidget(label_cycles)
        horizontalLayout_r3.addWidget(self.rcycles)
        # record button
        horizontalLayout_r4 = QHBoxLayout()
        self.recordButton = QPushButton('record', self)
        horizontalLayout_r4.addWidget(self.recordButton)
        #filename
        horizontalLayout_r5=QHBoxLayout()
        label_file=QLabel("file",recordGroupBox)
        self.name_text = QLineEdit('movie_', recordGroupBox)
        self.name_num = QDoubleSpinBox(recordGroupBox)
        self.name_num.setDecimals(0)
        self.name_num.setMinimum(1)
        self.name_num.setMaximum(1000)
        self.name_num.setValue(1)
        horizontalLayout_r5.addWidget(label_file)
        horizontalLayout_r5.addWidget(self.name_text)
        horizontalLayout_r5.addWidget(self.name_num)

        verticalLayout_r.addLayout(horizontalLayout_r1)
        verticalLayout_r.addLayout(horizontalLayout_r2)
        verticalLayout_r.addLayout(horizontalLayout_r3)
        verticalLayout_r.addLayout(horizontalLayout_r4)
        verticalLayout_r.addLayout(horizontalLayout_r5)

        recordGroupBox.setLayout(verticalLayout_r)
        self.gridLayout.addWidget(recordGroupBox, 3, 0, 1, 1)

        # display image window
        self.livewindow = QLabel(self)
        self.livewindow.setScaledContents(True)
        data = np.ones((2048, 2048), dtype=np.uint8)
        pixmap = QtGui.QImage(data, 2048, 2048, QtGui.QImage.Format_Indexed8)
        pixmap = QtGui.QPixmap.fromImage(pixmap)
        self.livewindow.setPixmap(pixmap)
        self.gridLayout.addWidget(self.livewindow,1,1,3,3)

        horizontalLayout_message = QHBoxLayout()
        # message label
        self.message_label = QLabel('message', self)
        horizontalLayout_message.addWidget(self.message_label)
        self.gridLayout.addLayout(horizontalLayout_message, 7, 0, 1, 3)

        self.liveButton.setCheckable(True)
        self.recordButton.setCheckable(True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    example = MainWindow()
    sys.exit(app.exec_())