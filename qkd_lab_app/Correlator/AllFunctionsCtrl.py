#*********************************************************************
#
#								ChronoXea
#						Python - All functions control
#
#*********************************************************************
# FileName:        Python_AllFunctionsCtrl.py
# Dependencies:    HTDC.dll
# Interpreter:     Python 3.x
# Company:         Copyright (C) Aurea Technology.
# Autor:		   Matthieu Grovel
#
# Description:		This application allows to manipulate all functions
#					available to control TDC device.
#
# revision             Date        Comment
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# v1.0		            02/09/19    All user functions tested
# v1.1                  20/05/20    Add functions
#********************************************************************/

from ctypes import *
import time
import platform
import sys

# Import TDC wrapper file  
import HTDC_wrapper as TDC

# Application banner
def displayInitMsg():
	print("----------------------------------------------------------------")
	print("--------------          AUREA TECHNOLOGY         ---------------")
	print("--------------             ChronoXea             ---------------")
	print("----------------------------------------------------------------")
	print("--------------  Python - All functions control   ---------------")
	print("----------------------------------------------------------------")

# Application menu
def drawMenu():
  print("\nMenu:")
  print("-----")
  print(" -0 : quit ")
  print(" -1 : Set Sync source (not available for OEM mode)")
  print(" -2 : Get Sync source")
  print(" -3 : Set internal Sync frequency (not available for OEM mode)")
  print(" -4 : Get internal Sync frequency")
  print(" -5 : Set Sync divider")
  print(" -6 : Get Sync divider")
  print(" -7 : Set Sync input config")
  print(" -8 : Get Sync input config")
  print(" -9 : Set channel delay")
  print(" -10: Get channel delay")
  print(" -11: Set channel(s) config")
  print(" -12: Get channel config")
  print(" -13: Arm channel(s)")
  print(" -14: Get channel state")
  print(" -15: Start channel(s)")
  print(" -16: Stop channel(s)")
  print(" -17: Recover channel data")
  print(" -18: Recover input events counts")
  
  
path = r"C:\Users\CRYPTO_B\Documents\GitHub\qkd-lab\qkd_lab_app\Correlator\HTDC.dll"

