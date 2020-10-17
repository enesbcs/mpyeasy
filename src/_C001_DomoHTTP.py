import controller
import pglobals
from inc.helper_domoticz import *
import misc
#from multiprocessing import Process
#import base64
try:
        import ubinascii as binascii
except ImportError:
        import binascii
try:
 import urequests
 fake = False
except:
 import urllib.request as urequests
 fake = True

class Controller(controller.ControllerProto):
 CONTROLLER_ID = 1
 CONTROLLER_NAME = "Domoticz HTTP"

 def __init__(self,controllerindex):
  controller.ControllerProto.__init__(self,controllerindex)
  self.usesID = True
  self.usesAccount = True
  self.usesPassword = True

 def senddata(self,idx,taskobj,changedvalue=-1):
  if self.enabled:
   if int(idx) != 0:
    if int(taskobj.vtype)==pglobals.SENSOR_TYPE_SWITCH:
      url = "/json.htm?type=command&param=switchlight&idx="
      url += str(idx)
      url += "&switchcmd="
      if round(float(taskobj.uservar[0])) == 0:
         url += "Off"
      else:
         url += "On"
    elif int(taskobj.vtype)==pglobals.SENSOR_TYPE_DIMMER:
      url = "/json.htm?type=command&param=switchlight&idx="
      url += str(idx)
      url += "&switchcmd="
      if float(taskobj.uservar[0]) == 0:
       url += "Off"
      else:
       url += "Set%20Level&level="
       url += str(taskobj.uservar[0])
    else:
     url = "/json.htm?type=command&param=udevice&idx="
     url += str(idx)
     url += "&nvalue=0&svalue="
     url += formatDomoticzSensorType(taskobj.vtype,taskobj.uservar)
    url += "&rssi="
    url += mapRSSItoDomoticz(taskobj.rssi)
    if taskobj.battery != -1 and taskobj.battery != 255: # battery input 0..100%, 255 means not supported
     url += "&battery="
     url += str(taskobj.battery)
    else:
     bval = misc.get_battery_value()
     url += "&battery="
     url += str(bval)
    urlstr = self.controllerip+":"+self.controllerport+url+self.getaccountstr()
    misc.addLog(pglobals.LOG_LEVEL_DEBUG,urlstr) # sendviahttp
    self.urlget(urlstr)
#    httpproc = Process(target=self.urlget, args=(urlstr,))  # use multiprocess to avoid blocking
#    httpproc.start()
   else:
    misc.addLog(pglobals.LOG_LEVEL_ERROR,"MQTT : IDX cannot be zero!")

 def urlget(self,url):
  global fake
  url = "http://"+str(url)
  try:
   if fake:
    content = urequests.urlopen(url,None,1)
   else:
    content = urequests.get(url)
  except Exception as e:
   misc.addLog(pglobals.LOG_LEVEL_ERROR,"Controller: "+self.controllerip+" connection failed "+str(e))

 def getaccountstr(self):
  retstr = ""
  if self.controlleruser!="" or self.controllerpassword!="":
    acc = binascii.b2a_base64(bytes(self.controlleruser))
    pw =  binascii.b2a_base64(bytes(self.controllerpassword))
    retstr = "&username="+ str(acc) +"&password="+ str(pw)
  return retstr
