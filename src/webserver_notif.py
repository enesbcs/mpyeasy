import webserver_global as ws
import settings
import pglobals
import gc

def handle_notif(httpResponse,responsearr):
 edit = ws.arg("edit",responsearr)

 nindex = ws.arg("index",responsearr)
 nNotSet = (nindex == 0) or (nindex == '')
 if nindex!="":
  nindex = int(nindex) - 1
 enabled = (ws.arg("nenabled",responsearr)=="on")
 protocol = ws.arg("protocol",responsearr)
 if protocol!="":
  protocol=int(protocol)
 else:
  protocol=0

 if ((protocol == 0) and (edit=='') and (nindex!='')) or (ws.arg('del',responsearr) != ''):
   try:
    settings.Notifiers[nindex].plugin_exit()
   except:
    pass
   settings.Notifiers[nindex] = False
   nNotSet = True
   settings.savenotifiers()

 if (nNotSet==False): # submitted
  if (protocol > 0): # submitted
   try:
    if (settings.Notifiers[nindex]):
     settings.Notifiers[nindex].enabled = enabled
     settings.Notifiers[nindex].webform_save(responsearr)
     settings.savenotifiers()
   except:
    pass
  else:
   try:
    if (settings.Notifiers[nindex]):
     protocol = settings.Notifiers[nindex].number
   except:
    pass

 ws.TXBuffer = ""
 httpResponse.WriteResponseOk(
        headers = ({'Cache-Control': 'no-cache'}),
        contentType = 'text/html',
        contentCharset = 'UTF-8',
        content = "" )
 ws.navMenuIndex=6
 ws.sendHeadandTail("TmplStd",ws._HEAD)

 ws.TXBuffer += "<form name='frmselect' method='post'>"
 if (nNotSet): # show all in table
    ws.TXBuffer += "<table class='multirow' border=1px frame='box' rules='all'><TR><TH style='width:70px;'><TH style='width:50px;'>Nr<TH style='width:100px;'>Enabled<TH>Service<TH>ID"
    for x in range(pglobals.NOTIFICATION_MAX):
      ws.TXBuffer += "<tr><td><a class='button link' href=\"notifications?index={0}&edit=1\">Edit</a><td>{0}</td><td>".format(x+1)
      try:
       if (settings.Notifiers[x]):
        ws.addEnabled(settings.Notifiers[x].enabled)
        ws.TXBuffer += "</td><td>{0}</td><td>{1}".format(settings.Notifiers[x].getdevicename(),settings.Notifiers[x].getuniquename())
       else:
        ws.TXBuffer += "<td><td>"
      except:
       ws.TXBuffer += "<td><td>"
    ws.TXBuffer += "</table></form>"
 else: # edit
    ws.TXBuffer += "<table class='normal'><TR><TH style='width:150px;' align='left'>Notification Settings<TH><tr><td>Notification:<td>"
    ws.addSelector_Head("protocol", True)
    for x in range(len(pglobals.notifierselector)):
      ws.addSelector_Item(pglobals.notifierselector[x][2],int(pglobals.notifierselector[x][1]),(str(protocol) == str(pglobals.notifierselector[x][1])),False,"")
    ws.addSelector_Foot()
    if (int(protocol) > 0):
      createnewn = True
      try:
       if (settings.Notifiers[nindex].getnpluginid()==int(protocol)):
        createnewn = False
      except:
       pass
      exceptstr = ""
      if createnewn:
       for y in range(len(pglobals.notifierselector)):
        if int(pglobals.notifierselector[y][1]) == int(protocol):
         if len(settings.Notifiers)<=nindex:
          while len(settings.Notifiers)<=nindex:
           settings.Notifiers.append(False)
         try:
           m = __import__(pglobals.notifierselector[y][0])
         except Exception as e:
          settings.Notifiers[nindex] = False
          exceptstr += str(e)
          m = False
         if m:
          try:
           settings.Notifiers[nindex] = m.Plugin(nindex)
          except Exception as e:
           settings.Notifiers.append(m.Plugin(nindex))
           exceptstr += str(e)
         break
      if settings.Notifiers[nindex] == False:
       ws.TXBuffer += "Importing failed: {0}</td></tr></table>".format(exceptstr)
       ws.sendHeadandTail("TmplStd",ws._TAIL)
       httpResponse._write(ws.TXBuffer,strEncoding='UTF-8')
       ws.TXBuffer = ""
       return
      else:
       try:
        settings.Notifiers[nindex].plugin_init() # call plugin init
       except:
        pass
    if nindex != '':
     ws.TXBuffer += "<input type='hidden' name='index' value='{0}'>".format(nindex+1)
     if int(protocol)>0:
      ws.addFormCheckBox("Enabled", "nenabled", settings.Notifiers[nindex].enabled)
      settings.Notifiers[nindex].webform_load()
      if (ws.arg('test',responsearr) != ''):
       settings.Notifiers[nindex].notify("Test message")
    ws.addFormSeparator(2)
    ws.TXBuffer += "<tr><td><td><a class='button link' href=\"notifications\">Close</a>"
    ws.addSubmitButton()
    if nindex != '':
     ws.addSubmitButton("Delete", "del")
     ws.addSubmitButton("Test", "test")
    ws.TXBuffer += "</table></form>"

 ws.sendHeadandTail("TmplStd",ws._TAIL)
 httpResponse._write(ws.TXBuffer,strEncoding='UTF-8')
 ws.TXBuffer = ""
