import ctypes
import sys
import os.path

NO_USBDAQ = -1
DevIndex_Overflow = -2
Bad_Firmware = -3
USBDAQ_Closed = -4
Transfer_Data_Fail = -5
NO_Enough_Memory = -6
Time_Out = -7
Not_Reading = -8

class SmacqException(Exception):
    def __init__(self, err = 'SmacqException'):
        Exception.__init__(self, err)

class NoUSBDAQ(SmacqException):
    def __init__(self, err = 'NO_USBDAQ'):
        SmacqException.__init__(self, err)

class DevIndexOverflow(SmacqException):
    def __init__(self, err = 'DevIndex_Overflow'):
        SmacqException.__init__(self, err)

class BadFirmware(SmacqException):
    def __init__(self, err = 'Bad_Firmware'):
        SmacqException.__init__(self, err)

class USBDAQClosed(SmacqException):
    def __init__(self, err = 'USBDAQ_Closed'):
        SmacqException.__init__(self, err)

class TransferDataFail(SmacqException):
    def __init__(self, err = 'Transfer_Data_Fail'):
        SmacqException.__init__(self, err)

class NOEnoughMemory(SmacqException):
    def __init__(self, err = 'NO_Enough_Memory'):
        SmacqException.__init__(self, err)

class TimeOut(SmacqException):
    def __init__(self, err = 'Time_Out'):
        SmacqException.__init__(self, err)

class NotReading(SmacqException):
    def __init__(self, err = 'Not_Reading'):
        SmacqException.__init__(self, err)


def SmacqCustomizeRaise( error_code ):
    if error_code == NO_USBDAQ:
        raise NoUSBDAQ()
    elif error_code == DevIndex_Overflow:
        raise DevIndexOverflow()
    elif error_code == Bad_Firmware:
        raise BadFirmware()
    elif error_code == USBDAQ_Closed:
        raise USBDAQClosed()
    elif error_code == Transfer_Data_Fail:
        raise TransferDataFail()
    elif error_code == NO_Enough_Memory:
        raise NOEnoughMemory()
    elif error_code == Time_Out:
        raise TimeOut()
    elif error_code == Not_Reading:
        raise NotReading()
    else:
        print("processing......")


""" if __name__ == '__main__':
    for num in range(-8, 0):
        try:
            SmacqCustomizeRaise( num )
        except SmacqException as e:
            print( e )
        else:
            print("processing...")
 """
