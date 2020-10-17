#############################################################################
######################## BLE Mijia plugin for mpyEasy #######################
#############################################################################
#
# Xiaomi Mijia Bluetooth Temperature Humidity Sensor plugin.
#
# Based on:
#  https://github.com/gheesung/BLEGateway/blob/master/devices/mithermometer.py
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
try:
 import ubinascii as binascii
except ImportError:
 import binascii
from random import uniform
import inc.lib_blehelper as BLEHelper

BATTERY_HANDLE = 0x0018
TEMP_HUM_WRITE_HANDLE = 0x0010
TEMP_HUM_READ_HANDLE = 0x000E
TEMP_HUM_WRITE_VALUE = bytes([0x01, 0x00])

_HANDLE_READ_NAME = 0x03
_HANDLE_READ_BATTERY = 0x18
_HANDLE_READ_VERSION = 0x24
_HANDLE_READ_SENSOR_DATA = 0x10

class Plugin(plugin.PluginProto):
 PLUGIN_ID = 512
 PLUGIN_NAME = "Environment - BLE Xiaomi Mijia Temperature&Humidity (TESTING)"
 PLUGIN_VALUENAME1 = "Temperature"
 PLUGIN_VALUENAME2 = "Humidity"
 PLUGIN_VALUENAME3 = "Battery"

 def __init__(self,taskindex): # general init
  plugin.PluginProto.__init__(self,taskindex)
  self.dtype = pglobals.DEVICE_TYPE_BLE
  self.vtype = pglobals.SENSOR_TYPE_TEMP_HUM
  self.valuecount = 2
  self.senddataoption = True
  self.recdataoption = False
  self.timeroption = True
  self.timeroptional = True
  self.connected = False
  self.formulaoption = True
  self._BLEPeripheral = False
  self.waitnotifications = False
  self.readinprogress = False
  self.readlevel = 0
  self.battery = 0
  self.lastbatteryreq = 0
  self._lastdataservetime = 0
  self.TARR = []
  self.HARR = []
  self._blestatus = None

 def webform_load(self): # create html page for settings
  ws.addFormTextBox("Device Address","plugin_512_addr",str(self.taskdevicepluginconfig[0]),20)
  ws.addFormNote("Enable blueetooth then <a href='blescanner'>scan MJ_HT_ address</a> first.")
  ws.addFormCheckBox("Add Battery value for non-Domoticz system","plugin_512_bat",self.taskdevicepluginconfig[1])
  return True

 def webform_save(self,params): # process settings post reply
  self.taskdevicepluginconfig[0] = str(ws.arg("plugin_512_addr",params)).strip()
  self.taskdevicepluginconfig[1] = (ws.arg("plugin_512_bat",params)=="on")
  self.plugin_init()
  return True

 def plugin_init(self,enableplugin=None):
  plugin.PluginProto.plugin_init(self,enableplugin)
  self.readinprogress = False
  self.readlevel = 0
  self.TARR = []
  self.HARR = []
  self.uservar[0] = 0
  self.uservar[1] = 0
  if self.enabled:
   self.battery = -1
   self._lastdataservetime = 0
   if self.taskdevicepluginconfig[1]:
    self.valuecount = 3
    self.vtype = pglobals.SENSOR_TYPE_TRIPLE
   else:
    self.valuecount = 2
    self.vtype = pglobals.SENSOR_TYPE_TEMP_HUM
   if len(str(self.taskdevicepluginconfig[0])) < 12:
     return False
   self.ports = str(self.taskdevicepluginconfig[0])
   try:
     self._blestatus  = BLEHelper.BLEStatus
     BLEHelper.bleinit(True)
     self._BLEPeripheral = TempHumDelegate(BLEHelper.BLEDev,str(self.taskdevicepluginconfig[0]),self.callbackfunc)
     misc.addLog(pglobals.LOG_LEVEL_INFO,"BLE Mijia init ok")
   except Exception as e:
     misc.addLog(pglobals.LOG_LEVEL_ERROR,"BLE Mijia init error"+str(e))
  else:
   self.ports = ""

 def plugin_read(self):
