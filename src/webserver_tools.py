import webserver_global as ws

def handle_tools(httpResponse,responsearr):
 ws.navMenuIndex=7
 ws.TXBuffer = ""
 httpResponse.WriteResponseOk(
        headers = ({'Cache-Control': 'no-cache'}),
        contentType = 'text/html',
        contentCharset = 'UTF-8',
        content = "" )
 webrequest = ws.arg("cmd",responsearr)
 ws.sendHeadandTail("TmplStd",ws._HEAD)
 ws.TXBuffer += "<form><table class='normal'>"
 ws.addFormHeader("Tools")
 ws.addFormSubHeader("Command")
 ws.TXBuffer += "<TR><TD style='width: 280px'><input class='wide' type='text' name='cmd' value='{0}'><TD>".format(webrequest)
 ws.addSubmitButton()
 try:
  httpResponse._write(ws.TXBuffer,strEncoding='UTF-8')
 except:
  pass
 ws.TXBuffer = ""
 responsestr = ""
 if webrequest.startswith('reboot'):
     ws.sendHeadandTail("TmplStd",ws._TAIL)
 try:
  if len(webrequest)>0:
   import commands
   responsestr = str(commands.doExecuteCommand(webrequest))
 except:
  pass
 if len(responsestr)>0:
  try:
   import misc
   ws.TXBuffer += "<TR><TD colspan='2'>Command Output<BR><textarea readonly rows='10' wrap='on'>"
   ws.TXBuffer += str(responsestr)
   lc = len(misc.SystemLog)
   if lc>5:
    ls = lc-5
   else:
    ls = 0
   for l in range(ls,lc):
    ws.TXBuffer += '\r\n'+str(misc.SystemLog[l]["t"])+" : "+ str(misc.SystemLog[l]["l"])
   ws.TXBuffer += "</textarea>"
  except Exception as e:
   print(str(e))
 httpResponse._write(ws.TXBuffer,strEncoding='UTF-8')
 ws.TXBuffer = ""
 ws.addFormSubHeader("System")

 ws.TXBuffer += "<tr><td height=30>"
 ws.TXBuffer += "<a class='button link wide' onclick="
 ws.TXBuffer += '"'
 ws.TXBuffer += "return confirm('Do you really want to Reboot device?')"
 ws.TXBuffer += '"'
 ws.TXBuffer += " href='/?cmd=reboot'>Reboot</a>"
 ws.TXBuffer += "<TD>"
 ws.TXBuffer += "Reboot System"

 ws.TXBuffer += "<tr><td height=30>"
 ws.addWideButton("log", "Log", "")
 ws.TXBuffer += "<TD>"
 ws.TXBuffer += "Open log output"

 ws.TXBuffer += "<tr><td height=30>"
 ws.addWideButton("sysinfo", "Info", "")
 ws.TXBuffer += "<TD>"
 ws.TXBuffer += "Open system info page"

 ws.TXBuffer += "<tr><td height=30>"
 ws.addWideButton("advanced", "Advanced", "")
 ws.TXBuffer += "<TD>"
 ws.TXBuffer += "Open advanced settings"
 httpResponse._write(ws.TXBuffer,strEncoding='UTF-8')
 ws.TXBuffer = ""
 
 ws.TXBuffer += "<tr><td height=30>"
 ws.addWideButton("sysvars", "System Variables", "")
 ws.TXBuffer += "<TD>"
 ws.TXBuffer += "Show all system variables"

 ws.TXBuffer += "<tr><td height=30>"
 ws.addWideButton("update", "OTA Update", "")
 ws.TXBuffer += "<TD>"
 ws.TXBuffer += "OTA update"

 ws.TXBuffer += "<tr><td height=30>"
 ws.TXBuffer += "<a class='button link wide red' onclick="
 ws.TXBuffer += '"'
 ws.TXBuffer += "return confirm('Do you really want to Reset/Erase all settings?')"
 ws.TXBuffer += '"'
 ws.TXBuffer += " href='/?cmd=reset'>Reset device settings</a>"
 ws.TXBuffer += "<TD>"
 ws.TXBuffer += "Erase all setting files"
 httpResponse._write(ws.TXBuffer,strEncoding='UTF-8')
 ws.TXBuffer = ""

 ws.addFormSubHeader("Scan")

 ws.TXBuffer += "<tr><td height=30>"
 ws.addWideButton("wifiscanner", "WiFi Scan", "")
 ws.TXBuffer += "<TD>"
 ws.TXBuffer += "Scan WiFi AP's"

 ws.TXBuffer += "<tr><td height=30>"
 ws.addWideButton("blescanner", "BLE Scan", "")
 ws.TXBuffer += "<TD>"
 ws.TXBuffer += "Scan nearby BLE devices"

 ws.TXBuffer += "<tr><td height=30>"
 ws.addWideButton("i2cscanner", "I2C Scan", "")
 ws.TXBuffer += "<TD>"
 ws.TXBuffer += "Scan I2C devices"

 ws.TXBuffer += "</table></form>"

 ws.sendHeadandTail("TmplStd",ws._TAIL)
 httpResponse._write(ws.TXBuffer,strEncoding='UTF-8')
 ws.TXBuffer = ""
