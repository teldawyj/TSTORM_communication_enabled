import hamamatsu_camera as cam
import tifffile as tiff
import numpy as np
import c_image_manipulation_c as c_image
import time
import threading
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
import PyDAQmx
import ctypes
import sys
import os
import windowUI as ui

import aotf as aotfui
import stage as Stage
import message
import shutter as shutter
import galvo as Galvo
import synchronization as syn
import tinytiffwriter
import tifffile
import libtiff


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
        self.waiting_thread_flag=None
        self.filename = None
        self.rescale_min = 0
        self.rescale_max = 65535
        self.file=None
        self.lock = threading.Lock()
        self.hcam = cam.HamamatsuCameraMR(camera_id=0)
        #self.hcam.setPropertyValue("trigger_source", 2)
        #self.hcam.setPropertyValue("trigger_active", 3)
        #self.hcam.setPropertyValue("trigger_polarity", 2)


        self.ui.shutterButton.clicked.connect(lambda: self.shutterUi())
        self.ui.AOTFButton.clicked.connect(lambda: self.aotfUi())
        self.ui.GalvoButton.clicked.connect(lambda: self.galvoUi())
        self.ui.StageButton.clicked.connect(lambda: self.stageUi())
        self.ui.set_parameter.clicked.connect(lambda: self.set_parameter_button_pushed())
#        self.ui.exposurebutton.clicked.connect(lambda: self.set_exposure())
        self.ui.liveButton.clicked.connect(lambda: self.live_state_change())
        self.ui.recordButton.clicked.connect(lambda: self.record_state_change())
        self.ui.autoscalebutton.clicked.connect(lambda: self.autoscale())

        self.live_thread = threading.Thread(target=self.living, name='liveThread')
        self.record_thread = threading.Thread(target=self.recording, name="recordThread")


    def loop(self):

            [self.frames, dims] = self.hcam.getFrames()#FIXME: cannot get buffer when external triger
            #print("frames number=  " ,len(self.frames))
            '''if len(self.frames)==0:
                #self.hcam.stopAcquisition()
                self.getbuffer_timer.stop()
                if self.ui.recordButton.isChecked():
                    self.ui.recordButton.setChecked(False)
                    self.ui.recordButton.setText("record")
                    self.record_thread_flag=False
                self.ui.set_parameter.setText("start camera")
                self.ui.set_parameter.setChecked(False)
                return(0)'''
            self.ui.message_label.setText("current cycle time is : " + str(self.cycle / 1000.0))
            self.ui.message_label.setText("cycle time: " + str(self.cycle / 1000.0)+"frames : " + str(len(self.frames))
                                          )

            if self.live_thread_flag == True:
                if  self.live_thread.is_alive():
                    self.live_thread_flag =False
                    time.sleep(0.075)
                    self.live_thread_flag = True
                #print("display start")
                self.live_thread = threading.Thread(target=self.living, name='liveThread')
                self.live_thread.start()

            if self.record_thread_flag == True and not self.record_thread.is_alive():
                self.record_thread = threading.Thread(target=self.recording, name="recordThread")
                self.record_thread.start()

