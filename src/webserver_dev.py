import webserver_global as ws
import pglobals
import gc
import esp_os # debug
import settings
import misc

def handle_devices(httpResponse,responsearr):
 ws.navMenuIndex=4
 ws.TXBuffer = ""
 httpResponse.WriteResponseOk(
        headers = ({'Cache-Control': 'no-cache'}),
        contentType = 'text/html',
        contentCharset = 'UTF-8',
        content = "" )

 taskdevicenumber = ws.arg('TDNUM',responsearr)
 if taskdevicenumber=='':
  taskdevicenumber=0
 else:
  taskdevicenumber=int(float(taskdevicenumber))

 taskdevicetimer = ws.arg('TDT',responsearr)
 if taskdevicetimer=='':
  taskdevicetimer=0
 else:
  taskdevicetimer=float(taskdevicetimer)

 edit = ws.arg("edit",responsearr)
 page = ws.arg("page",responsearr)
 setpage = ws.arg("setpage",responsearr)
 taskIndex = ws.arg("index",responsearr)
 runIndex = ws.arg("run",responsearr)

 if page=='':
  page=0
 else:
  page=int(float(page))
 if page==0:
  page = 1
 if setpage=='':
  setpage=0
 else:
  setpage=int(float(setpage))
 if (setpage>0):
  if setpage <= (pglobals.TASKS_MAX / ws.TASKS_PER_PAGE):
   page = setpage
  else:
   page = int(pglobals.TASKS_MAX / ws.TASKS_PER_PAGE)

 ws.sendHeadandTail("TmplStd",ws._HEAD)
 taskIndexNotSet = (taskIndex == 0) or (taskIndex == '')

 if taskIndex!="":
  taskIndex = int(taskIndex) - 1
 if ws.arg('del',responsearr) != '':
  taskdevicenumber=0
  ttid = -1
  try:
    ttid = settings.Tasks[taskIndex].pluginid
  except:
    ttid = -1

  if ttid != -1:
   try:
    settings.Tasks[taskIndex].plugin_exit()
    taskIndexNotSet = True
    settings.Tasks[taskIndex] = False
    settings.savetasks() # savetasksettings!!!
   except Exception as e:
    misc.addLog(pglobals.LOG_LEVEL_ERROR, "Deleting failed: "+str(e))

 if runIndex != "":
  if len(settings.Tasks)<1:
   return False
  try:
   s = int(runIndex)
  except:
   s = -1
  try:
   if s >0 and (s<=len(settings.Tasks)):
    s = s-1 # array is 0 based, tasks is 1 based
    if (type(settings.Tasks[s])!=bool) and (settings.Tasks[s]):
     if (settings.Tasks[s].enabled):
      settings.Tasks[s].plugin_read()
  except Exception as e:
    print(e)
 httpResponse._write(ws.TXBuffer,strEncoding='UTF-8')
 ws.TXBuffer = ""

 if taskIndexNotSet==False: #Show edit form if a specific entry is chosen with the edit button

    ws.TXBuffer += "<form name='frmselect' method='post'><table class='normal'>"
    ws.addFormHeader("Task Settings")
    ws.TXBuffer += "<TR><TD style='width:150px;' align='left'>Device:<TD>"
    tte = taskdevicenumber
    try:
      tte = settings.Tasks[taskIndex].pluginid
    except:
      pass
    if (tte<=0):
      ws.addSelector_Head("TDNUM",True)
      for y in range(0,len(pglobals.deviceselector)):
       pname = pglobals.deviceselector[y][2]
       try:
        if int(pglobals.deviceselector[y][1]) != 0:
         pname = "P"+str(int(pglobals.deviceselector[y][1])).rjust(3,"0")+" - "+ pglobals.deviceselector[y][2]
       except:
        pass
       ws.addSelector_Item(pname,int(pglobals.deviceselector[y][1]),(pglobals.deviceselector[y][1]==tte),False,"")
      ws.addSelector_Foot()
      httpResponse._write(ws.TXBuffer,strEncoding='UTF-8')
      ws.TXBuffer = ""
    else: # device selected
      createnewdevice = True
      try:
       if (settings.Tasks[taskIndex].getpluginid()==int(tte)):
        createnewdevice = False
      except:
       pass
      exceptstr = ""
      gc.collect()      
      if createnewdevice:
       for y in range(len(pglobals.deviceselector)):
        if int(pglobals.deviceselector[y][1]) == int(tte):
         if len(settings.Tasks)<=taskIndex:
          while len(settings.Tasks)<=taskIndex:
           settings.Tasks.append(False)
         try:
           m = __import__(pglobals.deviceselector[y][0])
         except Exception as e:
          settings.Tasks[taskIndex] = False
          exceptstr += str(e)
          m = False
         if m:
          try:
           settings.Tasks[taskIndex] = m.Plugin(taskIndex)
          except Exception as e:
           settings.Tasks.append(m.Plugin(taskIndex))
           exceptstr += str(e)
         break
      if settings.Tasks[taskIndex] == False:
       ws.TXBuffer += "Importing failed: {0}</td></tr></table>".format(exceptstr)
       ws.sendHeadandTail("TmplStd",ws._TAIL)
       httpResponse._write(ws.TXBuffer,strEncoding='UTF-8')
       ws.TXBuffer = ""
       return True
      else:
       try:
        enableit = (ws.arg("TDE",responsearr) == "on")
