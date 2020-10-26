#############################################################################
##################### BLE Sniffer plugin for mpyEasy ########################
#############################################################################
#
# Copyright (C) 2020 by Alexander Nagy - https://bitekmindenhol.blog.hu/
#
import plugin
import webserver_global as ws
import pglobals
import misc
import time
import gc
import utime
import settings
import inc.lib_blehelper as BLEHelper
import inc.lib_blescan as BLEScanner
import ubinascii
import struct
from _thread import start_new_thread

class Plugin(plugin.PluginProto):
 PLUGIN_ID = 527
 PLUGIN_NAME = "Environment - BLE Xiaomi sniffer (EXPERIMENTAL)"
 PLUGIN_VALUENAME1 = "Value1"
 PLUGIN_VALUENAME2 = "Value2"
 PLUGIN_VALUENAME3 = "Value3"
 PLUGIN_VALUENAME4 = "Value4"

 def __init__(self,taskindex): # general init
  plugin.PluginProto.__init__(self,taskindex)
  self.dtype = pglobals.DEVICE_TYPE_BLE
  self.vtype = pglobals.SENSOR_TYPE_SINGLE
  self.valuecount = 1
  self.senddataoption = True
  self.recdataoption = False
  self.timeroption = True
  self.timeroptional = False
  self.formulaoption = True
  self.readinprogress = 0
  self._lastdataservetime = 0
  self._nextdataservetime = 0
  self._attribs = {}
  self._blescanner = None
  self._blestatus = None
  self.address = ""
  self.rssi = -1
  self.battery = 255

 def webform_load(self): # create html page for settings
  ws.addFormTextBox("Remote Device Address","plugin_527_addr",str(self.address),20)
  ws.addFormNote("Supported device types: LYWSD02, CGQ, CGG1, MiFlora")
  ws.addFormNote("If you are using Sniffer, you can not use any other BLE plugin, as scanning is continous! Although multiple sniffer task can be used.")
  choice1 = self.taskdevicepluginconfig[0]
  choice2 = self.taskdevicepluginconfig[1]
  choice3 = self.taskdevicepluginconfig[2]
  choice4 = self.taskdevicepluginconfig[3]
  options = ["None","Temperature","Humidity","Light","Moisture","Fertility","Battery","RSSI"]
  optionvalues = [-1,4,6,7,8,9,10,200]
  ws.addFormSelector("Indicator1","plugin_527_ind0",len(optionvalues),options,optionvalues,None,choice1)
  ws.addFormSelector("Indicator2","plugin_527_ind1",len(optionvalues),options,optionvalues,None,choice2)
  ws.addFormSelector("Indicator3","plugin_527_ind2",len(optionvalues),options,optionvalues,None,choice3)
  ws.addFormSelector("Indicator4","plugin_527_ind3",len(optionvalues),options,optionvalues,None,choice4)
  return True

 def webform_save(self,params): # process settings post reply
  self.address = str(ws.arg("plugin_527_addr",params)).strip()
  for v in range(0,4):
   par = ws.arg("plugin_527_ind"+str(v),params)
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
   if int(self.taskdevicepluginconfig[0])==4 and int(self.taskdevicepluginconfig[1])==6:
    self.vtype = pglobals.SENSOR_TYPE_TEMP_HUM
   else:
    self.vtype = pglobals.SENSOR_TYPE_DUAL
  elif self.valuecount == 3:
   self.vtype = pglobals.SENSOR_TYPE_TRIPLE
  elif self.valuecount == 4:
   self.vtype = pglobals.SENSOR_TYPE_QUAD
  self.plugin_init()
  return True

 def plugin_init(self,enableplugin=None):
  plugin.PluginProto.plugin_init(self,enableplugin)
  self.readinprogress = 0
  try:
     self._blestatus = BLEHelper.BLEStatus
     BLEHelper.bleinit(True)
  except:
     self._blestatus = None
  c = 0
  if self.enabled:
    self._attribs = {}
    try:
     self._blescanner = BLEScanner.request_blescan_device(BLEHelper.BLEDev,0) #params
     self._blestatus.requestimmediatestopscan = self._blescanner.stop
     if self._blescanner._scanning==False:
      start_new_thread(self._blescanner.sniff, (self.AdvDecoder,30))
     self.initialized = True
     self.ports = str(self.address)
     misc.addLog(pglobals.LOG_LEVEL_INFO,"BLE sniffer init ok")
    except Exception as e:
     misc.addLog(pglobals.LOG_LEVEL_ERROR,"BLE sniffer init error: "+str(e))
     self.initialized = False
  else:
    self.initialized = False
    self.ports = ""
    self.plugin_exit()

 def AdvDecoder(self,devip):
    try:
     devi = []
     try:
      if type(devip) is not bytes: # memoryview? LOL
       devi = misc.mvtoarr(devip,1)
      else:
       devi = devip
     except:
       pass
     resp = {'addr':0,'type':0,'rssi':0,'flag':3,'d':b''}
     resp['type'], resp['addr'], resp['flag'], resp['rssi'], resp['d'] = devi
     addr = ubinascii.hexlify(resp['addr']).decode('utf-8')
     addr = ':'.join([addr[i:i+2] for i in range(0,12,2)])     
     notfound = True
     daddr = 0
     advdat = misc.mvtoarr(resp['d'],0)
