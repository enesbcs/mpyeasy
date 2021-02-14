#############################################################################
##################### Dallas DS18B20 plugin for mpyEasy #####################
#############################################################################
#
# Copyright (C) 2020 by Alexander Nagy - https://bitekmindenhol.blog.hu/
#
import plugin
import pglobals
import misc
import webserver_global as ws
import utime
try:
 import onewire, ds18x20
 from machine import Pin
except:
 pass # do not load

class Plugin(plugin.PluginProto):
 PLUGIN_ID = 4
 PLUGIN_NAME = "Environment - DS18b20"
 PLUGIN_VALUENAME1 = "Temperature"

 def __init__(self,taskindex): # general init
  plugin.PluginProto.__init__(self,taskindex)
  self.dtype = pglobals.DEVICE_TYPE_SINGLE
  self.vtype = pglobals.SENSOR_TYPE_SINGLE
  self.readinprogress = 0
  self.valuecount = 1
  self.senddataoption = True
  self.timeroption = True
  self.timeroptional = False
  self.formulaoption = True
  self._ds = None
  self._roms = []
  self._arom = 0

 def plugin_init(self,enableplugin=None):
  plugin.PluginProto.plugin_init(self,enableplugin)
  self.initialized = False
  try:
    self._ds = ds18x20.DS18X20(onewire.OneWire(Pin( int(self.taskdevicepin[0]) )))
    misc.addLog(pglobals.LOG_LEVEL_DEBUG,"Dallas bus initialized!")
    self.initialized = True
  except Exception as e:
    self._ds = None
    misc.addLog(pglobals.LOG_LEVEL_ERROR,"Dallas device can not be initialized!")
  if str(self.taskdevicepluginconfig[0])=="0" or str(self.taskdevicepluginconfig[0]).strip()=="":
   self.initialized = False
   if self.enabled and enableplugin:
    misc.addLog(pglobals.LOG_LEVEL_INFO,"Dallas device not selected!")
  if self.initialized:
    self.ports = self.taskdevicepluginconfig[0]
    self._roms = self.find_dsb_devices()
    for rom in self._roms:
        if self.addresstostr(rom)==self.taskdevicepluginconfig[0]:
         self._arom = rom
         break
  else:
    self.ports = ""
  self.readinprogress = 0

 def webform_load(self):
  choice1 = self.addresstostr(self.taskdevicepluginconfig[0])
  self._roms = self.find_dsb_devices()
  options = []
  for opts in self._roms:
      options.append(self.addresstostr(opts))
  if len(options)>0:
   ws.addHtml("<tr><td>Device Address:<td>")
   ws.addSelector_Head("p004_addr",True)
   for o in range(len(options)):
    ws.addSelector_Item(options[o],options[o],(str(options[o])==str(choice1)),False)
   ws.addSelector_Foot()
  return True

 def webform_save(self,params):
  par = ws.arg("p004_addr",params)
  self.taskdevicepluginconfig[0] = par
  self.plugin_init()
  return True

 def plugin_read(self): # deal with data processing at specified time interval
  result = False
  if self.initialized and self.readinprogress==0 and self.enabled:
   self.readinprogress = 1
   try:
    succ, temp = self.read_temperature()
    if succ:
     self.set_value(1,temp,True)
    else:
     misc.addLog(pglobals.LOG_LEVEL_ERROR,"Dallas read error!")
   except Exception as e:
    misc.addLog(pglobals.LOG_LEVEL_ERROR,"Dallas read error! "+str(e))
    self.enabled = False
   self._lastdataservetime = utime.ticks_ms()
   result = True
   self.readinprogress = 0
  return result

 def find_dsb_devices(self):
  rlist = []
  try:
   rlist = self._ds.scan()
  except Exception as e:
   rlist = []
  return rlist

 def read_temperature(self):
   lines = []
   temp = 0
   try:
    self._ds.convert_temp()
    utime.sleep_ms(750)
    temp = self._ds.read_temp(self._arom)
   except:
    return False, 0
   return True, float(temp)

 def addresstostr(self,addrarray):
    try:
      tarr = hex(int.from_bytes(addrarray, 'little'))
    except:
      tarr = ""
    return str(tarr)