#        print("plugin init",enableit)
        if enableit:
         settings.Tasks[taskIndex].plugin_init(True) # call plugin init / (ws.arg("TDE",responsearr) == "on")
        else:
         settings.Tasks[taskIndex].plugin_init() # call plugin init / (ws.arg("TDE",responsearr) == "on")
       except:
        pass
    
      if edit != '' and not(taskIndexNotSet): # when form submitted
       if taskdevicenumber != 0: # save settings
        if taskdevicetimer > 0:
         settings.Tasks[taskIndex].interval = taskdevicetimer
        else:
         if not(settings.Tasks[taskIndex].timeroptional): # set default delay
          settings.Tasks[taskIndex].interval = settings.Settings["Delay"]
         else:
          settings.Tasks[taskIndex].interval = 0
       tasknamestr = str(ws.arg("TDN",responsearr)).strip()
       settings.Tasks[taskIndex].taskname = tasknamestr.replace(" ","")
       if tasknamestr:
        settings.Tasks[taskIndex].taskdeviceport = ws.arg("TDP",responsearr)
        maxcon = len(settings.Controllers)
        if maxcon>pglobals.CONTROLLER_MAX:
         maxcon = pglobals.CONTROLLER_MAX
        for controllerNr in range(0, maxcon):
          if ((settings.Controllers[controllerNr]) and (settings.Controllers[controllerNr].enabled)):
            sid = "TDSD"
            sid += str(controllerNr + 1)
            settings.Tasks[taskIndex].senddataenabled[controllerNr] = (ws.arg(sid,responsearr) == "on")
            if (settings.Tasks[taskIndex].senddataenabled[controllerNr]):
              if (settings.Controllers[controllerNr]):
               if (settings.Controllers[controllerNr].enabled):
                settings.Tasks[taskIndex].controllercb[controllerNr] = settings.Controllers[controllerNr].senddata
            if (settings.Tasks[taskIndex].senddataenabled[controllerNr]):
             sid = "TDID"
             sid += str(controllerNr + 1)
             ctrlidx = str(ws.arg(sid,responsearr)).strip()
             if ctrlidx=="":
              ctrlidx = -1
             else:
              ctrlidx = int(ctrlidx)
             settings.Tasks[taskIndex].controlleridx[controllerNr] = ctrlidx

        for pins in range(0,4):
         pinnum = ws.arg("taskdevicepin"+str(pins+1),responsearr)
         if pinnum:
          settings.Tasks[taskIndex].taskdevicepin[pins]=int(pinnum)
