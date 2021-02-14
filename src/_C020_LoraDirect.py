#############################################################################
################## LORA Direct controller for mPyEasy #######################
#############################################################################
#
# This controller is able to harvest datas arriving from direct LORA sensors
# or to send LORA RAW data. This is NOT LoraWan, it is direct LORA connection
# between local nodes!
#
# Supported hardware is SX1278 through uPyLora
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
import inc.lib_p2pbuffer as p2pbuffer
import unet
try:
 from inc.lora.sx127x import SX127x
 import inc.libhw as libhw
except:
 pass

CAPABILITY_BYTE = (1+2) # send and receive
REPORTINTERVAL = 1800 #sec

class Controller(controller.ControllerProto):
 CONTROLLER_ID = 20
 CONTROLLER_NAME = "LORA Direct (EXPERIMENTAL)"

 def __init__(self,controllerindex):
  controller.ControllerProto.__init__(self,controllerindex)
  self.usesID = True
  self.onmsgcallbacksupported = True
  self.controllerport = 1
  self._lora = None
  self.sysinfosent=0
  self.timer30s = True
  self.sf = 9
  self.bw = 250000
  self.coding = 5
  self.freq = 869.5
  self.sync = 0x12
  self.duty = 10
  self.defaultunit = 0
  self.enablesend = True
  self.dio_0 = -1
  self.ss = -1
  self.led = -1
  self.spi = -1
  self.rst = -1
  self._started = False
  self.nexttransmit = 0
  self.listening = False
  self.sending = False

 def controller_init(self,enablecontroller=None):
  lparams = {
            'frequency': 868E6,
            'tx_power_level': 2,
            'signal_bandwidth': 125E3,
            'spreading_factor': 8,
            'coding_rate': 5,
            'preamble_length': 8,
            'implicit_header': False,
            'sync_word': 0x12,
            'enable_CRC': True,
            'invert_IQ': False,
            }
  if enablecontroller != None:
   self.enabled = enablecontroller
  self.initialized = False
  if self.enabled:
   if int(settings.Settings["Unit"])>0:
    self.controllerport = settings.Settings["Unit"]
   try:
    if self._started:
     pass
   except:
    self._started = False
   spil = None
   try:
     if int(self.spi)==1:
      spil = libhw.spi1
     elif int(self.i2c)==2:
      spil = libhw.spi2
   except:
     pass
   if spil is None:
     return False
   try:
    lparams['frequency'] = self.freq * 1000000
    lparams['signal_bandwidth'] = self.bw
    lparams['spreading_factor'] = self.sf
    lparams['coding_rate'] = self.coding
    lparams['sync_word'] = self.sync
    lparams['enable_CRC'] = True
    pin_config = {}
    if self.dio_0>-1:
     pin_config["dio_0"] = self.dio_0
    if self.ss>-1:
     pin_config["ss"] = self.ss
    if self.led>-1:
     pin_config["led"] = self.led
    if self.rst>-1:
     pin_config["rst"] = self.rst
    self._lora = SX127x(spil, pins=pin_config, parameters=lparams)
    if self.dio_0>-1:
     self._lora.on_receive(self.pkt_receiver)
    self.listening = False
    self.sending = False
    self.initialized = True
    self._started = True
    self.sysinfosent=0
    self.nexttransmit = 0
    misc.addLog(pglobals.LOG_LEVEL_INFO,"LORA Direct initialized")
   except Exception as e:
    self.initialized = False
    self._started = False
    misc.addLog(pglobals.LOG_LEVEL_ERROR,"LORA Direct init error: "+str(e))
  return True

 def disconnect(self):
  self.connected = False
  try:
   if self._lora is not None:
     self._lora.sleep()
  except:
   pass

 def webform_load(self):
  ws.addFormNote("IP and Port parameter is not used!")
  ws.addFormNote("SX127x hardware supported by uPyLoRa library")
  ws.addHtml("<p>Example sender sketches could be find <a href='https://github.com/enesbcs/EasyLora'>here</a>.")
  ws.addTableSeparator("Hardware settings",2,3)
  try:
     options = libhw.getspilist()
  except:
     options = []
  ws.addHtml("<tr><td>SPI line:<td>")
  ws.addSelector_Head("spi",True)
  for d in range(len(options)):
     ws.addSelector_Item("SPI"+str(options[d]),options[d],(self.spi==options[d]),False)
  ws.addSelector_Foot()
  ws.addFormPinSelect("DIO0 (IRQ) pin", "dio_0", self.dio_0,0)
  ws.addFormPinSelect("SS pin", "ss", self.ss,1)
  ws.addFormPinSelect("RST pin", "rst", self.rst,1)
  ws.addFormNote("Optional")
  ws.addFormPinSelect("LED pin", "led", self.led,1)
  ws.addFormNote("Optional")
  try:
   ws.addTableSeparator("LoRa settings",2,3)
   ws.addFormFloatNumberBox("Frequency","freq",self.freq,433,928)
   ws.addUnit("Mhz")
   if self._lora is not None:
     try:
      afreq = (self._lora._frequency)/1000000
     except:
      afreq = "UNINITIALIZED"
     ws.addFormNote("Current frequency: "+str(afreq)+" Mhz")
   ws.addFormNote("Please check local regulations for your selected frequency!")

   options = ["10%","1%","0.1%"]
   optionvalues = [10,100,1000]
   ws.addFormSelector("Duty cycle","duty",len(optionvalues),options,optionvalues,None,self.duty)
   ws.addFormNote("Please check your local Duty cycle regulations for your selected frequency!")

   ws.addFormNumericBox("Spreading factor","spreading",self.sf,6,12)
   options = ["7.8","10.4","15.6","20.8","31.25","41.7","62.5","125","250"]
   optionvalues = [7.8E3, 10.4E3, 15.6E3, 20.8E3, 31.25E3, 41.7E3, 62.5E3, 125E3, 250E3]
   ws.addFormSelector("Bandwidth","bw",len(optionvalues),options,optionvalues,None,self.bw)
   ws.addUnit("khz")

   options = ["CR4/5","CR4/6","CR4/7","CR4/8"]
   optionvalues = [5,6,7,8]
   ws.addFormSelector("Coding rate","coding",len(optionvalues),options,optionvalues,None,self.coding)

   ws.addFormNumericBox("Sync Word","sync",self.sync,0,255)
   ws.addHtml( '( 0x{:02x} )'.format(self.sync) )

   ws.addFormNote("Default 0x12, LoRaWAN is 0x34. Nodes can only communicate each other if uses same sync word!")

   ws.addFormCheckBox("Enable Sending","sender",self.enablesend)
   ws.addFormNumericBox("Default destination node index","defaultnode",self.defaultunit,0,255)
   ws.addFormNote("Default node index for data sending")
  except Exception as e:
   misc.addLog(pglobals.LOG_LEVEL_ERROR,str(e))
  return True

 def webform_save(self,params):
  try:
   self.freq = float(ws.arg("freq",params))
   self.duty = int(ws.arg("duty",params))
   self.sf = int(ws.arg("spreading",params))
   self.coding = int(ws.arg("coding",params))
   self.sync = int(ws.arg("sync",params))
   self.defaultunit = int(ws.arg("defaultnode",params))
   self.enablesend = (ws.arg("sender",params)=="on")
   self.spi = int(ws.arg("spi",params))
   self.dio_0 = int(ws.arg("dio_0",params))
   self.ss = int(ws.arg("ss",params))
   self.led = int(ws.arg("led",params))
   self.rst = int(ws.arg("rst",params))
  except Exception as e:
   misc.addLog(pglobals.LOG_LEVEL_ERROR,"LORA parameter save: "+str(e))
  return True

 def nodesort(self,item):
  v = 0
  try:
   v = int(item["unitno"])
  except:
   v = 0
  return v

 def pkt_receiver(self,payload):
  if self.enabled:
    try:
     rssi = self._lora.packet_rssi()
    except:
     rssi = -100
    try:
     dp = p2pbuffer.data_packet()
     dp.buffer = payload
     dp.decode()
