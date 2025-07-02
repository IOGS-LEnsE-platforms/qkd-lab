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


dllpath = r"C:\Users\CRYPTO_B\Documents\GitHub\qkd-lab\qkd_lab_app\CPC\CPC.dll"

# Vérifie que le fichier existe
if not os.path.isfile(dllpath):
    raise FileNotFoundError(f"Fichier introuvable : {dllpath}")


import CPC_wrapper as CPC


class AureaCPC():
    def __init__(self, parent = None):
        print('Initializing CPC')
        
        self.parent = parent
        self.opened = False
        self.device_connected = False
        self.iDev_dict = {}

        self.devList = []
        self.openDevices()
        self.get_iDev_dict()
        print(self.iDev_dict)
        self.closeDevices()

    def openDevices(self):
        self.devList, nDev = CPC.listDevices(dllpath)
        print(self.devList)
        if nDev == 0:  # if no device detected, wait
            print("No device connected, waiting...")
            time_slept = 0
            while nDev == 0:
                self.devList, nDev = CPC.listDevices(dllpath)
                time.sleep(1)
                time_slept += 1
                if time_slept > 5:
                    print("No device found")
                    self.device_connected = False
                    break
        elif nDev > 1:  # if more 1 device detected, select target
            print("Found " + str(nDev) + " device(s) :")
            for i in range(nDev):
                print(" -" + str(i) + ": " + self.devList[i])
                self.device_connected = True
        else:
            self.device_connected = True

    def openDevice(self, iDev):
        if iDev < len(self.devList):
            if CPC.openDevice(iDev) < 0:
                CPC.closeDevice(iDev)
            else:
                self.opened = True
        else:
            print("\033[31mList index out of range : no device has been opened\033[0m")

    def closeDevices(self):
        self.opened = False
        self.device_connected = False
        for iDev in range(len(self.devList)):
            CPC.closeDevice(iDev)

    def getData(self, iDev):
        """Obtains the data from the specified device (iDev will have to be extracted in a dictionary from its serial #)"""
        if self.opened:
            ret, clk, det = CPC.getClockDetData(iDev)
            if ret < 0:
                return None
            else:
                print("\033[33mClock running at {}Hz, nb of counts: {}cts/s\033[0m".format(clk.value, det.value))
                return clk.value, det.value
        else:
            print("\033[31mThe CPC device has not been opened properly\033[0m")
        return None

    def initializeCPC(self, iDev):
        CPC.setDetectionMode(iDev, 0)
        CPC.setDeadtime(iDev, 40.0)
        CPC.setOutputFormat(0)
        CPC.setEfficiency(20)
        CPC.setOutputState(0)

    def get_iDev_dict(self):
        for iDev in range(len(self.devList)):
            serial_no = self.devList[iDev].split("- ")[1]
            self.iDev_dict[serial_no] = iDev

    def ready_devices(self):
        for iDev in range(len(self.devList)):
            self.openDevice(iDev)

if __name__ == "__main__":
    print(CPC.listDevices)
    aurea = AureaCPC()