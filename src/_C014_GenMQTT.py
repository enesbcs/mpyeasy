import controller
import pglobals
from inc.helper_domoticz import *
import misc
import ujson
try:
 import utime
except:
 import inc.faketime as utime
import webserver_global as ws
import settings
import commands
mqttok = False
try:
 from umqtt.simple import MQTTClient
 mqttok = True
except:
 pass
if mqttok==False:
 try:
  from inc.umqtt.simple import MQTTClient
  mqttok = True
 except:
  pass

class Controller(controller.ControllerProto):
 CONTROLLER_ID = 14
 CONTROLLER_NAME = "Generic MQTT"

 def __init__(self,controllerindex):
  controller.ControllerProto.__init__(self,controllerindex)
  self.usesID = False
  self.onmsgcallbacksupported = True
  self.controllerport = 1883
  self.inchannel = "%sysname%/#/state"
  self.outchannel = "%sysname%/#/set" # webformload?
  self._mqttclient = None
  self.lastreconnect = 0
  self.usesAccount = True
  self.usesPassword = True
  self.usesMQTT = True
  self.authmode = 0
  self.certfile = ""
  self.laststatus = -1
  self.keepalive = 60
  self._connected = False
  self._inch = ""
  self._outch = ""

 def controller_init(self,enablecontroller=None):
  if enablecontroller != None:
   self.enabled = enablecontroller
  self.connectinprogress = 0
  self._inch, state = commands.parseruleline(self.inchannel)    # replace global variables
  self._outch, state = commands.parseruleline(self.outchannel)
  state = self._outch.find('#')
  if state >-1:
   self._outch = self._outch[:(state+1)]
  else:
   state = self._outch.find('%tskname%')
   if state < 0:
    state = self._outch.find('%tskid%')
   if state >-1:
    self._outch = self._outch[:(state)]+"/#"
   else:
    state = self._outch.find('%valname%')
    if state >-1:
     self._outch = self._outch[:(state)]+"/#"
  self._outch = self._outch.replace('//','/').strip()
  if self._outch=="" or self._outch=="/" or self._outch=="/#" or self._outch=="%/#":
   self._outch = "#"
  try:
   ls = self.laststatus
  except:
   self.laststatus = -1
  if self.controllerpassword=="*****":
   self.controllerpassword=""
  self.initialized = True
  if self.enabled:
   try:
    if self._connected:
     pass
   except:
    self._connected = False
   try:
    if self._connected==False:
     misc.addLog(pglobals.LOG_LEVEL_DEBUG,"MQTT: Try to connect")
     self.connect()
   except:
    self._connected = False
  else:
     self.disconnect()
  return True

 def connect(self):
  if self.enabled and self.initialized:
   if self._connected:
    misc.addLog(pglobals.LOG_LEVEL_DEBUG,"Already connected force disconnect!")
    self.disconnect()
   self.connectinprogress = 1
   self.lastreconnect = utime.time()
   try:
    am = self.authmode
   except:
    am = 0
   cname = settings.Settings["Name"] + str(utime.time())
   mna = self.controlleruser
   if mna.strip()=="":
    mna = None
   mpw = self.controllerpassword
   if mpw.strip()=="":
    mpw = None
   try:
    self._mqttclient = MQTTClient(cname, self.controllerip,port=int(self.controllerport),user=mna,password=mpw,keepalive=self.keepalive,ssl=(am!=0))
    self._mqttclient.set_callback(self.on_message)
    self._mqttclient.connect()
    self._connected = self.isconnected()
    self._mqttclient.subscribe(self._outch.encode())
#    self.laststatus = 1
#    commands.rulesProcessing("DomoMQTT#Connected",pglobals.RULE_SYSTEM)
   except Exception as e:
    misc.addLog(pglobals.LOG_LEVEL_ERROR,"MQTT controller: "+self.controllerip+":"+str(self.controllerport)+" connection failed "+str(e))
    self._connected = False
    self.laststatus = 0
  else:
    self._connected = False
    self.laststatus = 0
  return self._connected

 def disconnect(self):
   try:
    self._mqttclient.disconnect()
   except:
    pass
   self._connected = False
   self.laststatus = 0
   try:
    commands.rulesProcessing("GenMQTT#Disconnected",pglobals.RULE_SYSTEM)
   except:
    pass

 def isconnected(self,ForceCheck=True):
  res = -1
  if self.enabled and self.initialized:
   if ForceCheck==False:
    return self._connected
   if self._mqttclient is not None:
    try:
     self._mqttclient.ping()
     res = 1
    except:
     res = 0
   if res != self.laststatus:
    if res==0:
     commands.rulesProcessing("GenMQTT#Disconnected",pglobals.RULE_SYSTEM)
    else:
     commands.rulesProcessing("GenMQTT#Connected",pglobals.RULE_SYSTEM)
    self.laststatus = res
   if res == 1 and self.connectinprogress==1:
    self.connectinprogress=0
  return res

 def webform_load(self): # create html page for settings
  ws.addFormTextBox("Report topic","inchannel",self.inchannel,255)
  ws.addFormTextBox("Command topic","outchannel",self.outchannel,255)
  try:
   kp = self.keepalive
  except:
   kp = 60
  ws.addFormNumericBox("Keepalive time","keepalive",kp,2,600)
  ws.addUnit("s")
  try:
   am = self.authmode
   fname = self.certfile
  except:
   am = 0
   fname = ""
  options = ["MQTT","MQTTS"]
  optionvalues = [0,1]
  ws.addFormSelector("Mode","c014_mode",len(optionvalues),options,optionvalues,None,int(am))
  return True

 def webform_save(self,params): # process settings post reply
  pchange = False
  pval = self.inchannel
  self.inchannel = ws.arg("inchannel",params)
  if pval != self.inchannel:
   pchange = True
  pval = self.outchannel
  self.outchannel = ws.arg("outchannel",params)
  if self.inchannel == self.outchannel:
   self.outchannel = self.outchannel+"/set"
  if pval != self.outchannel:
   pchange = True
  try:
   p1 = self.authmode
   self.authmode = int(ws.arg("c014_mode",params))
   if p1 != self.authmode:
    pchange = True
  except:
   self.authmode = 0
  pval = self.keepalive
  try:
   self.keepalive = int(ws.arg("keepalive",params))
  except:
   self.keepalive = 60
  if pval != self.keepalive:
   pchange = True
  if pchange and self.enabled:
   self.disconnect()
   utime.sleep(0.1)
   self.connect()
  return True

 def on_message(self, topic, msg):
  if self.enabled==False:
   return False
  success = False
  tstart = self._outch[:len(self._outch)-1]
  try:
   topic2 = topic.decode('utf-8')
  except:
   topic2 = str(topic)
  if topic2.startswith(tstart) or self._outch=="#":
   try:
    msg2 = msg.decode('utf-8')
   except:
    msg2 = str(msg)
   if (topic2 == tstart + "cmd") and (self._outch!="#"):   # global command arrived, execute
    commands.doExecuteCommand(msg2,True)
    success = True
   else:
    try:
#      tend = msg.topic[len(self.outch)-1:]
      dnames = topic2.split("/")
      dnames2 = self.outchannel.split("/")
    except:
      dnames = []
    if len(dnames)>1:
     v1 = -1
     v2 = -1
     if self.outchannel.endswith("/"+dnames[len(dnames)-1]): # set command arrived, forward it to the Task
      ttaskname = ""
      try:
       v1 = dnames2.index("#")
       v2 = v1+1
      except:
       v1 = -1
      if v1 == -1:
       try:
        v1 = dnames2.index("%tskname%")
       except:
        v1 = -1
       try:
        v2 = dnames2.index("%valname%")
       except:
        v2 = -1
       try:
        v3 = dnames2.index("%tskid%")
       except:
        v3 = -1
       if v3>-1:
        try:
          t = int(dnames[v3])-1
          if settings.Tasks[t] and type(settings.Tasks[t]) is not bool:
            ttaskname = settings.Tasks[t].gettaskname().strip()
        except:
         pass
       elif v1==-1 and v2>-1:
        try:
         for x in range(len(settings.Tasks)):
          if settings.Tasks[x] and type(settings.Tasks[x]) is not bool:
           for u in range(settings.Tasks[x].valuecount):
            if settings.Tasks[x].valuenames[u] == dnames[v2]:
             ttaskname = settings.Tasks[x].gettaskname().strip()
             break
           if ttaskname != "":
            break
        except:
         pass
      if ttaskname=="" and v1>-1:
        ttaskname = dnames[v1]
#      print(v1,v2,ttaskname,dnames) #debug
      if ttaskname != "" and v2>-1 and v2<len(dnames):
       self.onmsgcallbackfunc(self.controllerindex,-1,msg2,taskname=ttaskname,valuename=dnames[v2]) #-> Settings.callback_from_controllers()
       success = True

 def senddata(self,idx, taskobj, changedvalue = -1):
  if self.enabled:
   success = False
   if self.isconnected(False):
    tasknum = taskobj.taskindex
    if tasknum>-1:
     tname = taskobj.gettaskname()
     if changedvalue==-1:
      for u in range(taskobj.valuecount):
       vname = taskobj.valuenames[u]
       if vname != "":
        if ('%t' in self._inch) or ('%v' in self._inch):
         gtopic = self._inch.replace('#/','')
         gtopic = gtopic.replace('#','')
         gtopic = gtopic.replace('%tskname%',tname)
         gtopic = gtopic.replace('%tskid%',str(tasknum+1))
         gtopic = gtopic.replace('%valname%',vname)
        else:
         gtopic = self._inch.replace('#',tname+"/"+vname)
        gval = str(taskobj.uservar[u])
        if gval == "":
         gval = "0"
        try:
         self._mqttclient.publish(gtopic.encode(),gval.encode())
        except:
         self._connected = False
     else:
      vname = taskobj.valuenames[changedvalue-1]
      if ('%t' in self._inch) or ('%v' in self._inch):
         gtopic = self._inch.replace('#/','')
         gtopic = gtopic.replace('#','')
         gtopic = gtopic.replace('%tskname%',tname)
         gtopic = gtopic.replace('%tskid%',str(tasknum+1))
         gtopic = gtopic.replace('%valname%',vname)
      else:
         gtopic = self._inch.replace('#',tname+"/"+vname)
      if vname != "":
       gval = str(taskobj.uservar[changedvalue-1])
       if gval == "":
         gval = "0"
       try:
         self._mqttclient.publish(gtopic.encode(),gval.encode())
       except:
         self._connected = False
    else:
     misc.addLog(pglobals.LOG_LEVEL_ERROR,"MQTT taskname error, sending failed.")
   else:
    misc.addLog(pglobals.LOG_LEVEL_ERROR,"MQTT not connected, sending failed.")
    if (utime.time()-self.lastreconnect)>30:
     self.connect()

 def periodic_check(self):
    if self.enabled:
     try:
      if self._connected:
       self._mqttclient.check_msg()
     except:
      pass
     return self.onmsgcallbacksupported