#    def set_exposure(self):
#        self.hcam.setPropertyValue('exposure_time', float(self.ui.exp_t_doublespinbox.text()) / 1000)

    def autoscale(self):
        try:
            self.rescale_min = self.image_min
            self.rescale_max = self.image_max
        except:
            print("not start display yet")

    def start_running(self):
        if self.ui.recordButton.isChecked():
            self.message.send_message("camera", "start camera")
            self.message.send_message("mode","recording mode")
            self.getbuffer_timer = QtCore.QTimer()
            self.getbuffer_timer.timeout.connect(lambda: self.loop())
            self.lines = syn.Lines(message=self.message, time_405=float(self.ui.doublespinbox_405.text()),
                                   frames=float(self.ui.frames_doublespinbox.text()),
                                   cycles=float(self.ui.cycles_doublespinbox.text()),
                                   exposure=float(self.ui.recor_exp_t_doublespinbox.text()))
            self.lines.set_lines()
            self.lines.start()
            self.ui.set_parameter.setChecked(True)
            self.ui.set_parameter.setText("stop camera")
            self.message.send_message("camera state", "started")
            self.hcam.startAcquisition()
            self.hcam.setPropertyValue('exposure_time', float(self.ui.recor_exp_t_doublespinbox.text()) / 1000.0)
            cycle = float(self.ui.doublespinbox_405.text()) + \
                    float(self.ui.frames_doublespinbox.text()) * (float(self.ui.recor_exp_t_doublespinbox.text()) + 12)
            self.getbuffer_timer.start(cycle)
            self.ui.message_label.setText("current cycle time is : " + str(cycle / 1000.0))
        else:
            self.message.send_message("mode", "living mode")
            self.message.send_message("camera", "start camera")
            self.getbuffer_timer = QtCore.QTimer()
            self.getbuffer_timer.timeout.connect(lambda: self.loop())
            self.lines = syn.Lines(message=self.message, time_405=float(self.ui.doublespinbox_405.text()),
                                   frames=float(self.ui.frames_doublespinbox.text()),
                                   cycles=float(self.ui.cycles_doublespinbox.text()),
                                   exposure=float(self.ui.exp_t_doublespinbox.text()))
            self.lines.set_lines()
            self.lines.start()
            self.message.send_message("camera state","started")
            self.ui.set_parameter.setChecked(True)
            self.ui.set_parameter.setText("stop camera")
            self.hcam.startAcquisition()
            self.hcam.setPropertyValue('exposure_time', float(self.ui.exp_t_doublespinbox.text()) / 1000.0)
            self.cycle = float(self.ui.doublespinbox_405.text()) + \
                    float(self.ui.frames_doublespinbox.text()) * (float(self.ui.exp_t_doublespinbox.text()) + 12)
            self.getbuffer_timer.start(self.cycle)


    def stop_running(self):
        if float(self.ui.cycles_doublespinbox.text())==0:
            self.lines.stop()
            self.hcam.stopAcquisition()
            self.message.send_message("camera state","stopped")
            self.message.send_message("camera","waiting")
            self.getbuffer_timer.stop()
            self.ui.set_parameter.setText("start camera")
            self.ui.set_parameter.setChecked(False)
        else:
            if self.ui.recordButton.isChecked():
                self.message.send_message("camera", "stop camera do not stop stage")
            else:
                self.message.send_message("camera", "stop camera")
            while self.message.find_message("camera state")!="stopped":
                time.sleep(0.1)
            self.getbuffer_timer.stop()
            self.hcam.stopAcquisition()
            self.message.send_message("camera", "waiting")
            self.ui.set_parameter.setText("start camera")
            self.ui.set_parameter.setChecked(False)

    def set_parameter_button_pushed(self):
        '''main thread
        use NI digital output to trigger laser and camera'''
        if self.ui.set_parameter.isChecked():
            print("action start")
            self.start_running()

        else:
            print("action stop")
            self.stop_running()



    def living(self):
        '''live child thread
        display images when one cycle ends'''
        #num = min(len(self.frames), int(float(self.ui.frames_doublespinbox.text())))
        num=len(self.frames)
        step = 2
        sleep_time=70
        for i in range(0, num, step):
            if self.live_thread_flag == False:
                return (0)
            image = self.frames[i].np_array.reshape((2048, 2048))
            self.lock.acquire()
            rescale_min=self.rescale_min
            rescale_max = self.rescale_max
            self.lock.release()
            [temp, self.image_min, self.image_max] = c_image.rescaleImage(image,
                                                                          False,
                                                                          False,
                                                                          False,
                                                                          [rescale_min, rescale_max],
                                                                          None)
            qImg = QtGui.QImage(temp.data, 2048, 2048, QtGui.QImage.Format_Indexed8)
            pixmap01 = QtGui.QPixmap.fromImage(qImg)
            self.ui.livewindow.setPixmap(pixmap01)
            if self.live_thread_flag == False:
                return (0)
            time.sleep(sleep_time / 1000.0)

    # when live button is clicked, set live flag to True or False, then live thread will start or stop
    def live_state_change(self):
        if self.ui.liveButton.isChecked():
            #self.stop_running()
            #self.start_running()
            self.start_living()


        else:
            #self.stop_running()
            #self.start_running()
            self.stop_living()

    def start_living(self):
        self.ui.liveButton.setText('stop live')
        self.message.send_message("live", "start living")
        self.live_thread_flag = True

    def stop_living(self):
        self.ui.liveButton.setText('Live')
        self.message.send_message("live", "stop living")
        self.live_thread_flag = False

    # when record button is clicked, set record flag to True or False, then record thread will start or stop

    def record_state_change(self):
        if not self.ui.recordButton.isChecked():
            self.message.send_message("record","stop recording")
            self.stop_record()
            self.stop_running()
            #self.start_running()


        else:
            self.message.send_message("record","start recording")
            self.start_record()
            self.stop_running()
            self.start_running()

    def recording(self):
        '''record child thread
        record frames when one cycle ends'''
        # start = time.clock()
        for i in self.frames:
            if self.record_thread_flag == False:
                return (0)
            image = i.np_array.reshape((2048, 2048))
            #self.tiff.write_image(image)#use libtiff
            self.tiff.tinytiffwrite(image,self.file)
            #tifffile.imsave(self.filename, image) #use tifffile.py

    def start_record(self):
        self.filename = 'D:\\Data\\' + self.ui.name_text.text() + self.ui.name_num.text() + '.tif'
        '''if os.path.exists(self.filename):
            message, ok = QInputDialog.getText(self.ui, "file exists", "continue will cover the old file",
                                               QLineEdit.Normal,
                                               "Yes, please cover the old file")
            if not ok:
                self.stop_record()
                self.message.send_message("record","stop recording")
                return 0'''
        self.ui.recordButton.setText('stop')
        self.tiff = tinytiffwriter.tinytiffwriter()#use tinytiffwriter.dll
        self.file = self.tiff.tinytiffopen(self.filename,16,2048,2048)
        #self.tiff = libtiff.TIFF.open(self.filename, mode='w')#use libtiff
        self.record_thread_flag = True



    def stop_record(self):
        self.record_thread_flag = False
        self.ui.recordButton.setChecked(False)
        self.ui.recordButton.setText("record")
        try:
            #self.tiff.close()#use libtiff
            self.tiff.tinytiffclose(self.file)
        except:
            pass

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