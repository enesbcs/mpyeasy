#############################################################################
######################## Ping plugin for mpyEasy ############################
#############################################################################
#
# Ping plugin for testing availability of a remote TCP/IP station.
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
from inc.uping import ping

class Plugin(plugin.PluginProto):
 PLUGIN_ID = 89
 PLUGIN_NAME = "Network - Ping"
 PLUGIN_VALUENAME1 = "State"

 def __init__(self,taskindex): # general init
  plugin.PluginProto.__init__(self,taskindex)
  self.dtype = pglobals.DEVICE_TYPE_DUMMY
  self.vtype = pglobals.SENSOR_TYPE_SWITCH
  self.readinprogress = 0
  self.valuecount = 1
  self.senddataoption = True
  self.timeroption = True
  self.timeroptional = False
  self.formulaoption = True

 def plugin_init(self,enableplugin=None):
  plugin.PluginProto.plugin_init(self,enableplugin)
  self.decimals[0] = 0
  if self.enabled:
#   self.set_value(1,1,False)
   self.initialized = True
   self.readinprogress = 0
   try:
    if self.taskdevicepluginconfig[1]<=0:
     self.taskdevicepluginconfig[1] = 100
   except:
     self.taskdevicepluginconfig[1] = 100

 def webform_load(self):
  ws.addFormTextBox("Remote station address","plugin_89_addr",str(self.taskdevicepluginconfig[0]),128)
  ws.addFormNumericBox("Timeout","plugin_89_timeout",self.taskdevicepluginconfig[1],0,10000)
  ws.addUnit("millisec")
  return True

 def webform_save(self,params):
  self.taskdevicepluginconfig[0] = str(ws.arg("plugin_89_addr",params)).strip()
  if str(self.taskdevicepluginconfig[0])=="0":
   self.taskdevicepluginconfig[0]=""
  try:
   self.taskdevicepluginconfig[1] = int(ws.arg("plugin_89_timeout",params))
   if self.taskdevicepluginconfig[1]<=0:
    self.taskdevicepluginconfig[1] = 100
  except:
   self.taskdevicepluginconfig[1] = 100
  return True

 def plugin_read(self):
  result = False
  reply = 0
  if self.initialized and self.enabled and self.readinprogress==0:
   self.readinprogress = 1
   try:
    trans, reply = ping(self.taskdevicepluginconfig[0],count=3,timeout=self.taskdevicepluginconfig[1],quiet=True)
   except Exception as e:
    reply = 0
   if reply<1:
    res = 0
   else:
    res = 1
#   print(reply,res)
   self.set_value(1,res,True)
   self._lastdataservetime = utime.ticks_ms()
   result = True
   self.readinprogress = 0
  return result
