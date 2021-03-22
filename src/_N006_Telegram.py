import nplugin
import pglobals
import misc
import webserver_global as ws
import commands
import urequests
try:
 import ujson
except:
 import json as ujson

class Plugin(nplugin.NPluginProto):
 NPLUGIN_ID = 6
 NPLUGIN_NAME = "Telegram"

 def __init__(self,nindex): # general init
  nplugin.NPluginProto.__init__(self,nindex)
  self.server = "api.telegram.org"
  self.port = 443
  self.passw = ""
  self.chatid = ""
  self.body=""     # template

 def getuniquename(self):
  return self.server

 def plugin_init(self,enableplugin=None):
  nplugin.NPluginProto.plugin_init(self,enableplugin)
  if self.passw=="*****":
   self.passw=""
  self.initialized = False
  if self.enabled:
   if self.chatid == "":
    urlstr = "https://"+str(self.server)+":"+str(self.port)+"/bot"+str(self.passw)+"/getUpdates"
    try:
     content = urequests.get(urlstr)
     ret = content.text
     if ("{" in ret):
      list = ujson.loads(ret)
      self.chatid = list["result"][0]["message"]["from"]["id"]
    except Exception as e:
     self.chatid = ""
     misc.addLog(pglobals.LOG_LEVEL_ERROR,"Telegram request failed: "+str(e)+" "+urlstr)
   if self.chatid == "":
    misc.addLog(pglobals.LOG_LEVEL_ERROR,"Telegram ChatID not found!")
    self.initialized = False
   else:
    self.initialized = True

 def webform_load(self): # create html page for settings
  ws.addFormTextBox("Server","server",self.server,128)
  ws.addFormNumericBox("Port","port",self.port,1,65535)
  ws.addFormPasswordBox("Token","passw",self.passw,64)
  ws.addHtml("<TR><TD>Body:<TD><textarea name='body' rows='5' cols='80' size=255 wrap='off'>")
  ws.addHtml(str(self.body))
  ws.addHtml("</textarea>")
  ws.addFormNote("SSL is currently broken in WROOM, plugin will not work without PSRAM!")
  return True

 def webform_save(self,params): # process settings post reply
  self.server = ws.arg("server",params)
  par1 = ws.arg("port",params)
  try:
   par1=int(par1)
  except:
   par1=443
  if par1<1 or par1>65534:
   par1=443
  self.port=par1
  passw = ws.arg("passw",params)
  if "**" not in passw:
   self.passw  = passw
   self.chatid = ""
  self.body    = ws.arg("body",params)
  self.plugin_init()
  return True

 def notify(self,pmsg=""):
  if self.initialized==False or self.enabled==False:
   return False
  if pmsg=="":
   message = self.msgparse(self.body)
  else:
   message = self.msgparse(pmsg)
  if self.server=="0.0.0.0" or self.server=="":
   return False
  jdata = {}
  jdata['chat_id'] = self.chatid
  jdata['parse_mode'] = 'HTML'
  jdata['text'] = message
  urlstr = "https://"+str(self.server)+":"+str(self.port)+"/bot"+str(self.passw)+"/sendMessage"
  misc.addLog(pglobals.LOG_LEVEL_INFO,"Sending telegram notification")
  return self.urlpost(urlstr,jdata)

 def urlpost(self,url,postdata):
  try:
   headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
   response = urequests.post(url, json=postdata, headers=headers)
   return True
  except Exception as e:
   misc.addLog(pglobals.LOG_LEVEL_ERROR,"Controller: "+self.server+" connection failed "+str(e))
   return False

 def msgparse(self,ostr):
      cl, st = commands.parseruleline(ostr)
      if st=="CMD":
          resstr=str(cl)
      else:
          resstr=str(ostr)
      return resstr
