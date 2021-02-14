import webserver_global as ws
import commands
import gc

def handle_command(httpResponse,responsearr):
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
   responsestr = str(commands.doExecuteCommand(cmdline))
 except:
  pass

 if len(responsestr)>0:
   ws.TXBuffer += "<P>{0}<p>".format(responsestr)
 if responsestr == False:
  ws.TXBuffer += "FAILED"
 ws.sendHeadandTail("TmplStd",ws._TAIL)
 httpResponse._write(ws.TXBuffer,strEncoding='UTF-8')
 ws.TXBuffer = ""
