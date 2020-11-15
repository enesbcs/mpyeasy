#############################################################################
################## ESPEasy P2P controller for mpyEasy #######################
#############################################################################
#
# This controller is able to join ESPEasy P2P network, with auto registering
# itself, watching for Node advertisements, importing and exporting sensor
# data and information, and supports standard "sendto,unit" command scheme.
#
# Copyright (C) 2020 by Alexander Nagy - https://bitekmindenhol.blog.hu/
#
import controller
import pglobals
import misc
try:
 import utime
except:
 import inc.faketime as utime
import webserver_global as ws
import settings
import commands
import time
try:
 import usocket
except:
 import socket as usocket
import unet
import struct

class Controller(controller.ControllerProto):
 CONTROLLER_ID = 13
 CONTROLLER_NAME = "ESPEasy P2P"

 def __init__(self,controllerindex):
  controller.ControllerProto.__init__(self,controllerindex)
  self.usesID = False
  self.onmsgcallbacksupported = True
  self.controllerport = 65501
  self.timer30s = True
  self._s = None
  self._started = False
  self.cbinprogress = False
  self._dp = None

 def controller_init(self,enablecontroller=None):
  if enablecontroller != None:
   self.enabled = enablecontroller
  if self.enabled:
    try:
     if self._s is None:
      self._s = usocket.socket(usocket.AF_INET, usocket.SOCK_DGRAM)
      self._s.setsockopt(usocket.SOL_SOCKET, usocket.SO_REUSEADDR, 1) # Make Socket Reusable
#      self._s.setsockopt(usocket.SOL_SOCKET, usocket.SO_BROADCAST, 1) # Allow incoming broadcasts
      self._s.setblocking(False) # Set socket to non-blocking mode
      self._s.bind(('0.0.0.0',int(self.controllerport)))
     if self._s is not None:
      self._started = True
     else:
      self._started = False
     self.cbinprogress = False
    except Exception as e:
     self._started = False
  self.initialized = True
  self._dp = data_packet()
  return True

 def webform_load(self):
  ws.addFormNote("Hint: only the Controller Port parameter used!")
  return True

 def nodesort(self,item):
  v = 0
  try:
   v = int(item["unitno"])
  except:
   v = 0
  return v

 def periodic_check(self):
  if self.enabled and self._started and self.cbinprogress == False:
    self.cbinprogress = True
    self._dp.clear()
    address = ""
    try:
        self._dp.buffer,address = self._s.recvfrom(1024)
    except:
        pass
    pok = False
    try:
     if len(self._dp.buffer)>2 and int(self._dp.buffer[0]) != 0:
       pok = True
    except Exception as e:
     pass
    if pok:
      try:
#        print("buf",pok,self._dp.buffer,address)
        self._dp.decode()
