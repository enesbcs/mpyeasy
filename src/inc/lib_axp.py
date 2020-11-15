#############################################################################
####################### Helper Library for AXP192 ###########################
#############################################################################
#
# Copyright (C) 2020 by Alexander Nagy - https://bitekmindenhol.blog.hu/
#
from inc.axp192.axp192 import AXP192

axp_device = None
axpinit = 0

def request_axp_device(i2cbus):
    global axp_device, axpinit
    try:
     if axp_device is None:
      axp_device = AXP192(i2cbus)
      axpinit = 1
     else:
      axpinit = 1
     return axp_device
    except Exception as e:
     print("axpreq",str(e))#debug
     axpinit = 0
     return None

def init_axp_device(iLD02=True,iLD03=True,iRTC=True,iDCDC1=True,iDCDC3=True):
    global axp_device, axpinit
    if axpinit==1:
     try:
      axp_device.conf.LD02 = iLD02
      axp_device.conf.LD03 = iLD03
      axp_device.conf.RTC  = iRTC
      axp_device.conf.DCDC1 = iDCDC1
      axp_device.conf.DCDC3 = iDCDC3
      axp_device.setup()
      axpinit = 2
      return True
     except Exception as e:
      print("initaxp",str(e))#debug
      axpinit = 0
    elif axpinit==2:
     return True
    else:
     try:
      axp_device = AXP192(i2cbus)
      axpinit = 1
     except:
      pass
    return False

def alter_axp_device(iLD02=None,iLD03=None,iDCDC1=None,iDCDC3=None):
    global axp_device, axpinit
    if axpinit>0:
     try:
      if iLD02 is not None:
       axp_device.conf.LD02 = iLD02
      if iLD03 is not None:
       axp_device.conf.LD03 = iLD03
      if iDCDC1 is not None:
       axp_device.conf.DCDC1 = iDCDC1
      if iDCDC3 is not None:
       axp_device.conf.DCDC3 = iDCDC3
      axp_device._set_power_0x12()
      return True
     except:
      axpinit = 0
      return False
    return False
