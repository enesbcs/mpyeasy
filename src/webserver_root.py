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
 ws.sendHeadandTail("TmplStd",ws._TAIL)
 httpResponse._write(ws.TXBuffer,strEncoding='UTF-8')
 ws.TXBuffer = ""
