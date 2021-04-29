#############################################################################
################### Helper Library for BLE Scanner ##########################
#############################################################################
#
# Copyright (C) 2020 by Alexander Nagy - https://bitekmindenhol.blog.hu/
#

from inc.ubtle import Scanner
import inc.lib_blehelper as BLEHelper
import time
from random import uniform

class BLEScan():
 timeout = 10.0
 _scanner = None
 devices = []
 devrssi = []
 lastscan = 0

 def __init__(self,blehw,timeout=10.0):
  self.timeout = float(timeout)
  self.devices = []
  self.devrssi = []
  self.lastscan = 0
  self._blehw = blehw
  self._callback = None
  self._scanning = False
  self._scanner = None

 def stop(self):
    try:
     if self._scanner is not None:
      self._scanner.stop()
    except:
     pass
    self._scanning = False

 def scan(self):
    result = False
    devices = []
    self._scanning = True
    try:
     self._scanner = Scanner(self._blehw)
     devices = self._scanner.scan(self.timeout,passive=False)
     result = True
     self.lastscan = time.time()
    except Exception as e:
     print("BLE error: ",e)
     self.devices = []
     self.devrssi = []
    self._scanning = False
    tempdev = []
    temprssi = []
    for dev in devices:
      try:
        temprssi.append(dev.rssi)
        tempdev.append(str(dev.addr).lower().strip())
      except:
        pass
    self.devices = tempdev
    self.devrrsi = temprssi
    return result

 def isdevonline(self,devaddress):
  return (self.getdevrssi(devaddress) != -100)

 def getdevrssi(self,devaddress):
   try:
    for d in range(len(self.devices)):
     if str(devaddress).lower().strip()==str(self.devices[d]).lower().strip():
      return self.devrrsi[d]
    return -100
   except Exception as e:
    return -100

 def getage(self):
  if self.lastscan==0:
   return -1
  try:
   result = time.time()-self.lastscan
  except:
   result = -1
  return result

 def sniff(self, callback,startwait=0):
    self._callback = callback
    _blestatus = BLEHelper.BLEStatus
    self._scanning = True
    time.sleep(startwait)
    _stime = 10
    try:
     if self.timeout==0:
      while self._scanning:
       while _blestatus.norequesters()==False or _blestatus.nodataflows()==False or _blestatus.isscaninprogress():
        time.sleep(1.5)
       print("scan start")#debug
       _blestatus.reportscan(1)
       _stime = int(uniform(8,20))
       print(_stime,'sec')#debug
       try:
        if self._scanner is None:
         self._scanner = Scanner(self._blehw,self._callback)
        else:
         self._scanner.__ble.irq(self._scanner.__bt_irq)
       except Exception as e:
        print("blescan",e)#debug
       try:
        self._scanner.clear()
        self._scanner.start(timeout=_stime,passive=True)
        self._scanner.process()
        self._scanner.stop()
       except:
        pass
       _blestatus.reportscan(0)
       print("scan pause")#debug
       time.sleep(uniform(45,65))
     else:
      while _blestatus.norequesters()==False or _blestatus.nodataflows()==False or _blestatus.isscaninprogress():
        time.sleep(1.5)
      _blestatus.reportscan(1)
      try:
        self._scanner = Scanner(self._blehw,self._callback)
        self._scanner.scan(self.timeout,passive=True)
      except:
        pass
      _blestatus.reportscan(0)
     self.lastscan = time.time()
    except Exception as e:
     _blestatus.reportscan(0)
     print("sniff error",e)#debug
    self._scanning = False

blescan_devices = None

def request_blescan_device(blehw,rtimeout=10.0):
 global blescan_devices
 if blescan_devices is None:
  blescan_devices = BLEScan(blehw,rtimeout)
 return blescan_devices
