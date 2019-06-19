# -*- coding: utf-8 -*-
"""
Created on Fri Nov  2 15:31:43 2018

@author: djcruz
"""
from ctypes import *
import sys
import time
import errno

from Phidget22.PhidgetException import *
from Phidget22.Devices import *
from Phidget22.Devices.Manager import *
from Phidget22.Phidget import *
from Phidget22.Devices.VoltageRatioInput import *
from enum import Enum
import fcntl # used for file locking.
#from phidgetClass import *

#for csv files
import pandas as pd

# Path for OpenTap data storage
csvpath = '/opt/opentap/log/'

# Dictionary of recognized Phidgets sensors
voltageRatioDict = {'1102':[VoltageRatioSensorType.SENSOR_TYPE_1102, 'IR reflective 5mm'],
					'1103':[VoltageRatioSensorType.SENSOR_TYPE_1103, 'IR reflective 10cm'],
					'1104':[VoltageRatioSensorType.SENSOR_TYPE_1104, 'vibration'],
					'1111':[VoltageRatioSensorType.SENSOR_TYPE_1111, 'motion'],
					'1124':[VoltageRatioSensorType.SENSOR_TYPE_1124, 'temperature']
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


#HANDLER FOR PHIDGETS
def onAttachHandler(self):
	ph = self
	try:            
		"""
		* Get device information and display it.
		"""
		ph.setDataInterval(ph.getMinDataInterval()+1)
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
		print("Phidget has detached.")
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
	pass
	#Left empty set has a handler but should be unused.


interfaceList = []    
def onSensorChangeHandler(self, sensorValue, sensorUnit):
	ph = self

	global interfaceList
	global sensorOutPut

	for i in range(len(interfaceList)):
		if(interfaceList[i].getSerialNumber() == ph.getDeviceSerialNumber()):
			interfaceList[i].setSensorOutput(sensorValue, ph.getChannel())
			interfaceList[i].setHasNewData(True)


#MAIN---------------------------------------------------------------------------------
class phidgetSensor:

	def __init__(self):
		self.dataList = []
		self.sampleRate = None
		self.gatherData = None
		self.countSamples = None
		self.startTime = None
		self.pollingSensor = None
		self.csv_data = None
        
	def authenticateSensorLabel(self,sensorLabel):    
		for i in range(len(self.csv_data)):
			if(sensorLabel == self.csv_data["observation_pt_name"][i]):
				return True

		return False


    #polling function.
	def pollData(self):
		global interfaceList        

		data = [int(time.time()*1000)]	# add UNIX Epoch time timestamp (in milliseconds)
		for interfaceKit in interfaceList:
			if(interfaceKit.getHasNewData()):
				for index in range(8):
					if(interfaceKit.getChannelLabel(index) == self.pollingSensor):
						data.append(interfaceKit.getChannelData(index))

		self.dataList.append(data)
		self.countSamples = self.countSamples + 1
		return data


	def initSensor(self, sid):
		global interfaceList #store all instances object interfaceKit 8/8/8

		self.pollingSensor = sid        

		#when iterating csv file, insures all ports with the same serial number are put in the same 8/8/8 class.
		serialCreated = False

		try:
			self.csv_data = pd.read_csv('/etc/opentap/opentapSensorConf.csv')

			if(not self.authenticateSensorLabel(self.pollingSensor) ):
				return False

			line_count = 0
			for i in range(len(self.csv_data)):
				if(line_count == 0):
					line_count += 1
				line_count += 1

				#Get the index in which the 8/8/8 object has the same serial number as port in the csv
				interfaceIndex = 0
				for interfaceKit in interfaceList:
					if(interfaceKit.getSerialNumber() == int(self.csv_data["interface_serial_num"][i])):
						serialCreated = True
						break
					else:
						serialCreated = False
					interfaceIndex += 1

				#if the object already exits, set the sensor type to the port and the user made label for the port.
				if(serialCreated):
					interfaceList[interfaceIndex].setSensorType(voltageRatioDict[str(self.csv_data["sensor_id"][i])][0], int(self.csv_data["sensor_port"][i]))
					interfaceList[interfaceIndex].setChannelLabel(self.csv_data["observation_pt_name"][i], int(self.csv_data["sensor_port"][i]))
				#if the incoming port is from a new interfacekit device, then create a new object and apply the handlers.
				else: 
					interface = interfaceKit888()
					interface.setSerialNumber(int(self.csv_data["interface_serial_num"][i]))
					interface.setOnAttachHandler(onAttachHandler)
					interface.setOnDetachHandler(onDetachHandler)
					interface.setOnErrorHandler(onErrorHandler)
					interface.setOnVoltageRatioChangeHandler(onVoltageRatioChangeHandler)
					interface.setOnSensorChangeHandler(onSensorChangeHandler)
					interface.setHasSensor(True,int(self.csv_data["sensor_port"][i]))
					interface.open()
					time.sleep(.5) # wait for connections.
					interface.setSensorType(voltageRatioDict[str(self.csv_data["sensor_id"][i])][0], int(self.csv_data["sensor_port"][i]))
					interface.setChannelLabel(self.csv_data["observation_pt_name"][i], int(self.csv_data["sensor_port"][i]))
					interfaceList.append(interface)

			return True       		         

		except IOError as e:
			print("Error: sensor configuration file (opentapSensorConf.csv) not found.")
			exit(0)

		#if csv file exists but is somehow empty.
		if(line_count == 0):
			print("Error: sensor configuration file (opentapSensorConf.csv) is empty.")
			exit(0)


	def start(self, pollDuration, passSampleRate, fileID):
		global interfaceList		
		#	while(not(authenticateSensorLabel(pollingSensor))):
		self.sampleRate = float(passSampleRate)/1000

		file = open(csvpath + str(fileID) + '.csv', 'w+')

		#will hold the entire 2D list of samples.  Will be converted to a pandas datafram after polling.
		#dataframe header
		header = ['time']

		#add the rest of the column headers from the csv file.  converted to the human readable representation of the sensors.
		for i in range(len(self.csv_data)):
			if(self.csv_data["observation_pt_name"][i] == self.pollingSensor):
				header.append(voltageRatioDict[str(self.csv_data["sensor_id"][i])][1])

		fcntl.flock(file, fcntl.LOCK_EX | fcntl.LOCK_NB) #Lock file until finished writing.
		file.write(','.join(map(str,header)) + '\n')
		fcntl.flock(file, fcntl.LOCK_UN)   
    
		#Program takes precedence of correct sample amount over actual polling time.  For the most cases both correlate (slowdown occurs sub 3 ms polling rate.)
		self.countSamples = 0
		totalSamples = int(pollDuration)/self.sampleRate #calculate the expected amount of samples the program should end it.
        
        #first data sample.
		self.startTime = time.time()

		timeTrigger = self.sampleRate * self.countSamples
		time.sleep(1)

		sampleHold = []               #holds samples if lock cannot be acquired.

		print("Starting Phidgets sensor collection for " + self.pollingSensor)
		while(self.countSamples < totalSamples):
			if(time.time() - self.startTime >= timeTrigger):     #elected to multiply sample rate with amount of samples over 
				output = self.pollData()                                  #resetting the timer as continous calls to the timer is slower than this method.         		  
				try: 
					fcntl.flock(file, fcntl.LOCK_EX | fcntl.LOCK_NB) #Lock file until finished writing.
					sampleHold.append(output)
					for output in sampleHold: 
						file.write(','.join(map(str,output))+'\n')
					file.flush()
					fcntl.flock(file, fcntl.LOCK_UN)
					sampleHold.clear()
					timeTrigger = self.sampleRate * self.countSamples     # This method is probably more computationally intensive but elected for higher timing precisio
				except IOError as e:
					print("Phidgets sensor error")
					if e.errno != errno.EAGAIN: #if error is not relating to securing the log
						raise
					else:                                 #increment counter and wait for 100 milliseconds.  give up after 1 second (10 tries) of attempting
						sampleHold.append(output)

		#for debugging purposes, uncomment along with related print statement to see how long each polling session actually took.
		endTime = time.time()

        #closing Device Channel
		try:
			for interface in interfaceList:
				if(interface.getAttached):
					interface.close()
				while(interface.getAttached()):
					pass
			#Log.disable()
		except PhidgetException as e: LocalErrorCatcher(e)

		file.close()
		exit(0)
