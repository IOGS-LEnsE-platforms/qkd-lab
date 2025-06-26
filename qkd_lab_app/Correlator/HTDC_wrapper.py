# -*- coding: utf-8 -*-
#*********************************************************************
#                 Aurea Technology - HTDC 
#                   Lib Python wrapper
#*********************************************************************
# Language: python 3.x
# Dependency: HTDC.dll
# Description: library fonctions wrapper 
# Note: please check the path of HTDC.dll
#*********************************************************************

from ctypes import *
import time
import logging
import platform

# Load library
def htdc_shared_lib(path):
  if platform.system() == "Windows":
      return WinDLL(path)
  elif platform.system() == "Linux":
      return CDLL("libHTDC.so")
  elif platform.system() == "Darwin":
      return CDLL("libHTDC.dylib")
  else:
      return None

# Defines
HTDC_RES = 0.013           # TDC resolution in ns
N_SAMPLE_MAX = 10000000   # Maximum sample to recover
"""CH_1 = 1
CH_2 = 2
CH_3 = 4
CH_4 = 8"""

# List devices
# Description: scan all TDC devices available
def listDevices(path):
  global DEVICE
  devList = []
  nDev = c_short()
  DEVICE = htdc_shared_lib(path)
  listDev = DEVICE.HTDC_listDevices
  listDev.argtypes = [POINTER(POINTER(c_char)), POINTER(c_short)]
  listDev.restype = c_int
  devicesList = (POINTER(c_char)*10)()
  pdevicesList = devicesList[0]
  if listDev(byref(pdevicesList),byref(nDev))!=0: 
    nDev = 0
  else:
      for i in range(nDev.value):
        devList.append(str(string_at(devicesList[i]),'utf-8'))
  return devList, nDev.value

# Open device
# Description: connect the target HTDC device
def openDevice(iDev):
  if DEVICE.HTDC_openDevice(iDev) == 0:
    return 0
  else:
    return -1
  
# Close device
# Description: close USB connection
def closeDevice(iDev):
  if DEVICE.HTDC_closeDevice(iDev) == 0:
    return 0
  else:
    return -1

# Get system version
# Description: Return the system version (part/serial/firmware)
def getSystemVersion(iDev):
  DEVICE.HTDC_getSystemVersion.restype = c_short
  version=create_string_buffer(64) 
  ret = DEVICE.HTDC_getSystemVersion(iDev, byref(version))
  return ret,str(version.value,"utf-8")

# Set Sync source
# Description: apply new sync clock source between internal or external  
def setSyncSource(iDev, mode):
  ret = DEVICE.HTDC_setSyncSource(iDev, mode)
  return ret

# Get Sync source
# Description: return the current sync clock source between internal or external  
def getSyncSource(iDev):
  mode = c_short()
  ret = DEVICE.HTDC_getSyncSource(iDev, byref(mode))
  return ret, int(mode.value)


# Set internal Sync frequency
# Description: apply new sync frequency in Hz
def setInternalSyncFrequency(iDev, value):
  ret = DEVICE.HTDC_setInternalSyncFrequency(iDev, value)
  return ret

# Get internal Sync frequency
# Description: return the current sync frequency in Hz
def getInternalSyncFrequency(iDev):
  freq = c_uint()
  ret = DEVICE.HTDC_getInternalSyncFrequency(iDev, byref(freq))
  return ret, int(freq.value)


# Set Sync divider
# Description: apply new sync divider
def setSyncDivider(iDev, value):
  ret = DEVICE.HTDC_setSyncDivider(iDev, value)
  return ret

# Get Sync divider
# Description: return the current sync divider
def getSyncDivider(iDev):
  div = c_short()
  ret = DEVICE.HTDC_getSyncDivider(iDev, byref(div))
  return ret, int(div.value)

# Set Sync Input configuration
# Description: apply new sync configuration (power, edge, level)  
def setSyncInputConfig(iDev, enable,edge,level):
  ret = DEVICE.HTDC_setSyncInputConfig(iDev, enable, edge, level)
  return ret