#        if settings.Tasks[taskIndex].pullupoption:
#         settings.Tasks[taskIndex].pullup = (ws.arg("TDPPU",responsearr) == "on")
        if settings.Tasks[taskIndex].inverselogicoption:
         settings.Tasks[taskIndex].pininversed = (ws.arg("TDPI",responsearr) == "on")
        
        for varnr in range(0,settings.Tasks[taskIndex].valuecount):
         tvname = str(ws.arg("TDVN"+str(varnr+1),responsearr))
         if tvname:
          settings.Tasks[taskIndex].valuenames[varnr] = tvname.replace(" ","")
          settings.Tasks[taskIndex].formula[varnr] = ws.arg("TDF"+str(varnr+1),responsearr)
          tvdec = ws.arg("TDVD"+str(varnr+1),responsearr)
          if tvdec == "" or tvdec == False or tvdec == None:
           tvdec = 0
          settings.Tasks[taskIndex].decimals[varnr] = tvdec
         else:
          settings.Tasks[taskIndex].valuenames[varnr] = ""
        
        settings.Tasks[taskIndex].webform_save(responsearr) # call plugin read FORM
        settings.Tasks[taskIndex].enabled = (ws.arg("TDE",responsearr) == "on")
        
        try:
         settings.Tasks[taskIndex].i2c = int(ws.arg("i2c",responsearr))
        except:
         settings.Tasks[taskIndex].i2c = -1
        if settings.Tasks[taskIndex].taskname=="":
         settings.Tasks[taskIndex].enabled = False              
        settings.savetasks() # savetasksettings!!!

      ws.TXBuffer += "<input type='hidden' name='TDNUM' value='{0}'>{1}".format(settings.Tasks[taskIndex].pluginid,settings.Tasks[taskIndex].getdevicename())

      ws.addFormTextBox( "Name", "TDN", str(settings.Tasks[taskIndex].gettaskname()), 40)
      ws.addFormCheckBox("Enabled", "TDE", settings.Tasks[taskIndex].enabled)
      # section: Sensor / Actuator
      httpResponse._write(ws.TXBuffer,strEncoding='UTF-8')
      ws.TXBuffer = ""
      if (settings.Tasks[taskIndex].dtype>=pglobals.DEVICE_TYPE_SINGLE and settings.Tasks[taskIndex].dtype<= pglobals.DEVICE_TYPE_QUAD):
        ws.addFormSubHeader( "Sensor" if settings.Tasks[taskIndex].senddataoption else "Actuator" )

