#############################################################################
########################## OLED plugin for RPIEasy ##########################
#############################################################################
#
# Available commands:
#  OLEDCMD,<value>          - value can be: on, off, clear, low, med, high
#  OLEDCMD,clearline,<row>  - clears selected <row>
#  OLED,<row>,<col>,<text>  - write text message to OLED screen at the requested position
#
# Copyright (C) 2020 by Alexander Nagy - https://bitekmindenhol.blog.hu/
#
import plugin
import pglobals
import misc
import webserver_global as ws
import commands
import utime
import inc.libhw as libhw
try:
 from inc.ssd1306 import SSD1306_I2C
except:
 pass
from inc.writer.writer import Writer

class Plugin(plugin.PluginProto):
 PLUGIN_ID = 23
 PLUGIN_NAME = "Display - Simple OLED"
 PLUGIN_VALUENAME1 = "OLED"
 P23_Nlines = 8

 def __init__(self,taskindex): # general init
  plugin.PluginProto.__init__(self,taskindex)
  self.dtype = pglobals.DEVICE_TYPE_I2C
  self.vtype = pglobals.SENSOR_TYPE_NONE
  self.ports = 0
  self.valuecount = 0
  self.senddataoption = False
  self.timeroption = True
  self.timeroptional = True
  self.formulaoption = False
  self._device = None
  self.width  = None
  self.height = None
  self.lines  = []
  self.lineheight = 11
  self.charwidth   = 8
  self._dispimage = None

 def plugin_init(self,enableplugin=None):
  plugin.PluginProto.plugin_init(self,enableplugin)
  self.initialized = False
  if self.enabled:
    try:
     if "x" in str(self.taskdevicepluginconfig[3]):
      resstr = str(self.taskdevicepluginconfig[3]).split('x')
      self.width = int(resstr[0])
      self.height = int(resstr[1])
     else:
      self.width  = None
      self.height = None
    except:
     self.width  = None
     self.height = None
    if self.width is None:
     return False
    i2cl = None
    try:
     if int(self.i2c)==0:
      i2cl = libhw.i2c0
     elif int(self.i2c)==1:
      i2cl = libhw.i2c1
    except:
     pass
    if i2cl is None:
     return False
    err = ""
    try:
     self._device = SSD1306_I2C(self.width,self.height,i2cl,addr=int(self.taskdevicepluginconfig[1]))
     if self.taskdevicepluginconfig[2]==0:
        self._device.rotate(False)
     elif self.taskdevicepluginconfig[2]==2:
        self._device.rotate(True)
    except Exception as e:
     self._device = None
     err += str(e)
    try:
     if int(self.taskdevicepluginconfig[4])<1:
        self.taskdevicepluginconfig[4]=1
     if int(self.taskdevicepluginconfig[5])<1:
        self.taskdevicepluginconfig[5]=1
     fs = self.height / int(self.taskdevicepluginconfig[4])
     fw = self.width / int(self.taskdevicepluginconfig[5])
     fs2 = -1
     if fw>=19: #correct size by width
        fs2=31
     elif fw>=12:
        fs2=21
     elif fw>=9:
        fs2=16
     elif fw>=7:
        fs2=12
     elif fw>=6:
        fs2=10
     elif fw>=6:
        fs2=10
     elif fw>=5:
        fs2=9
     if fs2<fs:
        fs=fs2
     if fs>=31:
       import inc.writer.ufont31 as ufont
     elif fs>=21:
       import inc.writer.ufont21 as ufont
     elif fs>=16:
       import inc.writer.ufont16 as ufont
     elif fs>=12:
       import inc.writer.ufont12 as ufont
     elif fs>=10:
       import inc.writer.ufont10 as ufont
     elif fs>=9:
       import inc.writer.ufont9 as ufont
     else:
       import inc.writer.ufont8 as ufont
     self.lineheight = ufont.height()
     self.charwidth  = ufont.max_width()
     self._dispimage = Writer(self._device,ufont)
     self._dispimage.set_clip(wrap=False)
    except Exception as e:
     self._dispimage = None
     err += str(e)
    if self._device is not None and self._dispimage is not None:
     self.initialized = True
     misc.addLog(pglobals.LOG_LEVEL_INFO,"OLED initialized!")
    else:
     misc.addLog(pglobals.LOG_LEVEL_ERROR,"OLED can not be initialized! "+str(err))
  else:
   if self._device is not None:
    self.plugin_exit()

 def webform_load(self): # create html page for settings
  choice2 = int(float(self.taskdevicepluginconfig[1])) # store i2c address
  options = ["0x3c","0x3d"]
  optionvalues = [0x3c,0x3d]
  ws.addFormSelector("Address","p023_adr",len(options),options,optionvalues,None,choice2)
  ws.addFormNote("Enable <a href='hardware'>I2C bus</a> first, than <a href='i2cscanner'>search for the used address</a>!")
  choice3 = int(float(self.taskdevicepluginconfig[2])) # store rotation state
  options =      ["Normal","Rotate by 180"]
  optionvalues = [0,2]
  ws.addFormSelector("Mode","p023_rotate",len(optionvalues),options,optionvalues,None,choice3)
  options = ["128x64","128x128","128x32","96x96","96x64","64x48","64x32"]
  choice4 = self.taskdevicepluginconfig[3] # store resolution
  ws.addHtml("<tr><td>Resolution:<td>")
  ws.addSelector_Head("p023_res",False)
  for d in range(len(options)):
   ws.addSelector_Item(options[d],options[d],(choice4==options[d]),False)
  ws.addSelector_Foot()

  choice5 = int(float(self.taskdevicepluginconfig[4])) # store line count
  ws.addHtml("<tr><td>Number of lines:<td>")
  ws.addSelector_Head("p023_linecount",False)
  for l in range(1,self.P23_Nlines+1):
   ws.addSelector_Item(str(l),l,(l==choice5),False)
  ws.addSelector_Foot()
  ws.addFormNumericBox("Try to display # characters per row","p023_charperl",self.taskdevicepluginconfig[5],1,32)
  ws.addFormNote("Leave it '1' if you do not care")  
  ws.addFormCheckBox("Clear only used lines","p023_partialclear",self.taskdevicepluginconfig[6])
  if choice5 > 0 and choice5<9:
   lc = choice5
  else:
   lc = self.P23_Nlines
  for l in range(lc):
   try:
    linestr = self.lines[l]
   except:
    linestr = ""
   ws.addFormTextBox("Line"+str(l+1),"p023_template"+str(l),linestr,128)

  return True

 def plugin_exit(self):
  try:
   if self._device is not None:
    self._device.fill(0)
    self._device.poweroff()
  except:
   pass

 def webform_save(self,params): # process settings post reply
   par = ws.arg("p023_i2c",params)
   if par == "":
    par = 0
   self.i2c = int(par)

   par = ws.arg("p023_adr",params)
   if par == "":
    par = 0
   self.taskdevicepluginconfig[1] = int(par)

   par = ws.arg("p023_rotate",params)
   if par == "":
    par = 0
   self.taskdevicepluginconfig[2] = int(par)

   par = ws.arg("p023_res",params)
   self.taskdevicepluginconfig[3] = str(par)

   par = ws.arg("p023_linecount",params)
   if par == "":
    par = 8
   self.taskdevicepluginconfig[4] = int(par)

   par = ws.arg("p023_charperl",params)
   if par == "":
    par = 1
   self.taskdevicepluginconfig[5] = int(par)

   if (ws.arg("p023_partialclear",params)=="on"):
    self.taskdevicepluginconfig[6] = True
   else:
    self.taskdevicepluginconfig[6] = False

   for l in range(self.P23_Nlines):
    linestr = ws.arg("p023_template"+str(l),params).strip()
