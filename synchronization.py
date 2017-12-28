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
    def __init__(self,message,time_405=100,frames=3,cycles=0,exposure=20):
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
        self.list_405.extend([0]*self.frames*(self.exposure+12))


        self.list_647=[0]*self.time_405
        self.list_647.extend([1]*self.frames*(self.exposure+12))


        self.camera_list=[0]*self.time_405
        self.camera_list.extend(([1,1,1,1,1,1,1,1,1,1]+[0]*(self.exposure+2))*self.frames)


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
            self.task.CfgSampClkTiming("", 1000, DAQmx_Val_Rising, DAQmx_Val_FiniteSamps, 1000)
            self.list_405*=self.cycles
            self.list_647*=self.cycles
            self.camera_list*=self.cycles
            self.send_thread_flag=True
            print("communication mode")



        data=[self.list_405,self.list_647,self.camera_list]
        data=np.array(data,dtype=np.uint8)

        self.task.WriteDigitalLines(data.shape[1], 0, 10.0, DAQmx_Val_GroupByChannel, data, None,None)

    def start(self):
        self.task.StartTask()
        self.send_thread = threading.Thread(target=self.send_message, name="send_thread")
        self.send_thread.start()

    def process_message(self):
        i=0
        while(self.process_thread_flag==True):
            print(threading.get_ident(),"lines is waiting for message %d"%i)
            i+=1
            if self.message.find_message("lines")=="start lines":
                print(threading.get_ident(),"lines get message")
                try:
                    self.task.StopTask()
                except:
                    pass
                self.set_lines()
                self.start()
                self.process_thread_flag=False
            elif self.message.find_message("lines")=="finished":
                self.process_thread_flag=False
                self.message.send_message("camera","stop camera")
                self.send_thread_flag=True
            else:
                time.sleep(0.1)

    def send_message(self):
        i = 0
        while(self.send_thread_flag==True):
            #if i==0:
            print(threading.get_ident(),"lines is waiting to send message %d"%i)
            i+=1
            self.task.IsTaskDone(ctypes.byref(self.done))
            if self.done.value:
                print(threading.get_ident(),"lines is sending message")
                self.message.send_message("lines", "stop lines")
                self.send_thread_flag=False
                self.process_thread_flag = True
                processing_thread=threading.Thread(target=self.process_message,name="processing thread")
                processing_thread.start()
                self.task.ClearTask()
                self.message.send_message("stage", "start stage")
            else:
                time.sleep(0.1)


    def stop(self):
        self.task.StopTask()
        self.task.ClearTask()
        pass



if __name__=='__main__':
    app = QApplication(sys.argv)
    exa = Lines({})
    exa.start()
    sys.exit(app.exec_())