#   print("p512 read",self.enabled,self.readinprogress)#debug
   if self.enabled:
      if utime.ticks_ms()-self._lastdataservetime>(self.interval*2000):
          self.readinprogress = False
          self.readlevel=0          
   if self.enabled and self.readinprogress==False:       
      self.readinprogress = True
#      print(self.TARR,self.HARR)#debug
      if (len(self.TARR)+len(self.HARR))==0:
       try:
        if self._blestatus.isscaninprogress():
         self._blestatus.requeststopscan(self.taskindex)
         self.readinprogress = False
         return False
       except Exception as e:
        self.readinprogress = False
        return False
#       print(self._blestatus.nodataflows(),self._blestatus.dataflow)#debug
       if self._blestatus.nodataflows():
        self._blestatus.registerdataprogress(self.taskindex)
        try:
         print("getdata")#debug
         self.readlevel = 0         
         if ((time.time()-self.lastbatteryreq)>600) or (self.battery<=0):
          self._BLEPeripheral.getBatteryLevel()
          self.lastbatteryreq = time.time()
         res = self._BLEPeripheral.getSensorData()
        except Exception as e:
         print(e)#debug
         res = 9
        print("p512",res)#debug
        if res==9:
         try:
          self.disconnect()
#          BLEHelper.BLEDev.active(False)
          time.sleep(1)
          self.plugin_init()
#          BLEHelper.BLEDev.active(True)
         except Exception as e:
          print("reconn",e)#debug
      else:
        self.parsedata()
      self.readinprogress = False
 
 def parsedata(self):
       try:
         self.battery = self._BLEPeripheral.mitempdata["battery"]
       except:
         pass
       try:
        print(self.TARR,self.HARR)#debug
        maxl = len(self.TARR)
        if len(self.HARR)<maxl:
         maxl = len(self.HARR)
        for ii in reversed(range(maxl)):
         if self.TARR[ii] is not None:
          maxl = ii
          break
        if self.TARR[maxl] is not None:
         self.set_value(1,self.TARR[maxl],False)
         if self.taskdevicepluginconfig[1]:
          self.set_value(2,self.HARR[maxl],False)
          self.set_value(3,self.battery,False)
         else:
          self.set_value(2,self.HARR[maxl],False)
         self.plugin_senddata()
         self._lastdataservetime = utime.ticks_ms()
        self._blestatus.unregisterdataprogress(self.taskindex)
        if self.interval>10:
         self.disconnect()
        self.TARR = []
        self.HARR = []
        self.readlevel = 0
       except Exception as e:
        print("p512parse",e)#debug
        self.TARR = []
        self.HARR = []
        self.readlevel = 0

 def callbackfunc(self,temp=None,hum=None):
  print("p512cb",self.readlevel)#debug
  self.readlevel += 1
  try:
   self._blestatus.unregisterdataprogress(self.taskindex)
  except:
   pass
  if self.readlevel > 1:
     return False
  try:
   if self.enabled:
    self.TARR.append(temp)
    self.HARR.append(hum)
    if utime.ticks_ms()-self._lastdataservetime>2000:
     self.parsedata()
  except Exception as e:
   print("p512cf",e)#debug

 def disconnect(self):
  try:
   self._blestatus.unregisterdataprogress(self.taskindex)
   self._BLEPeripheral.disconnect()
  except:
   pass

 def plugin_exit(self):
  self.disconnect()

def encode_mac(mac):
    assert isinstance(mac, str) and len(mac) == 17, ValueError("mac address value error")
    return binascii.unhexlify(''.join( c for c in mac if  c not in ':' ))