#    if linestr!="" and linestr!="0":
    try:
      self.lines[l]=linestr
    except:
      self.lines.append(linestr)
   self.plugin_init()
   return True

 def plugin_read(self): # deal with data processing at specified time interval
  if self.initialized and self.enabled:
     try:
      if self.taskdevicepluginconfig[6] == False:
       self._device.fill(0)
      if self._dispimage:
       for l in range(int(self.taskdevicepluginconfig[4])):
        resstr = ""
        try:
         linestr=str(self.lines[l])
         resstr=self.oledparse(linestr)
        except:
         resstr=""
        if resstr != "":
         y = (l*self.lineheight)
         if self.taskdevicepluginconfig[6]:
          self._device.fill_rect( 0,y+2, self._device.width, y+self.lineheight, 0)
         self._dispimage.set_textpos(self._device,y,0)
         self._dispimage._printline(resstr,False)
       self._device.show()
     except Exception as e:
      misc.addLog(pglobals.LOG_LEVEL_ERROR,"OLED write error! "+str(e))
     self._lastdataservetime = utime.ticks_ms()
  return True

 def plugin_write(self,cmd):
  res = False
  cmdarr = cmd.split(",")
  cmdarr[0] = cmdarr[0].strip().lower()
  if cmdarr[0] == "oledcmd":
   try:
    cmd = cmdarr[1].strip()
   except:
    cmd = ""
   try:
    if self._device is not None:
     if cmd == "on":
      self._device.poweron()
      res = True
     elif cmd == "off":
      self._device.poweroff()
      res = True
     elif cmd == "clear":
      self._device.fill(0)
      self._device.show()
      res = True
     elif cmd == "clearline":
      try:
       l = int(cmdarr[2].strip())
      except Exception as e:
       misc.addLog(pglobals.LOG_LEVEL_ERROR,"Parameter error: "+str(e))
       return False
      if self._device is not None and self._dispimage is not None:
        if l>0:
         l-=1
        y = (l*self.lineheight)
        self._device.fill_rect( 0,y+2, self._device.width, y+self.lineheight, 0)
        self._device.show()
      res = True
     if cmd == "low":
      self._device.contrast(64)
      res = True
     if cmd == "med":
      self._device.contrast(0xcf)
      res = True
     if cmd == "high":
      self._device.contrast(0xff)
      res = True
   except Exception as e:
    misc.addLog(pglobals.LOG_LEVEL_ERROR,"OLED command error! "+str(e))
    res = False
  elif cmdarr[0] == "oled":
   sepp = len(cmdarr[0])+len(cmdarr[1])+len(cmdarr[2])+1
   sepp = cmd.find(',',sepp)
   try:
    y = int(cmdarr[1].strip())
    x = int(cmdarr[2].strip())
    text = cmd[sepp+1:]
   except Exception as e:
    misc.addLog(pglobals.LOG_LEVEL_ERROR,"Parameter error: "+str(e))
    return False
   if x>0:
    x -= 1
   if y>0:
    y -= 1
   try:
    if self._device is not None:
      resstr = self.oledparse(text)
      self._dispimage.set_textpos(self._device,(y*self.lineheight),(x*self.charwidth))
      self._dispimage.printstring(resstr)
      self._device.show()
      res = True
   except Exception as e:
    misc.addLog(pglobals.LOG_LEVEL_ERROR,"OLED command error! "+str(e))
    res = False
  return res

 def oledparse(self,ostr):
      cl, st = commands.parseruleline(ostr)
      if st=="CMD":
          resstr=str(cl)
      else:
          resstr=str(ostr)
      return resstr
