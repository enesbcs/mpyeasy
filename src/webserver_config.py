import webserver_global as ws
import settings

def handle_config(httpResponse,responsearr):
 ws.navMenuIndex=1

 saved = ws.arg("Submit",responsearr)
 if (saved):
  settings.Settings["Name"] = ws.arg("name",responsearr).replace(" ","")
  settings.Settings["Unit"] = ws.arg("unit",responsearr)
  tpw = ws.arg("password",responsearr)
  if "**" not in tpw:
   settings.Settings["Password"]  = tpw
  tpw = ws.arg("apkey",responsearr)
  if "**" not in tpw:
   settings.Settings['APKEY'] = tpw
  settings.Settings['APSSID'] = ws.arg("apssid",responsearr)
  settings.Settings['AP1SSID'] = ws.arg("ssid",responsearr)
  settings.Settings['AP2SSID'] = ws.arg("ssid2",responsearr)
  tpw = ws.arg("apkey",responsearr)
  if "**" not in tpw:
    settings.Settings["APKEY"] = tpw
  tpw = ws.arg("key",responsearr)
  if "**" not in tpw:
    settings.Settings["AP1KEY"] = tpw
  tpw = ws.arg("key2",responsearr)
  if "**" not in tpw:
    settings.Settings["AP2KEY"] = tpw
  settings.Settings['WifiClient'] = (ws.arg("wifista",responsearr)=="on")
  settings.Settings['WifiAP'] = int(ws.arg("apmode",responsearr))
  settings.Settings['APCAPTIVE'] = (ws.arg("ap_captive",responsearr)=="on")  
  settings.Settings['WDHCP'] = (ws.arg("w_dhcp",responsearr)=="on")
  if settings.Settings['WDHCP']==False:
   settings.Settings['WIP'] = ws.arg("w_ip",responsearr)
   settings.Settings['WMask'] = ws.arg("w_mask",responsearr)
   settings.Settings['WGW'] = ws.arg("w_gw",responsearr)
   settings.Settings['WDNS'] = ws.arg("w_dns",responsearr)
  settings.Settings['LANIF'] = (ws.arg("lanif",responsearr)=="on")
  if settings.Settings['LANIF']:
   settings.Settings['LDHCP'] = (ws.arg("l_dhcp",responsearr)=="on")
   if settings.Settings['LDHCP']==False:
    settings.Settings['LIP'] = ws.arg("l_ip",responsearr)
    settings.Settings['LMask'] = ws.arg("l_mask",responsearr)
    settings.Settings['LGW'] = ws.arg("l_gw",responsearr)
    settings.Settings['LDNS'] = ws.arg("l_dns",responsearr)

  settings.savesettings()
 else:
  settings.loadsettings()
 ws.TXBuffer = ""
 httpResponse.WriteResponseOk(
        headers = ({'Cache-Control': 'no-cache'}),
        contentType = 'text/html',
        contentCharset = 'UTF-8',
        content = "" )
 ws.sendHeadandTail("TmplStd",ws._HEAD)

 ws.TXBuffer += "<form name='frmselect' method='post'><table class='normal'>"
 ws.addFormHeader("Main Settings")
 ws.addFormTextBox( "Unit Name", "name", settings.Settings["Name"], 25)
 ws.addFormNumericBox( "Unit Number", "unit", settings.Settings["Unit"], 0, 256)
 ws.addFormPasswordBox( "Admin Password" , "password", settings.Settings["Password"], 25)
 ws.addFormSeparator(2)
 httpResponse._write(ws.TXBuffer,strEncoding='UTF-8')
 ws.TXBuffer = ""
 ws.addFormSubHeader("Wifi STA Settings")
 ws.addFormCheckBox("Enable Wifi STA mode","wifista", settings.Settings["WifiClient"])
 ws.addFormTextBox("SSID", "ssid", settings.Settings["AP1SSID"], 32)
 ws.addFormPasswordBox("Wifi Key", "key", settings.Settings["AP1KEY"], 64)
 ws.addFormTextBox("Fallback SSID", "ssid2", settings.Settings["AP2SSID"], 32)
 ws.addFormPasswordBox( "Fallback Wifi Key", "key2", settings.Settings["AP2KEY"], 64)
 ws.addFormCheckBox("DHCP","w_dhcp",settings.Settings["WDHCP"])
 ws.addFormNote("If DHCP enabled the settings below will not be saved or used!")
 ws.addFormTextBox("IP", "w_ip", settings.Settings["WIP"],15)
 ws.addFormTextBox("Mask", "w_mask",settings.Settings["WMask"],15)
 ws.addFormTextBox("GW", "w_gw", settings.Settings["WGW"],15)
 ws.addFormTextBox("DNS", "w_dns", settings.Settings["WDNS"],128)
 ws.addFormSubHeader("Wifi AP Settings")
 options = ["Disable","At startup always","When Wifi STA not connected","When LAN not connected"]
 optionvalues = [0,1,2,4]
 ws.addFormSelector("Start AP when","apmode",len(optionvalues),options,optionvalues,None,int(settings.Settings["WifiAP"]))
 ws.addFormTextBox("SSID", "apssid", settings.Settings["APSSID"], 32)
 ws.addFormPasswordBox("Wifi Key", "apkey", settings.Settings["APKEY"], 64)
 try:
   tpw = settings.Settings["APCAPTIVE"]
 except:
   tpw = False
 ws.addFormCheckBox("Captive AP","ap_captive",tpw)
 httpResponse._write(ws.TXBuffer,strEncoding='UTF-8')
 ws.TXBuffer = ""
 if int(settings.HW["lan-phy"])>-1:
  ws.addFormSubHeader("LAN Settings")
  ws.addFormCheckBox("Enable LAN","lanif", settings.Settings["LANIF"])
  ws.addFormCheckBox("DHCP","l_dhcp",settings.Settings["LDHCP"])
  ws.addFormNote("If DHCP enabled the settings below will not be saved or used!")
  ws.addFormTextBox("IP", "l_ip", settings.Settings["LIP"],15)
  ws.addFormTextBox("Mask", "l_mask",settings.Settings["LMask"],15)
  ws.addFormTextBox("GW", "l_gw", settings.Settings["LGW"],15)
  ws.addFormTextBox("DNS", "l_dns", settings.Settings["LDNS"],128)

 ws.TXBuffer += "<TR><TD style='width:150px;' align='left'><TD>"
 ws.addSubmitButton()
 ws.TXBuffer += "</table></form>"

 ws.sendHeadandTail("TmplStd",ws._TAIL)
 httpResponse._write(ws.TXBuffer,strEncoding='UTF-8')
 ws.TXBuffer = ""
