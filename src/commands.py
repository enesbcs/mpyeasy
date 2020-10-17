#############################################################################
############## Helper Library for RULES and COMMANDS ########################
#############################################################################
#
# Copyright (C) 2020 by Alexander Nagy - https://bitekmindenhol.blog.hu/
#
import misc
import settings
import esp_os as OS
try:
 import utime
except:
 import inc.faketime as utime
import upyTime
import pglobals
import unet
import re
try:
 import urequests
 fake = False
except:
 import urllib.request as urequests
 fake = True
try:
 import usocket
except:
 import socket as usocket
try:
 import inc.lib_gpiohelper as gpiohelper
except:
 pass    

GlobalRules = []
SysVars = ["systime","system_hm","lcltime","syshour","sysmin","syssec","sysday","sysmonth",
"sysyear","sysyears","sysweekday","sysweekday_s","unixtime","uptime","rssi","ip","ip4","sysname","unit","ssid","mac","mac_int","build","sunrise","sunset","sun_altitude","sun_azimuth","sun_radiation","br","lf","tab"]

def doCleanup():
  rulesProcessing("System#Shutdown",pglobals.RULE_SYSTEM)
  if (len(settings.Tasks)>1) or ( (len(settings.Tasks)==1) and (settings.Tasks[0] != False) ):
   settings.savetasks()
  procarr = []
  for x in range(0,len(settings.Tasks)):
   if (settings.Tasks[x]) and type(settings.Tasks[x]) is not bool: # device exists
    try:
     if (settings.Tasks[x].enabled): # device enabled
      settings.Tasks[x].plugin_exit()
#      t = threading.Thread(target=settings.Tasks[x].plugin_exit)
#      t.daemon = True
#      procarr.append(t)
#      t.start()
    except:
     pass
  try:
   for t in range(0,pglobals.RULES_TIMER_MAX):
    upyTime.Timers[t].pause()
  except:
   pass
  procarr = []
  for y in range(0,len(settings.Controllers)):
   if (settings.Controllers[y]):
    if (settings.Controllers[y].enabled):
      settings.Controllers[y].controller_exit()
#      t = threading.Thread(target=settings.Controllers[y].controller_exit)
#      t.daemon = True
#      procarr.append(t)
#      t.start()

def doExecuteCommand(cmdline,Parse=True):
 if Parse:
  retval, state = parseruleline(cmdline)
 else:
  retval = cmdline
 cmdarr = retval.split(",")
 if (" " in retval) and not("," in retval):
  cmdarr = retval.split(" ")
 elif (" " in retval) and ("," in retval): # workaround for possible space instead comma problem
   fsp = retval.find(" ")
   fco = retval.find(",")
   if fsp<fco:
    c2 = retval.split(" ")
    cmdarr = retval[(fsp+1):].split(",")
    cmdarr = [c2[0]] + cmdarr
 cmdarr[0] = cmdarr[0].strip().lower()
 commandfound = False
 misc.addLog(pglobals.LOG_LEVEL_INFO,"CMD: "+cmdline.replace("==","="))
 
 if cmdarr[0] == "delay":
  try:
   s = float(cmdarr[1])
  except:
   s = 1000
  utime.sleep_ms(s)
  commandfound = True
  return commandfound

 elif cmdarr[0] == "taskrun":
  if len(settings.Tasks)<1:
   return False
  try:
   s = int(cmdarr[1])
  except:
   s = -1
  if s >0 and (s<=len(settings.Tasks)):
   s = s-1 # array is 0 based, tasks is 1 based
   if (type(settings.Tasks[s])!=bool) and (settings.Tasks[s]):
    if (settings.Tasks[s].enabled):
     settings.Tasks[s].plugin_read()
   commandfound = True
  return commandfound

 elif cmdarr[0] == "taskvalueset":
  if len(settings.Tasks)<1:
   return False
  try:
   s = int(cmdarr[1])
  except:
   s = -1
  try:
   v = int(cmdarr[2])
  except:
   v = 1
  #v=v-1
  if s >0 and (s<=len(settings.Tasks)):
   s = s-1 # array is 0 based, tasks is 1 based
   if (type(settings.Tasks[s])!=bool) and (settings.Tasks[s]):
    if v>(settings.Tasks[s].valuecount):
     v = settings.Tasks[s].valuecount
    if v<1:
     v = 1
    try:
     settings.Tasks[s].set_value(v,parsevalue(str(cmdarr[3].strip())),False)
    except Exception as e:
     pass
