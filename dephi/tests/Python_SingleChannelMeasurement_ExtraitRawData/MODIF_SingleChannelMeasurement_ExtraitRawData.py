#*********************************************************************
#
#								ChronoXea
#					Python - Single channel measurement
#
#*********************************************************************
# FileName:        Python_SingleChannelMeas.py
# Dependencies:    HTDC.dll
# Interpreter:     Python 3.x
# Company:         Copyright (C) Aurea Technology.
# Autor:		   Matthieu Grovel
#
# Description:		copie du fichier SingleChannelMeasurement 
# extraction des raw data et écriture sur fichier texte 
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
TARGET_CH = int(2)
N_SAMPLE = int(1000)

# Application banner
def displayInitMsg():
	print("----------------------------------------------------------------")
	print("--------------          AUREA TECHNOLOGY         ---------------")
	print("--------------             ChronoXea             ---------------")
	print("----------------------------------------------------------------")
	print("--------------   Raw Data Single Measurement    ---------------")
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
  print("Set input Sync")
  ret = TDC.setSyncInputConfig(iDev,1,0,0)
  if ret < 0: print(" -> failed\n")
  else: print(" -> done\n")

  # Set target channel delay to 5.5ns
  print("Sync channel delay")
  print(TARGET_CH)
  ret = TDC.setChannelDelay(iDev, TARGET_CH, 5.5)
  if ret < 0: print(" -> failed\n")
  else: print(" -> done\n")

  # Set channel(s) configuration: Power ON, rising edge and TTL-CMOS level
  print("Channel configuration")
  ret = TDC.setChannelConfig(iDev, TARGET_CH, 1, 0, 0)
  if ret < 0: print(" -> failed\n")
  else: print(" -> done\n")
 
  # Arm channel(s): arm target channel to recover N_SAMPLE
  print("Arm channel")
  ret = TDC.armChannel(iDev,TARGET_CH,N_SAMPLE)
  if ret < 0: print(" -> failed\n")
  else: print(" -> done\n")
  nSampleToRecover = N_SAMPLE

  print("Waiting stable sync signal... ")
  time.sleep(5)
   
  # Start channel(s): start target channel
  print("Start channel")
  ret = TDC.startChannel(iDev, TARGET_CH)
  if ret < 0: print(" -> failed\n")
  else: print(" -> done\n")
  nSampleRecovered = 0 #ajout
  sampleList=[]
  print("Avant while")

  # Création du texte contenant toute la raw data (issue de sample)
  # ouverture fichier
  #'C:\Users\CRYPTO_B\Documents\mesure 2025\RawData_VisualStudio.txt'
  f=open('C:/Users/CRYPTO_B/Documents/mesure 2025/RawData_VisualStudio.txt', 'a')
  f.write("Raw data unite ")

  print("Version")
  ret , version = TDC.getLibVersion() 
  if ret < 0: print(" -> failed\n")
  else: print(" -> done\n")
  print(version)

  #Recover Data
  print("Recover target channel data... ")
  while nSampleRecovered<nSampleToRecover:
  
        # Recover target channel state, to known how much data are available
    ret, state, nSampleToRecover, nSample = TDC.getChannelState(iDev, TARGET_CH)
    if(ret == 0):
        print("nSample")
        print(nSample)
        nSampleRecovered += nSample

        # Get channel data
        ret, n, sample = TDC.getChannelData(iDev, TARGET_CH)

        if ret == 0:
            # Store result if data available
            if n > 0: sampleList+=sample
    
            # Wait and display progression
            time.sleep(0.5)
            print("\r State: {} | {}/{} data recovered".format(state,nSampleRecovered,nSampleToRecover))
        else: print("\nGet Channel Data: error\n")
    else: print("\nchannel State: error\n")
  
    #print(len(sampleList))
    #écriture  des valeurs dans le fichier texte
    for i in range (len(sampleList)):
        f.write(str(round(sampleList[i]*TDC.TDC_RES,3)))
        f.write("\n")



  
  
  # Display part of data recovered
  f.close()
  print("File written successfully")
    
  # fermeture fichier
  print("\nEnd of program")

  # Close device
  ret = TDC.closeDevice(iDev)
  if ret < 0: print(" -> failed to close communication\n")
  else: print(" ->  communication closed")
  
# Python main entry point
if __name__ == "__main__":
  main()
