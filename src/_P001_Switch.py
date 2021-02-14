########################################################################
##################### GPIO input plugin for mpyEasy ####################
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
 from machine import Pin
except:
 pass

class Plugin(plugin.PluginProto):
 PLUGIN_ID = 1
 PLUGIN_NAME = "Input - Switch Device/Generic GPIO"
 PLUGIN_VALUENAME1 = "State"

 def __init__(self,taskindex): # general init
  plugin.PluginProto.__init__(self,taskindex)
  self.dtype = pglobals.DEVICE_TYPE_SINGLE
  self.vtype = pglobals.SENSOR_TYPE_SWITCH
  self.valuecount = 1
  self.senddataoption = True
  self.timeroption = True
  self.timeroptional = True
  self.inverselogicoption = True
  self.recdataoption = False
  self._pin = None

 def plugin_exit(self):
  try:
   self._pin.irq(handler=None)
  except:
   pass

 def plugin_init(self,enableplugin=None):
  plugin.PluginProto.plugin_init(self,enableplugin)
  self.decimals[0]=0
  if int(self.taskdevicepin[0])>=0 and self.enabled:
   import inc.libhw as libhw
   self._pin = libhw.setgpio(int(self.taskdevicepin[0]))
   self.set_value(1,self._pin.value(),True) # Sync plugin value with real pin state
   try:
    self.plugin_exit()
    if self.taskdevicepluginconfig[0]:
     misc.addLog(pglobals.LOG_LEVEL_INFO,"Registering 10/sec timer as asked")
     self.timer100ms = True
     return True
    self._pin.irq(trigger=3,handler=self.p001_handler)
    misc.addLog(pglobals.LOG_LEVEL_DEBUG,"Event registered to pin "+str(self.taskdevicepin[0]))
    self.timer100ms = False
   except:
    misc.addLog(pglobals.LOG_LEVEL_ERROR,"Event can not be added, register backup timer")
    self.timer100ms = True

 def webform_load(self):
#  ws.addFormNote("Please make sure to select <a href='hardware'>pin configured</a> for input for default (or output to report back its state)!")
  ws.addFormCheckBox("Force 10/sec periodic checking of pin","p001_per",self.taskdevicepluginconfig[0])
#  ws.addFormNote("For output pin, only 10/sec periodic method will work!")
#  ws.addFormNumericBox("De-bounce (ms)","p001_debounce",self.taskdevicepluginconfig[1],0,1000)
  options = ["Normal Switch","Push Button Active Low","Push Button Active High"]
  optionvalues = [0,1,2]
  ws.addFormSelector("Switch Button Type","p001_button",len(optionvalues),options,optionvalues,None,self.taskdevicepluginconfig[2])
  ws.addFormNote("Use only normal switch for output type, i warned you!")
  return True

 def webform_save(self,params):
  if (ws.arg("p001_per",params)=="on"):
   self.taskdevicepluginconfig[0] = True
  else:
   self.taskdevicepluginconfig[0] = False
#  par = ws.arg("p001_debounce",params)
#  try:
#   self.taskdevicepluginconfig[1] = int(par)
#  except:
#   self.taskdevicepluginconfig[1] = 0
  par = ws.arg("p001_button",params)
  try:
   self.taskdevicepluginconfig[2] = int(par)
  except:
   self.taskdevicepluginconfig[2] = 0
  return True

 def plugin_read(self):
  result = False
  if self.initialized:
   self.set_value(1,int(float(self.uservar[0])),True)
   self._lastdataservetime = utime.ticks_ms() # compat
   result = True
  return result

 def p001_handler(self,channel):
  self.pinstate_check(True)

 def timer_ten_per_second(self):
  self.pinstate_check()

 def pinstate_check(self,postcheck=False):
  if self.initialized and self.enabled:
   prevval = int(float(self.uservar[0]))
   inval = self._pin.value()
   if self.pininversed:
    prevval=1-int(prevval)
   outval = prevval
   if int(self.taskdevicepluginconfig[2])==0: # normal switch
    outval = int(inval)
   elif int(self.taskdevicepluginconfig[2])==1: # active low button
    if inval==0:             # if low
     outval = 1-int(prevval) # negate
   elif int(self.taskdevicepluginconfig[2])==2: # active high button
    if inval==1:             # if high
     outval = 1-int(prevval) # negate
   if prevval != outval:
    self.set_value(1,int(outval),True)
    self._lastdataservetime = utime.ticks_ms() # compat
#    if self.taskdevicepluginconfig[2]>0 and self.timer100ms:
#      time.sleep(self.taskdevicepluginconfig[1]/1000) # force debounce if not event driven detection