# Application main
def main():
  key = ''
  iDev = int(0)
  nDev = c_short()
  devList = []
          
  # Init message    
  displayInitMsg()

  # Scan and open selected device
  devList, nDev = TDC.listDevices(path)
  if nDev == 0:   # if no device detected, wait
    print ("No device connected, waiting...")
    while nDev == 0:
        devList, nDev = TDC.listDevices(path)
        time.sleep(1)
  elif nDev > 1:  # if more 1 device detected, select target
    print("Found " + str(nDev) + " device(s) :")
    for i in range(nDev):
        print (" -"+str(i)+": " + devList[i])
    iDev = int(input("Select device to open (0 to n):")) 

  # Open device
  if TDC.openDevice(iDev) < 0:
    input(" -> Failed to open device, press enter to quit !")
    return 0	
  print("Device correctly opened")

  # Match command
  while key != '0':
    drawMenu()
    key = input("Enter cmd: ")
    if key == '0':    # Exit
      print("Exit")

    elif key == '1':  # Set sync source
        mode = int(input("\nSync source to set (0:external, 1=internal): "))
        ret = TDC.setSyncSource(iDev, mode)
        if ret < 0: print(" -> failed\n")
        else: print(" -> done\n")

    elif key == '2':  # Get sync source
        ret, source = TDC.getSyncSource(iDev)
        if ret < 0: print(" -> failed\n")
        else:       
            if source == 0: print("\nSync source: external\n")
            elif source == 1: print("\nSync source: internal\n")

    elif key == '3':  # Set internal sync frequeny
        val = int(input("\nInternal Sync frequency to set (1Hz to 4MHz): "))
        ret = TDC.setInternalSyncFrequency(iDev, val)
        if ret < 0: print(" -> failed\n")
        else: print(" -> done\n")

    elif key == '4':  # Get internal sync frequency
        ret, val = TDC.getInternalSyncFrequency(iDev)
        if ret < 0: print(" -> failed\n")
        else: print("\nInternal Sync frequency={}Hz\n".format(val))

    elif key == '5':  # Set sync divider
        value = int(input("\nSync divider to set (between 1 to 1024): "))
        ret = TDC.setSyncDivider(iDev, value)
        if ret < 0: print(" -> failed\n")
        else: print(" -> done\n")

    elif key == '6':  # Get sync divider
        ret, val = TDC.getSyncDivider(iDev)
        if ret < 0: print(" -> failed\n")
        else: print("\nSync divider={}\n".format(val))

    elif key == '7':  # Set sync input configuration
        print("\nSync input config:")
        enable = int(input(" - State to set (0:OFF or 1:ON): "))
        edge = int(input(" - Edge to set (0:rising or 1:falling): "))
        level = int(input(" - Level to set (0:TTL-CMOS or 1:NIM): "))
        ret = TDC.setSyncInputConfig(iDev, enable,edge,level)
        if ret < 0: print(" -> failed\n")
        else: print(" -> done\n")

    elif key == '8':  # Get sync input configuration
        ret, enable,edge,level = TDC.getSyncInputConfig(iDev)
        if ret < 0: print(" -> failed\n")
        else: print("\nSync input config:\n State = {}\n Edge  = {}\n Level = {}\n".format(enable,edge,level))

    elif key == '9':  # Set channel(s) delay
        print("\nChannel delay:")
        iCh = int(input(" - Target id(s) to set (1=CH_1, 2=CH_2, 4=CH_3, 8=CH_4, 15=CH_ALL): "))
        val = float(input(" - Delay to set (between 0.00 to 10.00ns by step of 0.01ns): "))
        ret = TDC.setChannelDelay(iDev, iCh, val)
        if ret < 0: print(" -> failed\n")
        else: print(" -> done\n")

    elif key == '10':  # Get channel delay
        iCh = int(input("Channel id to get (1=CH_1, 2=CH_2, 4=CH_3, 8=CH_4): "))
        ret, val = TDC.getChannelDelay(iDev, iCh)
        if ret < 0: print(" -> failed\n")
        else: print("\nChannel delay={}ns\n".format(val))

    elif key == '11':  # Set channel(s) configuration
        print("\nChannel to config:")
        iCh = int(input(" - Target id(s) to set (1=CH_1, 2=CH_2, 4=CH_3, 8=CH_4, 15=CH_ALL): "))
        power = int(input(" - State to set (0:OFF or 1:ON): "))
        edge = int(input(" - Edge to set (0:rising or 1:falling): "))
        level = int(input(" - Level to set (0:TTL-CMOS or 1:NIM: "))
        ret = TDC.setChannelConfig(iDev, iCh, power, edge, level)
        if ret < 0: print(" -> failed\n")
        else: print(" -> done\n")

    elif key == '12':  # Get channel configuration
        iCh = int(input("Channel id to get (1=CH_1, 2=CH_2, 4=CH_3, 8=CH_4): "))
        ret, power,edge,level = TDC.getChannelConfig(iDev, iCh)
        if ret < 0: print(" -> failed\n")
        else: print("\nChannel {} config:\n Power = {}\n Edge  = {}\n Level = {}\n".format(iCh,power,edge,level))

    elif key == '13':  # Arm channel(s)
        print("\nChannel to arm:")
        iCh = int(input(" - Target id(s) to set (1=CH_1, 2=CH_2, 4=CH_3, 8=CH_4, 15=CH_ALL): "))
        n = int(input(" - Sample to recover (0 to 1^8): "))
        ret = TDC.armChannel(iDev, iCh,n)
        if ret < 0: print(" -> failed\n")
        else: print(" -> done\n")

    elif key == '14':  # Get channel state
        iCh = int(input("Target channel id (1=CH_1, 2=CH_2, 4=CH_3, 8=CH_4): "))
        ret, state, nSampleToRecover, nSampleRecovered = TDC.getChannelState(iDev, iCh)
        if ret < 0: print(" -> failed\n")
        else: 
            if state == 0: strState = "stopped"
            elif state == 1: strState = "armed"
            else: strState = "running"
            print("\nChannel {}:\n State = {}\n {}/{} data recovered".format(iCh,strState,nSampleRecovered,nSampleToRecover))

    elif key == '15':  # Start channel(s)
        iCh = int(input("\nChannel id(s) to start (1=CH_1, 2=CH_2, 4=CH_3, 8=CH_4, 15=CH_ALL): "))
        ret = TDC.startChannel(iDev, iCh)
        if ret < 0: print(" -> failed\n")
        else: print(" -> done\n")

    elif key == '16':  # Stop channel(s)
        iCh = int(input("\nChannel id(s) to start (1=CH_1, 2=CH_2, 4=CH_3, 8=CH_4, 15=CH_ALL): "))
        ret = TDC.stopChannel(iDev, iCh)
        if ret < 0: print(" -> failed\n")
        else: print(" -> done\n")

    elif key == '17':  # Get channel data
        iCh = int(input("\nTarget id(s) of channel data (1=CH_1, 2=CH_2, 4=CH_3, 8=CH_4): "))
        ret,n,sample = TDC.getChannelData(iDev, iCh)
        if ret < 0: print(" -> failed\n")
        else:
            print("\n{} data recovered \n".format(n))
            if n != 0:
                ret = int(input("Action:\n  0:exit \n  1:display a part(10)\n "))
                if ret != 0:
                    print("\nData recovered")
                    for i in range (10):
                        print(" data[{}]={}ns".format(i,round(sample[i]*TDC.TDC_RES,3)))

    elif key == '18': # Get events count
        ret, inputCounts = TDC.getEventsCounts(iDev)
        if ret < 0: print(" -> failed\n")
        else:  
            if len(inputCounts) > 0: print("\nCounts: Sync={}evt/s, Ch1={}evt/s, Ch2={}evt/s, Ch3={}evt/s, Ch4={} evt/s".format(inputCounts[0],inputCounts[1],inputCounts[2],inputCounts[3],inputCounts[4]))
    else:
      print("Bad command")

  # Close device
  ret = TDC.closeDevice(iDev)
  if ret < 0: print(" -> failed to close communication\n")
  else: print(" ->  communication closed")

# Python main entry point
if __name__ == "__main__":
  main()