#     print(addr,advdat)#debug     
     while notfound and daddr<len(advdat):
        try:
          dlen = advdat[daddr]
          dt   = advdat[daddr+1]
          if int(dt) == 22:
             daddr = daddr + 2
             notfound = False
             break
          daddr = daddr+dlen+1
        except:
         notfound = False
         daddr = -1
#     print("proc",addr,resp['rssi'],advdat)#debug
#     print(advdat,daddr,advdat[daddr:])#debug     
     if daddr < 0:
      return False
     advdat = bytes(advdat[daddr:])
#     print(daddr,advdat)#debug
     ddat = {}
     try:
      if len(advdat)>2:
       ddat = self.decode_xiaomi(advdat) # forward to xiaomi decoder
     except Exception as e:
      print("decode xiaomi error",e)
#     print(addr,ddat)#debug
     if len(ddat)>0:
      try:
       self.dosync(addr,resp['rssi'],ddat) # if supported device, sync with all Tasks
      except:
       pass
    except Exception as e:
     print("Decoding error:",e)#debug

 def plugin_exit(self):
     try:
      self._blestatus.reportscan(0)
      if self._blescanner._scanning:
       self._blescanner._scanning = False
      self._blescanner.stop()
     except:
      pass

 def plugin_read(self):
  result = False
  if self.initialized and self.readinprogress==0:
   self.readinprogress = 1
   lastupdate = 0
   print(self._attribs)#debug
   for key in self._attribs.keys():
    if "-t" in key:
     if self._attribs[key]>lastupdate:
      lastupdate = self._attribs[key]
   if (time.time()-lastupdate) > (3*self.interval):
    self.rssi= -100
    self.battery = 0
   elif self.battery==0:
    self.battery=255
   for v in range(0,4):
    vtype = int(self.taskdevicepluginconfig[v])
    if vtype != 0:
     self.set_value(v+1,self.p527_get_value(vtype),False)
   self.plugin_senddata()
   self._lastdataservetime = utime.ticks_ms()
   self.readinprogress = 0   
   result = True
  return result

 def p527_get_value(self,ptype):
   value = 0
   if ptype == 4:
    if "temp" in self._attribs:
     value = self._attribs['temp']
    else:
     value = 0
   elif ptype == 6:
    if "hum" in self._attribs:
     value = self._attribs['hum']
    else:
     value = 0
   elif ptype == 7:
    if "light" in self._attribs:
     value = self._attribs['light']
    else:
     value = 0
   elif ptype == 8:
    if "moist" in self._attribs:
     value = self._attribs['moist']
    else:
     value = 0
   elif ptype == 9:
    if "fertil" in self._attribs:
     value = self._attribs['fertil']
    else:
     value = 0
   elif ptype == 10:
    value = self.battery #self._attribs['batt']
   elif ptype == 200:
    value = self.rssi
   return value

 def _updatedevice(self,newvals):
    res = False
    for key in newvals.keys():
     if key=="batt":
      self.battery = newvals[key]
     try:
      if key in self._attribs:
       if time.time()-self._attribs[key+"-t"]>1.5:
        self._attribs[key+"-t"] = time.time()
        self._attribs[key] = newvals[key]
        res = True
      else:
       self._attribs.update({key:newvals[key]})
       key = key + "-t"
       self._attribs.update({key:time.time()})
       res = True
     except Exception as e:
      print("update",e)#debug
    return res

 def decode_xiaomi(self,buf):
  res = {}
  ofs = 0
  try:
   if len(buf)>16:
    cdata = struct.unpack_from('<HHHB6BBBBB',buf)
   elif len(buf)>15:
    cdata = struct.unpack_from('<HHHB6BBBB',buf)
   else:
    cdata = [0]
  except Exception as e:
    cdata = [0]
  if cdata[0] == 0xFE95:
    if cdata[11] != 0x10 and cdata[12] == 0x10:
     ofs = 1
    try:
     if cdata[2] == 0x0576:
      cdata2 = struct.unpack_from('<hH',buf[15:])
      res = {"temp":cdata2[0]/10.0,"hum":cdata2[1]/10.0}
     elif cdata[10+ofs]==0xD and cdata[12+ofs]>3:
      cdata2 = struct.unpack_from('<HH',buf[16+ofs:])
      res = {"temp":cdata2[0]/10.0,"hum":cdata2[1]/10.0}
     elif cdata[10+ofs]==0xA and cdata[12+ofs]>0:
      res = {"batt": buf[16+ofs]}
