"""
OpenTap Demonstration

OpenTap Demonstration script

Author:  Christian Macias and Michael P. McGarry
Version: 0.1
Date:    February 15, 2018

"""

import pandas as pd
import matplotlib.pyplot as plt
import opentap
import time

# Start capture tasks
start = int(time.time() + 10)   # start now (UTC)
stop = int(start + 600)        # stop in 10 minutes
virgoInCaptureID = opentap.capture('netflow', start, stop, observationPt = 'in', location = opentap.VIRGO)

start = int(time.time() + 10)   # start now (UTC)
stop = int(start + 600)        # stop in 10 minutes
virgoOutCaptureID = opentap.capture('netflow', start, stop, observationPt = 'out', location = opentap.VIRGO)


# Retrieve data
virgoInData = opentap.retrieve('netflow', virgoInCaptureID, location = opentap.VIRGO)
virgoOutData = opentap.retrieve('netflow', virgoOutCaptureID, location = opentap.VIRGO)

#
# Add application classification data
#
virgoInData = opentap.netflowAddApplication(virgoInData)
virgoOutData = opentap.netflowAddApplication(virgoOutData)


def plotAppDistribution(data):
    apps = data.app.unique()
    apps = apps[pd.notnull(apps)]
    apps = np.sort(apps)
    appByteCount = {}
    totalBytes = 0
    for app in apps:
        appByteCount[app] = data[data['app'] == app]['dOctets'].sum()
        totalBytes = totalBytes + appByteCount[app]
    appDistr = {}
    for app in apps:
        appDistr[app] = float(data[data['app'] == app]['dOctets'].sum() / totalBytes)
    plt.bar(range(len(appDistr)), appDistr.values(), align='center')
    plt.xticks(range(len(appDistr)), appDistr.keys())
    plt.show()

plotAppDistribution(virgoInData)
plotAppDistribution(virgoOutData)

