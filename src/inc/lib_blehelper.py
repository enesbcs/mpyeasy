#!/usr/bin/env python3
#############################################################################
###################### Helper Library for BLE ###############################
#############################################################################
#
# Copyright (C) 2020 by Alexander Nagy - https://bitekmindenhol.blog.hu/
#
from micropython import const
import ubluetooth
import time

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = 3
_IRQ_GATTS_READ_REQUEST = 4
_IRQ_SCAN_RESULT = const(5)
_IRQ_SCAN_DONE = const(6)
_IRQ_PERIPHERAL_CONNECT = 7
_IRQ_PERIPHERAL_DISCONNECT = 8
_IRQ_GATTC_SERVICE_RESULT = 9
_IRQ_GATTC_SERVICE_DONE = 10
_IRQ_GATTC_CHARACTERISTIC_RESULT = 11
_IRQ_GATTC_CHARACTERISTIC_DONE = 12
_IRQ_GATTC_DESCRIPTOR_RESULT = const(13)
_IRQ_GATTC_DESCRIPTOR_DONE = const(14)
_IRQ_GATTC_READ_RESULT = 15
_IRQ_GATTC_READ_DONE = 16
_IRQ_GATTC_WRITE_DONE = 17
_IRQ_GATTC_NOTIFY = 18
_IRQ_GATTC_INDICATE = const(19)

class BLEStatusSemaphore():
 scanprogress = False
 requests = []
 dataflow = []
 requestimmediatestopscan = None
 lastflowtime = 0

 def __init__(self):
  self.scanprogress = False
  self.requests = []
  self.dataflow = []
  self.requestimmediatestopscan = None
  self.lastflowtime = 0

 def reportscan(self,status):     # called by scanner program
  if int(status)==0:
   if self.scanprogress==True:
    self.scanprogress = False
    self.requests = []
  else:
   self.scanprogress = True

 def norequesters(self):         # called by scanner program
  if len(self.requests)==0:
   return True
  else:
   return False

 def nodataflows(self):          # called by scanner program
  if len(self.dataflow)==0:
   return True
  else:
   try:
    if self.lastflowtime > 0:
     if time.time()-self.lastflowtime>300: #more than 5minutes?
      self.dataflow = []                   #reset line
   except:
    pass
   return False

 def isscaninprogress(self):            # called by standard ble plugin
  return self.scanprogress

 def forcestopscan(self):
  if (self.requestimmediatestopscan is not None) and self.scanprogress:
   try:
    self.requestimmediatestopscan()
   except:
    pass

 def requeststopscan(self,tskid):        # called by standard ble plugin
  if self.scanprogress == False:
   return True
  if not (int(tskid) in self.requests):
   self.requests.append(int(tskid))

 def registerdataprogress(self,tskid):   # called by standard ble plugin
  if not (int(tskid) in self.dataflow):
   self.dataflow.append(int(tskid))
   self.lastflowtime = time.time()

 def unregisterdataprogress(self,tskid): # called by standard ble plugin
  if (int(tskid) in self.dataflow):
   try:
    self.lastflowtime = 0
    self.dataflow.remove(int(tskid))
   except:
    pass

def bleinit(state=True):
    global BLEDev
    try:
     if BLEDev is None:
      BLEDev = ubluetooth.BLE()
    except:
     return False
    try:
     if state:
      if BLEDev.active()==False:
       BLEDev.active(True)
     else:
      if BLEDev.active():
       BLEDev.active(False)
    except:
     pass

def blestatusinit():
    global BLEStatus
    BLEStatus = BLEStatusSemaphore()

BLEDev = None
try:
 if BLEStatus is None:
  blestatusinit()
except:
  blestatusinit()