# Get Sync input configuration
# Description: return the current sync configuration (power, edge, level) 
def getSyncInputConfig(iDev):
  enable = c_short()
  edge = c_short()
  level = c_short()
  ret = DEVICE.HTDC_getSyncInputConfig(iDev, byref(enable), byref(edge), byref(level))
  return ret, int(enable.value), int(edge.value), int(level.value)

# Set Channel delay
# Description: apply new delay in ns for the selected channel  
def setChannelDelay(iDev, iCh,value):
  ret = DEVICE.HTDC_setChannelDelay(iDev, iCh,c_float(value))
  return ret

# Get Channel delay
# Description: return the current delay in ns for the selected channel  
def getChannelDelay(iDev, iCh):
  delay = c_float()
  ret = DEVICE.HTDC_getChannelDelay(iDev, iCh, byref(delay))
  return ret, round(delay.value,2)

# Set channel configuration
# Description: apply new channel configuration (power, edge, level)  
def setChannelConfig(iDev, iCh, power, edge, level):
  ret = DEVICE.HTDC_setChannelConfig(iDev, iCh, power, edge, level)
  return ret

# Get channel configuration
# Description: return the current channel configuration (power, edge, level)
def getChannelConfig(iDev, iCh):
  power = c_short()
  edge = c_short()
  level = c_short()
  ret = DEVICE.HTDC_getChannelConfig(iDev, iCh, byref(power), byref(edge), byref(level))
  return ret, int(power.value), int(edge.value), int(level.value)

# Arm channel
# Description: arm the selected channel with stop condition (time or sample number)
def armChannel(iDev, iCh,n):
  ret = DEVICE.HTDC_armChannel(iDev, iCh, n)
  return ret

def setCrossCorrelationALU(iDev, enable):
    ret = DEVICE.HTDC_setCrossCorrelationALU(iDev,enable)
    return(ret)

# Get channel state
# Description: return the current status, number of sample to recover and consign for the selected channel
def getChannelState(iDev, iCh):
  state = c_int()
  nSampleToRecover = c_ulong()
  nSampleRecovered = c_ulong()
  ret = DEVICE.HTDC_getChannelState(iDev, iCh, byref(state), byref(nSampleToRecover), byref(nSampleRecovered))
  return ret, int(state.value),int(nSampleToRecover.value),int(nSampleRecovered.value)

# Start channel
# Description: start data recovery on the selected channel
def startChannel(iDev, iCh):
  ret = DEVICE.HTDC_startChannel(iDev, iCh)
  return ret

# Stop channel
# Description: stop data recovery on the selected channel
def stopChannel(iDev, iCh):
  ret = DEVICE.HTDC_stopChannel(iDev, iCh)
  return ret

# Get channel data
# Description: return the current data from the selected channel (depending on the mode set)
def getChannelData(iDev, iCh):
  global data 
  sample = []
  data = (c_ulonglong*N_SAMPLE_MAX)()
  nb = c_ulong(0)
  if iCh == 1:
    ret = DEVICE.HTDC_getCh1Data(iDev, byref(data), byref(nb))
  elif iCh == 2:
    ret = DEVICE.HTDC_getCh2Data(iDev, byref(data), byref(nb))
  elif iCh == 4:
    ret = DEVICE.HTDC_getCh3Data(iDev, byref(data), byref(nb))
  elif iCh == 8:
    ret = DEVICE.HTDC_getCh4Data(iDev, byref(data), byref(nb))
  # store result in list
  for i in range(nb.value):
    sample.append(data[i])
  return ret, int(nb.value),sample

def getCrossCorrelationData(iDev):
  global data 
  sample = []
  data = (c_ulonglong*N_SAMPLE_MAX)()
  nb = c_ulong(0)
  ret = DEVICE.HTDC_getCrossCorrelationData(iDev, byref(data), byref(nb))
  # store result in list
  for i in range(nb.value):
    sample.append(data[i])
  return ret, int(nb.value),sample

# Get counts inputs events 
# Description: return the current events counts on each input
def getEventsCounts(iDev):
  counts = (c_ulong*5)()
  nEvents = c_short()
  countsList = []
  ret = DEVICE.HTDC_getEventsCounts(iDev, byref(nEvents), counts)
  #print(ret)
  if(ret == 0):
    for i in range(nEvents.value):
      countsList.append(counts[i])
  return ret, countsList
  

