#############################################################################
#################### Dashboard plugin for RPIEasy ###########################
#############################################################################
#
# Copyright (C) 2020 by Alexander Nagy - https://bitekmindenhol.blog.hu/
#
import plugin
import pglobals
import webserver_global as ws
try:
 import utime
except:
 import inc.faketime as utime
import settings

class Plugin(plugin.PluginProto):
 PLUGIN_ID = 212
 PLUGIN_NAME = "GUI - Dashboard"
 PLUGIN_VALUENAME1 = "State"

 def __init__(self,taskindex): # general init
  plugin.PluginProto.__init__(self,taskindex)
  self.dtype = pglobals.DEVICE_TYPE_DUMMY
  self.vtype = pglobals.SENSOR_TYPE_NONE
  self.readinprogress = 0
  self.valuecount = 0
  self.senddataoption = False
  self.timeroption = True
  self.timeroptional = False
  self.formulaoption = False
  self._nextdataservetime = 0
  self.celldata = []

 def plugin_init(self,enableplugin=None):
  plugin.PluginProto.plugin_init(self,enableplugin)
  self.initialized = False

 def webform_load(self): # create html page for settings
  ws.addFormCheckBox("Use standard HTML head","p212_head",self.taskdevicepluginconfig[2])
  try:
   sp = settings.AdvSettings["startpage"]
  except:
   sp = "/"
  ws.addFormCheckBox("Set as startpage","p212_start",(sp=="/dash"))
  ws.addHtml("<tr><td>Columns:<td>")
  ws.addSelector_Head("p212_cols",False)
  for o in range(7):
   ws.addSelector_Item(str(o),o,(str(o)==str(self.taskdevicepluginconfig[0])),False)
  ws.addSelector_Foot()

  ws.addHtml("<tr><td>Rows:<td>")
  ws.addSelector_Head("p212_rows",False)
  for o in range(16):
   ws.addSelector_Item(str(o),o,(str(o)==str(self.taskdevicepluginconfig[1])),False)
  ws.addSelector_Foot()

  if int(self.taskdevicepluginconfig[0])>0 and int(self.taskdevicepluginconfig[1])>0:
   if self.enabled:
    ws.addHtml("<tr><td>Dashboard address:</td><td><a href='dash'>/dash</a></td></tr>")
   options1 = ["None","Text","Binary input","Switch output","Meter","Gauge","Slider output","Select output"]
   optionvalues1 = [-1,0,1,2,3,4,5,6]
   options2 = ["None"]
   optionvalues2 = ["_"]
   for t in range(0,len(settings.Tasks)):
     if (settings.Tasks[t] and (type(settings.Tasks[t]) is not bool)):
      for v in range(0,settings.Tasks[t].valuecount):
       options2.append("T"+str(t+1)+"-"+str(v+1)+" / "+str(settings.Tasks[t].taskname)+"-"+str(settings.Tasks[t].valuenames[v]))
       optionvalues2.append(str(t)+"_"+str(v))

   for r in range(int(self.taskdevicepluginconfig[1])):
    for c in range(int(self.taskdevicepluginconfig[0])):
     offs = (r * int(self.taskdevicepluginconfig[0])) + c
     try:
      adata = self.celldata[offs]
     except:
      adata = {}
     dtype = -1
     if "type" in adata:
      dtype = int(adata["type"])
     ws.addHtml("<tr><td><b>Cell"+str(offs)+" (y"+str(r)+"x"+str(c)+")</b><td>")

     dname = ""
     if "name" in adata:
      dname = str(adata["name"])
     ws.addFormTextBox("Name overwrite","p212_names_"+str(offs),dname,64)

     ws.addFormSelector("Type","p212_type_"+str(offs),len(options1),options1,optionvalues1,None,dtype)
     ws.addHtml("<tr><td>Data source:<td>")
     ddata = "_"
     if "data" in adata:
      ddata = str(adata["data"])
     ws.addSelector_Head("p212_data_"+str(offs),False)
     for o in range(len(options2)):
      ws.addSelector_Item(options2[o],optionvalues2[o],(str(optionvalues2[o])==str(ddata)),False)
     ws.addSelector_Foot()

     if dtype in (0,4):
      try:
       udata = str(adata["unit"])
      except:
       udata = ""
      ws.addFormTextBox("Unit","p212_unit_"+str(offs),udata,16)
     if dtype in (3,4,5):
      try:
       umin = float(adata["min"])
      except:
       umin = 0
      try:
       umax = float(adata["max"])
      except:
       umax = 100
      ws.addFormFloatNumberBox("Min value","p212_min_"+str(offs),umin,-65535.0,65535.0)
      ws.addFormFloatNumberBox("Max value","p212_max_"+str(offs),umax,-65535.0,65535.0)
     elif dtype == 6:
      try:
       uon = str(adata["optionnames"])
      except:
       uon = ""
      try:
       uopt = str(adata["options"])
      except:
       uopt = ""
      ws.addFormTextBox("Option name list","p212_optionnames_"+str(offs),uon,1024)
      ws.addFormTextBox("Option value list","p212_options_"+str(offs),uopt,1024)
      ws.addFormNote("Input comma separated values for selector boxes!")
  return True

 def webform_save(self,params): # process settings post reply
   try:
    sp = settings.AdvSettings["startpage"]
   except:
    sp = "/"
   if (ws.arg("p212_start",params)=="on"):
    try:
     if sp != "/dash":
      settings.AdvSettings["startpage"]  = "/dash"
    except:
     pass
   else:
    try:
     if sp == "/dash":
      settings.AdvSettings["startpage"]  = "/"
    except:
     pass

   if (ws.arg("p212_head",params)=="on"):
    self.taskdevicepluginconfig[2] = True
   else:
    self.taskdevicepluginconfig[2] = False

   par = ws.arg("p212_cols",params)
   try:
    self.taskdevicepluginconfig[0] = int(par)
   except:
    self.taskdevicepluginconfig[0] = 1
   par = ws.arg("p212_rows",params)
   try:
    self.taskdevicepluginconfig[1] = int(par)
   except:
    self.taskdevicepluginconfig[1] = 1

   for c in range(int(self.taskdevicepluginconfig[0])):
    for r in range(int(self.taskdevicepluginconfig[1])):
     offs = (r * int(self.taskdevicepluginconfig[0])) + c
     mknew = True
     try:
      self.celldata[offs]["type"] = int(ws.arg("p212_type_"+str(offs),params))
      self.celldata[offs]["data"] = str(ws.arg("p212_data_"+str(offs),params))
      mknew = False
     except:
      pass
     if mknew:
      try:
       adata = {"type":int(ws.arg("p212_type_"+str(offs),params)), "data":str(ws.arg("p212_data_"+str(offs),params))}
      except:
       adata = {"type":-1, "data":"_"}
      self.celldata.append(adata)
     try:
      self.celldata[offs]["unit"] = str(ws.arg("p212_unit_"+str(offs),params))
     except:
      pass
     try:
      self.celldata[offs]["min"] = float(ws.arg("p212_min_"+str(offs),params))
      self.celldata[offs]["max"] = float(ws.arg("p212_max_"+str(offs),params))
     except:
      pass
     try:
      self.celldata[offs]["optionnames"] = str(ws.arg("p212_optionnames_"+str(offs),params))
      self.celldata[offs]["options"] = str(ws.arg("p212_options_"+str(offs),params))
      self.celldata[offs]["name"] = str(ws.arg("p212_names_"+str(offs),params))
     except:
      pass

   return True

 def plugin_read(self): # deal with data processing at specified time interval
  result = False
  if self.enabled:
     self._lastdataservetime = utime.ticks_ms()
  return result

