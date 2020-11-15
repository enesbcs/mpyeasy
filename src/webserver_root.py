import webserver_global as ws
import settings
import esp_os
import unet
import pglobals
import gc
import misc

def handle_root(httpResponse,responsearr):
 ws.navMenuIndex=0
 ws.TXBuffer = ""
 responsestr = ""

 httpResponse.WriteResponseOk(
        headers = ({'Cache-Control': 'no-cache'}),
        contentType = 'text/html',
        contentCharset = 'UTF-8',
        content = "" )
 ws.sendHeadandTail("TmplStd",ws._HEAD)
 try:
  cmdline = ws.arg("cmd",responsearr).strip()
  if cmdline.startswith('reboot'):
     ws.sendHeadandTail("TmplStd",ws._TAIL)

  if len(cmdline)>0:
   import commands
   responsestr = str(commands.doExecuteCommand(cmdline))
 except:
  pass

 if len(responsestr)>0:
   ws.TXBuffer += "<P>{0}<p>".format(responsestr)

 ws.TXBuffer += "<form><table class='normal'><tr><TH style='width:150px;' align='left'>System Info<TH align='left'>Value<TR><TD>Unit:<TD>"
 ws.TXBuffer += str(settings.Settings["Unit"])
 ws.TXBuffer += "<TR><TD>Uptime:<TD>" + str(misc.getuptime(1))
 httpResponse._write(ws.TXBuffer,strEncoding='UTF-8')
 ws.TXBuffer = ""
 try:
  ws.TXBuffer += "<TR><TD>Free Mem:<TD>" + str( int(esp_os.get_memory()['f'] /1024) ) + " kB"
 except:
  pass
 ws.TXBuffer += "<TR><TD>IP:<TD>" + str( unet.get_ip() )
 ws.TXBuffer += "<TR><TD>Wifi RSSI:<TD>" + str(unet.get_rssi())
 ws.TXBuffer += '<tr><td>Build<td>' + str(pglobals.PROGNAME) + " " + str(pglobals.PROGVER)
 ws.TXBuffer += "<TR><TD><TD>"
 ws.addButton("sysinfo", "More info")
 httpResponse._write(ws.TXBuffer,strEncoding='UTF-8')
 ws.TXBuffer = ""
 ws.TXBuffer += "</table><BR>"
 if len(settings.nodelist)>0:
   ws.TXBuffer += "<BR><table class='multirow'><TR><TH>Node List<TH>Name<TH>Build<TH>Type<TH>IP<TH>Age"
   for n in settings.nodelist:
    ws.TXBuffer += "<TR><TD>Unit "+str(n["unitno"])+"<TD>"+str(n["name"])+"<TD>"+str(n["build"])+"<TD>"
    ntype = ""
    if int(n["type"])==pglobals.NODE_TYPE_ID_ESP_EASY_STD:
     ntype = "ESP Easy"
    elif int(n["type"])==pglobals.NODE_TYPE_ID_ESP_EASYM_STD:
     ntype = "ESP Easy Mega"
    elif int(n["type"])==pglobals.NODE_TYPE_ID_ESP_EASY32_STD:
     ntype = "ESP Easy32"
    elif int(n["type"])==pglobals.NODE_TYPE_ID_ARDUINO_EASY_STD:
     ntype = "Arduino Easy"
    elif int(n["type"])==pglobals.NODE_TYPE_ID_NANO_EASY_STD:
     ntype = "Nano Easy"
    elif int(n["type"])==pglobals.NODE_TYPE_ID_RPI_EASY_STD:
     ntype = "RPI Easy"
    ws.TXBuffer += ntype+"<TD>"
    waddr = str(n["ip"])
    if str(n["port"]) != "" and str(n["port"]) != "0" and str(n["port"]) != "80":
     waddr += ":" + str(n["port"])
    ws.addWideButton("http://"+waddr, waddr, "")
    ws.TXBuffer += "<TD>"+str(n["age"])
   ws.TXBuffer += "</table></form>"

 if len(settings.p2plist)>0:
  try:
   ws.TXBuffer += "<BR><table class='multirow'><TR><TH>Protocol<TH>P2P node number<TH>Name<TH>Build<TH>Type<TH>MAC<TH>RSSI<TH>Last seen<TH>Capabilities"
   for n in settings.p2plist:
    hstr = str(n["protocol"])
    if hstr=="ESPNOW":
     hstr = "<a href='espnow'>"+hstr+"</a>"
    ws.TXBuffer += "<TR><TD>"+hstr+"<TD>Unit "+str(n["unitno"])+"<TD>"+str(n["name"])+"<TD>"+str(n["build"])+"<TD>"
    ntype = "Unknown"
    if int(n["type"])==pglobals.NODE_TYPE_ID_ESP_EASY_STD:
     ntype = "ESP Easy"
    elif int(n["type"])==pglobals.NODE_TYPE_ID_ESP_EASYM_STD:
     ntype = "ESP Easy Mega"
    elif int(n["type"])==pglobals.NODE_TYPE_ID_ESP_EASY32_STD:
     ntype = "ESP Easy32"
    elif int(n["type"])==pglobals.NODE_TYPE_ID_ARDUINO_EASY_STD:
     ntype = "Arduino Easy"
    elif int(n["type"])==pglobals.NODE_TYPE_ID_NANO_EASY_STD:
     ntype = "Nano Easy"
    elif int(n["type"])==pglobals.NODE_TYPE_ID_RPI_EASY_STD:
     ntype = "RPI Easy"
    elif int(n["type"])==pglobals.NODE_TYPE_ID_ATMEGA_EASY_LORA:
     ntype = "LoRa32u4"
    ws.TXBuffer += ntype
    ws.TXBuffer += "<TD>"+str(n["mac"])
    ws.TXBuffer += "<TD>"+str(n["lastrssi"])
    ldt = n["lastseen"]
    lstr = ""
    try:
     lstr = '{:04}-{:02}-{:02} {:02}:{:02}:{:02}'.format(ldt[0],ldt[1],ldt[2],ldt[3],ldt[4],ldt[5])
    except:
     lstr = str(ldt)
    ws.TXBuffer += "<TD>"+lstr
    wm = int(n["cap"])
    wms = ""
    if (wm & 1)==1:
     wms = "SEND "
    if (wm & 2)==2:
     wms += "RECEIVE "
    ws.TXBuffer += "<TD>"+wms
   ws.TXBuffer += "</table></form>"
  except Exception as e:
   pass

 ws.sendHeadandTail("TmplStd",ws._TAIL)
 httpResponse._write(ws.TXBuffer,strEncoding='UTF-8')
 ws.TXBuffer = ""
