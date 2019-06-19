#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Authors: Christian Macias

Description: Python script that implements the "capture" OpenTap invocation for the 
             Ethernet data type
"""

import subprocess

def linkstat(iface):
    """
    Description: Returns a dictionary of network link statistics

    Parameters:
    - iface: interface name

    Notes:
    * If the interface does not exist or is None, the function will return None.
    * The dictionary contains the following information. rx_bytes, rx_packets,
      rx_errors, rx_dropped, rx_overrun, rx_memset, tx_bytes, tx_packets,
      tx_errors, tx_dropped, tx_carrier, tx_collision, state.
    """

    linkStatistics = {}

    output = subprocess.check_output(["/sbin/ip", "-s", "link"]).decode('UTF-8')
    output = output.split('\n')
    del      output[-1] #remove extra blank line at the end

    ifaceCount = int(len(output)/6)

    #Check which interface we need
    counter       = 0
    while(counter < ((ifaceCount * 6) - 1)): #every interface has 6 items to filter through
        interfaceName = ((output[counter].split(':'))[1]).strip()
        if(interfaceName == iface):
            #found the interface!
            rx_info = output[counter+3].split()
            tx_info = output[counter+5].split()
            linkDiscription=(output[counter].split())[2]
            linkDiscription=(linkDiscription.replace("<","")).replace(">","")
            linkDiscription=linkDiscription.split(",")

            linkStatistics["rx_bytes"]   = rx_info[0]
            linkStatistics["rx_packets"] = rx_info[1]
            linkStatistics["rx_errors"]  = rx_info[2]
            linkStatistics["rx_dropped"] = rx_info[3]
            linkStatistics["rx_overrun"] = rx_info[4]
            linkStatistics["rx_memset"]  = rx_info[5]

            linkStatistics["tx_bytes"]      = tx_info[0]
            linkStatistics["tx_packets"]    = tx_info[1]
            linkStatistics["tx_errors"]     = tx_info[2]
            linkStatistics["tx_dropped"]    = tx_info[3]
            linkStatistics["tx_carrier"]    = tx_info[4]
            linkStatistics["tx_collision"]  = tx_info[5]

            linkStatistics["state"] = "0"
            for linkDisc in linkDiscription:
                if(linkDisc == "UP"):
                    linkStatistics["state"] = "1"
            return linkStatistics
        else:
            #Didn't find the interface yet...
            counter = counter + 6
    return None #Didn't find the interface at all
