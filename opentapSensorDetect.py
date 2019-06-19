# -*- coding: utf-8 -*-
"""
Created on Fri Nov  2 15:31:43 2018

@author: djcruz
"""


from ctypes import *
import sys
import time

try:
	from Phidget22.PhidgetException import *
	from Phidget22.Devices import *
	from Phidget22.Devices.Manager import *
	from Phidget22.Phidget import *
	from Phidget22.Devices.VoltageRatioInput import *
except ModuleNotFoundError:
	print('ERROR: Phidgets Python module not found, Install Phidget22 Python module')
	exit(1)

#from phidgetClass import *
#for the gui
import curses
from curses import wrapper

#for csv files
import csv

voltageRatioDict = {'1102':[VoltageRatioSensorType.SENSOR_TYPE_1102, 'IR Reflective 5mm'],
                    '1103':[VoltageRatioSensorType.SENSOR_TYPE_1103, 'IR Reflective 10cm'],
                    '1104':[VoltageRatioSensorType.SENSOR_TYPE_1104, 'Vibration'],
                    '1111':[VoltageRatioSensorType.SENSOR_TYPE_1111, 'Motion'],
                    '1124':[VoltageRatioSensorType.SENSOR_TYPE_1124, 'Temperature']
                    }



class interfaceKit888:
    def __init__(self):
        self.channelList = [VoltageRatioInput(),VoltageRatioInput(),VoltageRatioInput(),VoltageRatioInput(),VoltageRatioInput(),VoltageRatioInput(),VoltageRatioInput(),VoltageRatioInput()]
        i = 0
        for i in range(len(self.channelList)):
            self.channelList[i].setChannel(i)
            i = i+1
            
        self.sensorOutput = [0,0,0,0,0,0,0,0]
        self.hasSensor = [False]*8 
        self.hasNewData = False
        self.channelLabel = [""]*8
            
    def setSerialNumber(self, serialNumber):
        for i in range(len(self.channelList)):
            self.channelList[i].setDeviceSerialNumber(serialNumber)
    
    def setOnAttachHandler(self, onAttachHandler):
        for i in range(len(self.channelList)):
            self.channelList[i].setOnAttachHandler(onAttachHandler)
    
    def setOnDetachHandler(self, onDetachHandler):
        for i in range(len(self.channelList)):
            self.channelList[i].setOnDetachHandler(onDetachHandler)
    
    def setOnErrorHandler(self, onErrorHandler):
        for i in range(len(self.channelList)):
            self.channelList[i].setOnErrorHandler(onErrorHandler)
    
    def setOnVoltageRatioChangeHandler(self, onVoltageRatioChangeHandler):
        for i in range(len(self.channelList)):
            self.channelList[i].setOnVoltageRatioChangeHandler(onVoltageRatioChangeHandler)
    
    def setOnSensorChangeHandler(self, onSensorChangeHandler):
        for i in range(len(self.channelList)):
            self.channelList[i].setOnSensorChangeHandler(onSensorChangeHandler)    
            
    def setSensorType(self, sensorEnum, index):
        self.channelList[index].setSensorType(sensorEnum)
    
    def setSensorOutput(self, voltageOutput, index):
        self.sensorOutput[index] = voltageOutput

    def setHasSensor(self, boolean,index):
        self.hasSensor[index] = boolean
    
    def setHasNewData(self, boolean):
        self.hasNewData = boolean
    
    def setChannelLabel(self, newName, index):
        self.channelLabel[index] = newName
    
    def getSerialNumber(self):
        return self.channelList[0].getDeviceSerialNumber()
    
    def getSensorType(self, index):
        return self.channelList[index].getSensorType()
    
    def getHasSensor(self, index):
        return self.hasSensor[index] 

    def getHasNewData(self):
        return self.hasNewData
    
    def getChannelData(self, index):
        return self.sensorOutput[index]
    
    def getChannelLabel(self, index):
        return self.channelLabel[index]
    
    def open(self):
       for i in range(len(self.channelList)):
            self.channelList[i].open() 
            while(not(self.channelList[i].getAttached())):
                pass
        
    def openWaitForAttachment(self, period):
       for i in range(len(self.channelList)):
            self.channelList[i].openWaitForAttachment(period)  
            
    def getAttached(self):
        if(self.channelList[0].getAttached() and self.channelList[1].getAttached() and self.channelList[2].getAttached() and self.channelList[3].getAttached() and self.channelList[4].getAttached() and self.channelList[5].getAttached() and self.channelList[6].getAttached() and self.channelList[7].getAttached()):
            return True
        else:
            return False
        #To be used with curses
    def printOutput(self, stdscrn):
        currentCursor= stdscrn.getyx()
        stdscrn.move(currentCursor[0],0)

        stdscrn.addstr("ChannelOutPut: for " + str(self.getSerialNumber()) + "\nPort 0 " + str(self.channelLabel[0]) + " : " + str(self.sensorOutput[0]) + "\nPort 1 " + str(self.channelLabel[1]) + " : " + str(self.sensorOutput[1]) + "\nPort 2 " + str(self.channelLabel[2]) + " : " + str(self.sensorOutput[2]) + "\nPort 3 " + str(self.channelLabel[3]) + " : " + str(self.sensorOutput[3]) + "\nPort 4 " + str(self.channelLabel[4]) + " : " + str(self.sensorOutput[4]) + "\nPort 5 " + str(self.channelLabel[5]) + " : " + str(self.sensorOutput[5]) + "\nPort 6 " + str(self.channelLabel[6]) + " : " + str(self.sensorOutput[6]) + "\nPort 7 " + str(self.channelLabel[7]) + " : " + str(self.sensorOutput[7]) + "\n")

    def printLabels(self):
        for i in range(8):
            print(str(self.channelLabel[i]), end = " ")
        print()
        
    def close(self):
        for i in range(len(self.channelList)):
            self.channelList[i].close()
                        
     
    #HANDELS FOR PHIDGETS
