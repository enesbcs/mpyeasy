import webserver_global as ws
import commands

def handle_sysvars(httpResponse):
 ws.navMenuIndex=7
 ws.TXBuffer = ""
 httpResponse.WriteResponseOk(
        headers = ({'Cache-Control': 'no-cache'}),
        contentType = 'text/html',
        contentCharset = 'UTF-8',
        content = "" ) 
 ws.sendHeadandTail("TmplStd",ws._HEAD)
 ws.TXBuffer += "<table class='normal'><TR><TH align='left'>System Variables<TH align='left'>Normal"
 for sv in commands.SysVars:
  ws.TXBuffer += "<TR><TD>%" + sv + "%</TD><TD>"
  ws.TXBuffer += str(commands.getglobalvar(sv)) + "</TD></TR>"
  httpResponse._write(ws.TXBuffer,strEncoding='UTF-8')
  ws.TXBuffer = ""
 ws.TXBuffer += "</table></form>"
 ws.sendHeadandTail("TmplStd",ws._TAIL)
 httpResponse._write(ws.TXBuffer,strEncoding='UTF-8')
 ws.TXBuffer = ""