#     print("Set value error: ",e)
    commandfound = True
  return commandfound

 elif cmdarr[0] == "taskvaluesetandrun":
  if len(settings.Tasks)<1:
   return False
  try:
   s = int(cmdarr[1])
  except:
   s = -1
  try:
   v = int(cmdarr[2])
  except:
   v = 1
  #v=v-1
  if s >0 and (s<=len(Settings.Tasks)):
   s = s-1 # array is 0 based, tasks is 1 based
   if (type(settings.Tasks[s])!=bool) and (settings.Tasks[s]):
    if v>(settings.Tasks[s].valuecount):
     v = settings.Tasks[s].valuecount
    if v<1:
     v = 1
    settings.Tasks[s].set_value(v,parsevalue(str(cmdarr[3]).strip()),True)
    commandfound = True
  return commandfound

 elif cmdarr[0] == "timerpause":
  if len(upyTime.Timers)<1:
   return False
  try:
   s = int(cmdarr[1])
  except:
   s = -1
  if s>0 and (s<len(upyTime.Timers)):
   s = s-1 # array is 0 based, timers is 1 based
   upyTime.Timers[s].pause()
  commandfound = True
  return commandfound

 elif cmdarr[0] == "timerresume":
  if len(upyTime.Timers)<1:
   return False
  try:
   s = int(cmdarr[1])
  except:
   s = -1
  if s>0 and (s<len(upyTime.Timers)):
   s = s-1 # array is 0 based, timers is 1 based
   upyTime.Timers[s].resume()
  commandfound = True
  return commandfound

 elif cmdarr[0] == "timerset":
  if len(upyTime.Timers)<1:
   return False
  try:
   s = int(cmdarr[1])
  except:
   s = -1
  try:
   v = int(cmdarr[2])
  except:
   v = 1
  if s >0 and (s<len(upyTime.Timers)):
   s = s-1 # array is 0 based, timers is 1 based
   if v==0:
    upyTime.Timers[s].stop(False)
   else:
    upyTime.Timers[s].addcallback(TimerCallback)
    upyTime.Timers[s].start(v)
  commandfound = True
  return commandfound

 elif cmdarr[0] == "event":
  rulesProcessing(cmdarr[1],pglobals.RULE_USER)
  commandfound = True
  return commandfound

 elif cmdarr[0] == "sendto":
  try:
   unitno = int(cmdarr[1])
  except:
   unitno = -1
  data = ""
  if len(cmdarr)>2:
   sepp = ( len(cmdarr[0]) + len(cmdarr[1]) + 1 )
   sepp = cmdline.find(',',sepp)
   data = cmdline[sepp+1:].replace("==","=")
  else:
   unitno = -1
  if unitno>=0 and unitno<=255:
    cfound = False
    for y in range(len(settings.Controllers)):
     if (settings.Controllers[y]):
      if (settings.Controllers[y].enabled):
       if "ESPEasy P2P" in settings.Controllers[y].getcontrollername():
        settings.Controllers[y].udpsender(unitno,data,1)
        cfound = True
    if cfound==False:
     misc.addLog(pglobals.LOG_LEVEL_ERROR,"ESPEasy P2P controller not found!")
  commandfound = True
  return commandfound

 elif cmdarr[0] == "blecommand":
  try:
   unitno = int(cmdarr[1])
  except:
   unitno = -1
  data = ""
  if len(cmdarr)>2:
   sepp = ( len(cmdarr[0]) + len(cmdarr[1]) + 1 )
   sepp = cmdline.find(',',sepp)
   data = cmdline[sepp+1:].replace("==","=")
  else:
   unitno = -1
  if unitno>=0 and unitno<=255:
    cfound = False
    for y in range(len(settings.Controllers)):
     if (settings.Controllers[y]):
      if (settings.Controllers[y].enabled):
       if "BLE Direct" in settings.Controllers[y].getcontrollername():
        settings.Controllers[y].sendcommand(unitno,data)
        cfound = True
    if cfound==False:
     misc.addLog(pglobals.LOG_LEVEL_ERROR,"BLE controller not found!")
  commandfound = True
  return commandfound

 elif cmdarr[0] == "loracommand":
  try:
   unitno = int(cmdarr[1])
  except:
   unitno = -1
  data = ""
  if len(cmdarr)>2:
   sepp = ( len(cmdarr[0]) + len(cmdarr[1]) + 1 )
   sepp = cmdline.find(',',sepp)
   data = cmdline[sepp+1:].replace("==","=")
  else:
   unitno = -1
  if unitno>=0 and unitno<=255:
    cfound = False
    for y in range(len(settings.Controllers)):
     if (settings.Controllers[y]):
      if (settings.Controllers[y].enabled):
       if "LORA Direct" in settings.Controllers[y].getcontrollername():
        settings.Controllers[y].sendcommand(unitno,data)
        cfound = True
    if cfound==False:
     misc.addLog(pglobals.LOG_LEVEL_ERROR,"LORA controller not found!")
  commandfound = True
  return commandfound

 elif cmdarr[0] == "publish":
  topic = cmdarr[1].strip()
  data = ""
  if len(cmdarr)>2:
   sepp = ( len(cmdarr[0]) + len(cmdarr[1]) + 1 )
   sepp = cmdline.find(',',sepp)
   data = cmdline[sepp+1:].replace("==","=")
  else:
   topic = ""
  commandfound = False
  if topic!="":
    cfound = False
    for y in range(len(settings.Controllers)):
     if (settings.Controllers[y]):
      if (settings.Controllers[y].enabled):
       try:
        if settings.Controllers[y].mqttclient is not None:
         settings.Controllers[y].mqttclient.publish(topic,data)#MISSING!!!
         commandfound = True
         cfound = True
         break
       except:
        cfound = False
    if cfound==False:
      misc.addLog(pglobals.LOG_LEVEL_ERROR,"MQTT capable controller not found!")
  return commandfound

 elif cmdarr[0] == "sendtohttp":
  destaddr = cmdarr[1].strip()
  try:
   destport = int(cmdarr[2])
  except:
   destport = -1
  data = ""
  if len(cmdarr)>3:
   sepp = ( len(cmdarr[0]) + len(cmdarr[1])+ len(cmdarr[2]) + 2 )
   sepp = cmdline.find(',',sepp)
   data = cmdline[sepp+1:].replace("==","=")
  else:
   destport = -1
  if destport > 0:
   commandfound = True
   curl = "http://"+destaddr+":"+str(destport)+data
   urlget(curl)
  else:
   commandfound = False
  return commandfound

 elif cmdarr[0] == "sendtoudp":
  destaddr = cmdarr[1].strip()
  try:
   destport = int(cmdarr[2])
  except:
   destport = -1
  data = ""
  if len(cmdarr)>3:
   sepp = ( len(cmdarr[0]) + len(cmdarr[1])+ len(cmdarr[2]) + 2 )
   sepp = cmdline.find(',',sepp)
   data = cmdline[sepp+1:].replace("==","=")
  else:
   destport = -1
  if destport > 0:
   s = usocket.socket(usocket.AF_INET, usocket.SOCK_DGRAM)
   for r in range(0,1):
    s.sendto(bytes(data,"utf-8"), (destaddr,int(destport)))
    if r<1:
     utime.sleep(0.1)
   commandfound = True
  else:
   commandfound = False
  return commandfound
 elif cmdarr[0] == "wifiapmode":
  commandfound = False
  return commandfound
 elif cmdarr[0] == "wifistamode":
  commandfound = False
  return commandfound
 elif cmdarr[0] == "wificonnect": # implement it
  commandfound = False
  return commandfound
 elif cmdarr[0] == "wifimode":    # implement it
  commandfound = False
  return commandfound
 elif cmdarr[0] == "reboot":
