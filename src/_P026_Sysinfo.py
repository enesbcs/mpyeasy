#############################################################################
############ Generic System Information plugin for mpyEasy ##################
#############################################################################
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
try:
 import unet
 import esp_os
except:
 pass

class Plugin(plugin.PluginProto):
 PLUGIN_ID = 26
 PLUGIN_NAME = "Generic - System Info"
 PLUGIN_VALUENAME1 = "Value1"
 PLUGIN_VALUENAME2 = "Value2"
 PLUGIN_VALUENAME3 = "Value3"
 PLUGIN_VALUENAME4 = "Value4"

 def __init__(self,taskindex): # general init
  plugin.PluginProto.__init__(self,taskindex)
  self.dtype = pglobals.DEVICE_TYPE_DUMMY
  self.vtype = pglobals.SENSOR_TYPE_QUAD
  self.readinprogress = 0
  self.valuecount = 4
  self.senddataoption = True
  self.timeroption = True
  self.timeroptional = False
  self.formulaoption = True

 def webform_load(self): # create html page for settings
  choice1 = self.taskdevicepluginconfig[0]
  choice2 = self.taskdevicepluginconfig[1]
  choice3 = self.taskdevicepluginconfig[2]
  choice4 = self.taskdevicepluginconfig[3]
  options = ["None","Uptime","Free RAM", "Wifi RSSI","CPU Temp"]
  optionvalues = [0,1,2,3,4]
  ws.addFormSelector("Indicator1","plugin_026_ind0",len(options),options,optionvalues,None,choice1)
  ws.addFormSelector("Indicator2","plugin_026_ind1",len(options),options,optionvalues,None,choice2)
  ws.addFormSelector("Indicator3","plugin_026_ind2",len(options),options,optionvalues,None,choice3)
  ws.addFormSelector("Indicator4","plugin_026_ind3",len(options),options,optionvalues,None,choice4)
  return True

 def webform_save(self,params): # process settings post reply
  for v in range(0,4):
   par = ws.arg("plugin_026_ind"+str(v),params)
   if par == "":
    par = 0
   if str(self.taskdevicepluginconfig[v])!=str(par):
    self.uservar[v] = 0
   self.taskdevicepluginconfig[v] = int(par)
   if int(par)>0:
    self.valuecount = (v+1)
  if self.valuecount == 1:
   self.vtype = pglobals.SENSOR_TYPE_SINGLE
  elif self.valuecount == 2:
   self.vtype = pglobals.SENSOR_TYPE_DUAL
  elif self.valuecount == 3:
   self.vtype = pglobals.SENSOR_TYPE_TRIPLE
  elif self.valuecount == 4:
   self.vtype = pglobals.SENSOR_TYPE_QUAD
  return True

 def plugin_read(self): # deal with data processing at specified time interval
  result = False
  if self.initialized and self.readinprogress==0:
   self.readinprogress = 1
   vtype = 0
   for v in range(0,4):
    vtype = int(self.taskdevicepluginconfig[v])
    if vtype != 0:
     self.set_value(v+1,self.p026_get_value(vtype),False)
   self.plugin_senddata()
   self._lastdataservetime = utime.ticks_ms()
   result = True
   self.readinprogress = 0
  return result

 def p026_get_value(self,ptype):
   value = 0
   if ptype == 1:
    value = misc.getuptime(0)
   elif ptype == 2:
    value = esp_os.FreeMem()
   elif ptype == 3:
    value = unet.get_rssi()
   elif ptype == 4:
    value = esp_os.read_cpu_temp()
   return value
