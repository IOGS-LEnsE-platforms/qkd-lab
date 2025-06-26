
#*********************************************************************
#
#								ChronoXea
#					Python - TimeTagging measurement and Raw Data
#
#*********************************************************************
# FileName:        Python_SingleChannelMeas.py
# Dependencies:    HTDC.dll
# Interpreter:     Python 3.x
# Company:         LensE // FIE
# Autor:		   Vincent PRADERE
#
# Description:		permet de reprodire les fonctions du mode time tagging
# extraction des raw data et écriture sur fichier texte 
#
# revision             Date        Comment
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# v1.0		            21/02/2025
#********************************************************************/



from ctypes import *
import time
import platform
import sys

# Import TDC wrapper file  
import MODIF_HTDC_wrapper as TDC

#définition de fonction propre au time tagging
def save_data_in_file(data, file):
  tag_0, time_0 = convert_tag_time(data)
  f = open(file, "w")
  print("Saving data : " + file)
  f.write("%Time Tag\n") 
  for i in range(len(tag_0)):
    f.write('%s\t%s\n' % (time_0[i], tag_0[i]))
 
  f.close()
 
def convert_tag_time(buffer):
  tag_ = []
  time_ = []
  TDC_res = 0.013 #en ns
  for el in buffer:
    tag_.append((el >> 32) & (0xffffffff))
    time_.append(round((el & (0xffffffff))*TDC_res, 3))
  return tag_, time_

# USER PARAMETERS
TARGET_CHA = int(1)
TARGET_CHB = int(2)
TARGET_CHC = int(4)
TARGET_CHD = int(8)
N_SAMPLE = int(1000)
ON = 1
OFF = 0