#  print("rst upt:",misc.getuptime(0))#debug
  doCleanup()
  OS.reboot()
  commandfound = True
  return commandfound
 elif cmdarr[0] == "reset":
  try:
    import os
    files = os.listdir('data')
    for fn in files:
     if '.dat' in fn:
      os.remove('data/'+fn)   
  except:
   pass
  try:
   settings.Settings = {"Name":"mpyEasy","Unit":"2","Password":"","Delay":60,"WifiClient":false,"AP1SSID":"","AP1KEY":"","AP2SSID":"","AP2KEY":"","WifiAP":2,"APSSID":"mpyEasy","APKEY":"configesp","LANIF":false,"WDHCP":true,"WIP":"","WMask":"","WGW":"","WDNS":"","LDHCP":true,"LIP":"","LMask":"","LGW":"","LDNS":""}
   settings.Controllers = [False]
   settings.Tasks = [False]
   settings.Pinout = []
   settings.savesettings()
   settings.savetasks()
  except:
   pass
  OS.reboot()
  commandfound = True
  return commandfound

 elif cmdarr[0] == "notify":
  try:
   plugin = int(cmdarr[1])
  except:
   plugin = 0
  data = ""
  if len(cmdarr)>1 and plugin>0:
   sepp = ( len(cmdarr[0]) + len(cmdarr[1])+ 2 )
   data = cmdline[sepp:].replace("==","=")
   commandfound = doExecuteNotification(plugin-1,data)
  return commandfound

 elif cmdarr[0] in gpiohelper.commandlist:
  commandfound = True
  try:
   res = gpiohelper.gpio_commands(retval)
  except Exception as e:
   print("gpio err",str(e))#debug
  return res

 if commandfound==False:
  commandfound = doExecutePluginCommand(retval)
 if commandfound==False:
  misc.addLog(pglobals.LOG_LEVEL_ERROR,"Unknown command: "+cmdline)
 return commandfound

