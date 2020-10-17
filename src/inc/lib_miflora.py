#############################################################################
##################### Helper Library for BLE Mi Flora #######################
#############################################################################
#
# Copyright (C) 2020 by Alexander Nagy - https://bitekmindenhol.blog.hu/
#
import gc
import time
try:
 import utime
except:
 import faketime as utime
try:
 import ubinascii as binascii
except ImportError:
 import binascii
import inc.lib_blehelper as BLEHelper
from struct import unpack

_HANDLE_READ_BATTERY  = 0x38
_HANDLE_READ_SENSOR   = 0x35
TEMP_HUM_WRITE_HANDLE = 0x33
TEMP_HUM_WRITE_VALUE  = bytes([0xA0, 0x1F])

def encode_mac(mac):
    assert isinstance(mac, str) and len(mac) == 17, ValueError("mac address value error")
    return binascii.unhexlify(''.join( c for c in mac if  c not in ':' ))

class MiFlora():
    def __init__(self, hw, devname, cachetimeout=60):
        self.__ble = hw
        self.address = devname

        self.read_done = False
        self.busy = False
        self.__cache = None
        self._readok = False

        self.timeout = cachetimeout
        if self.timeout<5:
         self.timeout=5

        self.battery = 255
        self._temperature = None
        self._light = None
        self._moisture = None
        self._conductivity = None
        self._last_read = 0
        self._last_bread = 0

        self.conn_handle = None
        self.connect_retry_timeout = 5000 # millisecond
        self.connect_retry = 5
        self.connected = False
        self.addrbinary = encode_mac(self.address)

    def getBatteryLevel(self):
        '''
        get the battery level.
        '''
        if self.busy:
         return False
        if self.battery==255 or self.battery<=0 or (time.time() - self.timeout > self._last_bread):
         self.busy = True
         self.connect()
         if self.connected == False:
            self.busy = False
            return False
         try:
          self.__ble.gattc_read(self.conn_handle, _HANDLE_READ_BATTERY)
         except:
          self.busy = False
          return False
         stime = time.time()
         while self.busy and time.time()-stime<self.timeout:
          utime.sleep_ms(100)
        return True

    def read(self,force=False):
        if force or ((time.time() - self.timeout > self._last_read) and self.busy==False):
         self.busy = True
         self.connect()
         if self.connected == False:
            self.busy = False
            return False
         self._readok = False
         try:
          self.__ble.gattc_write(self.conn_handle, TEMP_HUM_WRITE_HANDLE, TEMP_HUM_WRITE_VALUE,1)
          stime = time.time()
          while self.busy and time.time()-stime<self.timeout:
           utime.sleep_ms(50)
          self.busy = True
          if self.connected == False:
             self.connect()
          self.__ble.gattc_read(self.conn_handle, _HANDLE_READ_SENSOR)
         except Exception as e:
          self.busy = False
          self.connected = False
          return False
         stime = time.time()
         while self.busy and time.time()-stime<self.timeout:
          utime.sleep_ms(50)
        return True


    def bt_irq(self, event, data):
#        print(event,data)#debug
        if event == BLEHelper._IRQ_PERIPHERAL_CONNECT:
            self.conn_handle, self.addr_type, self.addr = data
            self.connected=True

        elif event == BLEHelper._IRQ_PERIPHERAL_DISCONNECT:
            self.connected = False
            self.conn_handle = None

        elif event == BLEHelper._IRQ_GATTC_WRITE_DONE:
            # A gattc_write() has completed.
            conn_handle, value_handle, status = data
            self.busy = False

        elif event == BLEHelper._IRQ_GATTC_READ_RESULT:
            # A gattc_read() has completed.
            conn_handle, value_handle, char_data = data
            if value_handle == _HANDLE_READ_BATTERY:
                self.__cache=char_data
                self.battery = int(char_data[0])
                self._last_bread = time.time()

            elif value_handle == _HANDLE_READ_SENSOR:
                self.__cache=char_data
                try:
                 temp, p1, light, moisture, cond, p2, p3 = unpack('<hbIBhIh', char_data)
                 temp = float(temp) / 10.0
                except:
                 temp = -100
                if temp >= -20 and temp <= 50: # valid range is -20..+50C
                 self._readok = True
                 self._temperature  = temp
                 self._light        = light
                 self._moisture     = moisture
                 self._conductivity = cond
                 self._last_read = time.time()

        elif event == BLEHelper._IRQ_GATTC_READ_DONE:
            conn_handle, value_handle, status = data
            self.read_done = True
            self.busy = False

#        else:
#            print("Unhandled event: {}, data: {}".format(event, data))
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
#                    print("BLE connection to device FAILED!")
                    self.mitempdata["result"] = 9
                    break
                connect_retry += 1
                utime.sleep(int(self.connect_retry_timeout/1000))
            except OSError as exc:
                print ("OSError:", exc.args[0], connect_retry)
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

    def get_temperature(self):
        try:
         res = self.read()
        except:
         res = False
        if res==False:
         try:
             self.disconnect()
             utime.sleep(1)
             self.read(True)
         except:
            pass
        return self._temperature

    def get_light(self):
        try:
         res = self.read()
        except:
         res = False
        if res==False:
         try:
             self.disconnect()
             utime.sleep(1)
             self.read(True)
         except:
            pass
        return self._light

    def get_moisture(self):
        try:
         res = self.read()
        except:
         res = False
        if res==False:
         try:
             self.disconnect()
             utime.sleep(1)
             self.read(True)
         except:
            pass
        return self._moisture

    def get_conductivity(self):
        try:
         res = self.read()
        except:
         res = False
        if res==False:
         try:
             self.disconnect()
             utime.sleep(1)
             self.read(True)
         except:
            pass
        return self._conductivity

    def battery_level(self):
        try:
          self.getBatteryLevel()
        except:
          pass
        return self.battery

flora_devices = []

def request_flora_device(hw,address,timeout=60):
 global flora_devices
 for i in range(len(flora_devices)):
  if (str(flora_devices[i].address).lower().strip() == str(address).lower().strip()):
   return flora_devices[i]
 flora_devices.append(MiFlora(hw,address,timeout))
 return flora_devices[-1]
