import pglobals
import ujson
import pglobals
import gc

settingsfile    = 'data/settings.dat'
tasksfile       = 'data/tasks.dat'
controllersfile = 'data/controllers.dat'
notifiersfile   = 'data/notifiers.dat'
pinoutfile      = 'data/pinout.dat'
advsettingsfile = 'data/advsettings.dat'
hwsettingsfile = 'data/hwsettings.dat'

Settings = {
"Name":"mpyEasy",
"Unit":0,
"Password":"",
"Delay":60,
"WifiClient":0,
"AP1SSID":"",
"AP1KEY":"",
"AP2SSID":"",
"AP2KEY":"",
"WifiAP":2,
"APSSID":"mpyEasy",
"APKEY":"configesp",
"LANIF":0,
"WDHCP":True,
"WIP":"",
"WMask":"",
"WGW":"",
"WDNS":"",
"LDHCP":True,
"LIP":"",
"LMask":"",
"LGW":"",
"LDNS":""
}

AdvSettings = {
"webloglevel":2,
"consoleloglevel":2,
"usentp":False,
"ntpserver":"",
"timezone":0
}

HW = {
 "freq":160,
 "i2c0":False,
 "i2c0-freq":0,
 "i2c0-sda":-1,
 "i2c0-scl":-1,
 "i2c1":False,
 "i2c1-freq":0,
 "i2c1-sda":-1,
 "i2c1-scl":-1,
 "spi1":False,
 "spi1-cs":-1,
 "spi1-baud":0,
 "spi2":False,
 "spi2-cs":-1,
 "spi2-baud":0,
 "psram-cs":-1,
 "psram-clk":-1,
 "lan-phy":-1,
 "lan-mdc":23,
 "lan-mdio":18,
 "lan-pwr":16,
 "lan-addr":0,
 "lan-clk":-1,
 "uart1":False,
 "uart1-baud":9600,
 "uart1-rx":25,
 "uart1-tx":26,
 "uart1-timeout":5000,
 "uart2":False,
 "uart2-baud":9600,
 "uart2-rx":16,
 "uart2-tx":17,
 "uart2-timeout":5000
}

Pinout = []
PinStatesMax = 9
PinStates = ["Default","Input","Input-Pulldown","Input-Pullup","Output","Output-Lo","Output-Hi","Alternate","Special","Reserved"]

Tasks = [False]
Controllers = [False]
Notifiers = [False]

nodelist = [] # for ESPEasy P2P, fill at runtime!
p2plist = [] # for LORA/P2P peer list

def loadsettings():
 global Settings, settingsfile
 print("Loading settings")
 try:
  cf = open(settingsfile,'r')
  Settings = ujson.load(cf)
 except:
  pass

def savesettings():
 global Settings, settingsfile
 print("Save settings")
 try:
  with open(settingsfile,'w') as cf:
   ujson.dump(Settings,cf)
 except:
  pass

def loadadvsettings():
 global AdvSettings, advsettingsfile
 print("Loading AdvSettings")
 try:
  cf = open(advsettingsfile,'r')
  AdvSettings = ujson.load(cf)
 except:
  pass

def saveadvsettings():
 global AdvSettings, advsettingsfile
 print("Save AdvSettings")
 try:
  with open(advsettingsfile,'w') as cf:
   ujson.dump(AdvSettings,cf)
 except:
  pass

def loadhwsettings():
 global HW, hwsettingsfile
 print("Loading HW settings")
 try:
  cf = open(hwsettingsfile,'r')
  HW = ujson.load(cf)
 except:
  pass

def savehwsettings():
 global Settings, settingsfile
 print("Save HW settings")
 try:
  with open(hwsettingsfile,'w') as cf:
   ujson.dump(HW,cf)
 except:
  pass

def loadpinout():
 global Pinout, pinoutfile
 print("Loading Pinout settings")
 try:
  cf = open(pinoutfile,'r')
  Pinout = ujson.load(cf)
 except Exception as e:
  pass

def savepinout():
 global Pinout, pinoutfile
 print("Save Pinout settings")
 try:
  with open(pinoutfile,'w') as cf:
   ujson.dump(Pinout,cf)
 except:
  pass

def loadtasks():
 global Tasks,tasksfile
 print("Loading tasks")
 tc = []
 try:
  cf = open(tasksfile,'r')
  tc = ujson.load(cf)
 except Exception as e:
  return False
 Tasks = []
 for c in range(len(tc)):
  if 'pluginid' in tc[c]:
   fnamew = str(tc[c]['pluginid'])
   fnamew = "_P"+zfill(fnamew,3)
   fnameok = ""
   for fn in range(len(pglobals.deviceselector)):
    try:
     fname = pglobals.deviceselector[fn][0]
     if fname.startswith(fnamew):
      fnameok = fname
      break
    except:
     pass
   if fnameok!="":
    try:
     m = __import__(fnameok)
     Tasks.append(m.Plugin(c))
    except Exception as e:
     Tasks.append(False)
    gc.collect()
    for key in tc[c]:
     if key == 'initialized':
      tc[c][key] = False
     try:
      setattr( Tasks[c], key, tc[c][key] )
     except Exception as e:
      pass
  else:
     Tasks.append(False)
 #print(tc,Tasks)#debug