def urlget(url):
  global fake
  try:
   if fake:
    urequests.urlopen(url,None,1)
   else:
    urequests.get(url)
  except Exception as e:
   misc.addLog(pglobals.LOG_LEVEL_ERROR,str(e))

def TimerCallback(tid):
  rulesProcessing("Rules#Timer="+str(tid),pglobals.RULE_TIMER)

def doExecutePluginCommand(cmdline):
  retvalue = False
  if len(settings.Tasks)<1:
   return False
  for s in range(len(settings.Tasks)):
    if (type(settings.Tasks[s])!=bool) and (settings.Tasks[s].enabled):
     try:
      retvalue = settings.Tasks[s].plugin_write(cmdline)
     except Exception as e:
      retvalue = str(e)
     if retvalue!=False:
      return retvalue
  return retvalue

def doExecuteNotification(num,cmdline):
  retvalue = False
  if len(settings.Notifiers)<1:
   return False
  try:
   num=int(num)
   if num>=0 and num<len(settings.Notifiers) and type(settings.Notifiers[num]) is not bool and (settings.Notifiers[num].enabled):
    retvalue = settings.Notifiers[num].notify(cmdline)
  except Exception as e:
   misc.addLog(pglobals.LOG_LEVEL_ERROR,"Notification error: "+str(e))
  return retvalue

def decodeeventname(eventname):
 ten = eventname.strip().lower()
 ec = -1
 if ("system#" in ten) or ("mqtt#connected" in ten) or ("mqtt#disconnected" in ten):
   ec = pglobals.RULE_SYSTEM
 elif ("clock#time" in ten):
   ec = pglobals.RULE_CLOCK
 elif ("rules#timer" in ten):
   ec = pglobals.RULE_TIMER
 else:
  ec = pglobals.RULE_USER
 return ec

