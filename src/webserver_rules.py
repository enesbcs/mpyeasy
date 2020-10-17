import webserver_global as ws
import pglobals
import commands

def handle_rules(httpResponse,responsearr):
 ws.navMenuIndex=5
 ws.TXBuffer = ""
 httpResponse.WriteResponseOk(
        headers = ({'Cache-Control': 'no-cache'}),
        contentType = 'text/html',
        contentCharset = 'UTF-8',
        content = "" )
 ws.sendHeadandTail("TmplStd",ws._HEAD)

 rules = ""
 saved = ws.arg("Submit",responsearr)
 if (saved):
  rules = ws.arg("rules",responsearr)
  try:
     with open(pglobals.FILE_RULES,'w') as f:
      f.write(rules)
  except:
     pass
  if len(rules)>0:
    commands.splitruletoevents(rules)
 if rules=="":
    try:
     with open(pglobals.FILE_RULES,'r') as f:
      rules = f.read()
    except:
     pass
 httpResponse._write(ws.TXBuffer,strEncoding='UTF-8')
 ws.TXBuffer = "<form name = 'frmselect' method = 'post'><table class='normal'><TR><TH align='left'>Rules<tr><td><textarea name='rules' rows='30' wrap='off'>{0}</textarea>".format(rules)
 ws.addFormSeparator(2)
 ws.addSubmitButton()
 ws.TXBuffer += "</table></form>"

 ws.sendHeadandTail("TmplStd",ws._TAIL)
 httpResponse._write(ws.TXBuffer,strEncoding='UTF-8')
 ws.TXBuffer = ""
