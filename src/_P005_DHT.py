#############################################################################
################### DHT11/22 plugin for mpyEasy #############################
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
 import dht
 from machine import Pin
except Exception as e:
 pass

class Plugin(plugin.PluginProto):
 PLUGIN_ID = 5
 PLUGIN_NAME = "Environment - DHT11/22/AM2302"
 PLUGIN_VALUENAME1 = "Temperature"
 PLUGIN_VALUENAME2 = "Humidity"

 def __init__(self,taskindex): # general init
  plugin.PluginProto.__init__(self,taskindex)
  self.dtype = pglobals.DEVICE_TYPE_SINGLE
  self.vtype = pglobals.SENSOR_TYPE_TEMP_HUM
  self.readinprogress = 0
  self.valuecount = 2
  self.senddataoption = True
  self.timeroption = True
  self.timeroptional = False
  self.formulaoption = True
  self._nextdataservetime = 0
  self.lastread = 0
  self.samples = 9
  self.preread = self.samples*2000 # 9 * 2 sec
  self.TARR = []
  self.HARR = []
  self._dht = None
  self.initialized = False

 def plugin_init(self,enableplugin=None):
  plugin.PluginProto.plugin_init(self,enableplugin)
  self.TARR = []
  self.HARR = []
  self.uservar[0] = 0
  self.uservar[1] = 0
  if self.enabled:
   if self.interval>2:
    nextr = self.interval-2
   else:
    nextr = 0
   try:
    if self.taskdevicepluginconfig[0]==11:
     self._dht = dht.DHT11(Pin(int(self.taskdevicepin[0])))
    else:
     self._dht = dht.DHT22(Pin(int(self.taskdevicepin[0])))
    self.initialized = True
    self.readinprogress=0
   except Exception as e:
    misc.addLog(pglobals.LOG_LEVEL_ERROR,"DHT init error "+str(e))
    self.initialized = False
   self._lastdataservetime = utime.ticks_ms()-(nextr*1000)
   self.lastread = 0

 def webform_load(self): # create html page for settings
  try:
   choice1 = self.taskdevicepluginconfig[0]
   options = ["DHT11","DHT22/AM2302"]
   optionvalues = [11,22]
   ws.addFormSelector("Sensor type","plugin_005_type",2,options,optionvalues,None,int(choice1))
  except:
   pass
  ws.addFormCheckBox("Oversampling","plugin_005_over",self.timer2s)
  ws.addFormNote("Strongly recommended to enable oversampling for reliable readings!")
  return True

 def webform_save(self,params): # process settings post reply
  par = ws.arg("plugin_005_type",params)
  try:
   if par == "":
     par = 22
  except:
   par = 22
  self.taskdevicepluginconfig[0] = int(par)

  if (ws.arg("plugin_005_over",params)=="on"):
   self.timer2s = True
  else:
   self.timer2s = False
  return True

 def timer_two_second(self):
  if self.timer2s and self.initialized and self.readinprogress==0 and self.enabled:
   if self._nextdataservetime-utime.ticks_ms()<=self.preread:
    self.readinprogress = 1
    self.p005_get_value()
    self.readinprogress = 0
  return self.timer2s

 def plugin_read(self): # deal with data processing at specified time interval
  result = False
  if self.initialized and self.readinprogress==0:
   prevt = self.uservar[0]
   prevh = self.uservar[1]
   self.readinprogress = 1
   self.p005_get_value()
   if len(self.TARR)==1:
     self.set_value(1,self.TARR[0],False)
   if len(self.HARR)==1:
     self.set_value(2,self.HARR[0],False)
   if len(self.TARR)>1:
    atemp = round((sum(self.TARR) / len(self.TARR)),3)
    if ((max(self.TARR) - min(self.TARR)) > 2): # too much deviation found for temp
       difft = abs(max(self.TARR) - atemp)
       if (difft > abs(atemp-min(self.TARR))):
        difft = abs(atemp-min(self.TARR))
       if (difft < 1):
        difft = 1
       if (difft > 5):
        difft = 5
       TARR2 = []
       for i in range(0,len(self.TARR)):
        if (abs(atemp-self.TARR[i]) <= difft):
         TARR2.append(self.TARR[i])
       if len(TARR2)>0:
        atemp = round((sum(TARR2) / len(TARR2)),3)
    self.set_value(1,atemp,False)
   if len(self.HARR)>1:
    ahum = round((sum(self.HARR) / len(self.HARR)),2)
    if ((max(self.HARR) - min(self.HARR)) > 4): # too much deviation for humidity
       diffh = abs(max(self.HARR) - ahum)
       if (diffh > abs(ahum-min(self.HARR))):
        diffh = abs(ahum-min(self.HARR))
       if (diffh < 2):
        diffh = 2
       if (diffh > 8):
        diffh = 8
       HARR2 = []
       for i in range(0,len(self.HARR)):
        if (abs(ahum-self.HARR[i]) <= diffh):
         HARR2.append(self.HARR[i])
       if len(HARR2)>0:
        ahum = round((sum(HARR2) / len(HARR2)),2)
    self.set_value(2,ahum,False)
   if len(self.TARR)<1 or len(self.HARR)<1: # no value returned, cheating
    misc.addLog(pglobals.LOG_LEVEL_ERROR,"DHT read failed, using cached value!")
    self.uservar[0] = prevt # avoid using formulas!
    self.uservar[1] = prevh # avoid using formulas!
   self._lastdataservetime = utime.ticks_ms()
   if float(self.uservar[0])!=0 and float(self.uservar[1])!=0:
    self.plugin_senddata()
    self._nextdataservetime = self._lastdataservetime + (self.interval*1000)
   elif self.timer2s:
    self._nextdataservetime = self._lastdataservetime + 6000 # force next try sooner if oversampling requested and read failed
    self._lastdataservetime = self._nextdataservetime-(self.interval*1000)
#   print(self.TARR,self.HARR) # DEBUG only!
   self.TARR = []
   self.HARR = []
   result = True
   self.readinprogress = 0
  return result

 def p005_get_value(self):
   if utime.ticks_ms()>=(self.lastread+2000):
    humidity = None
    temperature = None
    try:
     self._dht.measure()
     temperature = self._dht.temperature()
     humidity = self._dht.humidity()
    except Exception as e:
     humidity = None
     temperature = None
    if humidity is not None and temperature is not None:
     self.HARR.append(round(humidity, 2))
     self.TARR.append(round(temperature, 2))
    self.lastread = utime.ticks_ms()
