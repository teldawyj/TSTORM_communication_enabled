from PyDAQmx import Task
import module
from PyQt5 import QtWidgets
import shutterUI as ui

class Shutter(module.Module):
    def __init__(self,message):
        super().__init__(message)
        self.message=message
        self.gui=ui.shutterGui()
        self.gui.setupUI()
        self.gui.button_state.clicked.connect(lambda: self.shutter())
        self.gui.button_I.clicked.connect(lambda: self.intensity())

    def shutter(self):
        task = Task()
        task.CreateDOChan("/Dev1/port1/line0", "", DAQmx_Val_ChanForAllLines)
        task.StartTask()
        if self.gui.button_state.isChecked():
            self.gui.button_atate.setText('ON')
            task.WriteDigitalScalarU32(1, 10.0, 1, None)
            task.StopTask()
        else:
            self.gui.button_state.setText('OFF')
            task.WriteDigitalScalarU32(1, 10.0, 0, None)
            task.StopTask()

    def intensity(self):
        task = Task()
        task.CreateAOVoltageChan("/Dev1/ao1", "", minVal=0, maxVal=2, units=DAQmx_Val_Volts,
                                 customScaleName=None)
        task.StartTask()
        task.WriteAnalogScalarF64(1, 10.0, float((self.textbox.text())), reserved=None)
        task.StopTask()

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Shutter({})
    sys.exit(app.exec_())