#        if (Settings.Tasks[taskIndex].ports != 0):
#          addFormNumericBox("Port", "TDP", Settings.Tasks[taskIndex].taskdeviceport)
#        if (settings.Tasks[taskIndex].pullupoption):
#          ws.addFormCheckBox("Internal PullUp", "TDPPU", settings.Tasks[taskIndex].pullup)
        if (settings.Tasks[taskIndex].inverselogicoption):
          ws.addFormCheckBox("Inversed Logic", "TDPI", settings.Tasks[taskIndex].pininversed)
        if (settings.Tasks[taskIndex].dtype>=pglobals.DEVICE_TYPE_SINGLE and settings.Tasks[taskIndex].dtype<=pglobals.DEVICE_TYPE_QUAD):
          ws.addFormPinSelect("1st GPIO", "taskdevicepin1", settings.Tasks[taskIndex].taskdevicepin[0],settings.Tasks[taskIndex].pinfilter[0])
        if (settings.Tasks[taskIndex].dtype>=pglobals.DEVICE_TYPE_DUAL and settings.Tasks[taskIndex].dtype<=pglobals.DEVICE_TYPE_QUAD):
          ws.addFormPinSelect("2nd GPIO", "taskdevicepin2",settings.Tasks[taskIndex].taskdevicepin[1],settings.Tasks[taskIndex].pinfilter[1])
        if (settings.Tasks[taskIndex].dtype>=pglobals.DEVICE_TYPE_TRIPLE and settings.Tasks[taskIndex].dtype<=pglobals.DEVICE_TYPE_QUAD):
          ws.addFormPinSelect("3rd GPIO", "taskdevicepin3", settings.Tasks[taskIndex].taskdevicepin[2],settings.Tasks[taskIndex].pinfilter[2])
        if (settings.Tasks[taskIndex].dtype==pglobals.DEVICE_TYPE_QUAD):
          ws.addFormPinSelect("4th GPIO", "taskdevicepin4", settings.Tasks[taskIndex].taskdevicepin[3],settings.Tasks[taskIndex].pinfilter[3])
      if (settings.Tasks[taskIndex].dtype==pglobals.DEVICE_TYPE_I2C):
          try:
           import inc.libhw as libhw
           options = libhw.geti2clist()
          except:
           options = []
          ws.addHtml("<tr><td>I2C line:<td>")
          ws.addSelector_Head("i2c",True)
          for d in range(len(options)):
           ws.addSelector_Item("I2C"+str(options[d]),options[d],(settings.Tasks[taskIndex].i2c==options[d]),False)
          ws.addSelector_Foot()

      httpResponse._write(ws.TXBuffer,strEncoding='UTF-8')
      ws.TXBuffer = ""
      try:
       settings.Tasks[taskIndex].webform_load() # call plugin function to fill ws.TXBuffer
      except Exception as e:
       print(e)
      httpResponse._write(ws.TXBuffer,strEncoding='UTF-8')
      ws.TXBuffer = ""

      if (settings.Tasks[taskIndex].senddataoption): # section: Data Acquisition
        ws.addFormSubHeader("Data Acquisition")
        maxcon = len(settings.Controllers)
        if maxcon>pglobals.CONTROLLER_MAX:
         maxcon = pglobals.CONTROLLER_MAX
        for controllerNr in range(0, maxcon):
          if ((settings.Controllers[controllerNr]) and (settings.Controllers[controllerNr].enabled)):
            sid = "TDSD"
            sid += str(controllerNr + 1)

            ws.TXBuffer += "<TR><TD>Send to Controller {0}<TD>".format(ws.getControllerSymbol(controllerNr))
            ws.addCheckBox(sid, settings.Tasks[taskIndex].senddataenabled[controllerNr])

            sid = "TDID"
            sid += str(controllerNr + 1)

            if (settings.Controllers[controllerNr].enabled) and settings.Tasks[taskIndex].senddataenabled[controllerNr]:
             if (settings.Controllers[controllerNr].usesID):
              ws.TXBuffer += "<TR><TD>IDX:<TD>"
              ws.addNumericBox(sid, settings.Tasks[taskIndex].controlleridx[controllerNr], 0, 9999)
             else:
              ws.TXBuffer += "<input type='hidden' name='{0}' value='0'>".format(sid) # no id, set to 0
            else:
             ws.TXBuffer += "<input type='hidden' name='{0}' value='-1'>".format(sid) # disabled set to -1

      ws.addFormSeparator(2)
      httpResponse._write(ws.TXBuffer,strEncoding='UTF-8')
      ws.TXBuffer = ""
      if (settings.Tasks[taskIndex].timeroption):
        ws.addFormNumericBox( "Interval", "TDT", settings.Tasks[taskIndex].interval, 0, 65535)
        ws.addUnit("sec")
        if (settings.Tasks[taskIndex].timeroptional):
          ws.TXBuffer += " (Optional for this Device)"

      if (settings.Tasks[taskIndex].valuecount>0): # //section: Values
        ws.addFormSubHeader("Values")
        ws.TXBuffer += "</table><table class='normal'><TR><TH style='width:30px;' align='center'>#<TH align='left'>Name"
        if (settings.Tasks[taskIndex].formulaoption):
          ws.TXBuffer += "<TH align='left'>Formula"

        if (settings.Tasks[taskIndex].formulaoption or settings.Tasks[taskIndex].decimalsonly):
          ws.TXBuffer += "<TH style='width:30px;' align='left'>Decimals"

        for varNr in range(0, settings.Tasks[taskIndex].valuecount):
          ws.TXBuffer += "<TR><TD>{0}<TD>".format(str(varNr + 1))
          sid = "TDVN" + str(varNr + 1)
          ws.addTextBox(sid, settings.Tasks[taskIndex].getdevicevaluenames()[varNr], 40)

          if (settings.Tasks[taskIndex].formulaoption):
            ws.TXBuffer += "<TD>"
            sid = "TDF"+str(varNr + 1)
            ws.addTextBox(sid, settings.Tasks[taskIndex].formula[varNr], 140)

          if (settings.Tasks[taskIndex].formulaoption or settings.Tasks[taskIndex].decimalsonly):
            ws.TXBuffer += "<TD>"
            sid = "TDVD"+str(varNr + 1)
            ws.addNumericBox(sid, settings.Tasks[taskIndex].decimals[varNr], 0, 6)

    ws.addFormSeparator(4)
    httpResponse._write(ws.TXBuffer,strEncoding='UTF-8')
    ws.TXBuffer = ""
    gc.collect()
    ws.TXBuffer += "<TR><TD><TD colspan='3'><a class='button link' href='devices?setpage={0}'>Close</a>".format(page)
    ws.addSubmitButton()
    ws.TXBuffer += "<input type='hidden' name='edit' value='1'>"
    if taskIndex != '':
     ws.TXBuffer += "<input type='hidden' name='index' value='{0}'>".format(taskIndex+1)
    ws.TXBuffer += "<input type='hidden' name='page' value='1'>"

    if (tte>0): # if user selected a device, add the delete button
      ws.addSubmitButton("Delete", "del")

    ws.TXBuffer += "</table></form>"

 ws.sendHeadandTail("TmplStd",ws._TAIL)
 httpResponse._write(ws.TXBuffer,strEncoding='UTF-8')
 ws.TXBuffer = ""
