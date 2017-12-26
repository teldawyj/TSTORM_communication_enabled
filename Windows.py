#import hamamatsu_camera as cam
import tifffile as tiff
import numpy as np
import c_image_manipulation_c as c_image
import time
import threading
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
#import PyDAQmx
import ctypes
import sys
import os
import windowUI as ui

import aotf as aotfui
import stage as Stage
import message
#import shutter as shutter
#import galvo as Galvo
import synchronization as syn
import tinytiffwriter


class MainWindow:
    def __init__(self):
        super().__init__()
        self.ui=ui.MainWindow()
        self.ui.setupMainWindow()
        self.ui.show()
        self.message=message.Message()
        self.frames = []
        self.lines = None
        self.live_thread_flag = None
        self.record_thread_flag = None
        self.filename = None
        self.rescale_min = 0
        self.rescale_max = 65535
        self.file=None
        #self.hcam = cam.HamamatsuCameraMR(camera_id=0)

        self.ui.shutterButton.clicked.connect(lambda: self.shutterUi())
        self.ui.AOTFButton.clicked.connect(lambda: self.aotfUi())
        self.ui.GalvoButton.clicked.connect(lambda: self.galvoUi())
        self.ui.StageButton.clicked.connect(lambda: self.stageUi())
        self.ui.set_parameter.clicked.connect(lambda: self.start_camera())
        self.ui.exposurebutton.clicked.connect(lambda: self.set_exposure())
        self.ui.liveButton.clicked.connect(lambda: self.live_state_change())
        self.ui.recordButton.clicked.connect(lambda: self.record_state_change())
        self.ui.autoscalebutton.clicked.connect(lambda: self.autoscale())

        self.live_thread = threading.Thread(target=self.display, name='liveThread')
        self.record_thread = threading.Thread(target=self.record, name="recordThread")



    '''def loop(self):
        ''''''thread 1, restart live thread and/or record thread when flags are Ture and cycle ends''''''
        # self.hcam.startAcquisition()
        #i=0
        while (self.loop_flag == True):

            #print("loop thread %d     live thread  %d     record thread  %d" %(i,self.live.is_alive(),self.record_thread.is_alive()))
            #i+=1
            if True: #signal  # if self.count==int(self.frames_doublespinbox.text()):
                #[self.frames, dims] = self.hcam.getFrames()
                if self.live_thread_flag == True and not self.live.is_alive():
                    self.live = threading.Thread(target=self.display, name='liveThread')
                    self.live.start()
                if self.record_thread_flag == True and not self.record_thread.is_alive():
                    self.record_thread = threading.Thread(target=self.record, name="recordThread")
                    self.record_thread.start()
            time.sleep(0.005)'''

    '''def signal(self):
        while(self.signal_thread_flag==True):
            self.lines.DItask.ReadDigitalU32(1, 10.0, PyDAQmx.DAQmx_Val_GroupByChannel, self.lines.data, 1, ctypes.byref(self.lines.read), None)
            if self.lines.data[0]==1:
                self.loop_thread = threading.Thread(target=self.loop, name="loopThread")
                self.loop_thread.start()'''


    def loop(self):

            [self.frames, dims] = self.hcam.getFrames()
            self.ui.message_label.setText("number of frames : " + str(len(self.frames)))
            if self.live_thread_flag == True and not self.live_thread.is_alive():
                self.live_thread = threading.Thread(target=self.display, name='liveThread')
                self.live_thread.start()

            if self.record_thread_flag == True and not self.record_thread.is_alive():
                self.record_thread = threading.Thread(target=self.record, name="recordThread")
                self.record_thread.start()

    def set_exposure(self):
        self.hcam.setPropertyValue('exposure_time', float(self.ui.exp_t_doublespinbox.text()) / 1000)

    def autoscale(self):
        self.rescale_min = self.image_min
        self.rescale_max = self.image_max

    def start_camera(self):
        '''main thread
        use NI digital output to trigger laser and camera'''
        if self.ui.set_parameter.isChecked():
            self.ui.set_parameter.setText("stop camera")
            self.getbuffer_timer = QtCore.QTimer()
            self.getbuffer_timer.timeout.connect(lambda: self.loop())
            self.lines = syn.Lines(float(self.ui.doublespinbox_405.text()), float(self.ui.frames_doublespinbox.text()),
                                   float(self.ui.cycles_doublespinbox.text()),
                                   float(self.ui.exp_t_doublespinbox.text()))
            self.lines.set_lines()
            self.lines.start()
            #self.hcam.startAcquisition()
            self.hcam.setPropertyValue('exposure_time', float(self.ui.exp_t_doublespinbox.text()) / 1000.0)
            expo=float(self.ui.exp_t_doublespinbox.text())
            cycle=float(self.ui.doublespinbox_405.text())+float(self.ui.frames_doublespinbox.text())*(expo+12)
            self.getbuffer_timer.start(cycle)
            self.ui.message_label.setText("current cycle time is : " + str(cycle / 1000.0))

        else:
            self.ui.set_parameter.setText("start camera")
            #self.hcam.stopAcquisition()
            self.lines.stop()
            self.getbuffer_timer.stop()

    def display(self):
        '''live child thread
        display images when one cycle ends'''
        num = min(len(self.frames), int(float(self.ui.frames_doublespinbox.text())))
        display_time = 18
        step = 1 if float(self.ui.exp_t_doublespinbox.text())  > display_time else 2
        sleep_time = step * (float(self.ui.exp_t_doublespinbox.text()) ) - display_time-0.1
        #step = 1 if float(self.exp_t_doublespinbox.text()) +11> display_time else 2
        #sleep_time = step * (float(self.exp_t_doublespinbox.text())+11) - display_time - 0.5
        for i in range(0, num, step):
            #start = time.clock()
            if self.live_thread_flag == False:
                return (0)
            # self.live_event.wait()
            image = self.frames[i].np_array.reshape((2048, 2048))
            [temp, self.image_min, self.image_max] = c_image.rescaleImage(image,
                                                                          False,
                                                                          False,
                                                                          False,
                                                                          [self.rescale_min, self.rescale_max],
                                                                          None)
            qImg = QtGui.QImage(temp.data, 2048, 2048, QtGui.QImage.Format_Indexed8)
            pixmap01 = QtGui.QPixmap.fromImage(qImg)
            self.ui.livewindow.setPixmap(pixmap01)
            time.sleep(sleep_time / 1000.0)

            #stop=time.clock()
            #self.message_label.setText(str(stop-start))
    # when live button is clicked, set live flag to True or False, then live thread will start or stop
    def live_state_change(self):
        if self.ui.liveButton.isChecked():
            self.ui.liveButton.setText('stop live')
            self.live_thread_flag = True

        else:
            self.ui.liveButton.setText('Live')
            self.live_thread_flag = False

    # when record button is clicked, set record flag to True or False, then record thread will start or stop

    def record_state_change(self):
        if not self.ui.recordButton.isChecked():
            self.hcam.setPropertyValue('exposure_time', float(self.ui.exp_t_doublespinbox.text()) / 1000)
            self.ui.recordButton.setText('record')
            self.record_thread_flag = False
            self.tiff.tinytiffclose(self.file)
            self.getbuffer_timer.stop()
            self.lines.stop()
            self.lines = syn.Lines(float(self.ui.doublespinbox_405.text()), float(self.ui.frames_doublespinbox.text()),
                                   float(self.ui.cycles_doublespinbox.text()),
                                   float(self.ui.exp_t_doublespinbox.text()))
            self.lines.set_lines()
            self.lines.start()
            expo = float(self.ui.exp_t_doublespinbox.text())
            cycle = float(self.ui.doublespinbox_405.text()) + float(self.ui.frames_doublespinbox.text()) * (expo + 12)
            self.getbuffer_timer.start(cycle)

        else:
            self.filename = 'D:\\Data\\' + self.ui.name_text.text() + self.ui.name_num.text() + '.tif'
            if os.path.exists(self.filename):
                message, ok = QInputDialog.getText(self.ui, "file exists", "continue will cover the old file",
                                                   QLineEdit.Normal,
                                                   "Yes, please cover the old file")
                if not ok:
                    self.ui.recordButton.setText('record')
                    self.ui.recordButton.setChecked(False)
                    self.record_thread_flag = False
                    return 0
                    # self.tif = tiff.TiffWriter(filename,
                    #                          imagej=True)
            self.ui.recordButton.setText('stop')
            self.hcam.setPropertyValue('exposure_time', float(self.ui.recor_exp_t_doublespinbox.text()) / 1000)
            self.lines.stop()
            self.getbuffer_timer.stop()
            self.lines = syn.Lines(float(self.ui.doublespinbox_405.text()), float(self.ui.frames_doublespinbox.text()),
                                   float(self.ui.cycles_doublespinbox.text()),
                                   float(self.ui.recor_exp_t_doublespinbox.text()))
            self.lines.set_lines()
            self.lines.start()
            expo = float(self.ui.recor_exp_t_doublespinbox.text())
            cycle = float(self.ui.doublespinbox_405.text()) + float(self.ui.frames_doublespinbox.text()) * (expo + 12)
            self.getbuffer_timer.start(cycle)
            self.record_thread_flag = True
            self.tiff=tinytiffwriter.tinytiffwriter()
            self.file=self.tiff.tinytiffopen(self.filename)

    def record(self):
        '''record child thread
        record frames when one cycle ends'''
        # start = time.clock()
        for i in self.frames:
            if self.record_thread_flag == False:
                return (0)
            image = i.np_array.reshape((2048, 2048))
            self.tiff.tinytiffwrite(image,self.file)


    def stageUi(self):
        self.ui.message_label.setText('initializing stage Gui')
        example = Stage.Stage(self.message)
        self.ui.message_label.setText('stage Gui initialized')

    def shutterUi(self):
        Shutter = shutter.shutterGui(self.message)

    def aotfUi(self):
        AotfUi = aotfui.Aotf(self.message)

    def galvoUi(self):
        galvo_ = Galvo.Galvo(self.message)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    example = MainWindow()
    sys.exit(app.exec_())