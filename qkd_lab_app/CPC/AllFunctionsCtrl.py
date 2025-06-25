# -*- coding: utf-8 -*-
#*********************************************************************
#
#					   Aurea Technology - CPC
#						All functions control
#
#*********************************************************************
# FileName:        AllFunctionsCtrl.py
# Dependency:      CPC.dll
# Interpreter:     Python 3.x
# Company:         Copyright (C) Aurea Technology.
# Autor:		   Matthieu Grovel
#
# Description:		This application allows to manipulate all functions
#					available to control CPC device.
#
# revision             Date        Comment
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# v1.0		            22/06/21    All user functions tested
#********************************************************************/

from ctypes import *
import time
import platform
import sys

# Import CPC wrapper file  
import CPC_wrapper as CPC        

# Application banner
def displayInitMsg():
  print("----------------------------------------------------------------")
  print("--------------      Aurea Technology - CPC       ---------------")
  print("----------------------------------------------------------------")
  print("--------------       All functions control       ---------------")
  print("----------------------------------------------------------------")

# Application menu
def drawMenu():
  print("\nMenu:")
  print("-----")
  print(" -0 : quit ")

  print(" -1 : get system version")
  print(" -2 : save all settings")
  print(" -3 : apply factory settings")
  print(" -4 : reset system")

  print(" -5 : get efficiency range")
  print(" -6 : get efficiency")
  print(" -7 : set efficiency")

  print(" -8 : get deadtime range")
  print(" -9 : get deadtime")
  print(" -10: set deadtime")

  print(" -11: get detection mode")
  print(" -12: set detection mode")

  print(" -13: get output format")
  print(" -14: set output format")
  print(" -15: get output state")
  print(" -16: set output state")

  print(" -17: get clock & detections")
  print(" -18: get body socket temperature")

