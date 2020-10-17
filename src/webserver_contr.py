import webserver_global as ws
import settings
import pglobals
import gc

def handle_controllers(httpResponse,responsearr):
 edit = ws.arg("edit",responsearr)
 controllerindex = ws.arg("index",responsearr)
 controllerNotSet = (controllerindex == 0) or (controllerindex == '')
 if controllerindex!="":
  controllerindex = int(controllerindex) - 1
 controllerip = ws.arg("controllerip",responsearr)
 controllerport = ws.arg("controllerport",responsearr)
 protocol = ws.arg("protocol",responsearr)
 if protocol!="":
  protocol=int(protocol)
 else:
  protocol=0
 controlleruser = ws.arg("controlleruser",responsearr)
 controllerpassword = ws.arg("controllerpassword",responsearr)
 enabled = (ws.arg("controllerenabled",responsearr)=="on")

 if ((protocol == 0) and (edit=='') and (controllerindex!='')) or (ws.arg('del',responsearr) != ''):
   try:
    settings.Controllers[controllerindex].controller_exit()
   except:
    pass
   settings.Controllers[controllerindex] = False
   controllerNotSet = True
   settings.savecontrollers()

 if (controllerNotSet==False): # submitted
  if (protocol > 0): # submitted
   try:
    if (settings.Controllers[controllerindex]):
     settings.Controllers[controllerindex].controllerip = controllerip
     settings.Controllers[controllerindex].controllerport = controllerport
     settings.Controllers[controllerindex].controlleruser = controlleruser
     if "**" not in controllerpassword:
      settings.Controllers[controllerindex].controllerpassword = controllerpassword
     settings.Controllers[controllerindex].enabled = enabled
     settings.Controllers[controllerindex].webform_save(responsearr)
     settings.savecontrollers()
   except:
    pass
  else:
   try:
    if (settings.Controllers[controllerindex]):
     protocol = settings.Controllers[controllerindex].controllerid
   except:
    pass
 ws.TXBuffer = ""
 httpResponse.WriteResponseOk(
        headers = ({'Cache-Control': 'no-cache'}),
        contentType = 'text/html',
        contentCharset = 'UTF-8',
        content = "" ) 
 ws.navMenuIndex=2
 ws.sendHeadandTail("TmplStd",ws._HEAD)

 ws.TXBuffer += "<form name='frmselect' method='post'>"
 if (controllerNotSet): # show all in table
    ws.TXBuffer += "<table class='multirow' border=1px frame='box' rules='all'><TR><TH style='width:70px;'>"
    ws.TXBuffer += "<TH style='width:50px;'>Nr<TH style='width:100px;'>Enabled<TH>Protocol<TH>Host<TH>Port"
    for x in range(pglobals.CONTROLLER_MAX):
      ws.TXBuffer += "<tr><td><a class='button link' href=\"controllers?index="
      ws.TXBuffer += str(x + 1)
      ws.TXBuffer += "&edit=1\">Edit</a><td>"
      ws.TXBuffer += ws.getControllerSymbol(x)
      ws.TXBuffer += "</td><td>"
      try:
       if (settings.Controllers[x]):
        ws.addEnabled(settings.Controllers[x].enabled)
        ws.TXBuffer += "</td><td>"
        ws.TXBuffer += str(settings.Controllers[x].getcontrollername())
        ws.TXBuffer += "</td><td>"
        ws.TXBuffer += str(settings.Controllers[x].controllerip)
        ws.TXBuffer += "</td><td>"
        ws.TXBuffer += str(settings.Controllers[x].controllerport)
       else:
        ws.TXBuffer += "<td><td><td>"
      except:
       ws.TXBuffer += "<td><td><td>"
      httpResponse._write(ws.TXBuffer,strEncoding='UTF-8')
      ws.TXBuffer = ""
    ws.TXBuffer += "</table></form>"
    httpResponse._write(ws.TXBuffer,strEncoding='UTF-8')
    ws.TXBuffer = ""
 else: # edit
    ws.TXBuffer += "<table class='normal'><TR><TH style='width:150px;' align='left'>Controller Settings<TH>"
    ws.TXBuffer += "<tr><td>Protocol:<td>"
    ws.addSelector_Head("protocol", True)
    for x in range(len(pglobals.controllerselector)):
      ws.addSelector_Item(pglobals.controllerselector[x][2],int(pglobals.controllerselector[x][1]),(str(protocol) == str(pglobals.controllerselector[x][1])),False,"")
    ws.addSelector_Foot()
    httpResponse._write(ws.TXBuffer,strEncoding='UTF-8')
    ws.TXBuffer = ""    
