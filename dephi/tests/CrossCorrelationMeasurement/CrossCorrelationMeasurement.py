#*********************************************************************
#
#								ChronoXea
#					Python - Cross channel measurement
#
#*********************************************************************
# FileName:        Python_SingleChannelMeas.py
# Dependencies:    HTDC.dll
# Interpreter:     Python 3.x
# Company:         Copyright (C) Aurea Technology.
# Autor:		   Isaline
#
# Description:		This application allows to get n sample time from
#					a target channel tdc.
#					User can adjust the target channel by changing 
#					the TARGET_CH define and choose the number of
#					sample time to get from the define N_SAMPLE.
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
import MODIF_HTDC_wrapper as TDC

# USER PARAMETERS
TARGET_CHA = int(1)
TARGET_CHB = int(2)
CH_CROSS = int(16)
N_SAMPLE = int(1000)
ON = 1
OFF = 0

# Application banner
def displayInitMsg():
	print("----------------------------------------------------------------")
	print("--------------          AUREA TECHNOLOGY         ---------------")
	print("--------------             ChronoXea             ---------------")
	print("----------------------------------------------------------------")
	print("--------------   Python - Cross channel meas    ---------------")
	print("----------------------------------------------------------------")

# Application main
def main():
  key = ''
  iDev = int(0)
  nDev = c_short()
  devList = []
          
  # Init message    
  displayInitMsg()

  # Scan and open selected device
  devList, nDev = TDC.listDevices()
  if nDev == 0:   # if no device detected, wait
    print ("No device connected, waiting...")
    while nDev == 0:
        devList, nDev = TDC.listDevices()
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

  # Set sync source: in internal
  print("Sync source")
  ret = TDC.setSyncSource(iDev, 1)
  if ret < 0: print(" -> failed\n")
  else: print(" -> done\n")

   # Set internal sync frequency to 10kHz
  print("Internal Sync frequency")
  ret = TDC.setInternalSyncFrequency(iDev, 10000)
  if ret < 0: print(" -> failed\n")
  else: print(" -> done\n")

  # Set sync divider to 1
  print("Sync divier")
  ret = TDC.setSyncDivider(iDev, 1)
  if ret < 0: print(" -> failed\n")
  else: print(" -> done\n")

  # Set sync input configuration: Enable, rising edge and TTL-CMOS level 
  # Remarque : sync pas avec horloge interne
  print("Set input Sync")
  ret = TDC.setSyncInputConfig(iDev,1,0,0)
  if ret < 0: print(" -> failed\n")
  else: print(" -> done\n")

  # Set target channelA delay to 5.5ns 
  # Remarque : pourquoi ce nombre ?
  print("Sync channel A delay")
  ret = TDC.setChannelDelay(iDev, TARGET_CHA, 5.5)
  if ret < 0: print(" -> failed\n")
  else: print(" -> done\n")

  
  # Set channel(s) configuration A: Power ON, rising edge and TTL-CMOS level
  print("Channel configuration")
  ret = TDC.setChannelConfig(iDev, TARGET_CHA, 1, 0, 0)
  if ret < 0: print(" -> failed\n")
  else: print(" -> done\n")
 
  # Set channel(s) configuration B: Power ON, rising edge and TTL-CMOS level
  print("Channel configuration")
  ret = TDC.setChannelConfig(iDev, TARGET_CHB, 1, 0, 0)
  if ret < 0: print(" -> failed\n")
  else: print(" -> done\n")
  
  #Set channel measurement to continuous UTILE ???
  print("Continuous Channel measurement mode A")
  ret = TDC.setMeasMode(iDev,TARGET_CHA,0)
  if ret < 0: print(" -> failed\n")
  else: print(" -> done\n")
  
  print("Continuous Channel measurement mode B")
  ret = TDC.setMeasMode(iDev,TARGET_CHB,0)
  if ret < 0: print(" -> failed\n")
  else: print(" -> done\n")

  
  # Arm channel(s): arm target channel A to recover N_SAMPLE
  print("Arm channel A")
  ret = TDC.armChannel(iDev,TARGET_CHA,-1)
  if ret < 0: print(" -> failed\n")
  else: print(" -> done\n")
 
  # Arm channel(s): arm target channel B to recover N_SAMPLE
  print("Arm channel B")
  ret = TDC.armChannel(iDev,TARGET_CHB,-1)
  if ret < 0: print(" -> failed\n")
  else: print(" -> done\n")

  # Arm channel(s): arm target channel CH_CROSS to recover N_SAMPLE
  print("Arm channel CH_CROSS")
  ret = TDC.armChannel(iDev,CH_CROSS,N_SAMPLE)
  if ret < 0: print(" -> failed\n")
  else: print(" -> done\n")
  
  #Init ALU
  print("Init ALU")
  ret = TDC.setCrossCorrelationALU(iDev,ON)
  if ret < 0: print(" -> failed\n")
  else: print(" -> done\n")
  nSampleToRecover = N_SAMPLE
  
  print("Waiting stable sync signal... ")
  time.sleep(5)
   
  # Start channel(s): start target channel
  print("Start channel A B and CROSS")
  ret = TDC.startChannel(iDev, TARGET_CHA) 
  if ret < 0: print(" -> failed\n")
  else: print(" -> done\n")
  ret = TDC.startChannel(iDev, TARGET_CHB) 
  if ret < 0: print(" -> failed\n")
  else: print(" -> done\n")
  ret = TDC.startChannel(iDev, CH_CROSS) 
  if ret < 0: print(" -> failed\n")
  else: print(" -> done\n")
  sampleList=[]
  nData = 0 #ajout

  # Recover data
  print("Recover target channel data... ")
  
  while nData<nSampleToRecover:
  
    # Recover target channel state, to known how much data are available
    ret, state, __nSampleToRecover, nSample = TDC.getChannelState(iDev, CH_CROSS) #4294967295=-1
    if(ret == 0):
        nData += nSample
        print("__nsampletorecover")
        print(state)
        # Get channel data
        ret, count, sample = TDC.getCrossCorrelationData(iDev) 
        if(ret == 0):
            # Store result if data available
            if count > 0: sampleList+=sample
    
            # Wait and display progression
            time.sleep(0.5)
            print("\r State: {} | {}/{} data recovered".format(state,nData,nSampleToRecover))
        else: print("\nGet Channel Data: error\n")
    else: print("\nchannel State: error\n")

  # Display part of data recovered
  print("\nSample time recovered:")
  for i in range (10):
    print(" sample[{}]={}ns".format(i,round(sampleList[i]*TDC.TDC_RES,3)))

  print("\nEnd of program")

  # Close device
  ret = TDC.closeDevice(iDev)
  if ret < 0: print(" -> failed to close communication\n")
  else: print(" ->  communication closed")
  
# Python main entry point
if __name__ == "__main__":
  main()