def onAttachHandler(self):
    
    ph = self
    try:
                
        """
        * Get device information and display it.
        """

        ph.setDataInterval(1000)

        ph.setVoltageRatioChangeTrigger(0.0)

        if(ph.getChannelSubclass() == ChannelSubclass.PHIDCHSUBCLASS_VOLTAGERATIOINPUT_SENSOR_PORT):
            ph.setSensorType(VoltageRatioSensorType.SENSOR_TYPE_VOLTAGERATIO)
        
        
    except PhidgetException as e:
        print("\nError in Attach Event:")
        DisplayError(e)
        traceback.print_exc()
        return


def onDetachHandler(self):

    ph = self

    try:
        
        """
        * Get device information and display it.
        """
        print("Phidget as detached.")
        channelClassName = ph.getChannelClassName()
        serialNumber = ph.getDeviceSerialNumber()
        channel = ph.getChannel()
        if(ph.getDeviceClass() == DeviceClass.PHIDCLASS_VINT):
            hubPort = ph.getHubPort()
        
    except PhidgetException as e:
        print("\nError in Detach Event:")
        DisplayError(e)
        traceback.print_exc()
        return



def onErrorHandler(self, errorCode, errorString):

    sys.stderr.write("[Phidget Error Event] -> " + errorString + " (" + str(errorCode) + ")\n")


def onVoltageRatioChangeHandler(self, voltageRatio):
    ph = self
    global interfaceList
    global sensorOutPut
    
    for i in range(len(interfaceList)):
        if(interfaceList[i].getSerialNumber() == ph.getDeviceSerialNumber()):
            if voltageRatio == 0.0:
                interfaceList[i].setSensorOutput("No input", ph.getChannel())
            else:
                interfaceList[i].setSensorOutput(voltageRatio, ph.getChannel())
                interfaceList[i].setHasSensor(True, ph.getChannel())

def onSensorChangeHandler(self, sensorValue, sensorUnit):
    ph = self
    

    
#END OF HANDELS FOR PHIDGETS



#HANDELS FOR MANAGER
def AttachHandler(self, channel):
    global connectedInterfaceSerialList
    
    newDevice = channel

    if(newDevice.getDeviceID() == DeviceID.PHIDID_1010_1013_1018_1019):
        if(not connectedInterfaceSerialList.count(newDevice.getDeviceSerialNumber())):
            print("new " + str(newDevice.getDeviceName()) + " has been attached.")
            print("Serial number: " + str(newDevice.getDeviceSerialNumber()))
            connectedInterfaceSerialList.append(newDevice.getDeviceSerialNumber())
    

