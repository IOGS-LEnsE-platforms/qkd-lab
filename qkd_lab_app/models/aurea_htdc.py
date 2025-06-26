# -*- coding: utf-8 -*-
"""
Created on Wed Jun 25 12:50:28 2025

@author: CRYPTO_B
"""

from ctypes import *
import time
import sys, os

sys.path.append(os.path.abspath("../Correlator"))


# Exemple : chemin absolu vers CPC.dll
dllpath = r"C:\Users\CRYPTO_B\Documents\GitHub\qkd-lab\qkd_lab_app\Correlator\HTDC.dll"

# Vérifie que le fichier existe
if not os.path.isfile(dllpath):
    raise FileNotFoundError(f"Fichier introuvable : {dllpath}")

import HTDC_wrapper as ChronoXea


class AureaHTDC():
    def __init__(self, parent = None):
        print('Initializing HTDC')
        
        self.parent = parent
        
        
        ### Correlator settings
        iDev = int(0)
        nDev = c_short()
        self.nSampleRecovered=int(0)
        self.nSampleToRecover=int(0)
        self.devList = []
        self.N_SAMPLE = int(200)
        self.TARGET_CH = int(2)
        
        ### Acquisition result
        self.sampleList = []
        self.file_path = os.path.dirname(os.path.abspath(__file__)) + r"\test"
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
            self.SingleChannelMes(iDev, self.file_path)
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
        
        self.setSyncDivider(iDev)
        self.setFrequency(iDev)
        self.setChanDelay(iDev)
        self.inputConfig(iDev)
        self.armChannel(iDev)
        self.startChannel(iDev)
        self.getData(iDev, path)
        
        print(self.sampleList)
    
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
        
    
    def setChanDelay(self, iDev, delay = 5.5):
        '''Set target channel delay to <delay>'''
        print("Sync channel delay")
        ret = ChronoXea.setChannelDelay(iDev, self.TARGET_CH, delay)
        if ret == 0:
            print("\nChannel Delay Set\n")
        else:
            print("\nset Channel delay: error\n")
    
    def setFrequency(self, iDev, frequency = 10000):
        '''Set internal sync frequency to <frequency>'''
        print("Internal Sync frequency")
        ret = ChronoXea.setInternalSyncFrequency(iDev, 10000)
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
    
    def armChannel(self, iDev):
        #Arm channel(s): arm target channel to recover N_SAMPLE
        print("Arm channel")
        ret = ChronoXea.armChannel(iDev,self.TARGET_CH,self.N_SAMPLE)
        if ret == 0:
            print("\nChannel Armed\n")
        else:
            print("\nArm Channel: error\n")
        self.nSampleToRecover=self.N_SAMPLE
        print("Waiting stable sync signal... ")
        #time.sleep()
    
    def startChannel(self, iDev):
        print("Start channel")
        ret = ChronoXea.startChannel(iDev, self.TARGET_CH)
        if ret < 0: print(" -> failed\n")
        else: print(" -> done\n")
        self.nSampleRecovered = 0 #ajout
        self.sampleList=[]
    
    def version(self, iDev):
        print("Version")
        ret , version = ChronoXea.getLibVersion() 
        if ret < 0: print(" -> failed\n")
        else: print(" -> done\n")
        print(version)
    
    def createDestination(self, path):
        self.file = open(path, 'a')
    
    def getData(self, iDev, path = None):
        if path is not None:
            self.createDestination(path)
        print("Recover target channel data... ")
        while self.nSampleRecovered<self.nSampleToRecover:
            # Recover target channel state, to known how much data are available
            ret, state, self.nSampleToRecover, nSample = ChronoXea.getChannelState(iDev, self.TARGET_CH)
            if(ret == 0):
                  print("\33[0m\tnSample : {}".format(nSample))
                  self.nSampleRecovered += nSample

                  # Get channel data
                  ret, n, sample = ChronoXea.getChannelData(iDev, self.TARGET_CH)
              
                  if ret == 0:
                      # Store result if data available
                      if n > 0: self.sampleList+=sample
                      if path is not None:
                          for s in sample:
                              self.file.write(str(round(s*ChronoXea.HTDC_RES,3)) + '\n')
                              #self.file.write("\n")

          
                      # Wait and display progression
                      time.sleep(0.5)
                      print("\033[33m\r State: {} | {}/{} data recovered".format(state,self.nSampleRecovered,self.nSampleToRecover))
                  else: print("\33[0m\nGet Channel Data: error\n")
            else: print("\nchannel State: error\n")
        

aurea = AureaHTDC()