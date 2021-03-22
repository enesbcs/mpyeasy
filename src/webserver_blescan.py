import webserver_global as ws
import settings
import pglobals
import gc
import misc
try:
 import inc.ubtle as BTLE
 import inc.lib_blehelper as BLEHelper
 import ubluetooth
 bleok = True
except:
 bleok = False

def handle_blescan(httpResponse):
 global bleok
 ws.navMenuIndex=7
 ws.TXBuffer = ""
 httpResponse.WriteResponseOk(
        headers = ({'Cache-Control': 'no-cache'}),
        contentType = 'text/html',
        contentCharset = 'UTF-8',
        content = "" )
 ws.sendHeadandTail("TmplStd",ws._HEAD)
 if bleok:
  try:
   BLEHelper.BLEStatus.reportscan(1)
   scanner = BTLE.Scanner(ubluetooth.BLE())
   devices = scanner.scan(15,passive=False)
   BLEHelper.BLEStatus.reportscan(0)
  except Exception as e:
   ws.TXBuffer += "BLE scanning failed "
   ws.TXBuffer += str(e)
   bleok = False
 else:
  ws.TXBuffer += "BLE not supported"
 if bleok:
     ws.TXBuffer += "<table class='multirow'><TR><TH>Address<TH>Address type<TH>RSSI<TH>Connectable<TH>Name<TH>Appearance</TH><TH>Actions</TH></TR>"
     cc = 0
     for dev in devices:
      cc += 1
      ws.TXBuffer += "<TR><TD><div id='mac"+str(cc)+"_1' name='mac"+str(cc)+"_1'>"+str(dev.addr)+"</div><TD>"+str(dev.addrType)+"<TD>"+str(dev.rssi)+" dBm<TD>"+str(dev.connectable)
      dname = ""
      shortdname = ""
      appear = ""
      for (adtype, desc, value) in dev.getScanData():
#        print(adtype,desc,value)#debug
        try:
         if desc.lower() == "complete local name":
          dname = str(value)
        except:
         pass
        try:        
         if desc.lower() == "shortened local name":
          shortdname = str(value)
        except:
         pass
        try:                
         if desc.lower() == "appearance":
          appear = str(value)
        except:
         pass
      if dname.strip()=="":
        dname = shortdname
      ws.TXBuffer += "<TD>"+str(dname)+"<TD>"+str(appear)+"<TD>"
      ws.TXBuffer += "</TR>"
      httpResponse._write(ws.TXBuffer,strEncoding='UTF-8')
      ws.TXBuffer = ""
     ws.TXBuffer += "</table>"
 ws.sendHeadandTail("TmplStd",ws._TAIL)
 httpResponse._write(ws.TXBuffer,strEncoding='UTF-8')
 ws.TXBuffer = ""
