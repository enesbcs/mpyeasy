import pglobals
import misc
import unet
try:
 import utime
except:
 import faketime as utime

_lastRSSIval = 0
_lastRSSItime = 0

def humStatDomoticz(humidity):
 res=3
 try:
  hum = misc.str2num(humidity)
  if (hum<30):
   res=2
  elif (hum<40):
   res=0
  elif (hum<59):
   res=1
 except:
  pass
 return str(res)

def mapRSSItoDomoticz(urssi=-1):
 global _lastRSSIval, _lastRSSItime
 res = 12
 if ((utime.time()-_lastRSSItime)>=3) and (urssi==-1):
  _lastRSSIval = unet.get_rssi()
  _lastRSSItime = utime.time()
 try:
  if urssi != -1:
   rssi = urssi
  else:
   rssi = int(_lastRSSIval)
  if (-50<rssi):
   res = 10
  elif (rssi<= -98):
   res = 0
  else:
   res = int(round((rssi+97)/5,0)+1)
 except:
  pass
 return str(res)

def formatDomoticzSensorType(sensortype,valuearr):
  valuestr = ""
  if (sensortype==pglobals.SENSOR_TYPE_SINGLE) or (sensortype==pglobals.SENSOR_TYPE_TEXT):
   valuestr += str(valuearr[0]).strip()
  elif (sensortype==pglobals.SENSOR_TYPE_LONG):
   valuearr[0] = float(valuearr[0])
   valuearr[1] = float(valuearr[1])
   valuestr += str(valuearr[0] + (valuearr[1] << 16)).strip()
  elif (sensortype==pglobals.SENSOR_TYPE_DUAL):
   valuestr += str(valuearr[0]).strip() + ";" + str(valuearr[1]).strip()
  elif (sensortype==pglobals.SENSOR_TYPE_TEMP_HUM):
   valuestr += str(valuearr[0]).strip() + ";" + str(valuearr[1]).strip()+ ";" + humStatDomoticz(valuearr[1])
  elif (sensortype==pglobals.SENSOR_TYPE_TEMP_HUM_BARO):
   valuestr += str(valuearr[0]).strip() + ";" + str(valuearr[1]).strip()+ ";" + humStatDomoticz(valuearr[1])
   valuestr += ";"+str(valuearr[2]).strip() + ";0"
  elif (sensortype==pglobals.SENSOR_TYPE_TEMP_BARO):
   valuestr += str(valuearr[0]).strip() + ";" + str(valuearr[1]).strip()
   valuestr += ";0;0"
  elif (sensortype==pglobals.SENSOR_TYPE_TEMP_EMPTY_BARO):
   valuestr += str(valuearr[0]).strip() + ";" + str(valuearr[2]).strip()
   valuestr += ";0;0"
  elif (sensortype==pglobals.SENSOR_TYPE_TRIPLE):
   valuestr += str(valuearr[0]).strip() + ";" + str(valuearr[1]).strip()
   valuestr += ";"+str(valuearr[2]).strip()
  elif (sensortype==pglobals.SENSOR_TYPE_QUAD):
   valuestr += str(valuearr[0]).strip() + ";" + str(valuearr[1]).strip()
   valuestr += ";"+str(valuearr[2]).strip()+";"+str(valuearr[3]).strip()
  elif (sensortype==pglobals.SENSOR_TYPE_SWITCH) or (sensortype==pglobals.SENSOR_TYPE_DIMMER):
   pass # Too specific for HTTP/MQTT
  else:
   misc.addLog(pglobals.LOG_LEVEL_ERROR,"Domoticz Controller: Not yet implemented sensor type: "+sensortype)
  return valuestr
