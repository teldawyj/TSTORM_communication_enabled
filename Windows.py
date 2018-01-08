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
        self.camera()
        self.message=message.Message()
        self.frames = []
        self.readout_time=None
        self.lines = None
        self.live_thread_flag = None
        self.record_thread_flag = None
        self.filename = None
        self.rescale_min = 0
        self.rescale_max = 65535
        self.file=None
        self.lock = threading.Lock()
        self.hcam = cam.HamamatsuCameraMR(camera_id=0)
        self.hcam.setPropertyValue("trigger_polarity", 2)

        self.ui.shutterButton.clicked.connect(lambda: self.shutterUi())
        self.ui.AOTFButton.clicked.connect(lambda: self.aotfUi())
        self.ui.GalvoButton.clicked.connect(lambda: self.galvoUi())
        self.ui.StageButton.clicked.connect(lambda: self.stageUi())
        self.ui.liveButton.clicked.connect(lambda: self.live_state_change())
        self.ui.recordButton.clicked.connect(lambda: self.record_state_change())
        self.ui.autoscalebutton.clicked.connect(lambda: self.autoscale())
        self.ui.set_button.clicked.connect(lambda: self.camera())

        self.live_thread = threading.Thread(target=self.living, name='liveThread')
        self.record_thread = threading.Thread(target=self.recording, name="recordThread")


    def camera(self):
        if self.ui.source.currentText()=='internal':
            self.hcam.setPropertyValue("trigger_source", 1)
            self.message.send_message('trigger source','internal')
            self.readout_time=0
        else:
            self.hcam.setPropertyValue("trigger_source", 2)
            self.message.send_message('trigger source','external')
            if self.ui.active.currentText() == 'edge':
                self.hcam.setPropertyValue("trigger_active", 1)
                self.message.send_message('trigger active','edge')
                self.readout_time = 11
            else:
                self.hcam.setPropertyValue("trigger_active", 3)
                self.message.send_message('trigger active','synchronous')
                self.readout_time = 0



    def loop(self):
            [self.frames, dims] = self.hcam.getFrames()
            if len(self.frames)==0:
                self.hcam.stopAcquisition()
                self.getbuffer_timer.stop()
                if self.ui.recordButton.isChecked():
                    self.ui.recordButton.setChecked(False)
                    self.ui.recordButton.setText("record")
                    self.record_thread_flag=False
                self.ui.liveButton.setText("live")
                self.ui.liveButton.setChecked(False)
                return(0)
            self.ui.message_label.setText("cycle time: " + str(self.cycle / 1000.0)+
                                          "   frames : " + str(len(self.frames)))

            if self.live_thread_flag == True:
                if  self.live_thread.is_alive():
                    self.live_thread_flag =False
                    time.sleep(0.1)
                    self.live_thread_flag = True
                self.live_thread = threading.Thread(target=self.living, name='liveThread')
                self.live_thread.start()

            if self.record_thread_flag == True and not self.record_thread.is_alive():
                self.record_thread = threading.Thread(target=self.recording, name="recordThread")
                self.record_thread.start()


    def autoscale(self):
        try:
            self.rescale_min = self.image_min
            self.rescale_max = self.image_max
        except:
            print("not start display yet")

    def start_running(self):
        try:
            self.aotf.ui.button_analog.setChecked(True)
            self.aotf.analog()
        except:
            pass
        self.message.send_message("camera", "start camera")
        self.getbuffer_timer = QtCore.QTimer()
        self.getbuffer_timer.timeout.connect(lambda: self.loop())

        if self.ui.recordButton.isChecked():
            self.message.send_message("mode","recording mode")
            args=[self.message,float(self.ui.r_405_expo.text()),float(self.ui.r_405_amp.text()),
                  float(self.ui.r_647_amp.text()),
                  float(self.ui.rframes.text()),float(self.ui.rcycles.text()),float(self.ui.rcam_expo.text())]
            if not (self.ui.source.currentText()=='external' and self.ui.active.currentText()=='synchronous'):
                self.hcam.setPropertyValue('exposure_time', float(self.ui.rcam_expo.text()) / 1000.0)

            self.cycle = float(self.ui.r_405_expo.text()) + \
                    float(self.ui.rframes.text()) * (float(self.ui.rcam_expo.text()) + self.readout_time)

        else:
            self.message.send_message("mode", "living mode")
            args = [self.message, float(self.ui._405_expo.text()), float(self.ui._405_amp.text()),
                    float(self.ui._647_amp.text()),
                    float(self.ui.frames.text()), float(self.ui.cycles.text()), float(self.ui.cam_expo.text())]
            if not (self.ui.source.currentText()=='external' and self.ui.active.currentText()=='synchronous'):
                self.hcam.setPropertyValue('exposure_time', float(self.ui.cam_expo.text()) / 1000.0)

            self.cycle = float(self.ui._405_expo.text()) + \
                    float(self.ui.frames.text()) * (float(self.ui.cam_expo.text()) + self.readout_time)

        self.lines = syn.Lines(args)
        self.lines.set_lines()
        self.lines.start()
        self.ui.liveButton.setChecked(True)
        self.ui.liveButton.setText("stop")
        self.message.send_message("camera state", "started")
        self.hcam.startAcquisition()
        self.getbuffer_timer.start(self.cycle)
        self.ui.message_label.setText("current cycle time is : " + str(self.cycle / 1000.0))


    def stop_running(self):
        try:
            self.aotf.ui.button_analog.setChecked(False)
            self.aotf.analog()
        except:
            pass
        if self.message.find_message('illumination') == 'continuous':
            self.lines.stop()
        else:
            if self.ui.recordButton.isChecked():
                self.message.send_message("camera", "stop camera do not stop stage")
            else:
                self.message.send_message("camera", "stop camera")
            while self.message.find_message("camera state") != "stopped":
                time.sleep(0.5)

        self.hcam.stopAcquisition()
        self.getbuffer_timer.stop()
        self.message.send_message("camera state", "stopped")
        self.message.send_message("camera", "waiting")
        self.ui.liveButton.setText("live")
        self.ui.liveButton.setChecked(False)

    def living(self):
        '''live child thread
        display images when one cycle ends'''
        num=len(self.frames)
        step = 3
        sleep_time=100
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
            time.sleep(sleep_time / 2000.0)
            if self.live_thread_flag == False:
                return (0)
            time.sleep(sleep_time / 2000.0)

    # when live button is clicked, set live flag to True or False, then live thread will start or stop
    def live_state_change(self):
        if self.ui.liveButton.isChecked():
            print("action start")
            #make sure that aotf is on external mode
            self.start_running()
            self.start_living()


        else:
            print("action stop")
            #turn aotf to internal mode
            self.stop_running()
            self.stop_living()

    def start_living(self):
        self.message.send_message("live", "start living")
        self.live_thread_flag = True

    def stop_living(self):
        self.message.send_message("live", "stop living")
        self.live_thread_flag = False

    # when record button is clicked, set record flag to True or False, then record thread will start or stop

    def record_state_change(self):
        if not self.ui.recordButton.isChecked():
            self.message.send_message("record","stop recording")
            self.stop_record()
            self.stop_running()


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
        self.ui.recordButton.setText('stop')
        self.tiff = tinytiffwriter.tinytiffwriter()#use tinytiffwriter.dll
        self.file = self.tiff.tinytiffopen(self.filename,16,2048,2048)
        self.ui.name_num.setValue(int(self.ui.name_num.text())+1)
        #self.tiff = libtiff.TIFF.open(self.filename, mode='w8')#use libtiff
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
        self.stage = Stage.Stage(self.message)
        self.ui.message_label.setText('stage Gui initialized')

    def shutterUi(self):
        self.shutter = shutter.shutterGui(self.message)

    def aotfUi(self):
        self.aotf = aotfui.Aotf(self.message)

    def galvoUi(self):
        self.galvo = Galvo.Galvo(self.message)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    example = MainWindow()
    sys.exit(app.exec_())