def splitruletoevents(rulestr): # parse rule string into array of events
 global GlobalRules
 GlobalRules = []
 rcount = -1
 evfound = False
 ename = ""
 evarr = []
 rulearr = rulestr.splitlines()
 for line in rulearr:
  cs = line.find(' //')
  if cs>-1:
   line = line[:cs]
  linelower = line.strip().lower()
  if linelower.startswith("on ") and linelower.endswith(" do"):
   rcount += 1
   evfound = True
   tstr = line.strip().split(" ")
   ename = tstr[1]
  elif evfound:
   if linelower.startswith("endon"):
    evfound = False
    GlobalRules.append({"ename":ename,"ecat":decodeeventname(ename), "ecode":evarr,"lastcheck":0,"evalue":-1})
    evarr = []
    ename = ""
   else:
    evarr.append(line.strip())

def getfirstequpos(cstr):
 res = -1
 for c in range(len(cstr)):
  if cstr[c] in "<>=!":
   res = c
   break
 return res

def removeequchars(cstr):
 remc = getequchars(cstr)
 res = cstr
 for c in range(len(remc)):
  res = res.replace(remc[c],"")
 return res

def getequchars(cstr,arr=False):
 res = ""
 res2 = []
 equs = "<>=!"
 for c in range(len(equs)):
  if equs[c] in cstr:
   if equs[c] not in res:
    res += equs[c]
    res2.append(equs[c])
 if arr:
  return res2
 else:
  return res

def gettaskvaluefromname(taskname): # taskname#valuename->value
 res = -1
 try:
  taskprop = taskname.split("#")
  taskprop[0] = taskprop[0].strip().lower()
  taskprop[1] = taskprop[1].strip().lower() 
 except:
  res = -1
  return res
 try:
  for s in range(len(settings.Tasks)):
   if type(settings.Tasks[s]) is not bool:
    if settings.Tasks[s].taskname.lower()==taskprop[0]:
     for v in range(len(settings.Tasks[s].valuenames)):
      if settings.Tasks[s].valuenames[v].lower() == taskprop[1]:
       res = settings.Tasks[s].uservar[v]
       break
 except:
   res=-1
 return res

suntimesupported = -1

