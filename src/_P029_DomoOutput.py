#############################################################################
################# (Domoticz) Output helper for mpyEasy ######################
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
 from machine import Pin
except:
 pass # do not load
import settings

class Plugin(plugin.PluginProto):
 PLUGIN_ID = 29
 PLUGIN_NAME = "Output - Domoticz Output Helper (No feedback)"
 PLUGIN_VALUENAME1 = "State"

 def __init__(self,taskindex): # general init
  plugin.PluginProto.__init__(self,taskindex)
  self.dtype = pglobals.DEVICE_TYPE_SINGLE
  self.vtype = pglobals.SENSOR_TYPE_SWITCH
  self.pinfilter[0]=1
  self.valuecount = 1
  self.senddataoption = True
  self.recdataoption = True
  self.inverselogicoption = False
  self._pin = None

 def plugin_init(self,enableplugin=None):
  plugin.PluginProto.plugin_init(self,enableplugin)
  self.decimals[0]=0
  if self.enabled:
   try:
    import inc.libhw as libhw
    self._pin = libhw.setgpio(self.taskdevicepin[0])
    self.initialized = True
   except Exception as e:
    self.initialized = False
    misc.addLog(pglobals.LOG_LEVEL_ERROR,self.taskname+": "+str(e))
   self.sync()
  else:
   self.timer1s = False

 def webform_load(self):
  ws.addFormNote("Please make sure to select <a href='hardware'>pin configured for Output!</a>")
  ws.addFormCheckBox("Preserve state at startup","p029_preserve",self.taskdevicepluginconfig[0])
  ws.addFormNumericBox("Auto OFF after","p029_off",self.taskdevicepluginconfig[1],0,3600)
  ws.addUnit("s")
  return True

 def webform_save(self,params):
  if (ws.arg("p029_preserve",params)=="on"):
   self.taskdevicepluginconfig[0] = True
  else:
   self.taskdevicepluginconfig[0] = False
  par = ws.arg("p029_off",params)
  try:
    self.taskdevicepluginconfig[1] = int(par)
  except:
    self.taskdevicepluginconfig[1] = 0
  self.sync()
  return True

 def sync(self):
  if self.enabled:
   if self.taskdevicepin[0]>=0:
    try:
     v1 = self._pin.value()
    except:
     v1 = 0
    if v1 != self.uservar[0]:
     if self.taskdevicepluginconfig[0]==True:
      self.set_value(1,int(self.uservar[0]),True) # restore previous state from uservar
      misc.addLog(pglobals.LOG_LEVEL_INFO,self.taskname+": Restoring previous GPIO value "+str(self.uservar[0]))
     else:
      self.uservar[0] = v1 # store actual pin state into uservar
      misc.addLog(pglobals.LOG_LEVEL_INFO,self.taskname+": Syncing actual GPIO value "+str(v1))
    self._lastdataservetime = utime.ticks_ms()
   if self.initialized:
    if self.taskdevicepluginconfig[0]==True:
     sps = "en"
    else:
     sps = "dis"
    misc.addLog(pglobals.LOG_LEVEL_INFO,"State preserving is "+sps+"abled")
  if self.taskdevicepluginconfig[1]>0:
       self.timer1s = True
  else:
       self.timer1s = False


 def set_value(self,valuenum,value,publish=True): # Also reacting and handling Taskvalueset
  if self.initialized:
   if self.taskdevicepin[0]>=0:
    if 'on' in str(value).lower() or str(value)=="1":
     val = 1
    else:
     val = 0
    try:
     self._pin.value(val)
     self._lastdataservetime = utime.ticks_ms()
    except Exception as e:
     misc.addLog(pglobals.LOG_LEVEL_ERROR,"Please set up GPIO type before use "+str(e))
  plugin.PluginProto.set_value(self,valuenum,value,publish)

 def plugin_receivedata(self,data):                        # set value based on mqtt input
  if (len(data)>0) and self.initialized and self.enabled:
   if 'on' in str(data[0]).lower() or str(data[0])=="1":
    val = 1
   else:
    val = 0
   self.set_value(1,val,False)
#  print("Data received:",data) # DEBUG

 def timer_once_per_second(self):
  if int(self.uservar[0]) > 0:
   if (utime.ticks_ms()-self._lastdataservetime >= (self.taskdevicepluginconfig[1]*1000)):
    self.set_value(1,0,False)
