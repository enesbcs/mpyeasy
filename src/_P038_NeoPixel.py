#############################################################################
###################### Neopixel plugin for mpyEasy ##########################
#############################################################################
#
# Available commands:
#  NeoPixel,<led nr>,<red 0-255>,<green 0-255>,<blue 0-255>
#  NeoPixelAll,<red 0-255>,<green 0-255>,<blue 0-255>
#  NeoPixelLine,<start led nr>,<stop led nr>,<red 0-255>,<green 0-255>,<blue 0-255>
#
# Copyright (C) 2020 by Alexander Nagy - https://bitekmindenhol.blog.hu/
#
import plugin
import pglobals
import misc
import webserver_global as ws
import utime
try:
 import neopixel
 from machine import Pin
except:
 pass # do not load

class Plugin(plugin.PluginProto):
 PLUGIN_ID = 38
 PLUGIN_NAME = "Output - NeoPixel Basic"
 PLUGIN_VALUENAME1 = ""

 def __init__(self,taskindex): # general init
  plugin.PluginProto.__init__(self,taskindex)
  self.dtype = pglobals.DEVICE_TYPE_SINGLE
  self.vtype = pglobals.SENSOR_TYPE_NONE
  self.pinfilter[0]=1
  self.valuecount = 0
  self.senddataoption = False
  self.timeroption = False
  self.timeroptional = False
  self._led = None
  self.pixelnum = 0

 def plugin_init(self,enableplugin=None):
  plugin.PluginProto.plugin_init(self,enableplugin)
  if enableplugin == False or self.enabled == False:
    self.clearall()
  self.initialized = False
  if int(self.taskdevicepin[0])>=0 and self.enabled:
   self.pixelnum = int(self.taskdevicepluginconfig[0])
   try:
     self._led = neopixel.NeoPixel(Pin(int(self.taskdevicepin[0])),self.pixelnum)
     self.clearall()
     self.initialized = True
   except Exception as e:
     misc.addLog(pglobals.LOG_LEVEL_ERROR,"Neopixel error "+str(e))
  else:
   self._led = None
   self.pixelnum = 0

 def webform_load(self): # create html page for settings
  ws.addFormNumericBox("Led Count","p038_leds",self.taskdevicepluginconfig[0],1,2700)
  return True

 def webform_save(self,params): # process settings post reply
   changed = False

   par = ws.arg("p038_leds",params)
   if par == "":
    par = 1
   if str(self.taskdevicepluginconfig[0]) != str(par):
    changed = True
    self.taskdevicepluginconfig[0] = int(par)

   if changed:
    self.plugin_init()
   return True

 def clearall(self):
  try:
    if self._led is not None:
     for l in range(self.pixelnum):
      self._led[l] = (0,0,0)
     self._led.write()
  except:
    pass

 def plugin_exit(self):
  self.clearall()

 def plugin_write(self,cmd):
  res = False
  if self.initialized == False:
   return res
  cmdarr = cmd.split(",")
  cmdarr[0] = cmdarr[0].strip().lower()
  if cmdarr[0] == "neopixel":
   pin = -1
   try:
    pin = int(cmdarr[1].strip())
   except:
    pin = -1
   try:
    r = int(cmdarr[2].strip())
    g = int(cmdarr[3].strip())
    b = int(cmdarr[4].strip())
   except:
    misc.addLog(pglobals.LOG_LEVEL_ERROR,"Neopixel error "+str(e))
    r = 0
    g = 0
    b = 0
   if pin>0 and self.pixelnum>=pin:
    pin = pin-1  # pixel number is 0 based
    try:
     self._led[pin] = (r,g,b)
     self._led.write()
     res = True
    except Exception as e:
     misc.addLog(pglobals.LOG_LEVEL_ERROR,"Neopixel error "+str(e))
     res = False
    if res:
     misc.addLog(pglobals.LOG_LEVEL_DEBUG,"NeoPixel "+str(pin+1)+" set to ("+str(r)+","+str(g)+","+str(b)+")")
  elif cmdarr[0]=="neopixelall":
   col = 0
   try:
    r = int(cmdarr[1].strip())
    g = int(cmdarr[2].strip())
    b = int(cmdarr[3].strip())
   except:
    misc.addLog(pglobals.LOG_LEVEL_ERROR,"Neopixel error "+str(e))
    r = 0
    g = 0
    b = 0
   try:
     for p in range(self.pixelnum):
      self._led[p] = (r,g,b)
     self._led.write()
     res = True
   except Exception as e:
     misc.addLog(pglobals.LOG_LEVEL_ERROR,"Neopixel error "+str(e))
     res = False
   if res:
    misc.addLog(pglobals.LOG_LEVEL_DEBUG,"All NeoPixel set to ("+str(r)+","+str(g)+","+str(b)+")")
  elif cmdarr[0]=="neopixelline":
   col = 0
   pin1 = -1
   pin2 = -1
   try:
    pin1 = int(cmdarr[1].strip())-1 # zero based
   except:
    pin1 = 0
   if pin1>=self.pixelnum:
    return False
   try:
    pin2 = int(cmdarr[2].strip())-1 # zero based
   except:
    pin2 = self.pixelnum
   if pin2<pin1:
    pin2=pin1+1
   if pin2>=self.pixelnum:
    pin2=self.pixelnum-1
   try:
    r = int(cmdarr[3].strip())
    g = int(cmdarr[4].strip())
    b = int(cmdarr[5].strip())
   except:
    misc.addLog(pglobals.LOG_LEVEL_ERROR,"Neopixel error "+str(e))
    r = 0
    g = 0
    b = 0
   try:
     for p in range(pin1,pin2+1):
      self._led[p] = (r,g,b)
     self._led.write()
     res = True
   except Exception as e:
     misc.addLog(pglobals.LOG_LEVEL_ERROR,"Neopixel error "+str(e))
     res = False
   if res:
    misc.addLog(pglobals.LOG_LEVEL_DEBUG,"NeoPixel "+str(pin1+1)+"-"+str(pin2+1)+" set to ("+str(r)+","+str(g)+","+str(b)+")")
  return res