#        print(self._dp.infopacket)
        if self._dp.pkgtype==1:
         un = getunitordfromnum(self._dp.infopacket["unitno"]) # process incoming alive reports
         if un==-1:
          settings.nodelist.append({"unitno":self._dp.infopacket["unitno"],"name":self._dp.infopacket["name"],"build":self._dp.infopacket["build"],"type":self._dp.infopacket["type"],"ip":self._dp.infopacket["ip"],"port":self._dp.infopacket["port"],"age":0})
          misc.addLog(pglobals.LOG_LEVEL_INFO,"New P2P unit discovered: "+str(self._dp.infopacket["unitno"])+" "+str(self._dp.infopacket["ip"])+" "+str(self._dp.infopacket["mac"]))
          settings.nodelist.sort(reverse=False,key=self.nodesort)
         else:
          settings.nodelist[un]["age"] = 0
          if int(self._dp.infopacket["unitno"]) != int(settings.Settings["Unit"]):
           misc.addLog(pglobals.LOG_LEVEL_DEBUG,"Unit alive: "+str(self._dp.infopacket["unitno"]))
        elif self._dp.pkgtype==3:                              # process incoming new devices
          if int(settings.Settings["Unit"])==int(self._dp.sensorinfo["dunit"]): # process only if we are the destination
           rtaskindex = int(self._dp.sensorinfo["dti"])
           if len(settings.Tasks)<=rtaskindex or settings.Tasks[rtaskindex]==False: # continue only if taskindex is empty
            misc.addLog(pglobals.LOG_LEVEL_DEBUG,"Sensorinfo arrived from unit "+str(self._dp.sensorinfo["sunit"]))
            devtype = 33
            for x in range(len(pglobals.deviceselector)):
             if int(pglobals.deviceselector[x][1]) == int(self._dp.sensorinfo["dnum"]):
              devtype = int(self._dp.sensorinfo["dnum"])
              break
            m = False
            try:
             for y in range(len(pglobals.deviceselector)):
              if int(pglobals.deviceselector[y][1]) == devtype:
               if len(settings.Tasks)<=rtaskindex:
                while len(settings.Tasks)<=rtaskindex:
                 settings.Tasks.append(False)
               m = __import__(pglobals.deviceselector[y][0])
               break
            except:
             m = False
            if m:
             try:
              settings.Tasks[rtaskindex] = m.Plugin(rtaskindex)
             except:
              settings.Tasks.append(m.Plugin(rtaskindex))
             settings.Tasks[rtaskindex].plugin_init(False)
             settings.Tasks[rtaskindex].remotefeed = True  # Mark that this task accepts incoming data updates!
             settings.Tasks[rtaskindex].taskname = self._dp.sensorinfo["taskname"]
             for v in range(4):
              self._dp.sensorinfo["valuenames"].append("")
             for v in range(settings.Tasks[rtaskindex].valuecount):
               settings.Tasks[rtaskindex].valuenames[v] = self._dp.sensorinfo["valuenames"][v]
        elif self._dp.pkgtype==5:                          # process incoming data
          if int(settings.Settings["Unit"])==int(self._dp.sensordata["dunit"]): # process only if we are the destination
           rtaskindex = int(self._dp.sensordata["dti"])
           if len(settings.Tasks)>rtaskindex and settings.Tasks[rtaskindex] and settings.Tasks[rtaskindex].remotefeed: # continue only if taskindex exists and accepts incoming datas
            misc.addLog(pglobals.LOG_LEVEL_DEBUG,"Sensordata update arrived from unit "+str(self._dp.sensordata["sunit"]))
            recok = False
            try:
             if self._onmsgcallbackfunc is not None and settings.Tasks[rtaskindex].recdataoption:
              self._onmsgcallbackfunc(self.controllerindex,-1,self._dp.sensordata["values"],settings.Tasks[rtaskindex].gettaskname())
              recok = True
            except:
              pass
            if recok==False:
             for v in range(settings.Tasks[rtaskindex].valuecount):
              settings.Tasks[rtaskindex].set_value(v+1,self._dp.sensordata["values"][v],False)
             settings.Tasks[rtaskindex].plugin_senddata()

        elif self._dp.pkgtype==0:
          misc.addLog(pglobals.LOG_LEVEL_INFO,"Command arrived from "+str(address))
          cmdline = decodezerostr(self._dp.buffer)
          commands.doExecuteCommand(cmdline,True)
      except Exception as e:
        print("c13loop",e)    
    self.cbinprogress = False
  return self.onmsgcallbacksupported

 def udpsender(self,unitno,data,retrynum=1):
  destip = ""
  if unitno==255:
   destip = "255.255.255.255"
  else:
   for n in settings.nodelist:
    if n["unitno"] == unitno:
     destip = n["ip"]
     break
  if destip != "":
    if type(data) is bytes:
     dsend = data
    elif type(data) is str:
     dsend = bytes(data,"utf-8")
    else:
     dsend = bytes(data)
    for r in range(retrynum):
      try:
#       print(dsend," ",destip," ",self.controllerport) # DEBUG
       self._s.sendto(dsend, (destip,int(self.controllerport)))
      except:
       pass
      if r<retrynum-1:
       time.sleep(0.1)

 def senddata(self,idx,taskobj, changedvalue = -1):
  tasknum = taskobj.taskindex
  if tasknum!=-1 and self.enabled:
   if tasknum<len(settings.Tasks):
    if taskobj != False:
     if taskobj.feedpublished == False:
      dp2 = data_packet() # publish sensor info if not yet published
      dp2.sensorinfo["sunit"] = settings.Settings["Unit"]
      dp2.sensorinfo["sti"] = tasknum
      dp2.sensorinfo["dti"] = tasknum
      dp2.sensorinfo["dnum"] = taskobj.getpluginid()
      dp2.sensorinfo["taskname"] = taskobj.gettaskname()
      for u in range(taskobj.valuecount):
       dp2.sensorinfo["valuenames"][u] = taskobj.valuenames[u]
      for n in settings.nodelist: # send to all known nodes
        if int(n["unitno"]) != int(settings.Settings["Unit"]):
         dp2.sensorinfo["dunit"] = n["unitno"]
         dp2.encode(3)
         self.udpsender(n["unitno"],dp2.buffer,2)
      taskobj.feedpublished = True # mark as published

     dp2 = data_packet() # do actual data sending
     dp2.sensordata["sunit"] = settings.Settings["Unit"]
     dp2.sensordata["sti"] = tasknum
     dp2.sensordata["dti"] = tasknum
     for u in range(taskobj.valuecount):
      dp2.sensordata["values"][u] = taskobj.uservar[u]
     for n in settings.nodelist: # send to all known nodes
        if int(n["unitno"]) != int(settings.Settings["Unit"]):
         dp2.sensordata["dunit"] = n["unitno"]
         dp2.encode(5)
         self.udpsender(n["unitno"],dp2.buffer,2)

 def timer_thirty_second(self):
  if self.enabled:
  #send alive signals
   dp = data_packet()
   dp.infopacket["ip"] = str(unet.get_ip())
   try:
    dp.infopacket["mac"] = str(unet.get_mac())
   except:
    dp.infopacket["mac"] = "00:00:00:00:00:00"
   dp.infopacket["unitno"] = int(settings.Settings["Unit"])
   dp.infopacket["build"] = int(pglobals.BUILD)
   dp.infopacket["name"] = settings.Settings["Name"]
   dp.infopacket["type"] = int(pglobals.NODE_TYPE_ID)
   dp.infopacket["port"] = int(80)
   dp.encode(1)
   self.udpsender(255,dp.buffer,1)
   misc.addLog(pglobals.LOG_LEVEL_DEBUG,"P2P alive pkt sent")
   #clear old nodes
   for n in range(len(settings.nodelist)):
    try:
     if settings.nodelist[n]["age"] >= 10:
      misc.addLog(pglobals.LOG_LEVEL_INFO,"P2P unit disappeared: "+str(settings.nodelist[n]["unitno"]))
      del settings.nodelist[n]
     else:
      settings.nodelist[n]["age"] += 1
    except:
     pass
  return True

