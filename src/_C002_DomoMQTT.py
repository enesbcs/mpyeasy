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
 CONTROLLER_ID = 2
 CONTROLLER_NAME = "Domoticz MQTT"

 def __init__(self,controllerindex):
  controller.ControllerProto.__init__(self,controllerindex)
  self.usesID = True
  self.onmsgcallbacksupported = True
  self.controllerport = 1883
  self.inchannel = "domoticz/in"
  self.outchannel = "domoticz/out" # webformload?
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

 def controller_init(self,enablecontroller=None):
  if enablecontroller != None:
   self.enabled = enablecontroller
  self.connectinprogress = 0
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
    self._mqttclient.subscribe(self.outchannel.encode())   
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
    commands.rulesProcessing("DomoMQTT#Disconnected",pglobals.RULE_SYSTEM)
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
     commands.rulesProcessing("DomoMQTT#Disconnected",pglobals.RULE_SYSTEM)
    else:
     commands.rulesProcessing("DomoMQTT#Connected",pglobals.RULE_SYSTEM)
    self.laststatus = res
   if res == 1 and self.connectinprogress==1:
    self.connectinprogress=0
  return res

 def webform_load(self): # create html page for settings
  ws.addFormTextBox("Controller Publish","inchannel",self.inchannel,255)
  ws.addFormTextBox("Controller Subscribe","outchannel",self.outchannel,255)
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
  ws.addFormSelector("Mode","c002_mode",len(optionvalues),options,optionvalues,None,int(am))
  return True

 def webform_save(self,params): # process settings post reply
  pchange = False
  pval = self.inchannel
  self.inchannel = ws.arg("inchannel",params)
  if pval != self.inchannel:
   pchange = True
  pval = self.outchannel
  self.outchannel = ws.arg("outchannel",params)
  if pval != self.outchannel:
   pchange = True
  try:
   p1 = self.authmode
   self.authmode = int(ws.arg("c002_mode",params))
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
  if self.enabled:
   msg2 = msg.decode('utf-8')
   list = []
   if ('{' in msg2):
    try:
     list = ujson.loads(msg2)
    except Exception as e:
     misc.addLog(pglobals.LOG_LEVEL_ERROR,"JSON decode error:"+str(e)+str(msg2))
     list = []
   if (list) and (len(list)>0):
    try:
     if list['Type'] == "Scene": # not interested in scenes..
      return False
    except:
     pass
    devidx = -1
    nvalue = "0"
    svalue = ""
    decodeerr = False
    tval = [-1,-1,-1,-1]
    try:
     devidx = str(list['idx']).strip()
    except:
     devidx = -1
     decodeerr = True
    try:
     nvalue = str(list['nvalue']).strip()
    except:
     nvalue = "0"
     decodeerr = True
    try:
     svalue = str(list['svalue']).strip()
    except:
     svalue = ""
    if (';' in svalue):
     tval = svalue.split(';')
    tval2 = []
    for x in range(1,4):
     sval = ""
     try:
      sval = str(list['svalue'+str(x)]).strip()
     except:
      sval = ""
     if sval!="":
      tval2.append(sval)
    if len(tval2)==1 and svalue=="":
     svalue=tval2[0]
    else:
     for y in range(len(tval2)):
       matches = misc.findall('[0-9]', tval2[y])
       if len(matches) > 0:
        tval[y] = tval2[y]
    forcesval1 = False
    try:
     if ("Selector" in list['switchType']) or ("Dimmer" in list['switchType']):
      forcesval1 = True
    except:
     forcesval1 = False
    if (tval[0] == -1) or (tval[0] == ""):
     if (float(nvalue)==0 and svalue.lower()!="off" and svalue!="") or (forcesval1):
      tval[0] = str(svalue)
     else:
      tval[0] = str(nvalue)
    if decodeerr:
     misc.addLog(pglobals.LOG_LEVEL_ERROR,"JSON decode error: "+msg2)
    else:
     self.onmsgcallbackfunc(self.controllerindex,devidx,tval)

 def senddata(self,idx, taskobj, changedvalue = -1):
  if self.enabled:
   mStates = ["Off","On"]
#   domomsg = '{{ "idx": {0}, "nvalue": {1:0.2f}, "svalue": "{2}" }}'
   domomsgw = '{{ "idx": {0}, "nvalue": {1:0.2f}, "svalue": "{2}", "RSSI": {3} }}'
   domomsgwb = '{{ "idx": {0}, "nvalue": {1:0.2f}, "svalue": "{2}", "RSSI": {3}, "Battery": {4} }}'
   domosmsgw = '{{"command": "switchlight", "idx": {0}, "switchcmd": "Set Level", "level":"{1}", "RSSI": {2} }}'
   domosmsgwb = '{{"command": "switchlight", "idx": {0}, "switchcmd": "Set Level", "level":"{1}", "RSSI": {2}, "Battery": {3} }}'
   if self._connected:
    try:
     usebattery = float(str(taskobj.battery).strip())
    except Exception as e:
     usebattery = -1
    if int(idx) > 0:
     if usebattery != -1 and usebattery != 255:
      bval = usebattery
     else:
      bval = misc.get_battery_value()
     msg = ""
     if (int(taskobj.vtype)==pglobals.SENSOR_TYPE_SWITCH):
      try:
       stateid = round(float(taskobj.uservar[0]))
      except:
       stateid = 0
      if stateid<0:
       stateid = 0
      if stateid>1:
       stateid = 1
      msg = domomsgwb.format(str(idx), int(stateid), mStates[stateid], mapRSSItoDomoticz(taskobj.rssi),str(bval))
     elif (int(taskobj.vtype)==pglobals.SENSOR_TYPE_DIMMER):
      msg = domosmsgwb.format(str(idx), str(taskobj.uservar[0]), mapRSSItoDomoticz(taskobj.rssi),str(bval))
     else:
      msg = domomsgwb.format(str(idx), 0, formatDomoticzSensorType(taskobj.vtype,taskobj.uservar), mapRSSItoDomoticz(taskobj.rssi),str(bval))
     try:
      self._mqttclient.publish(self.inchannel.encode(),msg.encode())
     except:
      self._connected = False

    else:
     misc.addLog(pglobals.LOG_LEVEL_ERROR,"MQTT idx error, sending failed.")
   else:
    misc.addLog(pglobals.LOG_LEVEL_ERROR,"MQTT not connected, sending failed.")
    if ((utime.time()-self.lastreconnect)>30):
#    if ((time.time()-self.lastreconnect)>30) and (self.connectinprogress==0):
     self.connect()

 def periodic_check(self):
    if self.enabled:
     try:
      if self._connected:
       self._mqttclient.check_msg()
     except:
      pass
     return self.onmsgcallbacksupported
