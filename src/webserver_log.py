import webserver_global as ws
import misc

def handle_log(httpResponse):
 ws.navMenuIndex=7
 ws.TXBuffer = ""
 httpResponse.WriteResponseOk(
        headers = ({'Cache-Control': 'no-cache'}),
        contentType = 'text/html',
        contentCharset = 'UTF-8',
        content = "" )
 ws.sendHeadandTail("TmplStd",ws._HEAD)

 ws.TXBuffer += "<table class=\"normal\"><TR><TH id=\"headline\" align=\"left\">Log"
 ws.addCopyButton("copyText", "", "Copy log to clipboard")
 ws.TXBuffer += "</TR></table><div id='current_loglevel' style='font-weight: bold;'>Logging: </div><div class='logviewer' id='copyText_1'>"
 for l in misc.SystemLog:
  ws.TXBuffer += '<div class="level_{0}"><font color="gray">{1}</font> {2}</div>'.format(l["lvl"],l["t"],l["l"])

 ws.TXBuffer += "</div><BR>"
 ws.TXBuffer += '<script type="text/javascript">var rtimer; function refreshpage() {window.location.reload(true);}'
 ws.TXBuffer += "function checkit(){ if (document.getElementById('autoscroll').checked) {rtimer = setInterval(refreshpage,20000);} else {clearInterval(rtimer);}}</script>"
 ws.TXBuffer += "Autoscroll: <label class='container'>&nbsp;<input type='checkbox' id='autoscroll' name='autoscroll' checked onclick='checkit();'><span class='checkmark'></span></label>"
 ws.TXBuffer += "<script defer>checkit();copyText_1.scrollTop = 99999;</script>"

 ws.sendHeadandTail("TmplStd",ws._TAIL)
 httpResponse._write(ws.TXBuffer,strEncoding='UTF-8')
 ws.TXBuffer = ""