#    print("REC",payload,dp.buffer) #debug
    except:
     pass
    try:
     if dp.pkgtype!=0:
        if dp.pkgtype==1:
#         print(dp.infopacket)
         if int(dp.infopacket["unitno"]) == int(settings.Settings["Unit"]): # skip own messages
          return False
         un = getunitordfromnum(dp.infopacket["unitno"]) # process incoming alive reports
         if un==-1:
          # CAPABILITIES byte: first bit 1 if able to send, second bit 1 if able to receive
          settings.p2plist.append({"protocol":"LORA","unitno":dp.infopacket["unitno"],"name":dp.infopacket["name"],"build":dp.infopacket["build"],"type":dp.infopacket["type"],"mac":dp.infopacket["mac"],"lastseen":utime.localtime(),"lastrssi":rssi,"cap":dp.infopacket["cap"]})
          misc.addLog(pglobals.LOG_LEVEL_INFO,"New LORA unit discovered: "+str(dp.infopacket["unitno"])+" "+str(dp.infopacket["name"]))
          settings.p2plist.sort(reverse=False,key=self.nodesort)
         else:
          misc.addLog(pglobals.LOG_LEVEL_DEBUG,"Unit alive: "+str(dp.infopacket["unitno"]))
          if settings.p2plist[un]["type"]==0:
           settings.p2plist[un]["name"] = dp.infopacket["name"]
           settings.p2plist[un]["build"] = dp.infopacket["build"]
           settings.p2plist[un]["type"] = dp.infopacket["type"]
           settings.p2plist[un]["mac"] = dp.infopacket["mac"]
          settings.p2plist[un]["cap"] = dp.infopacket["cap"]
          settings.p2plist[un]["lastseen"] = utime.localtime()
          settings.p2plist[un]["lastrssi"] = rssi

        elif dp.pkgtype==5:                          # process incoming data
          if int(dp.sensordata["sunit"])==int(settings.Settings["Unit"]):
           return False
          un = getunitordfromnum(dp.sensordata["sunit"])
          if un>-1: # refresh lastseen data
           settings.p2plist[un]["lastseen"] = utime.localtime()
           settings.p2plist[un]["lastrssi"] = rssi
          else:
           settings.p2plist.append({"protocol":"LORA","unitno":dp.sensordata["sunit"],"name":"","build":0,"type":0,"mac":"","lastseen":utime.localtime(),"lastrssi":rssi,"cap":1})

          if (int(settings.Settings["Unit"])==int(dp.sensordata["dunit"])) or (0==int(dp.sensordata["dunit"])): # process only if we are the destination or broadcast
           ltaskindex = -1
           for x in range(0,len(settings.Tasks)): # check if the sent IDX already exists?
             try:
              if (type(settings.Tasks[x]) is not bool and settings.Tasks[x]):
                if settings.Tasks[x].controlleridx[self.controllerindex]==int(dp.sensordata["idx"]):
                 ltaskindex = x
                 break
             except Exception as e:
              print(e)
           dvaluecount = int(dp.sensordata["valuecount"])
           if pglobals.VARS_PER_TASK<dvaluecount: # avoid possible buffer overflow
            dvaluecount = pglobals.VARS_PER_TASK
           if ltaskindex < 0: # create new task if necessarry
            devtype = int(dp.sensordata["pluginid"])
            m = False
            try:
             for y in range(len(pglobals.deviceselector)):
              if int(pglobals.deviceselector[y][1]) == devtype:
               m = __import__(pglobals.deviceselector[y][0])
               break
            except:
             m = False
            TempEvent = None
            if m:
             try:
              TempEvent = m.Plugin(-1)
             except:
              TempEvent = None
            if True:
             ltaskindex = -1
             for x in range(0,len(settings.Tasks)): # check if there are free TaskIndex slot exists
               try:
                if (type(settings.Tasks[x]) is bool):
                 if settings.Tasks[x]==False:
                  ltaskindex = x
                  break
               except:
                pass
             devtype = 33 # dummy device
             m = False
             try:
              for y in range(len(pglobals.deviceselector)):
               if int(pglobals.deviceselector[y][1]) == devtype:
                m = __import__(pglobals.deviceselector[y][0])
                break
             except:
              m = False
             if m:
              if ltaskindex<0:
               ltaskindex = len(settings.Tasks)
              try:
               settings.Tasks[ltaskindex] = m.Plugin(ltaskindex)
              except:
               ltaskindex = len(settings.Tasks)
               settings.Tasks.append(m.Plugin(ltaskindex))  # add a new device
              settings.Tasks[ltaskindex].plugin_init(True)
              settings.Tasks[ltaskindex].remotefeed = True  # Mark that this task accepts incoming data updates!
              settings.Tasks[ltaskindex].enabled  = True
              settings.Tasks[ltaskindex].interval = 0
              settings.Tasks[ltaskindex].senddataenabled[self.controllerindex]=True
              settings.Tasks[ltaskindex].controlleridx[self.controllerindex]=int(dp.sensordata["idx"])
              if TempEvent is not None:
               settings.Tasks[ltaskindex].taskname = TempEvent.PLUGIN_NAME.replace(" ","")
               for v in range(dvaluecount):
                settings.Tasks[ltaskindex].valuenames[v] = TempEvent.valuenames[v]
               settings.Tasks[ltaskindex].taskdevicepluginconfig[0] = TempEvent.vtype
               settings.Tasks[ltaskindex].vtype = TempEvent.vtype
              else:
               settings.Tasks[ltaskindex].taskname = settings.Tasks[ltaskindex].PLUGIN_NAME.replace(" ","")
              settings.Tasks[ltaskindex].valuecount = dvaluecount
              settings.savetasks()
           if ltaskindex<0:
            return False
           misc.addLog(pglobals.LOG_LEVEL_DEBUG,"Sensordata update arrived from unit "+str(dp.sensordata["sunit"])) # save received values
           if settings.Tasks[ltaskindex].remotefeed:
            recok = False
            try:
             if self._onmsgcallbackfunc is not None and settings.Tasks[ltaskindex].recdataoption:
              self._onmsgcallbackfunc(self.controllerindex,-1,self._dp.sensordata["values"],settings.Tasks[ltaskindex].gettaskname())
              recok = True
            except:
              pass
            if recok==False:
             for v in range(dvaluecount):
              settings.Tasks[ltaskindex].set_value(v+1,dp.sensordata["values"][v],False)
             settings.Tasks[ltaskindex].plugin_senddata()

        elif dp.pkgtype==7: # process incoming command
          if int(dp.cmdpacket["sunit"])==int(settings.Settings["Unit"]):
           return False
          un = getunitordfromnum(dp.cmdpacket["sunit"])
          if un>-1: # refresh lastseen data
           settings.p2plist[un]["lastseen"] = utime.localtime()
           settings.p2plist[un]["lastrssi"] = rssi
          else:
           settings.p2plist.append({"protocol":"LORA","unitno":dp.cmdpacket["sunit"],"name":"","build":0,"type":0,"mac":"","lastseen":utime.localtime(),"lastrssi":rssi,"cap":1})
          if (int(settings.Settings["Unit"])==int(dp.cmdpacket["dunit"])) or (0==int(dp.cmdpacket["dunit"])): # process only if we are the destination or broadcast
           misc.addLog(pglobals.LOG_LEVEL_INFO,"Command arrived from "+str(dp.cmdpacket["sunit"]))