def getglobalvar(varname):
 global SysVars, suntimesupported
 svname = varname.strip().lower()
 par = ""
 if ("-" in svname):
  resarr = svname.split("-")
  svname = resarr[0]
  par = "-"+resarr[1]
 if ("+" in svname):
  resarr = svname.split("+")
  svname = resarr[0]
  par = "+"+resarr[1]
 res = ""
 if svname in SysVars:
   if svname==SysVars[0]: #%systime%	01:23:54
    ret = utime.localtime()
    return '{:02}:{:02}:{:02}'.format(ret[3],ret[4],ret[5])
   elif svname==SysVars[1]: #%systm_hm% 	01:23 
    ret = utime.localtime()
    return '{:02}:{:02}'.format(ret[3],ret[4])
   elif svname==SysVars[2]: #%lcltime% 	2018-03-16 01:23:54 
    ret = utime.localtime()
    return '{:04}-{:02}-{:02} {:02}:{:02}:{:02}'.format(ret[0],ret[1],ret[2],ret[3],ret[4],ret[5])
   elif svname==SysVars[3]: #%syshour% 	11 	Current hour (hh)
    ret = utime.localtime()
    return '{:02}'.format(ret[3])
   elif svname==SysVars[4]: #%sysmin% 	22 	Current minute (mm)
    ret = utime.localtime()
    return '{:02}'.format(ret[4])
   elif svname==SysVars[5]: #%syssec% 	33 	Current second (ss)
    ret = utime.localtime()
    return '{:02}'.format(ret[5])
   elif svname==SysVars[6]: #%sysday% 	16 	Current day of month (DD)
    ret = utime.localtime()
    return '{:02}'.format(ret[2])
   elif svname==SysVars[7]: #%sysmonth% 	3 	Current month (MM)
    ret = utime.localtime()
    return '{:02}'.format(ret[1])
   elif svname==SysVars[8]: #%sysyear% 	2018 	4 digits (YYYY)
    ret = utime.localtime()
    return '{:04}'.format(ret[0])
   elif svname==SysVars[9]: #%sysyears% 	18 	2 digits (YY)
    ret = utime.localtime()
    ret2 = '{:04}'.format(ret[0])
    return ret2[2:]
   elif svname==SysVars[10]: #%sysweekday% 	5 	Weekday (integer) - 1, 2, 3... (1=Sunday, 2=Monday etc.)
    ret = utime.localtime()
    mday = ret[6]
    if mday==6:
     mday = 1
    else:
     mday = mday+2
    return mday
   elif svname==SysVars[11]: #%sysweekday_s% 	Fri 	Weekday (verbose) - Sun, Mon, Tue
    days = ['Mon','Tue',"Wed","Thu","Fri","Sat","Sun"]
    ret = utime.localtime()
    return days[ int(ret[6]) ]
   elif svname==SysVars[12]: #%unixtime% 	1521731277 	Unix time (seconds since epoch, 1970-01-01 00:00:00)
    import time
    return str(int(time.time()))
   elif svname==SysVars[13]: #%uptime% 	3244 	Uptime in minutes
    return str(misc.getuptime(2))
   elif svname==SysVars[14]: #%rssi% 	-45 	WiFi signal strength (dBm)
    return str(unet.get_rssi())
   elif svname==SysVars[15]: #%ip% 	192.168.0.123 	Current IP address
    return str(unet.get_ip())
   elif svname==SysVars[16]: #%ip4% ipcim 4.byte
    res2 = str(unet.get_ip())
    resarr = res2.split(".")
    if len(resarr)>3:
     return resarr[3]
   elif svname==SysVars[17]: #%sysname%	name
    return settings.Settings["Name"]
   elif svname==SysVars[18]: #%unit% 	32 	Unit number
    return settings.Settings["Unit"]
   elif svname==SysVars[19]: #%ssid% 
    return str(unet.get_ssid())
   elif svname==SysVars[20]: #%mac% 	00:14:22:01:23:45 	MAC address
    return str(unet.get_mac())
   elif svname==SysVars[21]: #%mac_int% 	2212667 	MAC address in integer to be used in rules (only the last 24 bit)
     res = ""
     try:
      res2 = str(unet.get_mac())
      resarr = res2.split(":")
      if len(resarr)>5:
       res = str(int("0x"+resarr[3]+resarr[4]+resarr[5],16))
     except:
      res = ""
     return res
   elif svname==SysVars[22]: #%build%
    bstr = str(pglobals.BUILD)
    return bstr
   elif svname==SysVars[23]: #sunrise
     res = "00:00"
     return res
   elif svname==SysVars[24]: #sunset
     res = "00:00"
     return res

   elif svname==SysVars[25]: #sun altitude
     res = "0"
     return res

   elif svname==SysVars[26]: #sun azimuth
     res = "0"
     return res

   elif svname==SysVars[27]: #sun radiation
     res = "-1"
     return res

   elif svname==SysVars[28]: #%br%
    return str("\r\n")

   elif svname==SysVars[29]: #%lf%
    return str("\n")

   elif svname==SysVars[30]: #%tab%
    return str("	")

 return res

def parsevalue(pvalue):
   retval = pvalue
   if ('%' in pvalue) or ('[' in pvalue):
    retval, state = parseruleline(pvalue) # replace variables
   oparr = "+-*/%&|^~<>"
   op = False
   for o in oparr:
    if o in retval:
     op = True
     break
   try:
    if op:
     retval = eval(retval)  # evaluate expressions
   except:
     retval = str(retval)
   return retval

