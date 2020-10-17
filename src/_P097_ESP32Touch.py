########################################################################
################# ESP32 Touch input plugin for mpyEasy #################
########################################################################
#
# Copyright (C) 2020 by Alexander Nagy - https://bitekmindenhol.blog.hu/
#
import plugin
import pglobals
import misc
import webserver_global as ws
import utime
try:
 from machine import Pin, TouchPad
except:
 pass # do not load

class Plugin(plugin.PluginProto):
 PLUGIN_ID = 97
 PLUGIN_NAME = "Input - ESP32 Touch"
 PLUGIN_VALUENAME1 = "Touch"

 def __init__(self,taskindex): # general init
  plugin.PluginProto.__init__(self,taskindex)
  self.dtype = pglobals.DEVICE_TYPE_SINGLE
  self.vtype = pglobals.SENSOR_TYPE_SWITCH
  self.pinfilter[0]=4
  self.valuecount = 1
  self.senddataoption = True
  self.timeroption = True
  self.timeroptional = True
  self.inverselogicoption = True
  self.recdataoption = False
  self._pin = None
  self.refvalue = 1500

 def plugin_init(self,enableplugin=None):
  plugin.PluginProto.plugin_init(self,enableplugin)
  self.decimals[0]=0
  self.initialized = False
  self.timer100ms = False
  if int(self.taskdevicepin[0])>=0 and self.enabled:
   try:
    self._pin = TouchPad( Pin(int(self.taskdevicepin[0])) )
    self.refvalue = int(self._pin.read()/2) # get value at startup, hope that it is in non-touched state, for reference
    self._pin.config(200)
    self.timer100ms = True
    self.initialized = True
    misc.addLog(pglobals.LOG_LEVEL_DEBUG,"Touch init, ref: "+str(self.refvalue))
   except Exception as e:
    misc.addLog(pglobals.LOG_LEVEL_ERROR,"Touch config failed "+str(e))

 def plugin_read(self):
  result = False
  if self.initialized:
   self.set_value(1,int(float(self.uservar[0])),True) # return with saved value
   self._lastdataservetime = utime.ticks_ms() # compat
   result = True
  return result

 def timer_ten_per_second(self):
  if self.initialized and self.enabled:
   prevval = int(float(self.uservar[0]))
   if (self._pin.read() < self.refvalue): # touch value read by 10 times per sec, report if change occures
    aval = 1
   else:
    aval = 0
   if prevval != aval:
    self.set_value(1,int(aval),True)
    self._lastdataservetime = utime.ticks_ms() # compat