# Application main
def main():
  key = ''
  iDev = c_short(0)
  nDev = c_short()
  devList = []

  # Init message    
  displayInitMsg()

  # Scan and open selected device
  devList, nDev = CPC.listDevices()
  if nDev == 0:   # if no device detected, wait
    print ("No device connected, waiting...")
    while nDev == 0:
        devList, nDev = CPC.listDevices()
        time.sleep(1)
  elif nDev > 1:  # if more 1 device detected, select target
    print("Found " + str(nDev) + " device(s) :")
    for i in range(nDev):
        print (" -" + str(i) + ": " + devList[i])
    iDev = int(input("Select device to open (0 to n):")) 

  # Open device
  if CPC.openDevice(iDev) < 0:
    input(" -> Failed to open device, press enter to quit !")
    return 0	
  print("Device correctly opened")

  # Match command
  while key != '0':
    drawMenu()
    key = input("Enter cmd: ")
    print("\n")
    if key == '0':    # Exit
      print("Exit")

    elif key =='1': # Get system version
        ret, version = CPC.getSystemVersion(iDev)
        if ret < 0: print(" -> failed\n")
        else: print("System version = {} \n".format(version))

    elif key =='2':  # Save all settings
        print("Settings saving...")
        ret = CPC.saveAllSettings(iDev)
        if ret < 0: print(" -> failed\n")
        else: print(" -> done\n")

    elif key =='3':  # Factory settings
        print("Factory settings...")
        ret = CPC.applyFactorySettings(iDev)
        if ret < 0: print(" -> failed\n")
        else: print(" -> done\n")

    elif key =='4':  # Reset system
        print("Reset system...")
        CPC.resetSystem(iDev)
        ret = CPC.closeDevice(iDev)
        if ret < 0: print(" -> failed to close communication\n")
        else: print(" ->  communication closed")
        print(" ->  usb connection restart...")
        time.sleep(20)

        # Scan and open selected device
        devList, nDev = CPC.listDevices()
        if nDev == 0:   # if no device detected, wait
          print ("No device connected, waiting...")
          while nDev == 0:
              devList, nDev = CPC.listDevices()
              time.sleep(1)
        elif nDev > 1:  # if more 1 device detected, select target
          print("Found " + str(nDev) + " device(s) :")
          for i in range(nDev):
              print (" -" + str(i) + ": " + devList[i])
          iDev = int(input("Select device to open (0 to n):")) 

        # Open device
        if CPC.openDevice(iDev) < 0:
          input(" -> Failed to open device, press enter to quit !")
          return 0    
        print("Device correctly opened")

    elif key =='5': # Get efficiency range
        ret, range_eff = CPC.getEfficiencyRange(iDev)
        if ret < 0: print(" -> failed\n")
        else: print("Efficiency available = {}% \n".format(range_eff))

    elif key =='6': # Get efficiency
        ret, val = CPC.getEfficiency(iDev)
        if ret < 0: print(" -> failed to recover efficiency\n")
        else: print("Efficiency = {}% \n".format(val))

    elif key =='7': # Set efficiency
        val = int(input("Enter efficiency to set (in %): "))
        ret = CPC.setEfficiency(iDev, val)
        if ret < 0: print(" -> failed\n")
        else: print(" -> done\n")

    elif key =='8': # Get deadtime range
        ret,min,max = CPC.getDeadtimeRange(iDev)
        if ret < 0: print(" -> failed\n")
        else: print("Deadtime range: min={}us max={}us\n".format(min,max))

    elif key =='9': # Get deadtime
        ret, val = CPC.getDeadtime(iDev)
        if ret < 0: print(" -> failed to recover deadtime\n")
        else: print("Deadtime = {}us \n".format(val))

    elif key =='10': # Set deadtime
        val = float(input("Enter deadtime to set (in us): "))
        ret = CPC.setDeadtime(iDev, val)
        if ret < 0: print(" -> failed\n")
        else: print(" -> done\n")

    elif key =='11': # Get detection mode
        ret, val = CPC.getDetectionMode(iDev)
        if ret < 0: print(" -> failed to recover detection mdoe\n")
        else:  
            if val == 0: print("Detection mode in continuous \n")
            else: print("Detection mode in gated \n")

    elif key =='12': # Set detection mode
        val = int(input("Enter detection mode to set (0=continuous, 1=gated): "))
        ret = CPC.setDetectionMode(iDev, val)
        if ret < 0: print(" -> failed\n")
        else: print(" -> done\n")

    elif key =='13': # Get output format
        ret, val = CPC.getOutputFormat(iDev)
        if ret < 0: print(" -> failed to recover output format\n")
        else:  
            if val == 0: print("Output format in numeric \n")
            elif val == 1: print("Output format in analogic \n")
            else: print("Output format in NIM \n")

    elif key =='14': # Set output format
        val = int(input("Enter ouput format to set (0=numeric, 1=analogic or 2:NIM): "))
        ret = CPC.setOutputFormat(iDev, val)
        if ret < 0: print(" -> failed\n")
        else: print(" -> done\n")

    elif key =='15': # Get output state
        ret, val = CPC.getOutputState(iDev)
        if ret < 0: print(" -> failed to recover output state\n")
        else:  
            if val == 0: print("Output state OFF \n")
            else: print("Output state ON \n")

    elif key =='16': # Set output state
        val = int(input("Enter ouput state to set (0=OFF or 1=ON): "))
        ret = CPC.setOutputState(iDev, val)
        if ret < 0: print(" -> failed\n")
        else: print(" -> done\n")

    elif key =='17':   # Get clock & detections
        ret,clk,det=CPC.getClockDetData(iDev)
        if ret < 0: print(" -> failed\n")
        else: print(" Clock     = {} Hz \n Detection = {} cnt\s \n".format(clk.value,det.value))

    elif key =='18': # Get body temperature
        ret,val = CPC.getBodySocketTemp(iDev)
        if ret < 0: print(" -> failed to recover body temp\n")
        else: print("Body temp = {}°C \n".format(val))
    else: 
      print("Bad command\n")

  ret = CPC.closeDevice(iDev)
  if ret < 0: print(" -> failed to close communication\n")
  else: print(" ->  communication closed")
  
# Python main entry point
if __name__ == "__main__":
  main()