def DetachHandler(self, channel):
    global connectedInterfaceSerialList
    detachedDevice = channel
    serialNumber = detachedDevice.getDeviceSerialNumber()
    deviceName = detachedDevice.getDeviceName()
    print("Goodbye Device " + str(deviceName) + ", Serial Number: " + str(serialNumber))
    print("You are Channel " + str(detachedDevice.getChannel()))
    detachedDevice.close()
    if(connectedInterfaceSerialList.count(detachedDevice.getDeviceSerialNumber())):
        connectedInterfaceSerialList.remove(detachedDevice.getDeviceSerialNumber())
    
    
def LocalErrorCatcher(e):
    print("Phidget Exception: " + str(e.code) + " - " + str(e.details) + ", Exiting...")
    exit(1)
    
#END OF HANDELS FOR MANAGER




   
#MAIN
connectedInterfaceSerialList = [] #list that will store all the serial list of interfaceKits 8/8/8 the manager will pick up.  See attach handler
try: manager = Manager()
except RuntimeError as e:
    print("Runtime Error " + e.details + ", Exiting...\n")
    exit(1)

try:
    manager.setOnAttachHandler(AttachHandler)
    manager.setOnDetachHandler(DetachHandler)
    #logging example, uncomment to generate a log file
    #print("Enable Logging")
    #Log.enable(LogLevel.PHIDGET_LOG_VERBOSE, "logManagerVerbose.txt")
    
except PhidgetException as e: LocalErrorCatcher(e)

print("Opening....")
print("This program is intended for use with 8/8/8 InterfaceKits only.\n")
try:
    manager.open()
except PhidgetException as e: LocalErrorCatcher(e)



print("Searching for connected 8/8/8 InterfaceKits.\n")
time.sleep(.5)



manager.close()
#Once all interfaceKits are attached, program will look through setting serials, opening, sensing ports with sensors,
#then looping again for all found interfaceKits.

if(len(connectedInterfaceSerialList) == 0):
    print("No devices detected. Please add interfaceKits before starting program. EXITING")
    exit(0)

interfaceList = [] #store all instances object interfaceKit 8/8/8
#add an instance for every serial value found when manager was open, do all the handlers.

for serial in connectedInterfaceSerialList:
    interface = interfaceKit888()
    interface.setSerialNumber(serial)
    print("setting Handlers for " + str(interface.getSerialNumber()))
    interface.setOnAttachHandler(onAttachHandler)
    interface.setOnDetachHandler(onDetachHandler)
    interface.setOnErrorHandler(onErrorHandler)
    interface.setOnVoltageRatioChangeHandler(onVoltageRatioChangeHandler)
    interface.setOnSensorChangeHandler(onSensorChangeHandler)
    interfaceList.append(interface)
    
    
#Create header for csv file.
with open('/etc/opentap/opentapSensorConf.csv', 'w') as csvfile:
    csv_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    csv_writer.writerow(["interface_serial_num", "sensor_port", "sensor_id", "sensor_type", "observation_pt_name"])
    
    
#These nested loops open all objects that have been created (will connect to the devices with serial numbers found from the manager)
#Then checks for which channel has data incoming from it. Prompt user for sensor type and a label.
#Save to a csv file.
for i in range(len(interfaceList)):   
    interfaceList[i].open()
    time.sleep(.5) # wait for connections.
    
    for j in range(8):
        if(interfaceList[i].getHasSensor(j)):
            print("Detected a sensor on channel: " + str(j) + " of interfaceKit " + str(interfaceList[i].getSerialNumber()))
            
            sensorTypeInput = None
            while(not(sensorTypeInput in voltageRatioDict)): #check if sensor exists in enum.
                print("Enter P/N written on sensor: ")
                sensorTypeInput = input()
            interfaceList[i].setSensorType(voltageRatioDict[str(sensorTypeInput)][0], j)
            print("Enter an observation point label for the " + str(voltageRatioDict[str(sensorTypeInput)][1]) + " sensor:")
            inputName = input()
            interfaceList[i].setChannelLabel(inputName, j)
            
            with open('/etc/opentap/opentapSensorConf.csv' , 'a') as csvfile:
                csv_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                csv_writer.writerow([str(interfaceList[i].getSerialNumber()),str(j), str(sensorTypeInput), voltageRatioDict[str(sensorTypeInput)][1], str(inputName)])
            
print("Infomation saved to a csv file")



    

#closing Device Channel
for interface in interfaceList:
    interface.close()



#Closing program
try:
    for interface in interfaceList:
        if(interface.getAttached):
            interface.close()
            while(interface.getAttached()):
                pass
    #Log.disable()
except PhidgetException as e: LocalErrorCatcher(e)

exit(0)
