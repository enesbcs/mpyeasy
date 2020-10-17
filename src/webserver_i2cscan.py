import webserver_global as ws
import settings
import pglobals
import gc
import misc
import inc.libhw as libhw

def handle_i2cscan(httpResponse):
 ws.navMenuIndex=7
 ws.TXBuffer = ""
 httpResponse.WriteResponseOk(
        headers = ({'Cache-Control': 'no-cache'}),
        contentType = 'text/html',
        contentCharset = 'UTF-8',
        content = "" )
 ws.sendHeadandTail("TmplStd",ws._HEAD)

 ws.TXBuffer += "<table class='multirow' border=1px frame='box' rules='all'><TH>I2C Addresses in use<TH>Supported devices</th></tr>"
 i2ca = []
 iname = ""
 iworks = None
 i2cdevs =0
 for i in range(0,2):
  httpResponse._write(ws.TXBuffer,strEncoding='UTF-8')
  ws.TXBuffer = ""
  i2cdevs =0
  iworks = None
  try:
   iname = "i2c{0}".format(i)
   if settings.HW[iname]:
    if i==0:
     if libhw.i2c0 is not None:
      iworks = libhw.i2c0
     else:
      break
    else:
     if libhw.i2c1 is not None:
      iworks = libhw.i2c1
     else:
      break
  except:
    pass
  ws.addFormSubHeader("I2C-{0}".format(i))
  ws.TXBuffer += "</td></tr>"
  i2ca = []
  if iworks is not None:
   try:
    i2ca = iworks.scan()
   except:
    pass
  try:
   for d in range(len(i2ca)):
      i2cdevs += 1
      ws.TXBuffer += "<TR><TD>0x{0:02x}</td><td>{1}</td></tr>".format(int(i2ca[d]),str(libhw.geti2cdevname(i2ca[d])).replace(";","<br>"))
  except Exception as e:
   print(e) # debug
  if i2cdevs==0:
   ws.TXBuffer += "<tr><td colspan=2>No device found on I2C bus</td></tr>"
 ws.TXBuffer += "</table>"

 ws.sendHeadandTail("TmplStd",ws._TAIL)
 httpResponse._write(ws.TXBuffer,strEncoding='UTF-8')
 ws.TXBuffer = ""
