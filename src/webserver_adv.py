import webserver_global as ws
import settings

def handle_adv(httpResponse,responsearr):
 ws.navMenuIndex=7
 ws.TXBuffer = ""
 httpResponse.WriteResponseOk(
        headers = ({'Cache-Control': 'no-cache'}),
        contentType = 'text/html',
        contentCharset = 'UTF-8',
        content = "" )

 saved = ws.arg("Submit",responsearr)
 if (saved):
   settings.AdvSettings["webloglevel"]  = int(ws.arg("webloglevel",responsearr))
   settings.AdvSettings["consoleloglevel"]  = int(ws.arg("consoleloglevel",responsearr))
   settings.AdvSettings["usentp"]  = (ws.arg("usentp",responsearr) == "on")
   settings.AdvSettings["ntpserver"]  = ws.arg("ntpserver",responsearr)
   settings.AdvSettings["timezone"]  = int(ws.arg("timezone",responsearr))
   try:
    settings.AdvSettings["rtci2c"] = int(ws.arg("rtci2c",responsearr))
    if settings.AdvSettings["rtci2c"]>=0:
     settings.AdvSettings["extrtc"] = int(ws.arg("extrtc",responsearr))
   except:
    pass
   settings.saveadvsettings()

 ws.sendHeadandTail("TmplStd",ws._HEAD)

 ws.TXBuffer += "<form  method='post'><table class='normal'>"
 ws.addFormHeader("Advanced Settings")
 ws.addFormSubHeader("Log Settings")
 httpResponse._write(ws.TXBuffer,strEncoding='UTF-8')
 ws.TXBuffer = ""
 ws.addFormLogLevelSelect("Console log Level","consoleloglevel", settings.AdvSettings["consoleloglevel"])
 ws.addFormLogLevelSelect("Web log Level",    "webloglevel",     settings.AdvSettings["webloglevel"])
 ws.addFormSubHeader("Time Settings")
 ws.addFormCheckBox("Enable NTP","usentp",settings.AdvSettings["usentp"])
 ws.addFormTextBox( "NTP server name", "ntpserver", settings.AdvSettings["ntpserver"], 100)
 ws.addFormNumericBox("Timezone offset", "timezone", settings.AdvSettings["timezone"], -720, 840)
 ws.addUnit("min")
 try:
  extrtc = settings.AdvSettings["extrtc"]
 except:
  settings.AdvSettings["extrtc"] = 0
  extrtc = 0
 options = ["Disable","DS1307","DS3231","PCF8523"]
 optionvalues = [0,1307,3231,8523]
 ws.addFormSelector("External RTC type","extrtc",len(optionvalues),options,optionvalues,None,extrtc)
 try:
    import inc.libhw as libhw
    options = libhw.geti2clist()
 except:
    options = []
 try:
  rtci2c = settings.AdvSettings["rtci2c"]
 except:
  settings.AdvSettings["rtci2c"] = 0
  rtci2c = 0
 ws.addHtml("<tr><td>RTC I2C line:<td>")
 ws.addSelector_Head("rtci2c",True)
 for d in range(len(options)):
    ws.addSelector_Item("I2C"+str(options[d]),options[d],(rtci2c==options[d]),False)
 ws.addSelector_Foot()

 ws.addFormSeparator(2)
 ws.TXBuffer += "<TR><TD style='width:150px;' align='left'><TD>"
 ws.addSubmitButton()
 ws.TXBuffer += "<input type='hidden' name='edit' value='1'>"
 ws.TXBuffer += "</table></form>"

 ws.sendHeadandTail("TmplStd",ws._TAIL)
 httpResponse._write(ws.TXBuffer,strEncoding='UTF-8')
 ws.TXBuffer = ""
