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
path = r"C:\Users\CRYPTO_B\Documents\GitHub\qkd-lab\qkd_lab_app\Correlator\HTDC.dll"

# Vérifie que le fichier existe
if not os.path.isfile(path):
    raise FileNotFoundError(f"Fichier introuvable : {path}")

import HTDC_wrapper as ChronoXea


class AureaHTDC():
    def __init__(self, parent = None):
        print('Initializing HTDC')
        
        self.parent = parent
        
        key = ''
        iDev = c_short(0)
        nDev = c_short()
        self.devList = []
        # Scan and open selected device
        self.devList,nDev=ChronoXea.listDevices(path)
        print(self.devList)
        if nDev==0: # if no device detected, wait
            print ("No device connected, waiting...")
            time_slept = 0
            while nDev==0:
                self.devList,nDev=ChronoXea.listDevices(path)
                time.sleep(1)
                time_slept += 1
                if time_slept > 5:
                    print("No device found")
                    return None
        elif nDev>1: # if more 1 device detected, select target
            print("Found " + str(nDev) + " device(s) :")
            for i in range(nDev):
                print (" -"+str(i)+": " + self.devList[i])
                #iDev=int(input("Select device to open (0 to n):"))
        # Open device
        #if ChronoXea.openDevice(iDev)<0:
            #ChronoXea.closeDevice(iDev)
            #input(" -> Failed to open device, press enter to quit !")
            #return 0
        print("Device correctly opened")
        # Recover system version
        #ret,version = ChronoXea.getSystemVersion(iDev)
        #print(ret)
        #if ret<0: print(" -> failed\n")
        #else:print("System version = {} \n".format(version))
        # Wait some time
        
        ### iCh : indice de channel
        ### iDev : indice de device (dans la liste)


aurea = AureaHTDC()