def parseconversions(cvalue):
 retval = cvalue
 if ("%c_" in retval):
  cf = retval.find("%c_m2day%")
  if cf>=0:
   ps = retval.find("(",cf)
   pe = -1
   if ps >=0:
    pe = retval.find(")",ps)
   if pe >= 0:
    param = retval[ps+1:pe].strip()
   try:
    param = float(param)
   except:
    param = 0
   retval = retval[:cf]+str(misc.formatnum((param/1440),2))+retval[pe+1:]
  cf = retval.find("%c_m2dh%")
  if cf>=0:
   ps = retval.find("(",cf)
   pe = -1
   if ps >=0:
    pe = retval.find(")",ps)
   if pe >= 0:
    param = retval[ps+1:pe].strip()
   try:
    param = float(param)
   except:
    param = 0
   days, remainder = divmod(param, 1440)
   hours, minutes = divmod(remainder, 60)
   retval = retval[:cf]+str(int(days))+"d "+str(int(hours))+"h"+retval[pe+1:]
  cf = retval.find("%c_m2dhm%")
  if cf>=0:
   ps = retval.find("(",cf)
   pe = -1
   if ps >=0:
    pe = retval.find(")",ps)
   if pe >= 0:
    param = retval[ps+1:pe].strip()
   try:
    param = float(param)
   except:
    param = 0
   days, remainder = divmod(param, 1440)
   hours, minutes = divmod(remainder, 60)
   retval = retval[:cf]+str(int(days))+"d "+str(int(hours))+"h "+str(int(minutes))+"m"+retval[pe+1:]
 return retval

def parseruleline(linestr,rulenum=-1):
 global GlobalRules
 cline = linestr.strip()
 state = "CMD"
 if "[" in linestr:
  m = misc.findall(r"\[([A-Za-z0-9_#\-]+)\]", linestr)
  if len(m)>0: # replace with values
   for r in range(len(m)):
    tval = str(gettaskvaluefromname(m[r]))
    if tval=="None":
     state = "INV"
    cline = cline.replace("["+m[r]+"]",tval)
  else:
   print("Please avoid special characters in names! ",linestr)
 if ("%eventvalue%" in linestr) and (rulenum!=-1):
  cline = cline.replace("%eventvalue%",str(GlobalRules[rulenum]["evalue"]))
 if "%" in cline:
  m = misc.findall(r"\%([A-Za-z0-9_#\+\-]+)\%", cline)
  if len(m)>0: # replace with values
   for r in range(len(m)):
    if m[r].lower() in SysVars:
     cline = cline.replace("%"+m[r]+"%",str(getglobalvar(m[r])))
    elif ("-" in m[r]) or ("+" in m[r]):
     val = str(getglobalvar(m[r]))
     if val != "":
      cline = cline.replace("%"+m[r]+"%",val)
 cline = parseconversions(cline)
 equ = getfirstequpos(cline)
 if equ!=-1:
  if cline[:3].lower() == "if ":
   if "=" in getequchars(cline,True):
    cline = cline.replace("=","==") # prep for python interpreter
    cline = cline.replace("!==","!=") # revert invalid operators
    cline = cline.replace(">==",">=")
    cline = cline.replace("<==","<=")
   tline = cline
   state = "IFST"
   try:
    cline = eval(cline[3:])
   except:
    cline = False                 # error checking?
   misc.addLog(pglobals.LOG_LEVEL_DEBUG,"Parsed condition: "+str(tline)+" "+str(cline))
 elif "endif" in cline:
  cline = True
  state = "IFEN"
 elif "else" in cline:
  cline = False
  state = "IFEL"
 elif cline.startswith("breakon"):
  cline = False
  state = "BREAK"
 return cline,state

def isformula(line):
 if "%value%" in line.lower():
  return True
 else:
  return False

def parseformula(line,value):
 fv = False
 if "%value%" in line.lower():
  l2 = line.replace("%value%",str(value))
  fv = parsevalue(l2)
 return fv