#    print(protocol)#debug
    if (int(protocol) > 0):
      createnewcontroller = True
      try:
       if (settings.Controllers[controllerindex].getcontrollerid()==int(protocol)):
        createnewcontroller = False
      except:
       pass
      exceptstr = ""
      if createnewcontroller:
       for y in range(len(pglobals.controllerselector)):
        if int(pglobals.controllerselector[y][1]) == int(protocol):
         if len(settings.Controllers)<=controllerindex:
          while len(settings.Controllers)<=controllerindex:
           settings.Controllers.append(False)
         try:
           m = __import__(pglobals.controllerselector[y][0])
         except Exception as e:
#          print(str(e))
          settings.Controllers[controllerindex] = False
          exceptstr += str(e)
          m = False
         gc.collect()
         if m:
          try: 
           settings.Controllers[controllerindex] = m.Controller(controllerindex)
          except Exception as e:
           settings.Controllers.append(m.Controller(controllerindex))
           exceptstr += str(e)
         break
      if settings.Controllers[controllerindex] == False:
       ws.TXBuffer += "Importing failed: {0}</td></tr></table>".format(exceptstr)
       ws.sendHeadandTail("TmplStd",ws._TAIL)
       httpResponse._write(ws.TXBuffer,strEncoding='UTF-8')
       ws.TXBuffer = ""
       return True
      else:
       try:
        settings.Controllers[controllerindex].controller_init() # call plugin init
        if (settings.Controllers[controllerindex]):
          if (settings.Controllers[controllerindex].enabled): 
           settings.Controllers[controllerindex].setonmsgcallback(settings.callback_from_controllers)
        for x in range(0,len(settings.Tasks)):
         if (settings.Tasks[x] and type(Settings.Tasks[x]) is not bool): # device exists
          if (settings.Tasks[x].enabled): # device enabled
            if (settings.Tasks[x].senddataenabled[controllerindex]):
             if (settings.Controllers[controllerindex]):
              if (settings.Controllers[controllerindex].enabled):
               settings.Tasks[x].controllercb[controllerindex] = settings.Controllers[controllerindex].senddata
       except:
        pass 
    if controllerindex != '':
     ws.TXBuffer += "<input type='hidden' name='index' value='" + str(controllerindex+1) +"'>"
     if int(protocol)>0:
      ws.addFormCheckBox("Enabled", "controllerenabled", settings.Controllers[controllerindex].enabled)
      ws.addFormTextBox("Controller Host Address", "controllerip", settings.Controllers[controllerindex].controllerip, 96)
      ws.addFormNumericBox("Controller Port", "controllerport", settings.Controllers[controllerindex].controllerport, 1, 65535)
      if settings.Controllers[controllerindex].usesAccount:
       ws.addFormTextBox("Controller User", "controlleruser", settings.Controllers[controllerindex].controlleruser,96)
      if settings.Controllers[controllerindex].usesPassword:
       ws.addFormPasswordBox("Controller Password", "controllerpassword", settings.Controllers[controllerindex].controllerpassword,96)
#      try:
      settings.Controllers[controllerindex].webform_load()
#      except:
#       pass

    ws.addFormSeparator(2)
    ws.TXBuffer += "<tr><td><td>"
    ws.TXBuffer += "<a class='button link' href=\"controllers\">Close</a>"
    ws.addSubmitButton()
    if controllerindex != '':
     ws.addSubmitButton("Delete", "del")
    ws.TXBuffer += "</table></form>"

 ws.sendHeadandTail("TmplStd",ws._TAIL)
 httpResponse._write(ws.TXBuffer,strEncoding='UTF-8')
 ws.TXBuffer = ""
