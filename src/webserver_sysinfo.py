import webserver_global as ws
import settings
import esp_os
import unet
import pglobals
import gc
import misc
import sys
try:
 import uos
except:
 pass

def handle_sysinfo(httpResponse):
 ws.navMenuIndex=7
 ws.TXBuffer = ""
 httpResponse.WriteResponseOk(
        headers = ({'Cache-Control': 'no-cache'}),
        contentType = 'text/html',
        contentCharset = 'UTF-8',
        content = "" )
 ws.sendHeadandTail("TmplStd",ws._HEAD)
 ws.TXBuffer += "<table class='normal'><TR><TH style='width:150px;' align='left'>System Info<TH align='left'>"
 ws.TXBuffer += "<TR><TD>Unit<TD>"
 ws.TXBuffer += str(settings.Settings["Unit"])
 ws.TXBuffer += "<TR><TD>Local Time<TD>" + misc.strtime(0) #Local Time: (2000, 1, 1, 0, 45, 20, 5, 1)
 ws.TXBuffer += "<TR><TD>Uptime<TD>" + str(misc.getuptime(1))
 httpResponse._write(ws.TXBuffer,strEncoding='UTF-8')
 ws.TXBuffer = ""
 ws.TXBuffer += "<TR><TD>Frequency<TD>" + str( int(esp_os.getfreq() /1000000)) +" Mhz"
 try:
  ws.TXBuffer += "<TR><TD>Flash<TD>" + str( int(esp_os.getstorage() /1024)) + " kB"
 except:
  pass
 try:
  ws.TXBuffer += "<TR><TD>Memory<TD>" + str( int(esp_os.get_memory()['t'] /1024) ) + " kB"
 except:
  pass
 try:
  ws.TXBuffer += "<TR><TD>Free Mem<TD>" + str( int(esp_os.get_memory()['f'] /1024) ) + " kB"
 except:
  pass
 ws.TXBuffer += "<TR><TD>PSRAM<TD>" + str( esp_os.psRamFound() )
 httpResponse._write(ws.TXBuffer,strEncoding='UTF-8')
 ws.TXBuffer = ""
 try:
  uver = uos.uname()
  uver2 = 'uPython '+ str(uver.version)
  umach = str(uver.machine)
 except:
  uver2 = ""
  umach = ""
 if umach != "":
  ws.TXBuffer += "<TR><TD>Device<TD>" + str( umach )
 ws.TXBuffer += '<tr><td>Platform<td>' +sys.platform
 ws.TXBuffer += "<TR><TD>Wifi RSSI<TD>" + str(unet.get_rssi())
 ws.TXBuffer += '<tr><td>SSID<td>'+str( unet.get_ssid())
 ws.TXBuffer += '<tr><td>STA IP<td>'+ str( unet.get_ip("STA") )
 ws.TXBuffer += '<tr><td>STA MAC<td>'+ str( unet.get_mac("STA") )
 ws.TXBuffer += '<tr><td>AP IP<td>'+ str( unet.get_ip("AP") )
 ws.TXBuffer += '<tr><td>AP MAC<td>'+ str( unet.get_mac("AP") )
 ws.TXBuffer += '<tr><td>LAN IP<td>'+ str( unet.get_ip("LAN") )
 ws.TXBuffer += '<tr><td>LAN MAC<td>'+ str( unet.get_mac("LAN") ) 
 httpResponse._write(ws.TXBuffer,strEncoding='UTF-8')
 ws.TXBuffer = ""
 ws.TXBuffer += '<tr><td>Build<td>' + str(pglobals.PROGNAME) + " " + str(pglobals.PROGVER)
 ws.TXBuffer += '<tr><td>Libraries<td>Python ' + sys.version.replace('\n','<br>')+" "+uver2
 ws.TXBuffer += '<tr><td>Plugins<td>'+str(len(pglobals.deviceselector)-1)
 ws.TXBuffer += "</tr></table>"
 try:
  import inc.lib_part as PartMgr
  pm = PartMgr.partmgr()
  pl = pm.getparts()
 except:
  pl = []
 if len(pl)>0:
  try:
   pr = pm.getrunningpart()[4]
   pb = pm.getbootpart()[4]
  except:
   pr = ""
   pb = ""
  ws.TXBuffer += "<p><table class='normal'><tr><th>Partition</th><th>Start address</th><th>Size</th><th>Flags</th></tr>"
  for p in pl:
   prf = ""
   if pr==p[4]:
    prf = "Running "
   if pb==p[4]:
    prf += "Boot "
   ws.TXBuffer += "<tr><td>{0}</td><td>0x{1:07x}</td><td>{2}</td><td>{3}</td></tr>".format(p[4],p[2],p[3],prf)
  ws.TXBuffer += "</table>"
 ws.sendHeadandTail("TmplStd",ws._TAIL)
 httpResponse._write(ws.TXBuffer,strEncoding='UTF-8')
 ws.TXBuffer = ""