class TempHumDelegate():
    def __init__(self, hw, devname, callback):
        self.callback = callback
        self.__ble = hw
        self.mac = devname

        self.read_done = False
        self.__cache = None

        # init the dict
        self.mitempdata = {}
        self.mitempdata["result"] = 9
        self.mitempdata["humidity"] = 0
        self.mitempdata["battery"] = 0
        self.mitempdata["temperature"] = 0

        self.conn_handle = None
        self.connect_retry_timeout = 5000 # millisecond
        self.connect_retry = 5
        self.connected = False
        self.addrbinary = encode_mac(self.mac)

    def bt_irq(self, event, data):
        if event == BLEHelper._IRQ_PERIPHERAL_CONNECT:
            self.conn_handle, self.addr_type, self.addr = data
            self.connected=True

        elif event == BLEHelper._IRQ_PERIPHERAL_DISCONNECT:
            self.connected = False
            self.conn_handle = None

        elif event == BLEHelper._IRQ_GATTC_WRITE_DONE:
            # A gattc_write() has completed.
            conn_handle, value_handle, status = data

        elif event == BLEHelper._IRQ_GATTC_READ_RESULT and self.connected:
            # A gattc_read() has completed.
            conn_handle, value_handle, char_data = data
            if value_handle == _HANDLE_READ_BATTERY:
                self.__cache=char_data
                self.mitempdata["battery"] = int(char_data[0])

        elif event == BLEHelper._IRQ_GATTC_READ_DONE:
            conn_handle, value_handle, status = data
            self.read_done = True

        elif event == BLEHelper._IRQ_GATTC_NOTIFY and self.connected:
            conn_handle, value_handle, notify_data = data
            self.__cache=notify_data
            if value_handle == TEMP_HUM_READ_HANDLE:
             self._parse_data()
            self.read_done = True

        gc.collect()

    def connect(self):
        self.__ble.irq(self.bt_irq)

        if self.connected == True:
            return 0
        connect_retry = 0
        self.read_done = False
        while self.connected == False:
            try:
                if connect_retry < self.connect_retry:
                    self.__ble.gap_connect(0, self.addrbinary, self.connect_retry_timeout)
                    if connect_retry > 1:
                        print ("retry...", connect_retry)
                else:
                    self.mitempdata["result"] = 9
                    break
                connect_retry += 1
                utime.sleep(self.connect_retry_timeout/1000)
            except OSError as exc:
#                print ("OSError:", exc.args[0], connect_retry)
                connect_retry += 1
        return 9

    def disconnect(self):
        '''
        disconnect from ble device.
        Normally the device will disconnect itself. Call this want to explicity disconnect
        '''
        if self.conn_handle != None:
            self.__ble.gap_disconnect(self.conn_handle)
        if self.connected == False:
            return 0
        else:
            return 9
        self.connected = False

    def _parse_data(self):
        """Parses the byte array returned by the sensor.
        The sensor returns a string with 14 bytes. Example: "T=26.2 H=45.4\x00"
        """
        data = self.__cache
        if type(data) is not bytes:
            data = bytes(data)
        temp = None
        hum = None
        try:
         data = data.decode("utf-8").strip(' \t\r\n\0')
         tarr = data.split(" ")
         td = tarr[0].split("=")
         th = tarr[1].split("=")
         temp = float(td[1])
         hum  = float(th[1])
        except Exception as e:
         pass #print("mjht parse error",data,str(e))
        print(self.mitempdata)#debug
        self.mitempdata["humidity"] = hum
        self.mitempdata["temperature"] = temp
        self.mitempdata["result"]=0
        self.callback(temp,hum)

    def getSensorData(self):
        '''
        get the temperature and humdity data.
        return 9 if connection not connected or cannot read data
        '''
        self.connect()
        if self.connected == False:
            return 9
        try:
         self.__ble.gattc_write(self.conn_handle, TEMP_HUM_WRITE_HANDLE, TEMP_HUM_WRITE_VALUE,0)
        except:
         return 9
        return 0

    def getBatteryLevel(self):
        '''
        get the battery level.
        '''
        self.connect()
        if self.connected == False:
            return 9
        self.__ble.gattc_read(self.conn_handle, _HANDLE_READ_BATTERY)
