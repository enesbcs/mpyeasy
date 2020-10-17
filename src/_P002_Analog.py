########################################################################
####################### Analog plugin for mpyEasy ######################
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
 from machine import Pin, ADC
except:
 pass # do not load

class Plugin(plugin.PluginProto):
 PLUGIN_ID = 2
 PLUGIN_NAME = "Input - Analog"
 PLUGIN_VALUENAME1 = "Analog"

 def __init__(self,taskindex): # general init
  plugin.PluginProto.__init__(self,taskindex)
  self.dtype = pglobals.DEVICE_TYPE_SINGLE
  self.vtype = pglobals.SENSOR_TYPE_SINGLE
  self.pinfilter[0]=2
  self.valuecount = 1
  self.senddataoption = True
  self.timeroption = True
  self.inverselogicoption = False
  self.recdataoption = False
  self.timer100ms = False
  self.readinprogress = False
  self.adc = None

 def plugin_init(self,enableplugin=None):
  plugin.PluginProto.plugin_init(self,enableplugin)
  self.decimals[0]=0
  self.initialized=False
  self.readinprogress = False
  if int(self.taskdevicepin[0])>=0 and self.enabled:
   try:
    self.adc = ADC(Pin(int(self.taskdevicepin[0])))
    self.initialized = True
   except Exception as e:
    misc.addLog(pglobals.LOG_LEVEL_ERROR,"Analog init error: "+str(e))

 def webform_save(self):
     self.plugin_init()
     return True
 
 def plugin_read(self):
  result = False
  if self.initialized and self.enabled and self.readinprogress==False and (self.adc is not None):
    self.readinprogress = True
    try:
     self.set_value(1,self.adc.read(),False)
     result = True
    except:
     pass
    self.plugin_senddata()
    self._lastdataservetime = utime.ticks_ms()
    self.readinprogress = False
  return result
