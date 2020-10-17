#############################################################################
##################### SI7021/HTU21D plugin for mpyEasy ######################
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
 PLUGIN_ID = 14
 PLUGIN_NAME = "Environment - SI7021/HTU21D"
 PLUGIN_VALUENAME1 = "Temperature"
 PLUGIN_VALUENAME2 = "Humidity"

 def __init__(self,taskindex): # general init
  plugin.PluginProto.__init__(self,taskindex)
  self.dtype = pglobals.DEVICE_TYPE_I2C
  self.vtype = pglobals.SENSOR_TYPE_TEMP_HUM
  self.readinprogress = 0
  self.valuecount = 2
  self.senddataoption = True
  self.timeroption = True
  self.timeroptional = False
  self.formulaoption = True
  self._nextdataservetime = 0
  self._htu = None

 def plugin_init(self,enableplugin=None):
  plugin.PluginProto.plugin_init(self,enableplugin)
  self.uservar[0] = 0
  self.uservar[1] = 0
  self.readinprogress = 0
  if self.enabled:
    i2cl = None
    try:
     if int(self.i2c)==0:
      i2cl = libhw.i2c0
     elif int(self.i2c)==1:
      i2cl = libhw.i2c1
    except:
     pass
    try:
     self._htu = HTU21D(i2cl)
     self.initialized = self._htu.init
    except Exception as e:
     self.initialized = False
    if self._htu is None:
     self.initialized = False
    if self.initialized:
     misc.addLog(pglobals.LOG_LEVEL_INFO,"HTU21D/Si7021 initialized")
    else:
     misc.addLog(pglobals.LOG_LEVEL_ERROR,"HTU21D/Si7021 can not be initialized!")

 def plugin_read(self): # deal with data processing at specified time interval
  result = False
  if self.initialized and self.readinprogress==0 and self.enabled:
   self.readinprogress = 1
   try:
    temp = self._htu.read_temperature()
    hum  = self._htu.read_humidity()
    if temp is not None and hum is not None:
     self.set_value(1,temp,False)
     self.set_value(2,hum,False)
   except Exception as e:
    misc.addLog(pglobals.LOG_LEVEL_ERROR,"HTU21 read error! "+str(e))
   self.plugin_senddata()
   self._lastdataservetime = utime.ticks_ms()
   result = True
   self.readinprogress = 0
  return result


class HTU21D:
    #control constants
    _I2C_ADDRESS = 0x40

    _SOFTRESET = bytes([0xFE])
    _TRIGGER_TEMPERATURE_NO_HOLD = bytes([0xF3])
    _TRIGGER_HUMIDITY_NO_HOLD = bytes([0xF5])

    def __init__(self, i2cbus):
     self.i2c = i2cbus
     try:
      self.i2c.writeto(self._I2C_ADDRESS, self._SOFTRESET)
      self.init = True
     except Exception as e:
      self.init = False

    def read_temperature(self):
     val = None
     if self.init:
      try:
       self.i2c.writeto(self._I2C_ADDRESS, self._TRIGGER_TEMPERATURE_NO_HOLD)
       utime.sleep_ms(50)
       temp = self.i2c.readfrom(self._I2C_ADDRESS, 3)
       temp2 = temp[0] << 8
       temp2 = temp2 | temp[1]
       val = (175.72 * temp2 / 65536) - 46.85
      except Exception as e:
       return None
     return val

    def read_humidity(self):
     val = None
     if self.init:
      try:
       self.i2c.writeto(self._I2C_ADDRESS, self._TRIGGER_HUMIDITY_NO_HOLD)
       utime.sleep_ms(50)
       rh = self.i2c.readfrom(self._I2C_ADDRESS, 3)
       rh2 = rh[0] << 8
       rh2 = rh2 | rh[1]
       val = (125 * rh2 / 65536) - 6
      except:
       return None
     return val