#      misc.addLog(rpieGlobals.LOG_LEVEL_DEBUG,str(res)+" "+str(cdata))
     elif cdata[10+ofs]==6 and cdata[12+ofs]>0:
      cdata2 = struct.unpack_from('<H',buf[16+ofs:])
      res = {"hum":cdata2[0]/10.0}
     elif cdata[10+ofs]==4 and cdata[12+ofs]>0:
      cdata2 = struct.unpack_from('<H',buf[16+ofs:])
      res = {"temp":cdata2[0]/10.0}
     elif cdata[10+ofs]==7 and cdata[12+ofs]>0:
      try:
       cdata2 = struct.unpack_from('<3B',buf[16+ofs:])
       res = cdata2[0]+cdata2[1]*256+cdata2[2]*65535
      except:
       res = buf[16+ofs]
      res = {"light":res} # 3byte
     elif cdata[10+ofs]==8 and cdata[12+ofs]>0:
      res = {"moist":buf[16+ofs]} #1byte
     elif cdata[10+ofs]==9 and cdata[12+ofs]>0:
      try:
       cdata2 = struct.unpack_from('<H',buf[16+ofs:])
       res = cdata2[0]
      except:
       res = buf[16+ofs]
      res = {"fertil":res} #2byte
     elif cdata[10+ofs]==5 and cdata[12+ofs]>0:
      res = {"stat":buf[16+ofs],"temp":buf[17+ofs]}
    except:
     res = {}
  else:
    if buf[0]==0x1A and buf[1]==0x18: # ATC
     try:
      cdata = struct.unpack_from('>H6BhBBHB',buf)
     except:
      cdata = [0]
     res = {"temp":cdata[7]/10.0,"hum":cdata[8],"batt":cdata[9]}
  return res

 def dosync(self,addr,rssi,values):
  for x in range(0,len(settings.Tasks)):
   if (settings.Tasks[x]) and type(settings.Tasks[x]) is not bool: # device exists
    if (settings.Tasks[x].enabled):
      if (settings.Tasks[x].pluginid==self.pluginid):
       if str(settings.Tasks[x].address) == str(addr):
        try:
         if settings.Tasks[x]._updatedevice(values):
          settings.Tasks[x].rssi = rssi
         else:
          break
        except:
         pass
