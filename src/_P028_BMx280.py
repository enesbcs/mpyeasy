#############################################################################
##################### BMP280/BME280 plugin for mpyEasy ######################
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
from inc.bme280.bme280_float import BME280

class Plugin(plugin.PluginProto):
 PLUGIN_ID = 28
 PLUGIN_NAME = "Environment - BMP280/BME280"
 PLUGIN_VALUENAME1 = "Temperature"
 PLUGIN_VALUENAME2 = "Humidity"
 PLUGIN_VALUENAME3 = "Pressure"

 def __init__(self,taskindex): # general init
  plugin.PluginProto.__init__(self,taskindex)
  self.dtype = pglobals.DEVICE_TYPE_I2C
  self.vtype = pglobals.SENSOR_TYPE_TEMP_HUM_BARO
  self.readinprogress = 0
  self.valuecount = 3
  self.senddataoption = True
  self.timeroption = True
  self.timeroptional = False
  self.formulaoption = True
  self._nextdataservetime = 0
  self._bme = None
  self.hashumidity = False

 def plugin_init(self,enableplugin=None):
  plugin.PluginProto.plugin_init(self,enableplugin)
  self.uservar[0] = 0
  self.uservar[1] = 0
  self.uservar[2] = 0
  self.readinprogress = 0
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
     self._bme = BME280(i2c=i2cl,address=int(self.taskdevicepluginconfig[0]))
     self.initialized = True
    except:
     self.initialized = False
    if self._bme is None:
     self.initialized = False
  if self.initialized and self.enabled:
   try:
    chiptype = int(self._bme.get_chip_id()[0])
   except:
    chiptype = 0
   self.hashumidity = False
   chipname = "Unknown"
   if chiptype == 0x60:
    chipname = "BME280"
    self.hashumidity = True
    self.vtype = pglobals.SENSOR_TYPE_TEMP_HUM_BARO
   elif chiptype in [0x56,0x57,0x58]:
    chipname = "BMP280"
    self.vtype = pglobals.SENSOR_TYPE_TEMP_EMPTY_BARO
   misc.addLog(pglobals.LOG_LEVEL_INFO,chipname+" ("+str(chiptype)+") initialized, Humidity: "+str(self.hashumidity))
  else:
   misc.addLog(pglobals.LOG_LEVEL_ERROR,"BMP280/BME280 can not be initialized!")

 def webform_load(self): # create html page for settings
  choice1 = self.taskdevicepluginconfig[0]
  options = ["0x76","0x77"]
  optionvalues = [0x76,0x77]
  ws.addFormSelector("I2C address","plugin_028_addr",2,options,optionvalues,None,int(choice1))
  ws.addFormNote("Enable <a href='hardware'>I2C bus</a> first, than <a href='i2cscanner'>search for the used address</a>!")
  return True

 def webform_save(self,params): # process settings post reply
  par = ws.arg("plugin_028_addr",params)
  if par == "":
    par = 0
  self.taskdevicepluginconfig[0] = int(par)
  return True

 def plugin_read(self): # deal with data processing at specified time interval
  result = False
  if self.initialized and self.readinprogress==0 and self.enabled and self._bme is not None:
   self.readinprogress = 1
   try:
    temp, press, hum = self._bme.read_compensated_data()
    self.set_value(1,temp,False)
    self.set_value(2,hum,False)
    self.set_value(3,(press/100),False) #hPa
   except Exception as e:
    misc.addLog(pglobals.LOG_LEVEL_ERROR,"BMx280 read error! "+str(e))
   self.plugin_senddata()
   self._lastdataservetime = utime.ticks_ms()
   result = True
   self.readinprogress = 0
  return result