#           print(dp.cmdpacket["cmdline"]) # DEBUG
           commands.doExecuteCommand(dp.cmdpacket["cmdline"],True)
    except Exception as e:
     print("C20 decode error",str(e))

 def senddata(self,idx, taskobj, changedvalue=-1): # called by plugin
  if self.enabled and self.initialized and self.enablesend:
   if int(idx)>0:
    if taskobj.remotefeed == False:  # do not republish received values
     dp2 = p2pbuffer.data_packet()
     dp2.sensordata["sunit"] = settings.Settings["Unit"]
     dp2.sensordata["dunit"] = self.defaultunit
     dp2.sensordata["idx"] = idx
     dp2.sensordata["pluginid"] = taskobj.pluginid
     dp2.sensordata["valuecount"] = taskobj.valuecount
     for u in range(taskobj.valuecount):
      dp2.sensordata["values"][u] = taskobj.uservar[u]
     try:
      dp2.encode(5)
      return self.lorasend(dp2.buffer)
     except:
      pass
  return False

 def sendcommand(self,unitno,commandstr):
  if self.enabled and self.initialized and self.enablesend:
    try:
     dpc = p2pbuffer.data_packet()
     dpc.cmdpacket["sunit"] = settings.Settings["Unit"]
     dpc.cmdpacket["dunit"] = unitno
     dpc.cmdpacket["cmdline"] = commandstr
     dpc.encode(7)
     return self.lorasend(dpc.buffer)
    except Exception as e:
     pass
  return False

 def timer_thirty_second(self):
  try:
   if self.enabled and self.initialized and ((self.sysinfosent==0) or (time.time()>self.sysinfosent+REPORTINTERVAL)):
    if self.sendsysinfo():
     self.sysinfosent = time.time()
  except Exception as e:
   self.sysinfosent = 0

 def sendsysinfo(self):
  if self.enabled and self.initialized and self.enablesend:
    dp = p2pbuffer.data_packet()
    try:
     dp.infopacket["mac"] = str(unet.get_mac())
    except:
     dp.infopacket["mac"] = "00:00:00:00:00:00"
    dp.infopacket["unitno"] = int(settings.Settings["Unit"])
    dp.infopacket["build"] = int(pglobals.BUILD)
    dp.infopacket["name"] = settings.Settings["Name"]
    dp.infopacket["type"] = int(pglobals.NODE_TYPE_ID)
    # CAPABILITIES byte: first bit 1 if able to send, second bit 1 if able to receive
    dp.infopacket["cap"] = int(CAPABILITY_BYTE)
    try:
     dp.encode(1)
     misc.addLog(pglobals.LOG_LEVEL_DEBUG,"LORA alive pkt sent")
     return self.lorasend(dp.buffer)
    except:
     pass
  return False

 def lorasend(self,data):
       while self.listening or self.sending:
         pass
       if (utime.ticks_ms()<self.nexttransmit):
        misc.addLog(pglobals.LOG_LEVEL_DEBUG,"Next possible transmit "+str(self.nexttransmit)+" Now:"+str(utime.ticks_ms()))
        return False
       try:
        self.sending = True
        self._lora.println(data)
        self.sending = False
       except Exception as e:
        self.sending = False
        self.nexttransmit = 0
        misc.addLog(pglobals.LOG_LEVEL_DEBUG,"LoRa send error: "+str(e))
        return False
       self.nexttransmit = ((self._lora._txend-self._lora._txstart)*self.duty)+self._lora._txend
#       print("Sending ",data,(self._lora._txend-self._lora._txstart)) #debug
       return True

 def periodic_check(self):
    try:
     if self.dio_0<0 and self.enabled and self.initialized: #backup check for msg when no IRQ setted
       if self._lora._lock==False and self._lora.received_packet() and self.listening==False:
          self.listening = True
          payload = self._lora.read_payload()
          self.pkt_receiver(payload)
          self.listening = False
    except Exception as e:
     self.listening = False
 
# Helper functions

def getunitordfromnum(unitno):
  for n in range(len(settings.p2plist)):
   if int(settings.p2plist[n]["unitno"]) == int(unitno) and str(settings.p2plist[n]["protocol"]) == "LORA":
    return n
  return -1