def savetasks():
 global Tasks, tasksfile
 print("Save tasks")
 try:
  with open(tasksfile,'w') as cf:
   cf.write('[')
   for c in Tasks:
     try:
      cf.write(c.toJSON())
      cf.write(",")
     except Exception as e:
      cf.write("{},")
   cf.write('{}]')
 except Exception as e:
  pass

def loadcontrollers():
 global Controllers, controllersfile
 print("Loading controllers")
 tc = []
 try:
  cf = open(controllersfile,'r')
  tc = ujson.load(cf)
 except Exception as e:
  return False
 Controllers = []
 for c in range(len(tc)):
  if 'controllerid' in tc[c]:
   fnamew = str(tc[c]['controllerid'])
   fnamew = "_C"+zfill(fnamew,3)
   fnameok = ""
   for fn in range(len(pglobals.controllerselector)):
    try:
     fname = pglobals.controllerselector[fn][0]
     if fname.startswith(fnamew):
      fnameok = fname
      break
    except:
     pass
   if fnameok!="":
    try:
     m = __import__(fnameok)
     Controllers.append(m.Controller(c))
    except Exception as e:
     Controllers.append(False)
    gc.collect()
    for key in tc[c]:
     if key == 'initialized':
      tc[c][key] = False
     try:
      setattr( Controllers[c], key, tc[c][key] )
     except Exception as e:
      pass
  else:
     Controllers.append(False)
# print(tc,Controllers)#debug
# print(controllersfile,cf,tc,Controllers)#debug


def savecontrollers():
 global Controllers, controllersfile
 print("Save controllers")
 try:
  with open(controllersfile,'w') as cf:
   cf.write('[')
   for c in Controllers:
     try:
      cf.write(c.toJSON())
      cf.write(",")
     except Exception as e:
      cf.write("{},")
   cf.write('{}]')
 except Exception as e:
  pass

def loadnotifiers():
 global Notifiers, notifiersfile
 print("Loading notifiers")
 tc = []
 try:
  cf = open(notifiersfile,'r')
  tc = ujson.load(cf)
 except Exception as e:
  return False
 Notifiers = []
 for c in range(len(tc)):
  if 'number' in tc[c]:
   fnamew = str(tc[c]['number'])
   fnamew = "_N"+zfill(fnamew,3)
   fnameok = ""
   for fn in range(len(pglobals.notifierselector)):
    try:
     fname = pglobals.notifierselector[fn][0]
     if fname.startswith(fnamew):
      fnameok = fname
      break
    except:
     pass
   if fnameok!="":
    try:
     m = __import__(fnameok)
     Notifiers.append(m.Plugin(c))
    except Exception as e:
     Notifiers.append(False)
    gc.collect()
    for key in tc[c]:
     if key == 'initialized':
      tc[c][key] = False
     try:
      setattr( Notifiers[c], key, tc[c][key] )
     except Exception as e:
      pass
  else:
     Notifiers.append(False)
# print(tc,Controllers)#debug
# print(controllersfile,cf,tc,Controllers)#debug


def savenotifiers():
 global Notifiers, notifiersfile
 print("Save notifiers")
 try:
  with open(notifiersfile,'w') as cf:
   cf.write('[')
   for c in Notifiers:
     try:
      cf.write(c.toJSON())
      cf.write(",")
     except Exception as e:
      cf.write("{},")
   cf.write('{}]')
 except Exception as e:
  pass

def zfill(s, width):
    s = str(s)
    width = int(width)
    return '{:0>{w}}'.format(s, w=width)

# msg arrived from a controller->reroute data to the destination device
# this will do the magic of the two way communication
def callback_from_controllers(controllerindex,idx,values,taskname="",valuename=""):
 global Tasks
 for x in range(len(Tasks)):
  if (Tasks[x] and type(Tasks[x]) is not bool): # device exists
   if (Tasks[x].enabled) and (Tasks[x].recdataoption): # device enabled and able to receive data, enable recdataoption at plugin!
    if taskname == "": # search task by idx
      if (str(Tasks[x].controlleridx[controllerindex])==str(idx)):
        Tasks[x].plugin_receivedata(values)            # implement plugin_receivedata() at plugin side!
        break
    else:             # search task by name
      if (Tasks[x].gettaskname().strip() == taskname.strip()): # match with taskname, case sensitive????
        tvalues = []
        for u in range(pglobals.VARS_PER_TASK):     # fill unused values with -9999, handle at plugin side!!!
         tvalues.append(-9999)
        for v in range(Tasks[x].valuecount):           # match with valuename
         if Tasks[x].valuenames[v]==valuename:
          tvalues[v] = values
          Tasks[x].plugin_receivedata(tvalues)
          break
        break

def get_i2c_pins(i2cline=0):
    global HW
    iname = "i2c{0}-s".format(i2cline)
    dname = iname+"da"
    cname = iname+"cl"
    return HW[dname], HW[cname]
