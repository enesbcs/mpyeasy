import webserver_global as ws
import settings
import pglobals
import sys
import misc
import unet
try:
 import uos
except:
 pass

def handle_json(httpResponse,responsearr):
 ws.navMenuIndex=7
 ws.TXBuffer = ""
 httpResponse.WriteResponseOk(
        headers = ({'Cache-Control': 'no-cache'}),
        contentType = 'application/json',
        contentCharset = 'UTF-8',
        content = "" )

 tasknrstr = ws.arg("tasknr",responsearr).strip()
 showspectask = -1
 if (len(tasknrstr)>0):
  try:
   showspectask = int(tasknrstr)-1
  except:
   showspectask = -1
 showsystem = True
 showwifi = True
 showdataacq = True
 showtaskdetail = True
 view = ws.arg("view",responsearr)
 if (len(view)>0):
  if view=="sensorupdate":
   showsystem = False
   showwifi = False
   showdataacq = False
   showtaskdetail = False
 ws.TXBuffer += "{"
 if showspectask==-1:
  if showsystem:
   ws.TXBuffer += '"System":{"Build":"'
   ws.TXBuffer += str(pglobals.PROGNAME) + " " + str(pglobals.PROGVER)
   try:
    uver = uos.uname()
    uver2 = 'uPython '+ str(uver.version)
    umach = str(uver.machine)
   except:
    uver2 = ""
    umach = ""

   ws.TXBuffer += '","System libraries":"Python '
   ws.TXBuffer += sys.version.replace('\n','<br>')+" "+uver2
   ws.TXBuffer += '","Plugins":'+str(len(pglobals.deviceselector)-1)
   ws.TXBuffer += ',"Local time":"'+ misc.strtime(0)
   ws.TXBuffer += '","Unit":'+str(settings.Settings["Unit"])
   ws.TXBuffer += ',"Name":"'+str(settings.Settings["Name"])
   try:
    ws.TXBuffer += '","Uptime":'+ str(misc.getuptime(0))
   except:
    ws.TXBuffer += '","Uptime":0'
   ws.TXBuffer += ',"Load":0' #not supported
   try:
    ws.TXBuffer += ',"Free RAM":'+str( int(esp_os.get_memory()['f'] /1024) )
   except:
    ws.TXBuffer += ',"Free RAM":0'
   ws.TXBuffer += "},"
  if showwifi:
   ws.TXBuffer += '"WiFi":{'
   ws.TXBuffer += '"IP config":"DHCP' #not supported
   ws.TXBuffer += '","IP":"'+unet.get_ip()
   ws.TXBuffer += '","Subnet Mask":"255.255.255.0' #not supported
   ws.TXBuffer += '","Gateway IP":"'
   ws.TXBuffer += '","MAC address":"'+unet.get_mac()
   ws.TXBuffer += ',"SSID":"'+str( unet.get_ssid())+'"'
   ws.TXBuffer += ',"RSSI":'+str(unet.get_rssi())
   ws.TXBuffer += "},"
  senstart = 0
  senstop  = len(settings.Tasks)
 else:
  senstart = showspectask
  senstop = senstart+1
 ws.TXBuffer += '"Sensors":['
 ttl = 120
 for sc in range(senstart,senstop):
  httpResponse._write(ws.TXBuffer,strEncoding='UTF-8')
  ws.TXBuffer = ""
  if settings.Tasks[sc] != False:
   ws.TXBuffer += '{"TaskValues": ['
   for tv in range(0,settings.Tasks[sc].valuecount):
    ws.TXBuffer += '{"ValueNumber":' + str(tv+1)+',"Name":"' + str(settings.Tasks[sc].valuenames[tv])+'",'
    ws.TXBuffer += '"NrDecimals":'+str(settings.Tasks[sc].decimals[tv])+','
    ws.TXBuffer += '"Value":'
    if str(settings.Tasks[sc].uservar[tv])=="":
     ws.TXBuffer += '""'
    else:
     if str(settings.Tasks[sc].decimals[tv]) == "-1":
      ival = '"'+ str(settings.Tasks[sc].uservar[tv]) + '"'
     else:
      try:
       ival = float(settings.Tasks[sc].uservar[tv])
      except:
       ival = '"'+ str(settings.Tasks[sc].uservar[tv]) + '"'
     ws.TXBuffer += str(ival)
    ws.TXBuffer += '},'
   if ws.TXBuffer[len(ws.TXBuffer)-1]==",":
    ws.TXBuffer = ws.TXBuffer[:-1]
   ws.TXBuffer += '],'
   ws.TXBuffer += '"DataAcquisition": ['
   for ca in range(pglobals.CONTROLLER_MAX):
    ws.TXBuffer += '{"Controller":'+str(ca+1)+',"IDX":'+str(settings.Tasks[sc].controlleridx[ca])+',"Enabled":"'+str(settings.Tasks[sc].senddataenabled[ca])+'"},'
   if ws.TXBuffer[len(ws.TXBuffer)-1]==",":
    ws.TXBuffer = ws.TXBuffer[:-1]
   ws.TXBuffer += '],'
   ws.TXBuffer += '"TaskInterval":'+str(settings.Tasks[sc].interval)+','
   ws.TXBuffer += '"Type":"'+str(settings.Tasks[sc].getdevicename())+'",'
   ws.TXBuffer += '"TaskName":"'+str(settings.Tasks[sc].gettaskname())+'",'
   ws.TXBuffer += '"TaskEnabled":"'+str(settings.Tasks[sc].enabled)+'",'
   ws.TXBuffer += '"TaskNumber":'+str(sc+1)+'},'
   if (settings.Tasks[sc].interval<ttl) and (settings.Tasks[sc].interval>0):
    ttl = settings.Tasks[sc].interval
 ws.TXBuffer += '],'
 ws.TXBuffer += '"TTL":'+str(ttl*1000)+'}'

 httpResponse._write(ws.TXBuffer,strEncoding='UTF-8')
