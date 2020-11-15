import webserver_global as ws
import pglobals
import gc
import esp_os # debug

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
 toggleIndex = ws.arg("toggle",responsearr)

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
 import settings
 import misc

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

 if toggleIndex != "":
  if len(settings.Tasks)<1:
   return False
  try:
   s = int(toggleIndex)
  except:
   s = -1
  try:
   if s >0 and (s<=len(settings.Tasks)):
    s = s-1 # array is 0 based, tasks is 1 based
    if (type(settings.Tasks[s])!=bool) and (settings.Tasks[s]):
     if (settings.Tasks[s].enabled):
      settings.Tasks[s].set_value(1,(1-int(settings.Tasks[s].uservar[0])),publish=True)
  except Exception as e:
    print(e)

 if taskIndexNotSet: # show all tasks as table

    ws.TXBuffer += "<table class='multirow' border=1px frame='box' rules='all'><TR><TH style='width:70px;'>"

    if (pglobals.TASKS_MAX != ws.TASKS_PER_PAGE):
      ws.TXBuffer += "<a class='button link' href='devices?setpage="
      if (page > 1):
        ws.TXBuffer += str(page - 1)
      else:
        ws.TXBuffer += str(page)
      ws.TXBuffer += "'>&lt;</a><a class='button link' href='devices?setpage="

      if (page < (pglobals.TASKS_MAX / ws.TASKS_PER_PAGE)):
        ws.TXBuffer += str(page + 1)
      else:
        ws.TXBuffer += str(page)
      ws.TXBuffer += "'>&gt;</a><TH style='width:50px;'>Task<TH style='width:100px;'>Enabled<TH>Device<TH>Name<TH>Port<TH style='width:100px;'>Ctr (IDX)<TH style='width:70px;'>GPIO<TH>Values"
      for x in range( ((page - 1) * ws.TASKS_PER_PAGE), ((page) * ws.TASKS_PER_PAGE) ):
       ws.TXBuffer += "<TR><TD><a class='button link' href='devices?index={0}&page={1}'>Edit</a>".format((x+1),page)
       try:
        if settings.Tasks[x] and settings.Tasks[x].enabled and settings.Tasks[x].remotefeed<1:
         ws.TXBuffer += "<a class='button link' href='devices?run={0}&page={1}'>Run</a>".format((x+1),page)
         if settings.Tasks[x].recdataoption and settings.Tasks[x].vtype==pglobals.SENSOR_TYPE_SWITCH:
          ws.TXBuffer += "<a class='button link' href='devices?toggle={0}&page={1}'>Toggle</a>".format((x+1),page)
       except:
        pass
       ws.TXBuffer += "<TD>{0}<TD>".format(x+1)

       lent = False
       try:
        if settings.Tasks[x]:
         lent = True
       except:
        lent = False

       if (len(settings.Tasks)>x) and (lent):
        try:
         ws.addEnabled(settings.Tasks[x].enabled)
        except Exception as e:
         pass
        ws.TXBuffer += "<TD>{0}<TD>{1}<TD>".format(settings.Tasks[x].getdevicename(),settings.Tasks[x].gettaskname())

        try:
          if (str(settings.Tasks[x].ports) != "0" and str(settings.Tasks[x].ports) != ""):
            ws.TXBuffer += str(settings.Tasks[x].ports)
        except:
         pass
        if settings.Tasks[x].remotefeed:
         ws.TXBuffer += "<TD style='background-color:#00FF00'>"
        else:
         ws.TXBuffer += "<TD>"
        try:
         if (settings.Tasks[x].senddataoption):
          doBR = False
          maxcon = len(settings.Controllers)
          if maxcon>pglobals.CONTROLLER_MAX:
           maxcon = pglobals.CONTROLLER_MAX
          try:
           for controllerNr in range(0,maxcon):
            if (settings.Tasks[x]) and (settings.Tasks[x].senddataenabled[controllerNr]) and (settings.Controllers[controllerNr].enabled):
              if (doBR):
                ws.TXBuffer += "<BR>"
              ws.TXBuffer += ws.getControllerSymbol(controllerNr)
              if (settings.Controllers[controllerNr].usesID):
                ws.TXBuffer += " ({0})".format(settings.Tasks[x].controlleridx[controllerNr])
                if (int(settings.Tasks[x].controlleridx[controllerNr]) <= 0):
                  ws.TXBuffer += " " + HTML_SYMBOL_WARNING
              doBR = True
          except Exception as e:
            pass
         ws.TXBuffer += "<TD>"
        except Exception as e:
         print(e)

        if (settings.Tasks[x].dtype == pglobals.DEVICE_TYPE_I2C):
            try:
             i2cpins = settings.get_i2c_pins(settings.Tasks[x].i2c)
             ws.TXBuffer += "{0}<BR>{1}".format(i2cpins[0],i2cpins[1])
            except:
             ws.TXBuffer += "NO-I2C"
        if (settings.Tasks[x].dtype == pglobals.DEVICE_TYPE_SPI):
            try:
             ws.TXBuffer += "SPI{0}".format(settings.Tasks[x].spi)
            except:
             ws.TXBuffer += "NO-SPI"
        for tp in range(0,len(settings.Tasks[x].taskdevicepin)):
          if int(settings.Tasks[x].taskdevicepin[tp])>=0:
            ws.TXBuffer += "<br>GPIO-{0}".format(settings.Tasks[x].taskdevicepin[tp])
        ws.TXBuffer += "<TD>"
        customValues = False
#        customValues = PluginCall(PLUGIN_WEBFORM_SHOW_VALUES, &TempEvent,ws.TXBuffer.buf);

        if not(customValues):
          if (settings.Tasks[x].vtype == pglobals.SENSOR_TYPE_LONG):
           try:
            numtodisp = str(float(settings.Tasks[x].uservar[0]) + float(settings.Tasks[x].uservar[1] << 16))
            ws.TXBuffer  += "<div class='div_l' id='valuename_{0}_0'>{1}:</div><div class='div_r' id='value_{2}_0'>{3}</div>".format(x,settings.Tasks[x].getdevicevaluenames()[0],x,str(misc.formatnum(numtodisp,0)))
           except Exception as e:
            print(e)
          else:
            try:
             for varNr in range(0,pglobals.VARS_PER_TASK):
              if ((settings.Tasks[x].enabled) and (varNr < settings.Tasks[x].valuecount)):
                if (varNr > 0):
                  ws.TXBuffer += "<div class='div_br'></div>"
                numtodisp = settings.Tasks[x].uservar[varNr]
                decimalv = settings.Tasks[x].decimals[varNr]
                ws.TXBuffer  += "<div class='div_l' id='valuename_{0}_{1}'>{2}:</div><div class='div_r' id='value_{3}_{4}'>{5}</div>".format(x,varNr,settings.Tasks[x].getdevicevaluenames()[varNr],x,varNr,str(misc.formatnum(numtodisp,decimalv)))
            except Exception as e:
             print(e)
       else:
        ws.TXBuffer += "<TD><TD><TD><TD><TD><TD>"
       httpResponse._write(ws.TXBuffer,strEncoding='UTF-8')
       ws.TXBuffer = ""
      ws.TXBuffer += "</table></form>"

 ws.sendHeadandTail("TmplStd",ws._TAIL)
 httpResponse._write(ws.TXBuffer,strEncoding='UTF-8')
 ws.TXBuffer = ""
