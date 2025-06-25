# -*- coding: utf-8 -*-
"""
Created on Wed Jun 25 11:47:15 2025

@author: CRYPTO_B
"""

from ctypes import *
import time
import sys, os
# Exemple : chemin absolu vers CPC.dll
sys.path.append(os.path.abspath("../CPC"))


path = r"C:\Users\CRYPTO_B\Documents\GitHub\qkd-lab\qkd_lab_app\CPC\CPC.dll"

# Vérifie que le fichier existe
if not os.path.isfile(path):
    raise FileNotFoundError(f"Fichier introuvable : {path}")


import CPC_wrapper as CPC


class AureaCPC():
    def __init__(self, parent = None):
        print('Initializing CPC')
        
        self.parent = parent
        self.opened = False
        
        key = ''
        iDev = c_short(0)
        nDev = c_short()
        self.devList = []
        # Scan and open selected device
        self.devList,nDev=CPC.listDevices(path)
        self.devList
        if nDev==0: # if no device detected, wait
            print ("No device connected, waiting...")
            time_slept = 0
            while nDev==0:
                self.devList,nDev=CPC.listDevices(path)
                time.sleep(1)
                time_slept += 1
                if time_slept > 5:
                    print("No device found")
                    return None
            self.opened = True
        elif nDev>=1: # if more 1 device detected, select target
            print("Found " + str(nDev) + " device(s) :")
            for i in range(nDev):
                print (" -"+str(i)+": " + self.devList[i])
                #iDev=int(input("Select device to open (0 to n):"))
                # Open device
            self.opened = True
        #if CPC.openDevice(iDev)<0:
            #self.opened = False
            #input(" -> Failed to open device, press enter to quit !")
            #return 0
        # Recover system version   
        """if self.opened:
            print("Device correctly opened")
            ret,version = CPC.getSystemVersion(1)
            if ret<0: print(" -> failed\n")
            else:print("System version = {} \n".format(version))"""
        # Wait some time
        time.sleep(2)
        # Close device communication
        CPC.closeDevice(iDev)
        # Python main entry point
        #print(self.devList)
        
print(CPC.listDevices)
aurea = AureaCPC()