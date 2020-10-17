########################################################################
##################### Dummy plugin for mpyEasy #########################
########################################################################
#
# Copyright (C) 2020 by Alexander Nagy - https://bitekmindenhol.blog.hu/
#
import plugin
import pglobals
import misc
import webserver_global as ws
try:
 import utime
except:
 import inc.faketime as utime

class Plugin(plugin.PluginProto):
 PLUGIN_ID = 33
 PLUGIN_NAME = "Generic - Dummy Device"
 PLUGIN_VALUENAME1 = "Dummy1"
 PLUGIN_VALUENAME2 = "Dummy2"
 PLUGIN_VALUENAME3 = "Dummy3"
 PLUGIN_VALUENAME4 = "Dummy4"

 def __init__(self,taskindex): # general init
  plugin.PluginProto.__init__(self,taskindex)
  self.dtype = pglobals.DEVICE_TYPE_DUMMY
  self.vtype = pglobals.SENSOR_TYPE_SINGLE
  self.valuecount = 4
  self.senddataoption = True
  self.timeroption = True
  self.timeroptional = True
  self.recdataoption = True
  self.formulaoption = True

 def plugin_receivedata(self,data):
  if (len(data)>0):
   for x in range(len(data)):
    if data[x] != -9999:
     self.set_value(x+1,data[x],False)
#  print("Data received:",data)

 def getvaluecount(self):
   if self.vtype in [pglobals.SENSOR_TYPE_SINGLE,pglobals.SENSOR_TYPE_SWITCH,pglobals.SENSOR_TYPE_DIMMER,pglobals.SENSOR_TYPE_LONG,pglobals.SENSOR_TYPE_WIND]:
    return 1
   elif self.vtype in [pglobals.SENSOR_TYPE_TEMP_HUM,pglobals.SENSOR_TYPE_TEMP_BARO,pglobals.SENSOR_TYPE_DUAL]:
    return 2
   elif self.vtype in [pglobals.SENSOR_TYPE_TEMP_HUM_BARO,pglobals.SENSOR_TYPE_TRIPLE]:
    return 3
   elif self.vtype == pglobals.SENSOR_TYPE_QUAD:
    return 4
   else:
    return 0

 def plugin_init(self,enableplugin=None):
  plugin.PluginProto.plugin_init(self,enableplugin)
  if int(self.taskdevicepluginconfig[0])>0:
    self.vtype = self.taskdevicepluginconfig[0]
    self.valuecount = self.getvaluecount()
    self.initialized = True
    print("initok")#debug

 def webform_load(self): # create html page for settings
  choice = self.taskdevicepluginconfig[0]
  options = ["Single","Hum","Baro","Hum+Baro","Dual","Triple","Quad","Switch","Dimmer","Long","Wind"]
  optionvalues = [pglobals.SENSOR_TYPE_SINGLE, pglobals.SENSOR_TYPE_TEMP_HUM,pglobals.SENSOR_TYPE_TEMP_BARO,pglobals.SENSOR_TYPE_TEMP_HUM_BARO,pglobals.SENSOR_TYPE_DUAL,pglobals.SENSOR_TYPE_TRIPLE,pglobals.SENSOR_TYPE_QUAD,pglobals.SENSOR_TYPE_SWITCH,pglobals.SENSOR_TYPE_DIMMER,pglobals.SENSOR_TYPE_LONG,pglobals.SENSOR_TYPE_WIND]
  ws.addFormSelector("Simulate Data Type","plugin_033_sensortype",len(options),options,optionvalues,None,choice)
  return True

 def webform_save(self,params): # process settings post reply
  par1 = ws.arg("plugin_033_sensortype",params)
  if par1:
   self.taskdevicepluginconfig[0] = int(par1)
   self.vtype = self.taskdevicepluginconfig[0]
   self.valuecount = self.getvaluecount()
  return True

 def plugin_read(self): # deal with data processing at specified time interval
  result = False
  if self.initialized:
   for x in range(self.valuecount):
    logs = self.gettaskname()+"#"+self.valuenames[x]+"="+str(misc.formatnum(self.uservar[x],self.decimals[x]))
    misc.addLog(pglobals.LOG_LEVEL_INFO,logs)
   self._lastdataservetime = utime.ticks_ms()
   self.plugin_senddata()
   result = True
  return result
