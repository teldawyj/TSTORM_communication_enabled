from PyDAQmx import *
import numpy as np
import ctypes
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
import module
import time
import threading
import sys

class Lines(module.Module):
    def __init__(self,message,time_405=0,frames=10,cycles=0,exposure=30):
        super().__init__(message)
        self.message=message
        self.read = np.int32()
        self.send_thread_flag = False
        self.process_thread_flag = False
        self.data = np.zeros(1, dtype=np.uint32)
        self.time_405=int(time_405)
        self.frames=int(frames)
        self.cycles=int(cycles)
        self.exposure=int(exposure)
        self.done=bool32(0)


    def lists(self):
        self.list_405=[1]*self.time_405
        self.list_405.extend([0]*self.frames*(self.exposure+11))


        self.list_647=[0]*self.time_405
        self.list_647.extend([1]*self.frames*(self.exposure+11))


        self.camera_list=[0]*self.time_405
        self.camera_list.extend(([1,1,1,1,1,1,1,1,1,1]+[0]*(self.exposure+1))*self.frames)


    def set_lines(self):
        self.task = Task()
        self.lists()
        self.task.CreateDOChan("/Dev1/port0/line1", "405", DAQmx_Val_ChanForAllLines)
        self.task.CreateDOChan("/Dev1/port0/line2", "647", DAQmx_Val_ChanForAllLines)
        self.task.CreateDOChan("/Dev1/port0/line3", "camera", DAQmx_Val_ChanForAllLines)


        if self.cycles==0:
            self.task.CfgSampClkTiming("", 1000, DAQmx_Val_Rising, DAQmx_Val_ContSamps, 1000)
            self.send_thread_flag = False



        else:
            self.list_405 *= self.cycles
            self.list_647 *= self.cycles
            self.camera_list *= self.cycles
            self.task.CfgSampClkTiming("", 1000, DAQmx_Val_Rising, DAQmx_Val_FiniteSamps, len(self.list_405))

        data=[self.list_405,self.list_647,self.camera_list]
        data=np.array(data,dtype=np.uint8)
        self.task.WriteDigitalLines(data.shape[1], 0, 10.0, DAQmx_Val_GroupByChannel, data, None,None)

    def start(self):
        self.task.StartTask()
        if self.message.find_message('stage mode')=="stage mode":
           self.stage_mode=True
        #self.loop_thread = threading.Thread(target=self.loop, name="loop_thread")
        #self.loop_thread.start()
        self.loop()

    def loop(self):
        if self.stage_mode==True:
            self.first_time=True
            while (self.stage_mode==True):
                self.task.IsTaskDone(ctypes.byref(self.done))

                if self.done.value:
                    if self.first_time==True:
                        self.send_message()
                        self.first_time=False

                    self.process_message()
                else:
                    time.sleep(0.1)


    def process_message(self):
        if self.message.find_message("camera")=="stop camera" or \
                self.message.find_message("camera")=="stop camera do not stop stage":
            self.stage_mode = False
            self.message.send_message("lines","stop lines")
            self.message.send_message("camera state","stopped")
            self.message.send_message("camera", "waiting")
        elif self.message.find_message("lines") == "start lines":
            print(threading.get_ident(), "lines get starting message")
            self.stop()
            self.set_lines()
            self.task.StartTask()
            self.first_time=True
            self.stage_mode = True
        else:
            time.sleep(0.1)

    def send_message(self):

        self.message.send_message("lines", "lines stopped")
        self.stage_mode = True
        self.message.send_message("stage", "start stage")



    def stop(self):
        self.task.StopTask()
        self.task.ClearTask()



if __name__=='__main__':
    app = QApplication(sys.argv)
    exa = Lines({})
    exa.set_lines()
    exa.start()
    sys.exit(app.exec_())