class SmacqController:

    def __init__(self) -> None:
        self.dllName = "gusb.dll"
        self.dllABSPath = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + self.dllName
        try:
            self.lib = ctypes.cdll.LoadLibrary(self.dllABSPath)
        except FileNotFoundError:
            print("dll not found!")
            sys.exit(1)

        # init work
        self.DevIndex = 0
        self.Range = 10
        self.SampleRate = 1000
        self.TrigSource = 0
        self.Trig = 1

        self.DioChanSel = 255

        self.ResetVolt = 0
        self.ResetDioOut = 0
        self.ResetTrig = 0

        try:
            SmacqCustomizeRaise(
                self.lib.OpenDevice(
                    ctypes.c_int(self.DevIndex)))

            SmacqCustomizeRaise(
                self.lib.SetUSB2AiRange(
                    ctypes.c_int(self.DevIndex),
                    ctypes.c_float(self.Range)))

            SmacqCustomizeRaise(
                self.lib.SetSampleRate(
                    ctypes.c_int(self.DevIndex), 
                    ctypes.c_uint(self.SampleRate)))

            SmacqCustomizeRaise(
                self.lib.SetTrigSource(
                    ctypes.c_int(self.DevIndex), 
                    ctypes.c_ubyte(self.TrigSource)))

            SmacqCustomizeRaise(
                self.lib.SetSoftTrig(
                    ctypes.c_int(self.DevIndex), 
                    ctypes.c_ubyte(self.Trig)))

            SmacqCustomizeRaise(
                self.lib.InitDA(
                    ctypes.c_int(self.DevIndex)))

        except SmacqException as e:
            print(e)
            sys.exit(1)
        else:
            print("device init successfully!")

    def select_pressure_channel(self, DANum, DAVolt)->None:
        # select work
        # DANum = 0 # High_Pressure = 0 #
        # DAVolt = 15 # 0 to 15
        # DANum = 1 # High_Minus_Pressure = 1 
        # DAvolt = -5 # Range[-5, 0]
        # DANum = 2 # Low_Pressure = 2 
        # # Range[0, 2]
        # DANum = 3 # Low_Minus_Pressure = 3 # Range[-2.2, 0]
        # DANum = 4 # Atomsphere = 4 # do nothing

        self.DANum = DANum
        self.DAVolt = DAVolt

        if DANum == 0 and (DAVolt >= 0 and DAVolt <= 15):
            print("High Pressure: ", DAVolt)
            DAVolt = DAVolt / 3
        elif DANum == 1 and ( DAVolt <= 0 and DAVolt >=-5 ):
            print("High Minus Pressure: ", DAVolt)
            DAVolt = DAVolt / -1.004
        elif DANum == 2 and ( DAVolt <= 2 and DAVolt >= 0 ):
            print("Low Pressure: ", DAVolt)
            DAVolt = DAVolt * 2.564
        elif DANum == 3 and ( DAVolt <= 0 and DAVolt >=-2.2 ):
            print("Low Minus Pressure: ", DAVolt)
            DAVolt = DAVolt * -2.294
        elif DAVolt == 4:
            print("Atomsphere")
            return
        else:
            print("Invalid pressure path input!")
            return
        
        try:
            SmacqCustomizeRaise(
                self.lib.SetDA(
                    ctypes.c_int(self.DevIndex),
                    ctypes.c_ubyte(DANum),
                    ctypes.c_float(DAVolt)))
        except SmacqException as e:
            print(e, " when set DA")
            os.exit(1)

    def start_read_pressure(self) -> None:
        try:
            SmacqCustomizeRaise(
                self.lib.StartRead(
                    ctypes.c_int(self.DevIndex)))
        except SmacqException as e:
            print(e, " when start read")
            os.exit(1)

    def set_pressure_channel(self):
        # DioOut = 96 # 01100000
        # High_Pressure_Dio_Out = 96       # 01100000
        # High_Minus_Pressure_Dio_Out = 72 # 01001000
        # Low_Pressure_Dio_Out = 16        # 00010000
        # Low_Minus_Pressure_Dio_Out = 4   # 00000100
        
        if self.DANum == 0:
            self.DioOut = 96
            self.ChSel = 1
        elif self.DANum == 1:
            self.DioOut = 72
            self.ChSel = 2
        elif self.DANum == 2:
            self.DioOut = 16
            self.ChSel = 4
        elif self.DANum == 3:
            self.DioOut = 4
            self.ChSel = 8
        else:
            print("Invalid input(set pressure channel)")
        
        try:
            SmacqCustomizeRaise(
                self.lib.SetDioOut(
                    ctypes.c_int(self.DevIndex), 
                    ctypes.c_uint(self.DioChanSel),
                    ctypes.c_uint(self.DioOut)))
        except SmacqException as e:
            print(e, " when set pressure channel")
            os.exit(1)


    def read_data(self) -> float:    
        Num = 1
        # self.ChSel = 1
        data = ctypes.c_float
        Ai = data()
        TimeOut = 4000

        try:
            SmacqCustomizeRaise(
                self.lib.GetAiChans(
                    ctypes.c_int(self.DevIndex),
                    ctypes.c_ulong(Num), 
                    ctypes.c_short(self.ChSel), 
                    Ai, 
                    ctypes.c_long(TimeOut)))
        except SmacqException as e:
            print(e, " when read data")
            os.exit(1)

        return Ai[0]


    def stop_process(self) -> None:
        
        try:
            SmacqCustomizeRaise(
                self.lib.SetDA(
                    ctypes.c_int(self.DevIndex),
                    ctypes.c_ubyte(self.DANum),
                    ctypes.c_float(self.ResetVolt)))

            SmacqCustomizeRaise(
                self.lib.SetDioOut(
                    ctypes.c_int(self.DevIndex), 
                    ctypes.c_uint(self.DioChanSel),
                    ctypes.c_uint(self.ResetDioOut)))

            SmacqCustomizeRaise(
                self.lib.StopRead(
                    ctypes.c_int(self.DevIndex)))

            SmacqCustomizeRaise(
                self.lib.SetSoftTrig(
                    ctypes.c_int(self.DevIndex),
                    ctypes.c_ubyte(self.ResetTrig)))

            SmacqCustomizeRaise(
                self.lib.ClearTrigger(
                    ctypes.c_int(self.DevIndex)))

            SmacqCustomizeRaise(
                self.lib.ClearBufs(
                    ctypes.c_int(self.DevIndex)))

        except SmacqException as e:
            print(e, " when stop precess")
            self.lib.CloseDevice(ctypes.c_int(self.DevIndex))

        self.lib.CloseDevice(ctypes.c_int(self.DevIndex))   

if __name__ == '__main__':
    data = []
    testcase = SmacqController()
    testcase.select_pressure_channel(0, 15)
    testcase.start_read_pressure()
    testcase.set_pressure_channel()
    while 1:
        data.append(testcase.read_data())
    testcase.stop_process()


