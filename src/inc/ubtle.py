import utime
import ubinascii
import struct
from micropython import const
try:
 import ubluetooth
except:
 print("No BLE support")

ADDR_TYPE_PUBLIC = "public"
ADDR_TYPE_RANDOM = "random"

_IRQ_SCAN_RESULT = const(5)
_IRQ_SCAN_DONE = const(6)

class UUID:
    def __init__(self, val, commonName=None):
        '''We accept: 32-digit hex strings, with and without '-' characters,
           4 to 8 digit hex strings, and integers'''
        if isinstance(val, int):
            if (val < 0) or (val > 0xFFFFFFFF):
                raise ValueError(
                    "Short form UUIDs must be in range 0..0xFFFFFFFF")
            val = "%04X" % val
        elif isinstance(val, self.__class__):
            val = str(val)
        else:
            val = str(val)  # Do our best

        val = val.replace("-", "")
        if len(val) <= 8:  # Short form
            val = ("0" * (8 - len(val))) + val + "00001000800000805F9B34FB"

        self.binVal = ubinascii.unhexlify(val.encode('utf-8'))
        if len(self.binVal) != 16:
            raise ValueError(
                "UUID must be 16 bytes, got '%s' (len=%d)" % (val,
                                                              len(self.binVal)))
        self.commonName = commonName

    def __str__(self):
        try:
         s = ubinascii.hexlify(self.binVal).decode('utf-8')
        except:
         return ""
        return "-".join([s[0:8], s[8:12], s[12:16], s[16:20], s[20:32]])

    def __eq__(self, other):
        return self.binVal == UUID(other).binVal

    def __cmp__(self, other):
        return cmp(self.binVal, UUID(other).binVal)

    def __hash__(self):
        return hash(self.binVal)


class ScanEntry:
    addrTypes = { 0 : ADDR_TYPE_PUBLIC,
                  1 : ADDR_TYPE_RANDOM
                }

    FLAGS                     = 0x01
    INCOMPLETE_16B_SERVICES   = 0x02
    COMPLETE_16B_SERVICES     = 0x03
    INCOMPLETE_32B_SERVICES   = 0x04
    COMPLETE_32B_SERVICES     = 0x05
    INCOMPLETE_128B_SERVICES  = 0x06
    COMPLETE_128B_SERVICES    = 0x07
    SHORT_LOCAL_NAME          = 0x08
    COMPLETE_LOCAL_NAME       = 0x09
    TX_POWER                  = 0x0A
    SERVICE_SOLICITATION_16B  = 0x14
    SERVICE_SOLICITATION_32B  = 0x1F
    SERVICE_SOLICITATION_128B = 0x15
    SERVICE_DATA_16B          = 0x16
    SERVICE_DATA_32B          = 0x20
    SERVICE_DATA_128B         = 0x21
    PUBLIC_TARGET_ADDRESS     = 0x17
    RANDOM_TARGET_ADDRESS     = 0x18
    APPEARANCE                = 0x19
    ADVERTISING_INTERVAL      = 0x1A
    MANUFACTURER              = 0xFF

    dataTags = {
        FLAGS                     : 'Flags',
        INCOMPLETE_16B_SERVICES   : 'Incomplete 16b Services',
        COMPLETE_16B_SERVICES     : 'Complete 16b Services',
        INCOMPLETE_32B_SERVICES   : 'Incomplete 32b Services',
        COMPLETE_32B_SERVICES     : 'Complete 32b Services',
        INCOMPLETE_128B_SERVICES  : 'Incomplete 128b Services',
        COMPLETE_128B_SERVICES    : 'Complete 128b Services',
        SHORT_LOCAL_NAME          : 'Short Local Name',
        COMPLETE_LOCAL_NAME       : 'Complete Local Name',
        TX_POWER                  : 'Tx Power',
        SERVICE_SOLICITATION_16B  : '16b Service Solicitation',
        SERVICE_SOLICITATION_32B  : '32b Service Solicitation',
        SERVICE_SOLICITATION_128B : '128b Service Solicitation',
        SERVICE_DATA_16B          : '16b Service Data',
        SERVICE_DATA_32B          : '32b Service Data',
        SERVICE_DATA_128B         : '128b Service Data',
        PUBLIC_TARGET_ADDRESS     : 'Public Target Address',
        RANDOM_TARGET_ADDRESS     : 'Random Target Address',
        APPEARANCE                : 'Appearance',
        ADVERTISING_INTERVAL      : 'Advertising Interval',
        MANUFACTURER              : 'Manufacturer',
    }

    def __init__(self, addr):
        self.addr = addr
        self.addrType = None
        self.rssi = None
        self.connectable = False
        self.rawData = None
        self.scanData = {}
        self.updateCount = 0

    def _update(self, resp):
        addrType = self.addrTypes.get(resp['type'], None)
        self.addrType = addrType
        self.rssi = resp['rssi']
        self.connectable = (resp['flag'] !=3)
        data = resp['d']
        self.rawData = data
        isNewData = False
        while len(data) >= 2:
            sdlen, sdid = struct.unpack_from('<BB', data)
            val = data[2 : sdlen + 1]
            if (sdid not in self.scanData) or (val != self.scanData[sdid]):
                isNewData = True
            self.scanData[sdid] = val
            data = data[sdlen + 1:]

        self.updateCount += 1
        return isNewData

    def _decodeUUID(self, val, nbytes):
        if len(val) < nbytes:
            return None
        bval=bytearray(val)
        rs=""
        # Bytes are little-endian; convert to big-endian string
        for i in range(nbytes):
            rs = ("%02X" % bval[i]) + rs
        return UUID(rs)

    def _decodeUUIDlist(self, val, nbytes):
        result = []
        for i in range(0, len(val), nbytes):
            if len(val) >= (i+nbytes):
                result.append(self._decodeUUID(val[i:i+nbytes],nbytes))
        return result

    def getDescription(self, sdid):
        return self.dataTags.get(sdid, hex(sdid))

    def getValue(self, sdid):
        val = self.scanData.get(sdid, None)
        if val is None:
            return None
        if sdid in [ScanEntry.SHORT_LOCAL_NAME, ScanEntry.COMPLETE_LOCAL_NAME]:
            try:
                return val.decode('utf-8')
            except UnicodeDecodeError:
                bbval = bytearray(val)
                return ''.join( [ (chr(x) if (x>=32 and x<=127) else '?') for x in bbval ] )
        elif sdid in [ScanEntry.INCOMPLETE_16B_SERVICES, ScanEntry.COMPLETE_16B_SERVICES]:
            return self._decodeUUIDlist(val,2)
        elif sdid in [ScanEntry.INCOMPLETE_32B_SERVICES, ScanEntry.COMPLETE_32B_SERVICES]:
            return self._decodeUUIDlist(val,4)
        elif sdid in [ScanEntry.INCOMPLETE_128B_SERVICES, ScanEntry.COMPLETE_128B_SERVICES]:
            return self._decodeUUIDlist(val,16)
        else:
            return val

    def getValueText(self, sdid):
        val = self.getValue(sdid)
        if val is None:
            return None
        if sdid in [ScanEntry.SHORT_LOCAL_NAME, ScanEntry.COMPLETE_LOCAL_NAME]:
            return val
        elif isinstance(val, list):
            return ','.join(str(v) for v in val)
        else:
            return ubinascii.hexlify(val)

    def getScanData(self):
        '''Returns list of tuples [(tag, description, value)]'''
        return [ (sdid, self.getDescription(sdid), self.getValueText(sdid))
                    for sdid in self.scanData.keys() ]

