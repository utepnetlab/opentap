"""
OpenTap Demonstration

OpenTap Demonstration script

Author:  Christian Macias and Michael P. McGarry
Version: 0.1
Date:    February 15, 2018

"""

import pandas as pd
#import matplotlib.pyplot as plt
import opentap
import time

#
# This demonstration script, starts a NetFlow capture on your OpenTap device for 10 minutes and then collects the data
# and plots the detected application distribution
#

#
# ATTENTION!: Update this device location dictionary and observation point name appropriate for you device
#
myOpenTapDevice = { 'name': 'local', 'ipaddr': '127.0.0.1', 'portnum': '2020' }
observationPointName = 'net'

# Start capture tasks
print("Initiating a 1 minute NetFlow capture from the " + observationPointName + " network observation point")
start = int(time.time() + 10)   # start now (UTC)
stop = int(start + 60)        	# stop in 1 minute
captureID = opentap.capture('netflow', start, stop, observationPt = observationPointName, location = myOpenTapDevice)

print("Waiting for the NetFlow capture to complete...", end='', flush=True)
time.sleep(70)
print("done.")

# Retrieve data
netflowData = opentap.retrieve('netflow', captureID, location = myOpenTapDevice)

# See the structure of the NetFlow data frame
print("Here is the structure of the NetFlow PANDAS dataframe")
netflowData.info()

# Print the first row
print("Here is the first flow record")
print(netflowData.iloc[0])

#
# Add application classification data
#
#netflowData = opentap.netflowAddApplication(netflowData)
#
#
#def plotAppDistribution(data):
#    apps = data.app.unique()
#    apps = apps[pd.notnull(apps)]
#    apps = np.sort(apps)
#    appByteCount = {}
#    totalBytes = 0
#    for app in apps:
#        appByteCount[app] = data[data['app'] == app]['dOctets'].sum()
#        totalBytes = totalBytes + appByteCount[app]
#    appDistr = {}
#    for app in apps:
#        appDistr[app] = float(data[data['app'] == app]['dOctets'].sum() / totalBytes)
#    plt.bar(range(len(appDistr)), appDistr.values(), align='center')
#    plt.xticks(range(len(appDistr)), appDistr.keys())
#    plt.show()
#
#plotAppDistribution(netflowData)

