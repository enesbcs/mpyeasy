#############################################################################
###################### BLE Mi Flora plugin for mpyEasy ######################
#############################################################################
#
# Xiaomi Mi Flora Bluetooth plant sensor plugin.
#
# Copyright (C) 2020 by Alexander Nagy - https://bitekmindenhol.blog.hu/
#
import plugin
import webserver_global as ws
import pglobals
import misc
import inc.lib_miflora as MiFloraMonitor
import inc.lib_blehelper as BLEHelper
import time
import gc
import utime
try:
 import ubinascii as binascii
except ImportError:
 import binascii

class Plugin(plugin.PluginProto):
 PLUGIN_ID = 515
 PLUGIN_NAME = "Environment - BLE Xiaomi Mi Flora (TESTING)"
 PLUGIN_VALUENAME1 = "Temperature" # Temperature/Brightness/Moisture/Conductivity

 def __init__(self,taskindex): # general init
  plugin.PluginProto.__init__(self,taskindex)
  self.dtype = pglobals.DEVICE_TYPE_BLE
  self.vtype = pglobals.SENSOR_TYPE_SINGLE
  self.valuecount = 1
  self.senddataoption = True
  self.recdataoption = False
  self.timeroption = True
  self.timeroptional = True
  self.formulaoption = True
  self._flora = None
  self.readinprogress=0
  self.initialized=False
  self.failures = 0
  self._blestatus = None

 def webform_load(self): # create html page for settings
  ws.addFormTextBox("Device Address","plugin_515_addr",str(self.taskdevicepluginconfig[0]),20)
  ws.addFormNote("Enable blueetooth then <a href='blescanner'>scan 'Flower care' address</a> first.")
  choice1 = self.taskdevicepluginconfig[1]
  choice2 = self.taskdevicepluginconfig[2]
  choice3 = self.taskdevicepluginconfig[3]
  choice4 = self.taskdevicepluginconfig[4]
  options = ["None","Temperature","Brightness", "Moisture","Conductivity","Battery"]
  optionvalues = [0,1,2,3,4,5]
  ws.addFormSelector("Indicator1","plugin_515_ind0",len(options),options,optionvalues,None,choice1)
  ws.addFormSelector("Indicator2","plugin_515_ind1",len(options),options,optionvalues,None,choice2)
  ws.addFormSelector("Indicator3","plugin_515_ind2",len(options),options,optionvalues,None,choice3)
  ws.addFormSelector("Indicator4","plugin_515_ind3",len(options),options,optionvalues,None,choice4)
  return True

 def webform_save(self,params): # process settings post reply
  try:
   self.taskdevicepluginconfig[0] = str(ws.arg("plugin_515_addr",params)).strip()
   for v in range(0,4):
    par = ws.arg("plugin_515_ind"+str(v),params)
    if par == "":
     par = 0
    else:
     par=int(par)
    if str(self.taskdevicepluginconfig[v+1])!=str(par):
     self.uservar[v] = 0
    self.taskdevicepluginconfig[v+1] = par
    options = ["None","Temperature","Brightness", "Moisture","Conductivity","Battery"]
    if int(par)>0 and self.valuecount!=v+1:
     self.valuecount = (v+1)
     self.valuenames[v]=options[par]
   if self.valuecount == 1:
    self.vtype = pglobals.SENSOR_TYPE_SINGLE
   elif self.valuecount == 2:
    self.vtype = pglobals.SENSOR_TYPE_DUAL
   elif self.valuecount == 3:
    self.vtype = pglobals.SENSOR_TYPE_TRIPLE
   elif self.valuecount == 4:
    self.vtype = pglobals.SENSOR_TYPE_QUAD
  except Exception as e:
   misc.addLog(pglobals.LOG_LEVEL_ERROR,+str(e))
  return True

 def plugin_init(self,enableplugin=None):
  plugin.PluginProto.plugin_init(self,enableplugin)
  self.taskdevicepluginconfig[0] = str(self.taskdevicepluginconfig[0]).strip()
  self.readinprogress=0
  self.initialized=False
  self.failures = 0
  if self.valuecount == 1:
    self.vtype = pglobals.SENSOR_TYPE_SINGLE
  elif self.valuecount == 2:
    self.vtype = pglobals.SENSOR_TYPE_DUAL
  elif self.valuecount == 3:
    self.vtype = pglobals.SENSOR_TYPE_TRIPLE
  elif self.valuecount == 4:
    self.vtype = pglobals.SENSOR_TYPE_QUAD
  if self.enabled and self.taskdevicepluginconfig[0]!="" and self.taskdevicepluginconfig[0]!="0":
   try:
     self._blestatus  = BLEHelper.BLEStatus
     BLEHelper.bleinit(True)
   except:
     pass
   self.ports = str(self.taskdevicepluginconfig[0])
   try:
    if self.interval<60:
     to = self.interval
    else:
     to = 60
    self._flora = MiFloraMonitor.request_flora_device(BLEHelper.BLEDev,str(self.taskdevicepluginconfig[0]),to)
    self.initialized = True
   except Exception as e:
    misc.addLog(pglobals.LOG_LEVEL_ERROR,"MiFlora error: "+str(e))
  else:
   self.ports = ""

 def plugin_read(self): # deal with data processing at specified time interval
  result = False
  if self.initialized and self.readinprogress==0 and self.enabled:
   try:
    if self._blestatus.isscaninprogress():
     self._blestatus.requeststopscan(self.taskindex)
     return False
   except Exception as e:
    return False
   if self._blestatus.nodataflows()==False: # BLE is in use
    return False
   self._blestatus.registerdataprogress(self.taskindex)
   self.readinprogress = 1
   try:
    self.battery = self._flora.battery_level()
   except:
    self.battery = 255
   failed = False
   for v in range(0,4):
    try:
     vtype = int(self.taskdevicepluginconfig[v+1])
     if vtype != 0:
      tvalue = self.p515_get_value(vtype)
      if v==0 and self._flora._readok == False:
        for i in range(3):
         utime.sleep(2)
         tvalue = self.p515_get_value(vtype)
         if self._flora._readok:
             break
      if (tvalue != -100):
       self.set_value(v+1,tvalue,False)
      else:
       failed = True
    except Exception as e:
        print("p515 read",str(e))        
   if self.interval>10:
    try:
     self._flora.disconnect()
    except:
     pass
   self._blestatus.unregisterdataprogress(self.taskindex)
   if failed==False:
    self.plugin_senddata()
    self._lastdataservetime = utime.ticks_ms()
   result = True
   self.readinprogress = 0
  return result

 def p515_get_value(self,ptype):
  value = -100
  try:
   if ptype == 1:
    value = self._flora.get_temperature()
   elif ptype == 2:
    value = self._flora.get_light()
   elif ptype == 3:
    value = self._flora.get_moisture()
   elif ptype == 4:
    value = self._flora.get_conductivity()
   elif ptype == 5:
    value = self._flora.battery_level()
   self.failures = 0
  except Exception as e:
    self.failures += 1
    misc.addLog(pglobals.LOG_LEVEL_ERROR,"MiFlora error: "+str(e))
    if self.failures>10:
     self.enabled=False
  return value
