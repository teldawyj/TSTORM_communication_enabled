from PyQt5 import QtCore, QtGui, QtWidgets
import stage_UI as ui
import pyapt
import module
import threading
import time
import mymclController as mcl
import sys

class Stage(module.Module):
    def __init__(self,message):
        super().__init__(message)
        self.message=message
        self.ui=ui.stageUI()
        self.ui.setupUI()
        self.ui.show()
        self.processing_flag = None
        self.move_distance=None
        self.handle_x = pyapt.APTMotor(83833850)
        self.handle_y = pyapt.APTMotor(83840820)
        self.handle_z = pyapt.APTMotor(83841441)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(lambda: self.readinfo())
        self.timer.start(20)
        self.handle_x.setStageAxisInformation(-4, 15)
        self.handle_y.setStageAxisInformation(-10, 10)
        self.handle_z.setStageAxisInformation(-15, 2.4)
        self.mcl_handle = mcl.MCLStage(mcl_lib="C:\Program Files\Mad City Labs\\NanoDrive\Madlib.dll")

        self.ui.xrangeLabel.setText('x range: '+'min: ' +str(self.handle_x.getStageAxisInformation()[0]) +
                                  ',   max: ' + str(self.handle_x.getStageAxisInformation()[1]))
        self.ui.yrangeLabel.setText('y range: '+'min: ' +str(self.handle_y.getStageAxisInformation()[0]) +
                                ',   max: ' + str(self.handle_y.getStageAxisInformation()[1]))
        self.ui.zrangeLabel.setText('z range: '+'min: ' +str(self.handle_z.getStageAxisInformation()[0]) +
                                ',   max: ' + str(format(self.handle_z.getStageAxisInformation()[1], '.3f')))
        self.ui.Vlimit.setText('max_acc:' + str(self.handle_y.getVelocityParameterLimits()[0]) + ' max_V:' + str(
            format(self.handle_y.getVelocityParameterLimits()[1], '.2f')))
        self.ui.rangelabel.setText('z range: ' + str(self.mcl_handle._getCalibration(3)))

        self.ui.VON_OFF.clicked.connect(lambda: self.VON_OFFstate())
        self.ui.zupButton.clicked.connect(lambda: self.ZUP())
        self.ui.zupLButton.clicked.connect(lambda: self.ZUPL())
        self.ui.zdownButton.clicked.connect(lambda: self.ZDOWN())
        self.ui.zdownLButton.clicked.connect(lambda: self.ZDOWNL())
        self.ui.upLButton.clicked.connect(lambda: self.XUPL())
        self.ui.upSButton.clicked.connect(lambda: self.XUP())
        self.ui.downLButton.clicked.connect(lambda: self.XDOWNL())
        self.ui.downSButton.clicked.connect(lambda: self.XDOWN())
        self.ui.leftLButton.clicked.connect(lambda: self.YLEFTL())
        self.ui.leftSButton.clicked.connect(lambda: self.YLEFT())
        self.ui.rightLButton.clicked.connect(lambda: self.YRIGHTL())
        self.ui.rightSButton.clicked.connect(lambda: self.YRIGHT())
        self.ui.exitButton.clicked.connect(lambda: self.Exit())

        self.piezo_timer = QtCore.QTimer()
        self.piezo_timer.timeout.connect(lambda: self.piezoinfo())
        self.piezo_timer.start(20)
        self.ui.goButton.clicked.connect(lambda: self.GO())
        self.ui.piezo_go.clicked.connect(lambda: self.piezo_Abs(distance=float(self.ui.piezo_doublespinbox.text())))
        self.ui.zRel_button.clicked.connect(lambda: self.piezo_Rel(distance=float(self.ui.zReldoublespinbox.text())))
        self.ui.move_stage_in_record.clicked.connect(lambda:self.change_button())


    def change_button(self):
        if self.ui.move_stage_in_record.isChecked():
            self.message.send_message("stage","stage awaiting")
            self.message.send_message('stage mode','stage mode')
            self.loop_flag = True
            self.move_distance = 0.0
            self.position=self.mcl_handle.getPosition(3)
            self.ui.move_stage_in_record.setText("running")
            self.loop_thread = threading.Thread(target=self.loop, name="loop thread")
            self.loop_thread.start()
        else:
            self.loop_flag = False
            self.message.send_message("stage mode","no mode")
            self.message.send_message("stage","stage stopped")
            self.ui.move_stage_in_record.setText("set")


    def loop(self):
        print(threading.get_ident(), " stage is started")
        while(self.loop_flag==True):
            if self.message.find_message("camera")=="stop camera":
                print("stage action over")
                self.loop_flag=False
                self.ui.move_stage_in_record.setChecked(False)
                self.ui.move_stage_in_record.setText("Set")
                self.message.send_message("stage","action stage stopped")
            elif self.message.find_message("camera")=="stop camera do not stop stage":
                #print("still in the siop mode")
                self.piezo_Abs(self.position)
                self.move_distance = 0.0
                time.sleep(1)
                #self.message.send_message("stage", " record stage stopped")
            elif self.message.find_message("stage")=="start stage":
                print(threading.get_ident(),"stage get starting message")
                self.send_message()
            else:
                time.sleep(0.1)

    def send_message(self):
        print(threading.get_ident(),"stage is sending message")
        if self.move_distance<float(self.ui.record_move_range.text()):
            self.piezo_Rel(distance=1.00)
            time.sleep(0.1)
            self.move_distance+=1.0
            self.message.send_message("stage", "lines stage stopped")
            self.message.send_message("lines", "start lines")
            self.loop_flag = True
        else:
            print("stage move action finished")
            self.message.send_message("camera", "stop camera")
            self.message.send_message("stage","stop stage")
            self.message.send_message('stage mode','no mode')
            self.ui.move_stage_in_record.setChecked(False)
            self.loop_flag = False
            self.ui.move_stage_in_record.setText("Set")




    def ZUP(self):
        self.handle_z.mRel(.01)

    def ZUPL(self):
        self.handle_z.mRel(.05)

    def ZDOWN(self):
        self.handle_z.mRel(-.01)

    def ZDOWNL(self):
        self.handle_z.mRel(-.05)

    def XUP(self):
        self.handle_y.mRel(.01)
        pass

    def XUPL(self):
        self.handle_y.mRel(.05)
        pass

    def XDOWN(self):
        self.handle_y.mRel(-.01)
        pass

    def XDOWNL(self):
        self.handle_y.mRel(-.05)
        pass

    def YLEFT(self):
        self.handle_x.mRel(-.01)

    def YLEFTL(self):
        self.handle_x.mRel(-.05)

    def YRIGHT(self):
        self.handle_x.mRel(.01)

    def YRIGHTL(self):
        self.handle_x.mRel(.05)

    def HOME(self):
        self.handle_x.mAbs(0)
        self.handle_y.mAbs(0)
        self.handle_z.mAbs(0)

    def readinfo(self):
        self.ui.xposLabel.setText("x position: " +str(format(self.handle_x.getPos(), '.3f')))
        self.ui.yposLabel.setText("y position: " + str(format(self.handle_y.getPos(), '.3f')))
        self.ui.zposLabel.setText("z position: " + str(format(self.handle_z.getPos(), '.3f')))

    def VON_OFFstate(self):
        if self.ui.VON_OFF.isChecked():
            self.ui.VON_OFF.setText('ON')

        else:
            self.ui.VON_OFF.setText('OFF')


    def GO(self):
        if self.ui.moveComboBox.currentText() == 'Rel':
            if self.ui.VON_OFF.isChecked():
                self.handle_x.mcRel(float(self.ui.xmoveDoubleSpinBox.text()), float(self.ui.VDoubleSpinBox.text()))
                self.handle_y.mcRel(float(self.ui.ymoveDoubleSpinBox.text()), float(self.ui.VDoubleSpinBox.text()))
                self.handle_z.mcRel(float(self.ui.zmoveDoubleSpinBox.text()), float(self.ui.VDoubleSpinBox.text()))

            else:
                self.handle_x.mRel(float(self.ui.xmoveDoubleSpinBox.text()))
                self.handle_y.mRel(float(self.ui.ymoveDoubleSpinBox.text()))
                self.handle_z.mRel(float(self.ui.zmoveDoubleSpinBox.text()))
        else:
            if self.ui.VON_OFF.isChecked():
                self.handle_x.mcAbs(float(self.ui.xmoveDoubleSpinBox.text()), float(self.ui.VDoubleSpinBox.text()))
                self.handle_y.mcAbs(float(self.ui.ymoveDoubleSpinBox.text()), float(self.ui.VDoubleSpinBox.text()))
                self.handle_z.mcAbs(float(self.ui.zmoveDoubleSpinBox.text()), float(self.ui.VDoubleSpinBox.text()))

            else:
                self.handle_x.mAbs(float(self.ui.xmoveDoubleSpinBox.text()))
                self.handle_y.mAbs(float(self.ui.ymoveDoubleSpinBox.text()))
                self.handle_z.mAbs(float(self.ui.zmoveDoubleSpinBox.text()))

    def Exit(self):
        self.timer.stop()
        self.handle_x.cleanUpAPT()
        self.handle_y.cleanUpAPT()
        self.handle_z.cleanUpAPT()
        self.mcl_handle.shutDown()

    def piezo_Abs(self,distance):
        self.mcl_handle.moveTo(3,distance)

    def piezo_Rel(self,distance=0.0):
        position=self.mcl_handle.getPosition(3)
        self.mcl_handle.moveTo(3,distance+position)
        #self.mcl_handle.moveTo(3, distance + position)
        #time.sleep(0.1)
        #small=position+distance-self.mcl_handle.getPosition(3)
        #self.mcl_handle.moveTo(3, small + self.mcl_handle.getPosition(3))

    def piezoinfo(self):
        self.ui.piezo_postext.setText("z_posi=" + str(format(self.mcl_handle.getPosition(3), '.3f')))


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = Stage({})
    sys.exit(app.exec_())