# Application banner
def displayInitMsg():
	print("----------------------------------------------------------------")
	print("--------------          AUREA TECHNOLOGY         ---------------")
	print("--------------             ChronoXea             ---------------")
	print("----------------------------------------------------------------")
	print("--------   Python - TimeTagging measurement and Raw Data  ------")
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

    # Remarque : pourquoi ce nombre ?
  print("Sync channel B delay")
  ret = TDC.setChannelDelay(iDev, TARGET_CHB, 5.5)
  if ret < 0: print(" -> failed\n")
  else: print(" -> done\n")

  # Remarque : pourquoi ce nombre ?
  print("Sync channel C delay")
  ret = TDC.setChannelDelay(iDev, TARGET_CHC, 5.5)
  if ret < 0: print(" -> failed\n")
  else: print(" -> done\n")
  
    # Remarque : pourquoi ce nombre ?
  print("Sync channel D delay")
  ret = TDC.setChannelDelay(iDev, TARGET_CHD, 5.5)
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

    # Set channel(s) configuration C: Power ON, rising edge and TTL-CMOS level
  print("Channel configuration")
  ret = TDC.setChannelConfig(iDev, TARGET_CHC, 1, 0, 0)
  if ret < 0: print(" -> failed\n")
  else: print(" -> done\n")
 
  # Set channel(s) configuration D: Power ON, rising edge and TTL-CMOS level
  print("Channel configuration")
  ret = TDC.setChannelConfig(iDev, TARGET_CHD, 1, 0, 0)
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

  print("Continuous Channel measurement mode C")
  ret = TDC.setMeasMode(iDev,TARGET_CHC,0)
  if ret < 0: print(" -> failed\n")
  else: print(" -> done\n")
  
  print("Continuous Channel measurement mode D")
  ret = TDC.setMeasMode(iDev,TARGET_CHD,0)
  if ret < 0: print(" -> failed\n")
  else: print(" -> done\n")

   #Set channel measurement to timetagging
  print("time tagging mode channel A")
  ret = TDC.setResultFormat(iDev,TARGET_CHA,1)
  if ret < 0: print(" -> failed\n")
  else: print(" -> done\n")

  print("time tagging mode channel B")
  ret = TDC.setResultFormat(iDev,TARGET_CHB,1)
  if ret < 0: print(" -> failed\n")
  else: print(" -> done\n")

  print("time tagging mode channel C")
  ret = TDC.setResultFormat(iDev,TARGET_CHC,1)
  if ret < 0: print(" -> failed\n")
  else: print(" -> done\n")

  print("time tagging mode channel D")
  ret = TDC.setResultFormat(iDev,TARGET_CHD,1)
  if ret < 0: print(" -> failed\n")
  else: print(" -> done\n")
  
  # Arm channel(s): arm target channel A to recover N_SAMPLE
  print("Arm channel A")
  ret = TDC.armChannel(iDev,TARGET_CHA,N_SAMPLE)
  if ret < 0: print(" -> failed\n")
  else: print(" -> done\n")
 
  # Arm channel(s): arm target channel B to recover N_SAMPLE
  print("Arm channel B")
  ret = TDC.armChannel(iDev,TARGET_CHB,N_SAMPLE)
  if ret < 0: print(" -> failed\n")
  else: print(" -> done\n")

    # Arm channel(s): arm target channel C to recover N_SAMPLE
  print("Arm channel C")
  ret = TDC.armChannel(iDev,TARGET_CHC,N_SAMPLE)
  if ret < 0: print(" -> failed\n")
  else: print(" -> done\n")
 
  # Arm channel(s): arm target channel D to recover N_SAMPLE
  print("Arm channel D")
  ret = TDC.armChannel(iDev,TARGET_CHD,N_SAMPLE)
  if ret < 0: print(" -> failed\n")
  else: print(" -> done\n")

 
  
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
  ret = TDC.startChannel(iDev, TARGET_CHC) 
  if ret < 0: print(" -> failed\n")
  else: print(" -> done\n")
  ret = TDC.startChannel(iDev, TARGET_CHD) 
  if ret < 0: print(" -> failed\n")
  else: print(" -> done\n")

  sampleList_A=[]
  sampleList_B=[]
  sampleList_C=[]
  sampleList_D=[]
  nSampleToRecovered_A,nSampleToRecovered_B,nSampleToRecovered_C,nSampleToRecovered_D= N_SAMPLE,N_SAMPLE,N_SAMPLE,N_SAMPLE
  nData_A,nData_B,nData_C,nData_D = int(0),0,0,0

  
  # Recover data
  print("Recover target channel data... ")
  
  nSampleToRecovered_B,nSampleToRecovered_C,nSampleToRecovered_D
  while min(nData_A,nData_B,nData_C,nData_D)<max(N_SAMPLE,nSampleToRecovered_B,nSampleToRecovered_C,nSampleToRecovered_D):
  
      if nData_A<nSampleToRecovered_A:
              # Recover target channel state, to known how much data are available
              ret, state, nSampleToRecovered_A, nSample_A = TDC.getChannelState(iDev, TARGET_CHA) #4294967295=-1
              if ret==0:
                  nData_A +=nSample_A
                  # Get channel data
                  ret, n, sample_A = TDC.getChannelData(iDev, TARGET_CHA)
                  if ret == 0:
                    # Store result if data available
                    if n > 0: save_data_in_file(sample_A, "C:/Users/CRYPTO_B/Documents/mesure 2025/TT_A.txt")
                    # Wait and display progression
                    time.sleep(0.5)
                    print("\r State: {} | {}/{} data recovered".format(state,nData_A,nSampleToRecovered_A))
                  else: print("\nGet Channel A Data: error\n")
              else: print("\nchannel A State: error\n")
      if nData_B<nSampleToRecovered_B:
              # Recover target channel state, to known how much data are available
              ret, state, nSampleToRecovered_B, nSample_B = TDC.getChannelState(iDev, TARGET_CHB) #4294967295=-1
              if ret==0:
                  nData_B +=nSample_B
                  # Get channel data
                  ret, n, sample_B = TDC.getChannelData(iDev, TARGET_CHB)
                  if ret == 0:
                    # Store result if data available
                    if n > 0: save_data_in_file(sample_B, "C:/Users/CRYPTO_B/Documents/mesure 2025/TT_B.txt")
                    # Wait and display progression
                    time.sleep(0.5)
                    print("\r State: {} | {}/{} data recovered".format(state,nData_B,nSampleToRecovered_B))
                  else: print("\nGet Channel B Data: error\n")
              else: print("\nchannel B State: error\n")
      if nData_C<nSampleToRecovered_C:
              # Recover target channel state, to known how much data are available
              ret, state, nSampleToRecovered_C, nSample_C = TDC.getChannelState(iDev, TARGET_CHC) #4294967295=-1
              if ret==0:
                  nData_C +=nSample_C
                  # Get channel data
                  ret, n, sample_C = TDC.getChannelData(iDev, TARGET_CHC)
                  if ret == 0:
                    # Store result if data available
                    if n > 0: save_data_in_file(sample_C, "C:/Users/CRYPTO_B/Documents/mesure 2025/TT_C.txt")
                    # Wait and display progression
                    time.sleep(0.5)
                    print("\r State: {} | {}/{} data recovered".format(state,nData_C,nSampleToRecovered_C))
                  else: print("\nGet Channel C Data: error\n")
              else: print("\nchannel C State: error\n")
      if nData_D<nSampleToRecovered_D:
              # Recover target channel state, to known how much data are available
              ret, state, nSampleToRecovered_D, nSample_D = TDC.getChannelState(iDev, TARGET_CHD) #4294967295=-1
              if ret==0:
                  nData_D +=nSample_D
                  # Get channel data
                  ret, n, sample_D = TDC.getChannelData(iDev, TARGET_CHD)
                  if ret == 0:
                    # Store result if data available
                    if n > 0: save_data_in_file(sample_D, "C:/Users/CRYPTO_B/Documents/mesure 2025/TT_D.txt")
                    # Wait and display progression
                    time.sleep(0.5)
                    print("\r State: {} | {}/{} data recovered".format(state,nData_D,nSampleToRecovered_D))
                  else: print("\nGet Channel D Data: error\n")
              else: print("\nchannel D State: error\n")


  # Close device
  ret = TDC.closeDevice(iDev)
  if ret < 0: print(" -> failed to close communication\n")
  else: print(" ->  communication closed")
  
# Python main entry point
if __name__ == "__main__":
  main()
