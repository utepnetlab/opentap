from Phidget22.Devices.VoltageInput import *
from Phidget22.PhidgetException import *
from Phidget22.Phidget import *
from Phidget22.Net import *

class temperature:

    temp=0.0

    try:
        ch = VoltageInput()
    except RuntimeError as e:
        raise e
        
    def VoltageInputAttached(self, e):
        try:
            attached = e
            print("\nAttach Event Detected (Information Below)")
            print("===========================================")
            print("Library Version: %s" % attached.getLibraryVersion())
            print("Serial Number: %d" % attached.getDeviceSerialNumber())
            print("Channel: %d" % attached.getChannel())
            print("Channel Class: %s" % attached.getChannelClass())
            print("Channel Name: %s" % attached.getChannelName())
            print("Device ID: %d" % attached.getDeviceID())
            print("Device Version: %d" % attached.getDeviceVersion())
            print("Device Name: %s" % attached.getDeviceName())
            print("Device Class: %d" % attached.getDeviceClass())
            print("\n")
    
        except PhidgetException as e:
    #       print("Phidget Exception %i: %s" % (e.code, e.details))
    #       print("Press Enter to Exit...\n")
    #       readin = sys.stdin.read(1)
            exit(1)   
        
    def VoltageInputDetached(self,e):
        detached = e   
    
    def ErrorEvent(e, eCode, description):
        print(" ")
    
    def VoltageChangeHandler(self, e, voltage):
        temperature=(voltage * 44.444) - 61.11
        temperature=(temperature * 1.8) + 32
        self.temp=temperature
        
    def SensorChangeHandler(self,e, sensorValue, sensorUnit):
        print(" ")
    
    def start(self): #start caputuring after this
        
        try:
            self.ch.setOnAttachHandler(self.VoltageInputAttached)
            self.ch.setOnDetachHandler(self.VoltageInputDetached)
            self.ch.setOnErrorHandler(self.ErrorEvent)
        
            self.ch.setOnVoltageChangeHandler(self.VoltageChangeHandler)
            self.ch.setOnSensorChangeHandler(self.SensorChangeHandler)
        
            # Please review the Phidget22 channel matching documentation for details on the device
            # and class architecture of Phidget22, and how channels are matched to device features.
        
            # Specifies the serial number of the device to attach to.
            # For VINT devices, this is the hub serial number.
            #
            # The default is any device.
            #
            # ch.setDeviceSerialNumber(<YOUR DEVICE SERIAL NUMBER>) 
        
            # For VINT devices, this specifies the port the VINT device must be plugged into.
            #
            # The default is any port.
            #
            # ch.setHubPort(0)
        
            # Specifies that the channel should only match a VINT hub port.
            # The only valid channel id is 0.
            #
            # The default is 0 (false), meaning VINT hub ports will never match
            #
            # ch.setIsHubPortDevice(1)
        
            # Specifies which channel to attach to.  It is important that the channel of
            # the device is the same class as the channel that is being opened.
            #
            # The default is any channel.
            #
            # ch.setChannel(0)
        
            # In order to attach to a network Phidget, the program must connect to a Phidget22 Network Server.
            # In a normal environment this can be done automatically by enabling server discovery, which
            # will cause the client to discovery and connect to available servers.
            #
            # To force the channel to only match a network Phidget, set remote to 1.
            #
            # Net.enableServerDiscovery(PhidgetServerType.PHIDGETSERVER_DEVICE);
            # ch.setIsRemote(1)
        
        #   print("Waiting for the Phidget VoltageInput Object to be attached...")
            self.ch.openWaitForAttachment(5000)
        except PhidgetException as e:
        #   print("Phidget Exception %i: %s" % (e.code, e.details))
        #   print("Press Enter to Exit...\n")
            exit(1)

    
    def close(self):
        try:
            self.ch.close()
        except PhidgetException as e:
        #   print("Phidget Exception %i: %s" % (e.code, e.details))
        #   print("Press Enter to Exit...\n")
        #   readin = sys.stdin.read(1)
            exit(1) 
                     