class data_packet:
 buffer = bytearray(255)
 infopacket = {"mac":"","ip":"","unitno":-1,"build":0,"name":"","type":0,"port":80}
 sensorinfo = {"sunit":0,"dunit":0,"sti":0,"dti":0,"dnum":0,"taskname":"","valuenames":["","","",""]}
 sensordata = {"sunit":0,"dunit":0,"sti":0,"dti":0,"values":[0,0,0,0]}
 pkgtype = 0

 def __init__(self):
  self.clear()

 def clear(self):
  self.buffer = bytearray(255)
  self.infopacket["mac"] = ""
  self.infopacket["ip"] = ""
  self.infopacket["unitno"] = -1
  self.infopacket["build"] = 0
  self.infopacket["name"] = ""
  self.infopacket["type"] = 0
  self.infopacket["port"] = 80
  self.sensorinfo["sunit"] = 0
  self.sensorinfo["dunit"] = 0
  self.sensordata["sunit"] = 0
  self.sensordata["dunit"] = 0
  self.pkgtype = 0

 def encode(self,ptype):
  self.pkgtype = ptype
  if ptype == 1:
   tbuf = [255,1]
   ta = self.infopacket["mac"].split(":")
   for m in ta:
    try:
     tbuf.append(int(m,16))
    except:
     tbuf.append(0)
   ta = self.infopacket["ip"].split(".")
   for m in ta:
    try:
     tbuf.append(int(m))
    except:
     tbuf.append(255)
   tbuf.append(int(self.infopacket["unitno"]))
   tbuf.append(int(self.infopacket["build"]%256))
   tbuf.append(int(self.infopacket["build"]/256))
   nl = len(self.infopacket["name"])
   if nl>24:
    nl = 24
   for s in range(nl):
    tbuf.append(ord(self.infopacket["name"][s]))
   try:
    for p in range(s,24):
     tbuf.append(0)
   except:
    pass
   tbuf.append(int(self.infopacket["type"]))
   tbuf.append(int(self.infopacket["port"]%256))
   tbuf.append(int(self.infopacket["port"]/256))
   for b in range(len(tbuf),80):
    tbuf.append(0)
   self.buffer = bytes(tbuf)
  if ptype == 3:
   tbuf = [255,3]
   tbuf.append(int(self.sensorinfo["sunit"]))
   tbuf.append(int(self.sensorinfo["dunit"]))
   tbuf.append(int(self.sensorinfo["sti"]))
   tbuf.append(int(self.sensorinfo["dti"]))
   if self.sensorinfo["dnum"] > 255: # bytes can go 0-255
    self.sensorinfo["dnum"] = 33
   tbuf.append(int(self.sensorinfo["dnum"]))
   sl = len(self.sensorinfo["taskname"])
   if sl>25:
    sl = 25
   for s in range(sl):
    tbuf.append(ord(self.sensorinfo["taskname"][s]))
   for p in range(s,25):
    tbuf.append(0)
   for v in range(pglobals.VARS_PER_TASK):
    sl = len(self.sensorinfo["valuenames"][v])
    if sl>25:
     sl = 25
    for s in range(sl):
     tbuf.append(ord(self.sensorinfo["valuenames"][v][s]))
    for p in range(s,25):
     tbuf.append(0)
   for b in range(len(tbuf),137):
    tbuf.append(0)
   self.buffer = bytes(tbuf)
  if ptype == 5:
   tbuf = [255,5]
   tbuf.append(int(self.sensordata["sunit"]))
   tbuf.append(int(self.sensordata["dunit"]))
   tbuf.append(int(self.sensordata["sti"]))
   tbuf.append(int(self.sensordata["dti"]))
   tbuf.append(0) # Do not know why this 2 bytes necessarry...
   tbuf.append(0)
   for v in range(pglobals.VARS_PER_TASK):
    try:
     val = float(self.sensordata["values"][v])
     cvf = list(struct.pack("<f",val))# convert float to bytearray
    except:
     if type(self.sensordata["values"][v]) is str:
      cvf = self.sensordata["values"][v][0:4]   # strip string if needed
     else:
      cvf = list(self.sensordata["values"][v])  # do anything that we can..
    cl = len(cvf)
    if cl>4:
     cl = 4
    for c in range(cl):
     tbuf.append(cvf[c])
   self.buffer = bytes(tbuf)

 def decode(self):
  tbuffer = list(self.buffer)
  self.pkgtype = 0
  if tbuffer[0] == 255:
   if tbuffer[1] == 1: # sysinfo len=80
    self.pkgtype = 1
    if len(self.buffer)>=41:
     cdata = struct.unpack_from('<BB6B4BBH25sBH',self.buffer)
    else:
     cdata = struct.unpack_from('<BB6B4BB',self.buffer)
    array_alpha = cdata[2:8]
    self.infopacket["mac"] = ':'.join('{:02x}'.format(x) for x in array_alpha).upper()
    array_alpha = cdata[8:12]
    self.infopacket["ip"] = '.'.join(str(int(x)) for x in array_alpha)
    self.infopacket["unitno"] = int(cdata[12])
    try:
     self.infopacket["build"] = int(cdata[13])
     self.infopacket["name"] = decodezerostr(cdata[14])
     self.infopacket["type"] = int(cdata[15])
     pport = int(cdata[16])
     if pport not in [80,8008,8080]:
      pport = 80
     self.infopacket["port"] = pport
    except:
     pass
   elif tbuffer[1] == 3: #sensor info min len=137
    self.pkgtype = 3
    if len(self.buffer)>162:
     cdata = struct.unpack_from('<BBBBBBB26s26s26s26s26s26s',self.buffer)
    else:
     cdata = struct.unpack_from('<BBBBBBB26s26s26s26s26s',self.buffer)
    self.sensorinfo["sunit"] = int(cdata[2])
    self.sensorinfo["dunit"] = int(cdata[3])
    self.sensorinfo["sti"]   = int(cdata[4])
    self.sensorinfo["dti"]   = int(cdata[5])
    self.sensorinfo["dnum"]  = int(cdata[6])
    self.sensorinfo["taskname"] = decodezerostr(cdata[7])
    self.sensorinfo["valuenames"] = []
    for v in range(pglobals.VARS_PER_TASK):
     tvn = decodezerostr(cdata[8+v])
     if tvn != "":
      self.sensorinfo["valuenames"].append(tvn)
   elif tbuffer[1] == 5: #sensor info min len=22
    self.pkgtype = 5
    cdata = struct.unpack_from('<8B4f',self.buffer)
    self.sensordata["sunit"] = int(cdata[2])
    self.sensordata["dunit"] = int(cdata[3])
    self.sensordata["sti"]   = int(cdata[4])
    self.sensordata["dti"]   = int(cdata[5])
    self.sensordata["values"] = []
    for f in range(pglobals.VARS_PER_TASK):
     self.sensordata["values"].append(float(cdata[8+f]))

# Helper functions

def getunitordfromnum(unitno):
  for n in range(len(settings.nodelist)):
   if int(settings.nodelist[n]["unitno"]) == int(unitno):
    return n
  return -1

def decodezerostr(barr):
 result = ""
 for b in range(len(barr)):
  if barr[b] == 0:
   try:
    result = barr[:b].decode("utf-8")
   except:
    result = str(barr[:b])
   break
 if b>=len(barr)-1:
   try:
    result = barr.decode("utf-8")
   except:
    result = str(barr)
 return result.strip()
