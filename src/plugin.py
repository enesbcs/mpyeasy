import pglobals
import commands
import misc
import ujson
try:
 import utime
except:
 import inc.faketime as utime

class PluginProto: # Skeleton for every plugin! Override necessary functions and extend as neeeded!
 PLUGIN_ID = -1
 PLUGIN_NAME = "Plugin"
 PLUGIN_VALUENAME1 = "Value"
 PLUGIN_VALUENAME2 = ""
 PLUGIN_VALUENAME3 = ""
 PLUGIN_VALUENAME4 = ""

 def __init__(self,taskindex): # general init
  self.valuenames = []
  self.enabled = False
  self.initialized = False
  self.pluginid = self.PLUGIN_ID
  self.taskindex = taskindex
  self.set_valuenames(self.PLUGIN_VALUENAME1,self.PLUGIN_VALUENAME2,self.PLUGIN_VALUENAME3,self.PLUGIN_VALUENAME4)
  self.taskdevicepin = [-1,-1,-1,-1]
  self.pinfilter = [0,0,0,0]
  self.taskdeviceport = -1
  self.dtype = pglobals.DEVICE_TYPE_SINGLE
  self.vtype = pglobals.SENSOR_TYPE_SWITCH
  self.ports = 0
  self.uart = -1
  self.i2c  = -1
  self.spi  = -1
  self.inverselogicoption = False
  self.pininversed = False
  self.valuecount = 0
  self.senddataoption = False
  self.recdataoption = False
  self.timeroption = False
  self.timeroptional = False
  self.remotefeed = False
  self.feedpublished = False
  self.formulaoption = False
  self.formula = ["","","",""]
  self.decimalsonly = False
  self.decimals = [1,1,1,1]
  self.interval = 0
  self._lastdataservetime = 0
  self.timer100ms = False # function exists that has to be executed ten time per sec
  self.timer20ms  = False # function exists that has to be executed fifty time per sec
  self.timer1s    = False # function exists that has to be executed one time per sec
  self.timer2s    = False # function exists that has to be executed in every two seconds
  self.taskname   = ""
  self.taskdevicepluginconfig = []
  self.readinprogress = 0
  for x in range(pglobals.PLUGIN_CONFIGVAR_MAX):
   self.taskdevicepluginconfig.append(0)
  self.uservar = []
  for x in range(pglobals.VARS_PER_TASK):
   self.uservar.append(0)
#  self.controllerid = []
  self.senddataenabled = []
  self.controlleridx = []
  self.controllercb = []
  self.rssi = -1
  self.battery = -1
  for x in range(pglobals.CONTROLLER_MAX):
#   self.controllerid.append(-1)
   self.senddataenabled.append(False)
   self.controlleridx.append(-1)
   self.controllercb.append(False)

 def toJSON(self):
        objs = {}
        for o,value in self.__dict__.items():
         if type(value) is not object and o!="controllercb" and o[0]!="_":
          objs.update( {o : value} )
        return ujson.dumps(objs)

 def getpluginid(self):
  return self.pluginid

 def getdevicename(self):
  return self.PLUGIN_NAME
  
 def gettaskname(self):
  return self.taskname

 def gettaskindex(self):
  return self.taskindex

 def getdevicevaluenames(self):
  return self.valuenames

 def set_valuenames(self,value1,value2=None,value3=None,value4=None):
  self.valuenames = []
  if value1:
   self.valuenames.append(value1.replace(" ",""))
   self.valuecount = 1
   if value2!=None:
    self.valuenames.append(value2.replace(" ",""))
    self.valuecount = 2
    if value3!=None:
     self.valuenames.append(value3.replace(" ","")) 
     self.valuecount = 3
     if value4!=None:
      self.valuenames.append(value4.replace(" ",""))
      self.valuecount = 4

 def set_value(self,valuenum,value,publish=True): # implement if GPIO used!!
  if float(valuenum)<=self.valuecount and float(valuenum)>0:
   rval = value
   if self.formulaoption: # handle formulas
    tval = False
    if len(self.formula[valuenum-1])>0 and commands.isformula(self.formula[valuenum-1]):
     tval = commands.parseformula(self.formula[valuenum-1],float(value))
     if tval!=False:
      rval = tval
   if self.pininversed:          # only binary sensors supported for inversion!
    if type(rval) is str:
     if (rval.lower() == "off") or (rval=="0"):
      rval = 1
     else:
      rval = 0
    else:
     if (float(rval) == 0):
      rval = 1
     else:
      rval = 0
   if int(float(self.decimals[valuenum-1]))>=0: # handle decimals if needed
    try:
     rval = misc.formatnum(rval,int(float(self.decimals[valuenum-1])))
    except:
     pass
   self.uservar[valuenum-1] = rval
   if self.valuenames[valuenum-1]!= "":
    try:
     commands.rulesProcessing(self.taskname+"#"+self.valuenames[valuenum-1]+"="+str(rval),pglobals.RULE_USER)
    except: # maximum recursion depth?
     pass
   if self.senddataoption and publish:
    self.plugin_senddata(pchangedvalue=valuenum)

 def webform_load(self): # create html page for settings
  return ""

 def webform_save(self,params): # process settings post reply
  return True

 def plugin_init(self,enableplugin=None): # init plugin when startup, load settings if available
  if enableplugin != None:
   self.enabled = enableplugin
   if enableplugin:
    self.feedpublished = False
  self._lastdataservetime = 0
  self.readinprogress = 0
  if self.enabled:
   if self.initialized == False:
    self.initialized = True
  if self.vtype == pglobals.SENSOR_TYPE_TEXT:
   self.decimals[0]=-1
  return True

 def plugin_exit(self): # deinit plugin, save settings?
  if self.initialized:
   self.initialized = False
  return True

 def plugin_read(self): # deal with data processing at specified time interval
  result = False
  if self.initialized:
   self._lastdataservetime = utime.ticks_ms()
   result = True
  return result

 def is_read_timely(self):
  result = False
  if self.initialized and self.enabled:
   if self.timeroption and int(self.interval)>0:
    result = ((utime.ticks_ms() - self._lastdataservetime) >= (self.interval*1000)) # maybe many multiply operation slows down the device a little?
  return result

 def plugin_write(self,cmd): # deal with command from outside
  result = False
  return result

 def plugin_receivedata(self,data): # data arrived from controller
  result = False
  return result

 def plugin_senddata(self,pchangedvalue=-1):
  for x in range(pglobals.CONTROLLER_MAX):
   if self.senddataenabled[x]:
    try:
     if type(self.controllercb[x])==type(self.plugin_senddata):
      self.controllercb[x](self.controlleridx[x],self,changedvalue=pchangedvalue)
    except Exception as e:
#      print(x,len(self.controllercb),self.controllercb,self.controlleridx)
      print("Plugin SendData Exception: ",e)

 def timer_once_per_second(self): # once per sec
  return self.timer1s

 def timer_two_second(self): # once per 2sec
  return self.timer2s

 def timer_ten_per_second(self): # ten per sec
  return self.timer100ms

 def timer_fifty_per_second(self): # fifty per sec
  return self.timer20ms