def rulesProcessing(eventstr,efilter=-1): # fire events
 global GlobalRules
 rfound = -1
 retval = 0
 misc.addLog(pglobals.LOG_LEVEL_INFO,"Event: "+eventstr)
 estr=eventstr.strip().lower()
 if len(GlobalRules)<1:             # if no rules found, exit
  return False
 for r in range(len(GlobalRules)):
  if efilter!=-1:
   if GlobalRules[r]["ecat"]==efilter:  # check event based on filter
     if efilter == pglobals.RULE_TIMER:
        if GlobalRules[r]["ename"].lower() == estr.lower():
         rfound = r
         break
     elif efilter == pglobals.RULE_CLOCK: # check time strings equality
      fe1 = getfirstequpos(estr)
      invalue = removeequchars(estr[fe1:].replace("=","").strip())
      fe2 = getfirstequpos(GlobalRules[r]["ename"])
      tes = invalue+GlobalRules[r]["ename"][fe2:]
      if comparetime(tes):
        rfound = r
        break
     else:
       fe1 = getfirstequpos(estr)
       if fe1 ==-1:
        fe1 = len(estr)
       if fe1<=len(GlobalRules[r]["ename"]):
        if GlobalRules[r]["ename"][:fe1].lower()==estr[:fe1].lower():
         rfound = r
         break
  else:                                      # it is general event, without filter
    fe1 = getfirstequpos(estr)
    if fe1 ==-1:
     fe1 = len(estr)
    if fe1<=len(GlobalRules[r]["ename"]):
      if GlobalRules[r]["ename"][:fe1].lower()==estr[:fe1].lower():
       rfound = r
       break
 if rfound>-1: # if event found, analyze that
  fe1 = getfirstequpos(estr)
  if (fe1>-1): # value found
    if GlobalRules[rfound]["ecat"] == pglobals.RULE_CLOCK: # check time strings equality
      pass
    elif GlobalRules[rfound]["ecat"] == pglobals.RULE_TIMER: # check timer
      pass
    else:
      invalue = ""
#      print("ename ",GlobalRules[rfound]["ename"]) # debug
      if getfirstequpos(str(GlobalRules[rfound]["ename"]))>-1:
       invalue = removeequchars(estr[fe1:].replace("=","").strip())
#      print("i1 ",invalue)                     # debug
#      print("estr ",estr,getfirstequpos(estr)) # debug
      if getfirstequpos(estr)>-1:
       if getfirstequpos(GlobalRules[rfound]["ename"][fe1:])>-1:
        invalue = removeequchars(estr[fe1:].replace("=","").strip())
       else:
        GlobalRules[rfound]["evalue"]=removeequchars(estr[fe1:].replace("=","").strip())
#      print("i2 ",invalue)                     # debug
      if invalue != "":
       GlobalRules[rfound]["evalue"]=invalue                 # %eventvalue%
       tes = str(invalue)+str(GlobalRules[rfound]["ename"][fe1:])
       try:
        if "=" == getequchars(tes):
         tes = tes.replace("=","==") # prepare line for python interpreter
        if eval(tes)==False:         # ask the python interpreter to eval conditions
         return False                # if False, than exit - it looks like a good idea, will see...
       except:
        return False
  if len(GlobalRules[rfound]["ecode"])>0:
   ifbool = True
   for rl in range(len(GlobalRules[rfound]["ecode"])):
     retval, state = parseruleline(GlobalRules[rfound]["ecode"][rl],rfound) # analyze condition blocks
     if state=="IFST":
       ifbool = retval
     elif state=="IFEL":
       ifbool = not(ifbool)
     elif state=="IFEN":
       ifbool = True
     elif ifbool:
      if state=="INV":
       misc.addLog(pglobals.LOG_LEVEL_ERROR,"Invalid command: "+retval)
      elif state=="BREAK":
       return True
      else:
       cret = doExecuteCommand(retval,False) # execute command

def comparetime(tstr):
 result = True
 try:
  tstr2 = tstr.replace(":",",")
  tstr2 = tstr2.replace("==","=")
  sides = tstr2.split("=")
  tleft = sides[0].split(",")
  tright = sides[1].split(",")
  tleft[0] = tleft[0].lower()
  tright[0] = tright[0].lower()
  l1 = len(tleft)
  l2 = len(tright)
  if l2<l1:
   l1 = l2
  for t in range(l1):
   if 'all' not in tright[t] and '**' not in tright[t]:
    if str(tright[t]).strip() != str(tleft[t]).strip():
     result = False
     break
 except:
  result = False
 return result
