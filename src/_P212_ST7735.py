#############################################################################
######################### ST7735 plugin for RPIEasy #########################
#############################################################################
#
# Available commands:
#  TFTCMD,<value>          - value can be: clear
#  TFTCMD,clearline,<row>  - clears selected <row>
#  TFT,<row>,<col>,<text>  - write text message to TFT screen at the requested position
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
 from inc.st7735 import ST7735
except:
 pass
from inc.writer.writer import CWriter
import gc

class Plugin(plugin.PluginProto):
 PLUGIN_ID = 212
 PLUGIN_NAME = "Display - Simple ST7735 (EXPERIMENTAL)"
 PLUGIN_VALUENAME1 = "TFT"
 P212_Nlines = 8

 def __init__(self,taskindex): # general init
  plugin.PluginProto.__init__(self,taskindex)
  self.dtype = pglobals.DEVICE_TYPE_SPI
  self.vtype = pglobals.SENSOR_TYPE_NONE
  self.ports = 0
  self.valuecount = 0
  self.senddataoption = False
  self.timeroption = True
  self.timeroptional = True
  self.formulaoption = False
  self._device = None
  self.width  = -1
  self.height = -1
  self.lines  = []
  self.lineheight = 11
  self.charwidth   = 8
  self._dispimage = None
  self.cs = -1
  self.dc = -1
  self.rst = None
  self.disptype = 'r'
  self.xoffset = 0
  self.yoffset = 0
  self.rotate = 0
  self.rgb = True

 def plugin_init(self,enableplugin=None):
  plugin.PluginProto.plugin_init(self,enableplugin)
  self.initialized = False
  if self.enabled:
    spil = None
    try:
     if int(self.spi)==1:
      spil = libhw.spi1
     elif int(self.i2c)==2:
      spil = libhw.spi2
    except:
     pass
    if spil is None:
     return False
    err = ""
    if self.rst < 0:
     srst = None
    else:
     srst = self.rst
    if self.dc > -1 and self.cs > -1 and self.width>0 and self.height>0:
     try:
      if self._device is None:
       self._device = ST7735(spil,self.cs,self.dc,rst=srst,width=self.width,height=self.height,disptype=self.disptype,xoffset=self.xoffset,yoffset=self.yoffset,rotate=self.rotate,rgb=self.rgb)
      self.initialized = self._device.initialized
     except Exception as e:
      err += str(e)
      self._device = None

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
     self._dispimage = CWriter(self._device,ufont,0xffff,0,False)
     self._dispimage.set_clip(wrap=False)
    except Exception as e:
     self._dispimage = None
     err += str(e)
    if self._device is not None and self._dispimage is not None:
     self.initialized = True
     misc.addLog(pglobals.LOG_LEVEL_INFO,"TFT initialized!")
    else:
     misc.addLog(pglobals.LOG_LEVEL_ERROR,"TFT can not be initialized! "+str(err))
  else:
   if self._device is not None:
    self.plugin_exit()

 def webform_load(self): # create html page for settings
     gc.collect()
     ws.addFormNote("Enable <a href='hardware'>SPI bus</a> first!")
     ws.addFormPinSelect("CS","p212_cs",self.cs,1)
     ws.addFormPinSelect("DC","p212_dc",self.dc,1)
     ws.addFormPinSelect("RST","p212_rst",self.rst,1)
     ws.addFormNote("Optional")
     try:
      ws.addHtml("<tr><td>Variant:<td>")
      options = ['Red/M5StickC','Blue','Blue2','Green']
      optionvalues = ['r','b','b2','g']
      ws.addSelector_Head("p212_disptype",False)
      for d in range(len(options)):
         ws.addSelector_Item(options[d],optionvalues[d],(self.disptype==optionvalues[d]),False)
      ws.addSelector_Foot()
     except:
      pass
     gc.collect()
     ws.addFormNumericBox("Width","p212_width",self.width,1,320)
     ws.addFormNumericBox("Height","p212_height",self.height,1,320)

     ws.addFormNumericBox("X offset","p212_xoffset",self.xoffset,0,100)
     ws.addFormNumericBox("Y offset","p212_yoffset",self.yoffset,0,100)
     options =      ["RGB","BGR"]
     optionvalues = [1,0]
     ws.addFormSelector("Color mode","p212_rgb",len(optionvalues),options,optionvalues,None,self.rgb)

     options =      ["0","90","180","270"]
     optionvalues = [0,90,180,270]
     ws.addFormSelector("Rotation","p212_rotate",len(optionvalues),options,optionvalues,None,self.rotate)
     ws.addUnit("deg")
     try:
      choice5 = int(float(self.taskdevicepluginconfig[4])) # store line count
      ws.addHtml("<tr><td>Number of lines:<td>")
      ws.addSelector_Head("p212_linecount",False)
      for l in range(1,self.P212_Nlines+1):
       ws.addSelector_Item(str(l),l,(l==choice5),False)
      ws.addSelector_Foot()
     except:
      pass
     ws.addFormNumericBox("Try to display # characters per row","p212_charperl",self.taskdevicepluginconfig[5],1,32)
     ws.addFormNote("Leave it '1' if you do not care")
     ws.addFormCheckBox("Clear only used lines","p212_partialclear",self.taskdevicepluginconfig[6])
     if choice5 > 0 and choice5<9:
      lc = choice5
     else:
      lc = self.P212_Nlines
     for l in range(lc):
      try:
       linestr = self.lines[l]
      except:
       linestr = ""
      ws.addFormTextBox("Line"+str(l+1),"p212_template"+str(l),linestr,128)
     return True

 def plugin_exit(self):
  try:
   if self._device is not None:
    self._device.clear()
  except:
   pass

 def webform_save(self,params): # process settings post reply
   par = ws.arg("p212_cs",params)
   if par == "":
    par = -1
   self.cs = int(par)
   par = ws.arg("p212_dc",params)
   if par == "":
    par = -1
   self.dc = int(par)
   par = ws.arg("p212_rst",params)
   if par == "":
    par = -1
   self.rst = int(par)
   par = ws.arg("p212_width",params)
   if par == "":
    par = 0
   self.width = int(par)
   par = ws.arg("p212_height",params)
   if par == "":
    par = 0
   self.height = int(par)
   par = ws.arg("p212_disptype",params)
   if par == "":
    par = 'r'
   self.disptype = str(par)

   par = ws.arg("p212_rotate",params)
   if par == "":
    par = 0
   self.rotate = int(par)

   par = ws.arg("p212_linecount",params)
   if par == "":
    par = 8
   self.taskdevicepluginconfig[4] = int(par)

   par = ws.arg("p212_charperl",params)
   if par == "":
    par = 1
   self.taskdevicepluginconfig[5] = int(par)

   par = ws.arg("p212_xoffset",params)
   if par == "":
    par = 1
   self.xoffset = int(par)
   par = ws.arg("p212_yoffset",params)
   if par == "":
    par = 1
   self.yoffset = int(par)
   par = ws.arg("p212_rgb",params)
   if par == "":
    par = 1
   self.rgb = int(par)

   if (ws.arg("p212_partialclear",params)=="on"):
    self.taskdevicepluginconfig[6] = True
   else:
    self.taskdevicepluginconfig[6] = False

   for l in range(self.P212_Nlines):
    linestr = ws.arg("p212_template"+str(l),params).strip()
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
         resstr=self.tftparse(linestr)
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
      misc.addLog(pglobals.LOG_LEVEL_ERROR,"TFT write error! "+str(e))
     self._lastdataservetime = utime.ticks_ms()
  return True

 def plugin_write(self,cmd):
  res = False
  cmdarr = cmd.split(",")
  cmdarr[0] = cmdarr[0].strip().lower()
  if cmdarr[0] == "tftcmd":
   try:
    cmd = cmdarr[1].strip()
   except:
    cmd = ""
   try:
    if self._device is not None:
     if cmd == "clear":
      self._device.clear()
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
   except Exception as e:
    misc.addLog(pglobals.LOG_LEVEL_ERROR,"TFT command error! "+str(e))
    res = False
  elif cmdarr[0] == "tft":
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
      resstr = self.tftparse(text)
      self._dispimage.set_textpos(self._device,(y*self.lineheight),(x*self.charwidth))
      self._dispimage.printstring(resstr)
      self._device.show()
      res = True
   except Exception as e:
    misc.addLog(pglobals.LOG_LEVEL_ERROR,"TFT command error! "+str(e))
    res = False
  return res

 def tftparse(self,ostr):
      cl, st = commands.parseruleline(ostr)
      if st=="CMD":
          resstr=str(cl)
      else:
          resstr=str(ostr)
      return resstr