class Scanner():
    def __init__(self,blehw,callback=None):
       self.scanned = {}
       self.__ble=blehw
       self.timeout = 10.0
       self._cached = []
       self._callback = callback
       self.scanended = True
       try:
        self.__ble.active(True)
        self.__ble.irq(self.__bt_irq)
       except:
        pass

    def __bt_irq(self,event, data):
     if event == _IRQ_SCAN_RESULT:
       self._cached.append(data)
       if self._callback is not None:
        try:
         self._callback(data)
        except Exception as e:
         pass

     elif event == _IRQ_SCAN_DONE:
       # Scan duration finished or manually stopped.
#       print('scan complete')
       self.scanended = True

    def start(self, timeout=10.0,passive=True):
       self.timeout = timeout
       try:
        self.scanended = False
        self.__ble.gap_scan(int(self.timeout * 1000),30000,30000) # active scan is still buggy in mpython!!
       except Exception as e:
        self.scanended = True

    def stop(self):
       if self.scanended==False:
        try:
         self.__ble.gap_scan(None)
        except:
         pass
       self.scanended = True

    def clear(self):
        self.scanned = {}
        self._cached = []

    def process(self):
        start = utime.time()
        while True:
            if self.scanended:
                break
            if self.timeout:
                remain = start + self.timeout - utime.time()
                if remain <= 0.0:
                    break
            else:
                remain = None
            while (len(self._cached)>0):
                # device found
                try:
                 resp = {'addr':0,'type':0,'rssi':0,'flag':3,'d':b''}
                 resp['type'], resp['addr'], resp['flag'], resp['rssi'], resp['d'] = self._cached[0]
                 try:
                  addr = ubinascii.hexlify(resp['addr']).decode('utf-8')
                  addr = ':'.join([addr[i:i+2] for i in range(0,12,2)])
                 except:
                  addr = ""
                 if addr in self.scanned:
                    dev = self.scanned[addr]
                 else:
                    dev = ScanEntry(addr)
                    self.scanned[addr] = dev
                 isNewData = dev._update(resp)
                except:
                 pass
                try:
                 del self._cached[0]
                except:
                 pass

    def getDevices(self):
        try:
            retval = self.scanned.values()
        except:
            retval = []
        return retval

    def scan(self, timeout=10, passive=True):
        self.clear()
        self.start(timeout,passive=passive)
        self.process()
        self.stop()
        return self.getDevices()

'''
try:
     scanner = Scanner(ubluetooth.BLE())
     devices = scanner.scan(10.0)
except Exception as e:
     print("BLE scanning failed ",str(e))
     devices = []

for dev in devices:
  print(dev.addr,dev.addrType,dev.rssi,dev.connectable)
  for (adtype, desc, value) in dev.getScanData():
      if 'name' in desc.lower():
       print("name:",value)
      else:
       print(adtype,desc,value)
'''
