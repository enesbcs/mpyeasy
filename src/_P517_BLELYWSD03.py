#############################################################################
####################### BLE LYWSD03 plugin for mpyEasy ######################
#############################################################################
#
# Xiaomi Mijia LYWSD03 Bluetooth Temperature Humidity Sensor plugin.
#
# Based on:
#  https://github.com/JsBergbau/MiTemperature2/blob/master/LYWSD03MMC.py
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

TEMP_HUM_WRITE_HANDLE = 0x0038
TEMP_HUM_WRITE_VALUE = bytes([0x01, 0x00])
TEMP_HUM_WRITE_HANDLE2 = 0x0046
TEMP_HUM_WRITE_VALUE2 = bytes([0xf4, 0x01, 0x00])

class Plugin(plugin.PluginProto):
 PLUGIN_ID = 517
 PLUGIN_NAME = "Environment - BLE Xiaomi LYWSD03 Hygrometer (TESTING)"
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
  self._lastdataservetime = 0
  self.TARR = []
  self.HARR = []
  self._blestatus = None

 def webform_load(self): # create html page for settings
  ws.addFormTextBox("Device Address","plugin_517_addr",str(self.taskdevicepluginconfig[0]),20)
  ws.addFormNote("Enable blueetooth then <a href='blescanner'>scan LYWSD03 address</a> first.")
  ws.addFormCheckBox("Add Battery value for non-Domoticz system","plugin_517_bat",self.taskdevicepluginconfig[1])
  return True

 def webform_save(self,params): # process settings post reply
  self.taskdevicepluginconfig[0] = str(ws.arg("plugin_517_addr",params)).strip()
  self.taskdevicepluginconfig[1] = (ws.arg("plugin_517_bat",params)=="on")
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
     self._BLEPeripheral = TempHumDelegate3(BLEHelper.BLEDev,str(self.taskdevicepluginconfig[0]),self.callbackfunc)
     misc.addLog(pglobals.LOG_LEVEL_INFO,"BLE LYWSD03 init ok")
   except Exception as e:
     misc.addLog(pglobals.LOG_LEVEL_ERROR,"BLE LYWSD03 init error"+str(e))
  else:
   self.ports = ""

 def plugin_read(self):
   if self.enabled:
      if utime.ticks_ms()-self._lastdataservetime>(self.interval*2000):
          self.readinprogress = False
          self.readlevel=0     
   if self.enabled and self.readinprogress==False:
      self.readinprogress = True
      if (len(self.TARR)+len(self.HARR))==0:
       try:
        if self._blestatus.isscaninprogress():
         self._blestatus.requeststopscan(self.taskindex)
         self.readinprogress = False
         return False
       except Exception as e:
        self.readinprogress = False
        return False
       if self._blestatus.nodataflows():
        self._blestatus.registerdataprogress(self.taskindex)
        try:
         self.readlevel = 0
         res = self._BLEPeripheral.getSensorData()
        except:
         res = 9
        if res==9:
         self.disconnect()
         time.sleep(1)
        utime.sleep_ms(40)
      else:
        self.parsedata()
      self.readinprogress = False

 def parsedata(self):
        try:
         self.battery = self._BLEPeripheral.mitempdata["battery"]
        except:
         pass
#        print(self.TARR,self.HARR)#debug
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
        if self.interval>10:
          self.disconnect()
        self._blestatus.unregisterdataprogress(self.taskindex)
        self.TARR = []
        self.HARR = []
        self.readlevel = 0

 def callbackfunc(self,temp=None,hum=None):
  print("p517cb",temp,hum,self.readlevel)#debug
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
   self.readinprogress = False    
  except:
   pass

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

class TempHumDelegate3():
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
        self.connect_retry = 2
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

        elif event == BLEHelper._IRQ_GATTC_NOTIFY and self.connected:
            conn_handle, value_handle, notify_data = data
            if int(value_handle) in [0x36,0x3c,0x4b]:
             self.__cache=notify_data
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
                utime.sleep(self.connect_retry_timeout/1000)
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
        The sensor returns a 5byte package
        """
        data = self.__cache
        if type(data) is not bytes:
            data = bytes(data)        
        temp = None
        hum = None
        batt = None
        try:
         temp = float(data[1]*256 + data[0]) / 100
         hum = data[2]
        except:
         pass
        try:
         battvolt = float(data[4]*256 + data[3]) / 1000
        except:
         battvolt = -1
        batt = min(int(round((battvolt - 2.1),2) * 100), 100)
        if battvolt<=0 or batt<=0:
         batt = 0
#        print("r",battvolt,batt,temp,hum)#debug
        if temp is not None or hum is not None:
          self.mitempdata["humidity"] = hum
          self.mitempdata["temperature"] = temp
          self.mitempdata["result"]=0
        self.mitempdata["battery"] = batt
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
#         utime.sleep(50)
#         self.__ble.gattc_write(self.conn_handle, TEMP_HUM_WRITE_HANDLE2, TEMP_HUM_WRITE_VALUE2,0)
#         utime.sleep(50)
        except Exception as e:
         self.connected = False
         return 9
        return 0
