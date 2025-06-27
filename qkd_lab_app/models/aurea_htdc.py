# -*- coding: utf-8 -*-
"""
Created on Wed Jun 25 12:50:28 2025

@author: CRYPTO_B
"""

from ctypes import *
import time
import sys, os
import numpy as np

sys.path.append(os.path.abspath("../Correlator"))


# Exemple : chemin absolu vers CPC.dll
dllpath = r"C:\Users\CRYPTO_B\Documents\GitHub\qkd-lab\qkd_lab_app\Correlator\HTDC.dll"

# Vérifie que le fichier existe
if not os.path.isfile(dllpath):
    raise FileNotFoundError(f"Fichier introuvable : {dllpath}")

import HTDC_wrapper as ChronoXea


class AureaHTDC():
    def __init__(self, parent = None):
        #super.__init__()
        print('Initializing HTDC')
        
        self.parent = parent
        self.res = ChronoXea.HTDC_RES
        
        
        ### Correlator settings
        iDev = int(0)
        nDev = c_short()
        self.nSampleRecovered=int(0)
        self.nSampleToRecover=int(0)
        self.devList = []
        self.N_SAMPLE = self.parent.N_SAMPLE
        self.TARGET_CH = int(2)
        self.frequency = self.parent.frequency
        
        ### Correlation channels
        self.A_CH = int(2)
        self.B_CH = int(4)
        self.COR_CH = int(16)
        
        ### Acquisition result
        self.sampleList = []
        self.file_path = os.path.dirname(os.path.abspath(__file__)) + r"\test.txt"
        self.file = None
        
        # Scan and open selected device
        self.devList,nDev=ChronoXea.listDevices(dllpath)
        #print(self.devList)
        if nDev==0: # if no device detected, wait
            print ("No device connected, waiting...")
            time_slept = 0
            while nDev==0:
                self.devList,nDev=ChronoXea.listDevices(dllpath)
                time.sleep(1)
                time_slept += 1
                if time_slept > 5:
                    print("No device found")
                    return None
        elif nDev>1: # if more 1 device detected, select target
            print("Found " + str(nDev) + " device(s) :")
            for i in range(nDev):
                print (" -"+str(i)+": " + self.devList[i])
                #iDev=int(input("Select device to open (0 to n):"))# A retirer
        # Open device
        #if ChronoXea.openDevice(iDev)<0:
            #ChronoXea.closeDevice(iDev)
            #input(" -> Failed to open device, press enter to quit !")
            #return 0
        
        print(self.devList[iDev])
        # Recover system version
        #ret,version = ChronoXea.getSystemVersion(iDev)
        #print(ret)
        #if ret<0: print(" -> failed\n")
        #else:print("System version = {} \n".format(version))
        # Wait some time
        if self.openDevice(iDev):
            print('starting')
            self.CrossCorrChannelMes(iDev, self.file_path)
        else:
            return None
        
        
        
        ### iCh : indice de channel
        ### iDev : indice de device (dans la liste)
        ChronoXea.closeDevice(iDev)
    
    def SingleChannelMes(self, iDev, path = None):
        print("Sync source")
        ret = ChronoXea.setSyncSource(iDev, 1)
        if ret == 0:
            print("\nSync Source Set\n")
        else:
            print("\nset Sync Source: error\n")
        
        self.setFrequency(iDev, self.frequency)
        self.setSyncDivider(iDev)
        self.inputConfig(iDev)
        self.setChanDelay(iDev)
        self.setChanConfig(iDev, self.TARGET_CH)
        self.armChannel(iDev, self.TARGET_CH, self.N_SAMPLE)
        self.startChannel(iDev, self.TARGET_CH)
        file = self.getSingleChanData(iDev, path)
        file.close()
        self.file = file
        
        print("\33[0m{}".format(len(self.sampleList)))
        
        
    def CrossCorrChannelMes(self, iDev, path = None):
        print("Sync source")
        ret = ChronoXea.setSyncSource(iDev, 1)
        if ret == 0:
            print("\nSync Source Set\n")
        else:
            print("\nset Sync Source: error\n")
        
        self.setFrequency(iDev, self.frequency)
        self.setSyncDivider(iDev)
        self.inputConfig(iDev)
        self.setChanDelay(iDev, self.A_CH)
        #self.setChanDelay(iDev, self.B_CH)
        #self.setChanDelay(iDev, self.COR_CH)
        self.setChanConfig(iDev, self.A_CH)
        self.setChanConfig(iDev, self.B_CH)
        self.setChanConfig(iDev, self.COR_CH)
        self.setContinuous(iDev, self.A_CH)
        self.setContinuous(iDev, self.B_CH)
        
        self.armChannel(iDev, self.A_CH, -1)
        self.armChannel(iDev, self.B_CH, -1)
        
        self.initCorrALU(iDev, self.A_CH, self.B_CH)
        
        self.startChannel(iDev, self.A_CH)
        self.startChannel(iDev, self.B_CH)
        self.startChannel(iDev, self.COR_CH)
        
        file = self.getCrossCorrData(iDev, path)
        file.close()
        self.file = file
    
    def openDevice(self, iDev):
        if ChronoXea.openDevice(iDev)<0:
            ChronoXea.closeDevice(iDev)
            #input(" -> Failed to open device, press enter to quit !")
            return False
        print("Device correctly opened")
        return True
        
    
    def inputConfig(self, iDev):
        '''Set sync input configuration: Enable, rising edge and TTL-CMOS level'''
        print("Set input Sync")
        ret = ChronoXea.setSyncInputConfig(iDev,1,0,0) #enable, edge, level
        if ret == 0:
            print("\nSync Input Config Set\n")
        else:
            print("\nset Sync Input Config: error\n")
        
    
    def setChanDelay(self, iDev, iCh, delay = 0):
        '''Set target channel delay to <delay>'''
        print("Sync channel delay")
        ret = ChronoXea.setChannelDelay(iDev, iCh, delay)
        if ret == 0:
            print("\nChannel Delay Set\n")
        else:
            print("\nset Channel delay: error\n")
    
    def setFrequency(self, iDev, frequency = 10000):
        '''Set internal sync frequency to <frequency>'''
        print("Internal Sync frequency")
        ret = ChronoXea.setInternalSyncFrequency(iDev, frequency)
        if ret == 0:
            print("\nInternal Sync frequency Set\n")
        else:
            print("\nset Internal Sync frequency: error\n")
    
    def setSyncDivider(self, iDev, divider = 1):
        '''Set sync divider to <divider>'''
        print("Sync divier")
        ret = ChronoXea.setSyncDivider(iDev, divider)
        if ret == 0:
            print("\nSync Divider Set\n")
        else:
            print("\nset Sync Divider: error\n")
    
    def setChanConfig(self, iDev, iCh):
        print("Channel configuration")
        ret = ChronoXea.setChannelConfig(iDev, iCh, 1, 0, 0) #power, edge, level
        if ret == 0:
            print("\nChannel config Set\n")
        else:
            print("\nset Channel config: error\n")
    
    def armChannel(self, iDev, iCh, N):
        '''Arm channel(s): arm target channel to recover N_SAMPLE'''
        print("Arm channel")
        ret = ChronoXea.armChannel(iDev,iCh,N)
        if ret == 0:
            print("\nChannel Armed\n")
        else:
            print("\nArm Channel: error\n")
        self.nSampleToRecover=N
        print("Waiting stable sync signal... ")
        #time.sleep()
    
    def startChannel(self, iDev, iCh):
        print("Start channel")
        ret = ChronoXea.startChannel(iDev, iCh)
        if ret < 0: print(" -> failed\n")
        else: print(" -> done\n")
        self.nSampleRecovered = 0
        self.sampleList=[]
        
    def stopChannel(self, iDev, iCh):
        print('stop channel')
        ret = ChronoXea.stopChannel(iDev, iCh)
        if ret < 0: print(" -> failed\n")
        else: print(" -> done\n")
    
    def version(self, iDev):
        print("Version")
        ret , version = ChronoXea.getLibVersion() 
        if ret < 0: print(" -> failed\n")
        else: print(" -> done\n")
        print(version)
    
    def createDestination(self, path, SavePreviousData = False):
        if SavePreviousData:
            file = open(path, 'a')
        else:
            file = open(path, 'w')
        return file
    
    def getSingleChanData(self, iDev, path = None):
        i = 0
        print("path =",  path)
        if path is not None:
            file = self.createDestination(path)
        print("Recover target channel data... ")
        while self.nSampleRecovered<self.nSampleToRecover and i<self.N_SAMPLE:
            # Recover target channel state, to known how much data are available
            ret, state, _, nSample = ChronoXea.getChannelState(iDev, self.TARGET_CH)
            if ret == 0:
                  print("\33[0m\tnSample : {}".format(nSample))
                  self.nSampleRecovered += nSample
                  i+=1

                  # Get channel data
                  ret, n, sample = ChronoXea.getChannelData(iDev, self.TARGET_CH)
              
                  if ret == 0:
                      # Store result if data available
                      if n > 0: 
                          self.sampleList+=sample
          
                      # Wait and display progression
                      time.sleep(0.1)
                      print("\033[33m\r State: {} | {}/{} data recovered""\033[0m".format(state,self.nSampleRecovered,self.nSampleToRecover))
                  else: print("\33[0m\nGet Channel Data: error\n")
            else: print("\nchannel State: error\n")
        if path is not None:
            for sample in self.sampleList:
                time_value = round(sample*ChronoXea.HTDC_RES,3)
                if time_value * 1e-9 <= 1/self.frequency:
                    file.write(str(time_value) + '\n')
                #self.file.write("\n")
            return file
        return None
    
    def initCorrALU(self, iDev, iCh1, iCh2):
        print("Init ALU")
        CH_1 = ChronoXea.CH_1
        CH_2 = ChronoXea.CH_2
        CH_3 = ChronoXea.CH_3
        value = 0
        if iCh1 == CH_1 and iCh2 == CH_2:
            value = 0
        elif iCh1 == CH_2 and iCh2 == CH_1:
            value = 1
        elif iCh1 == CH_2 and iCh2 == CH_3:
            value = 2
        elif iCh1 == CH_3 and iCh2 == CH_2:
            value = 3
        print("value = {}".format(value))
        ret = ChronoXea.setCrossCorrelationALU(iDev,value)
        if ret < 0: print(" -> failed\n")
        else: print(" -> done\n")
        self.nSampleToRecover = self.N_SAMPLE
        
    def setContinuous(self, iDev, iCh):
        print(f"Continuous Channel measurement mode {iCh}")
        ret = ChronoXea.setMeasMode(iDev,iCh,0)
        if ret < 0: print(" -> failed\n")
        else: print(" -> done\n")
        
    
    def getCrossCorrData(self, iDev, path = None):
        i = 0
        print("path =",  path)
        if path is not None:
            file = self.createDestination(path)
        print("Recover target channel data... ")
        while self.nSampleRecovered<self.nSampleToRecover and i<self.N_SAMPLE:
            # Recover target channel state, to known how much data are available
            ret, state, _, nSample = ChronoXea.getChannelState(iDev, self.COR_CH) #4294967295=-1
            print(ret, state, nSample)
            if(ret == 0):
                print("\33[0m\tnSample : {}".format(nSample))
                i+=1
                
                self.nSampleRecovered += nSample
                
                # Get channel data
                ret, n, sample = ChronoXea.getCrossCorrelationData(iDev)
                
                if ret == 0:
                    # Store result if data available
                    if n > 0:
                        self.sampleList+=sample
                        self.parent.update_histogram(np.array(sample)*ChronoXea.HTDC_RES)
            
                    # Wait and display progression
                    #time.sleep(0.1)
                    print("\033[33m\r State: {} | {}/{} data recovered\033[0m".format(state,self.nSampleRecovered,self.nSampleToRecover))
                else: print("\nGet Channel Data: error\n")
            else: print("\nchannel State: error\n")
        if path is not None:
            for sample in self.sampleList:
                time_value = round(sample*ChronoXea.HTDC_RES,3)
                if time_value * 1e-9 <= 1/self.frequency:
                    file.write(str(time_value) + '\n')
                #self.file.write("\n")
            return file
        return None
    
    
        
if __name__ == "__main__":
    aurea = AureaHTDC()