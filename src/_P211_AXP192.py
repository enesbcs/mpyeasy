#############################################################################
####################### AXP192 plugin for mpyEasy ###########################
#############################################################################
#
# Available commands:
#  axp,enable,ld02,ld03,dcdc1,dcdc3
#  axp,disable,ld02,ld03,dcdc1,dcdc3
#
# Copyright (C) 2020 by Alexander Nagy - https://bitekmindenhol.blog.hu/
#
import plugin
import pglobals
import misc
import webserver_global as ws
import utime
import inc.lib_axp as AXP
import inc.libhw as libhw

class Plugin(plugin.PluginProto):
 PLUGIN_ID = 211
 PLUGIN_NAME = "Control - AXP192 (M5StickC)"
 PLUGIN_VALUENAME1 = "Value1"
 PLUGIN_VALUENAME2 = "Value2"
 PLUGIN_VALUENAME3 = "Value3"
 PLUGIN_VALUENAME4 = "Value4"

 def __init__(self,taskindex): # general init
  plugin.PluginProto.__init__(self,taskindex)
  self.dtype = pglobals.DEVICE_TYPE_I2C
  self.vtype = pglobals.SENSOR_TYPE_QUAD
  self.valuecount = 4
  self.senddataoption = True
  self.timeroption = True
  self.timeroptional = True
  self.formulaoption = True
  self.readinprogress = 0
  self._axp = None
  self.axparams = [True,True,True,True,True]

 def plugin_init(self,enableplugin=None):
  plugin.PluginProto.plugin_init(self,enableplugin)
  if self.enabled:
    i2cl = None
    try:
     if int(self.i2c)==0:
      i2cl = libhw.i2c0
     elif int(self.i2c)==1:
      i2cl = libhw.i2c1
    except:
     pass
    try:
     self._axp = AXP.request_axp_device(i2cl)
     if self._axp is not None:
      AXP.init_axp_device(self.axparams[0],self.axparams[1],self.axparams[2],self.axparams[3],self.axparams[4])#params?
      self.initialized = True
     else:
      self.initialized = False
    except Exception as e:
     misc.addLog(pglobals.LOG_LEVEL_ERROR,"AXP192 init error "+str(e))
     self.initialized = False

 def webform_load(self): # create html page for settings
  ws.addFormNote("Default I2C address is 0x34")
  ws.addFormHeader("Initialization states")
  ws.addFormCheckBox("LD02", "p211_p0",self.axparams[0])
  ws.addFormCheckBox("LD03", "p211_p1",self.axparams[1])
  ws.addFormCheckBox("RTC",  "p211_p2",self.axparams[2])
  ws.addFormCheckBox("DCDC1","p211_p3",self.axparams[3])
  ws.addFormCheckBox("DCDC3","p211_p4",self.axparams[4])
  ws.addFormHeader("Values")
  choice1 = self.taskdevicepluginconfig[0]
  choice2 = self.taskdevicepluginconfig[1]
  choice3 = self.taskdevicepluginconfig[2]
  choice4 = self.taskdevicepluginconfig[3]
  options = ["None","Button","Temperature","BATT Voltage","BATT Current", "BATT Power","BATT Charge","IN Voltage","IN Current","Bus Voltage","Bus Current"]
  optionvalues = [0,1,2,3,4,5,6,7,8,9,10]
  ws.addFormSelector("Indicator1","plugin_211_ind0",len(options),options,optionvalues,None,choice1)
  ws.addFormSelector("Indicator2","plugin_211_ind1",len(options),options,optionvalues,None,choice2)
  ws.addFormSelector("Indicator3","plugin_211_ind2",len(options),options,optionvalues,None,choice3)
  ws.addFormSelector("Indicator4","plugin_211_ind3",len(options),options,optionvalues,None,choice4)
  return True

 def webform_save(self,params): # process settings post reply
  for v in range(0,4):
   par = ws.arg("plugin_211_ind"+str(v),params)
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
  for v in range(0,5):
   par = ws.arg("p211_p"+str(v),params)
   self.axparams[v] = (par == "on")
  return True

 def plugin_read(self): # deal with data processing at specified time interval
  result = False
  if self.initialized and self.readinprogress==0:
   self.readinprogress = 1
   vtype = 0
   for v in range(0,4):
    vtype = int(self.taskdevicepluginconfig[v])
    if vtype != 0:
     self.set_value(v+1,self.p211_get_value(vtype),False)
   self.plugin_senddata()
   self._lastdataservetime = utime.ticks_ms()
   result = True
   self.readinprogress = 0
  return result

 def p211_get_value(self,ptype):
   value = 0
   try:
    if ptype == 1:
     value = self._axp.button()
    elif ptype == 2:
     value = self._axp.temperature()
    elif ptype == 3:
     value = self._axp.battery_voltage()
    elif ptype == 4:
     value = self._axp.battery_current()
    elif ptype == 5:
     value = self._axp.battery_power()
    elif ptype == 6:
     value = self._axp.battery_charge_current()
    elif ptype == 7:
     value = self._axp.input_voltage()
    elif ptype == 8:
     value = self._axp.input_current()
    elif ptype == 9:
     value = self._axp.bus_voltage()
    elif ptype == 10:
     value = self._axp.bus_current()
   except:
    pass
   return value

 def plugin_write(self,cmd):
  res = False
  if self.initialized == False:
   return res
  cmd = cmd.lower()
  cmdarr = cmd.split(",")
  cmdarr[0] = cmdarr[0].strip()
  if cmdarr[0] == "axp":
   scmd = cmdarr[1].strip()
   l2 = None
   l3 = None
   d1 = None
   d3 = None
   if scmd == "enable":
    if "ld02" in cmd:
     l2 = True
    elif "ld03" in cmd:
     l3 = True
    elif "dcdc1" in cmd:
     d1 = True
    elif "dcdc3" in cmd:
     d3 = True
   elif scmd == "disable":
    if "ld02" in cmd:
     l2 = False
    elif "ld03" in cmd:
     l3 = False
    elif "dcdc1" in cmd:
     d1 = False
    elif "dcdc3" in cmd:
     d3 = False
   try:
    AXP.alter_axp_device(l2,l3,d1,d3)
    res = True
   except:
    misc.addLog(pglobals.LOG_LEVEL_ERROR,"AXP192 error "+str(e))
  return res
