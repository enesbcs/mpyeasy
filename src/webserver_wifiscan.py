import webserver_global as ws
import unet

def handle_wifiscan(httpResponse):
 ws.navMenuIndex=7
 ws.TXBuffer = ""
 httpResponse.WriteResponseOk(
        headers = ({'Cache-Control': 'no-cache'}),
        contentType = 'text/html',
        contentCharset = 'UTF-8',
        content = "" )
 ws.sendHeadandTail("TmplStd",ws._HEAD)

 try:
  sw2 = unet.wifi_sta.scan()
 except Exception as e:
  ws.TXBuffer += "<p>{0}".format(e)
  sw2 = []
 if sw2:
   ws.TXBuffer += "<table class='multirow'><TR><TH>SSID<TH>BSSID<TH>Security<TH>Channel<TH>Strength</TH></TR>"
   if len(sw2)>0:
    adata = []
    amac = ""
    security = ["open","WEP","WPA-PSK","WPA2-PSK","WPA/WPA2-PSK"]
    for w in range(len(sw2)):
      try:
       adata = sw2[w]
       amac = '{:02x}:{:02x}:{:02x}:{:02x}:{:02x}:{:02x}'.format(adata[1][0],adata[1][1],adata[1][2],adata[1][3],adata[1][4],adata[1][5])
       ws.TXBuffer += "<tr><td>{0}<td>{1}<td>{2}<td>{3}<td>{4}</tr>".format(adata[0].decode("utf-8"),amac,security[ adata[4] ],adata[2],adata[3])
      except:
       pass
   ws.TXBuffer += "</table>"
 else:
   ws.TXBuffer += "<p>No Access Points found"

 ws.sendHeadandTail("TmplStd",ws._TAIL)
 httpResponse._write(ws.TXBuffer,strEncoding='UTF-8')
 ws.TXBuffer = ""
