#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenTap Web Server (Flask version)

Created on Mon Jun 10 14:53:55 2019

@author: mmcgarry
"""

from flask import Flask, request, Response
import os
import subprocess
import glob
import json
import time
import random
import ethernet

# Hardcoded path for storing data collected by OpenTap
csvpath = '/opt/opentap/log/'

app = Flask(__name__)

@app.route("/capabilities")
def capabilities():
	capabilitiesDict = {}
	netObservationPts = []
	sensorObservationPts = []
	capabilitiesDict['capture_types'] = [ 'ethernet', 'netflow', 'sensor' ]
	# Open opentap.conf and read variables to report in capabilities dictionary
	try:
		f = open("/etc/opentap/opentap.conf")
	except:
		return json.dumps(capabilitiesDict), 200, {'Content-Type': 'application/json'}

	for line in f:
		if "retention" in line:
			capabilitiesDict['retention'] = (line.split())[1]
		elif "alias:" in line:
			netObservationPts.append(line.split()[2])
	capabilitiesDict['network_observation_pts'] = netObservationPts
	
	# Open Phidgets sensor configuration (CSV) to read observation point names
	try:
		f = open("/etc/opentap/opentapSensorConf.csv")
	except:
		return json.dumps(capabilitiesDict), 200, {'Content-Type': 'application/json'}

	for line in f:
		if "interface_serial_num" not in line:
			sensorObservationPts.append(line.split(',')[4].strip('\n'))
	capabilitiesDict['sensor_observation_pts'] = sensorObservationPts

	return json.dumps(capabilitiesDict), 200, {'Content-Type': 'application/json'}


@app.route("/capture/ethernet")
def captureEthernet():
    # obtain arguments
	captureID     = request.args.get('id')
	startTime     = request.args.get('start')
	stopTime      = request.args.get('stop')
	observationPt = request.args.get('observationPt')
	period        = request.args.get('period')
	changedStart = 0

	# if no observationPt specified, use the default from opentap.conf
	if(observationPt == None):
		try:
			f = open("/etc/opentap/opentap.conf")
		except:
			observationPt = None

		for line in f:
			if "default-network-observationpt" in line:
				observationPt = (line.split())[1]
	else:
		# if an observationPt was specified, check the aliases in opentap.conf for the OS identifier
		try:
			f = open("/etc/opentap/opentap.conf")
		except:
			observationPt = None
			print("opentap.conf: Unable to open file for reading")
		for line in f:
			if "alias:" in line:
				words = line.split()
				for word in words:
					if(word == str(observationPt)): #check if the alias is in this line
						observationPt = words[1]
						break #Found the alias we were looking for
    
	# if no sampling period was specified, use the default of 1000 msec (i.e., 1 sec)
	if(period == None):
		period = 1000

	# validate start and stop times
	changedStart = 0
	if ((startTime != None) & (stopTime != None)):
		if(int(startTime) < int(time.time())):
			startTime=time.time()
			changedStart = 1	
		if(int(startTime) > int(stopTime)):
			# Return an error response to the client
			if changedStart == 0:
				return json.dumps({"status": "error", "msg": "Start time is later than stop time."}), 200, {'Content-Type': 'application/json'}
			else:
				return json.dumps({"status": "error", "msg": "Stop time is earlier than current time."}), 200, {'Content-Type': 'application/json'}

		# if no id specified by the user, select a random number
		if(captureID == None):   
			captureID=random.randint(1, 100000000)

		# check that user specified id does not conflict with any existing data objects
		os.chdir(csvpath)
		while(os.path.isfile(str(captureID)+".csv")):
			# if so, use a random number
			captureID=random.randint(1, 100000000)

		print("Launching Ethernet data collection task")
		#fork to reply to the web request and allow the data collection to continue working
		pid=os.fork()
		if(pid == 0):
			#
			# Data capture code start
			#
			file=open(csvpath+str(captureID)+".csv", "w+")
			if((int(startTime)-int(time.time())) > 0 ):
				time.sleep(int(startTime)-int(time.time()))

			data=ethernet.linkstat(observationPt)
			if(data==None):
				return None
			file.write("time,state,rx_bytes,rx_packets,rx_errors,"\
						"rx_dropped,rx_overrun,rx_mcast,"\
						"tx_bytes,tx_packets,tx_errors,tx_dropped,"\
						"tx_carrier,tx_collision\n")

			while(int(time.time()) < int(stopTime)):
				data=ethernet.linkstat(observationPt)
				file.write(str(int(time.time() * 1000)) + ",")
				file.write(str(data["state"]) + ",")
				file.write(data["rx_bytes"] + ",")
				file.write(data["rx_packets"] + ",")
				file.write(data["rx_errors"] + ",")
				file.write(data["rx_dropped"] + ",")
				file.write(data["rx_overrun"] + ",")
				file.write(data["rx_memset"] + ",")

				file.write(data["tx_bytes"] + ",")
				file.write(data["tx_packets"] + ",")
				file.write(data["tx_errors"] + ",")
				file.write(data["tx_dropped"] + ",")
				file.write(data["tx_carrier"] + ",")
				file.write(data["tx_collision"])
				file.write("\n")

				file.flush();

				time.sleep(float(int(period)/1000))

			file.close()
			return
			#
			# Data capture code stop
			#

		else:
			#
			# Return a success response to the client (JSON)
			#
			if(changedStart == 1):
				procStarted={"status": "success", "msg": "Changed startTime to now because it was in the past.", \
							"id" : captureID, "startTime": int(startTime), "stopTime": stopTime, \
							"duration" : (int(stopTime) - int(startTime))
							}
			else:
				procStarted={"status": "success", "msg": "", \
							"id" : captureID, "startTime": startTime, "stopTime": stopTime, \
							"duration" : (int(stopTime) - int(startTime))}
			return json.dumps(procStarted), 200, {'Content-Type': 'application/json'}


#
# Capture NetFlow API
#
@app.route("/capture/netflow")
def captureNetflow():
	# obtain arguments
	captureID     = request.args.get('id')
	startTime     = request.args.get('start')
	stopTime      = request.args.get('stop')
	observationPt = request.args.get('observationPt')
	changedStart = 0

	# if no observationPt specified, use the default from opentap.conf
	if(observationPt == None):
		try:
			f = open("/etc/opentap/opentap.conf")
		except:
			observationPt = None

		for line in f:
			if "default-network-observationpt" in line:
				observationPt = (line.split())[1]
	else:
		# if an observationPt was specified, check the aliases in opentap.conf for the OS identifier
		try:
			f = open("/etc/opentap/opentap.conf")
		except:
			observationPt = None
			print("opentap.conf: Unable to open file for reading")
		for line in f:
			if "alias:" in line:
				words = line.split()
				for word in words:
					if(word == str(observationPt)): #check if the alias is in this line
						observationPt = words[1]
						break #Found the alias we were looking for
    
	# validate start and stop times
	changedStart = 0
	if ((startTime != None) & (stopTime != None)):
		if(int(startTime) < int(time.time())):
			startTime=time.time()
			changedStart = 1	
		if(int(startTime) > int(stopTime)):
			# Return an error response to the client
			if changedStart == 0:
				return json.dumps({"status": "error", "msg": "Start time is later than stop time."}), 200, {'Content-Type': 'application/json'}
			else:
				return json.dumps({"status": "error", "msg": "Stop time is earlier than current time."}), 200, {'Content-Type': 'application/json'}

		# if no id specified by the user, select a random number
		if(captureID == None):   
			captureID=random.randint(1, 100000000)

		# check that user specified id does not conflict with any existing data objects
		os.chdir(csvpath)
		while(os.path.isfile(str(captureID)+".csv")):
			# if so, use a random number
			captureID=random.randint(1, 100000000)

		print("Launching NetFlow data collection task")
		pid=os.fork()
		if(pid == 0):
			os.close(1) #close stdout and stderr
			os.close(2) 
			subprocess.Popen(["sudo", "/opt/opentap/dependencies/netflowcap", str(int(stopTime) - int(startTime)), str(captureID), str(int(startTime) - int(time.time())), str(observationPt)],\
							stdout=None, \
							stderr=None, \
							stdin=None)
			exit()
        	#
        	# Data capture code stop
        	#
		else:
			#
			# Return a success response to the client (JSON)
			#
			if(changedStart == 1):
				procStarted={"status": "success", "msg": "Changed startTime to now because it was in the past.", \
							"id" : captureID, "startTime": int(startTime), "stopTime": stopTime, \
							"duration" : (int(stopTime) - int(startTime))
							}
			else:
				procStarted={"status": "success", "msg": "", \
							"id" : captureID, "startTime": startTime, "stopTime": stopTime, \
							"duration" : (int(stopTime) - int(startTime))}
			return json.dumps(procStarted), 200, {'Content-Type': 'application/json'}


#
# Retrieve API, just dumps the CSV file from the correct directory to the client
#
@app.route("/retrieve")
def retrieve():
    captureID = request.args.get('id')
    try:
    	# Retrieve CSV file contents
    	csvcontents=open(csvpath+captureID+'.csv').read()
    except:
    	# On failure, return error message to client
    	return json.dumps({'status': 'error', 'msg': 'data file not found; may not be ready yet.'}), 200, {'Content-Type': 'application/json'}
    else:
    	return csvcontents, 200, {'Content-Type': 'text/csv'}

#
# Read opentap.conf to get server address data
#
try:
	f = open("/etc/opentap/opentap.conf")
except:
	serverIP = '127.0.0.1'
	serverPort = 2020
	print("opentap.conf: Unable to open file for reading")

for line in f:
	if "websrv-addr" in line:
		serverIP = (line.split())[1].split(':')[0]
		serverPort = int((line.split())[1].split(':')[1])

#
# Start OpenTap Flask webserver at specified server address
#
if __name__ == '__main__':
	app.run(host=serverIP, port=serverPort, debug=True)
