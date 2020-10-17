#############################################################################
######################### BH1750 plugin for mpyEasy #########################
#############################################################################
#
# Copyright (C) 2020 by Alexander Nagy - https://bitekmindenhol.blog.hu/
#
import plugin
import pglobals
import misc
import webserver_global as ws
import utime
import inc.libhw as libhw

class Plugin(plugin.PluginProto):
 PLUGIN_ID = 10
 PLUGIN_NAME = "Environment - BH1750 Lux sensor"
 PLUGIN_VALUENAME1 = "Lux"

 def __init__(self,taskindex): # general init
  plugin.PluginProto.__init__(self,taskindex)
  self.dtype = pglobals.DEVICE_TYPE_I2C
  self.vtype = pglobals.SENSOR_TYPE_SINGLE
  self.readinprogress = 0
  self.valuecount = 1
  self.senddataoption = True
  self.timeroption = True
  self.timeroptional = False
  self.formulaoption = True
  self._nextdataservetime = 0
  self._bh = None

 def plugin_init(self,enableplugin=None):
  plugin.PluginProto.plugin_init(self,enableplugin)
  self.uservar[0] = 0
  self.uservar[1] = 0
  self.readinprogress = 0
  self.initialized = False
  if self.enabled:
    if str(self.taskdevicepluginconfig[0])=="" or str(self.taskdevicepluginconfig[0])=="0":
     return False
    i2cl = None
    try:
     if int(self.i2c)==0:
      i2cl = libhw.i2c0
     elif int(self.i2c)==1:
      i2cl = libhw.i2c1
    except:
     pass
    try:
     self._bh = BH1750(i2cl,int(self.taskdevicepluginconfig[0]))
     self.initialized = self._bh.init
    except:
     self.initialized = False
    if self._bh is None:
     self.initialized = False
    if self.initialized:
     misc.addLog(pglobals.LOG_LEVEL_INFO,"BH1750 initialized")
    else:
     misc.addLog(pglobals.LOG_LEVEL_ERROR,"BH1750 can not be initialized!")
  else:
   self.initialized = False

 def webform_load(self): # create html page for settings
  choice1 = self.taskdevicepluginconfig[0]
  options = ["0x23","0x5c"]
  optionvalues = [0x23,0x5c]
  ws.addFormSelector("I2C address","plugin_010_addr",2,options,optionvalues,None,int(choice1))
  ws.addFormNote("Enable <a href='hardware'>I2C bus</a> first, than <a href='i2cscanner'>search for the used address</a>!")
  return True

 def webform_save(self,params): # process settings post reply
  par = ws.arg("plugin_010_addr",params)
  if par == "":
    par = 0
  self.taskdevicepluginconfig[0] = int(par)
  return True

 def plugin_read(self): # deal with data processing at specified time interval
  result = False
  if self.initialized and self.readinprogress==0 and self.enabled:
   self.readinprogress = 1
   try:
    lux = self._bh.read_luminance()
    self.set_value(1,lux,False)
   except Exception as e:
    misc.addLog(pglobals.LOG_LEVEL_ERROR,"BH1750 read error! "+str(e))
   self.plugin_senddata()
   self._lastdataservetime = utime.ticks_ms()
   result = True
   self.readinprogress = 0
  return result


class BH1750:
    #control constants
    _PWRON = bytes([0x01])
    _PWROFF = bytes([0x00])
    _SOFTRESET = bytes([0x07])
    _ONCE_HIRES_2 = bytes([0x21])

    def __init__(self, i2cbus, i2caddress):
     self.i2c = i2cbus
     self.address = i2caddress
     try:
      self.i2c.writeto(self.address, self._PWROFF)
      utime.sleep_ms(10)
      self.i2c.writeto(self.address, self._PWRON)
      utime.sleep_ms(10)
      self.i2c.writeto(self.address, self._SOFTRESET)
      self.init = True
     except:
      self.init = False

    def read_luminance(self):
     val = None
     if self.init:
      try:
       self.i2c.writeto(self.address, self._ONCE_HIRES_2)
       utime.sleep_ms(180)
       data = self.i2c.readfrom(self.address,2)
       val = (data[0]<<8 | data[1]) / (1.2)
      except:
       return None
     return val
