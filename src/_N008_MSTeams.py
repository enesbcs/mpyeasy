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
import gc

class Plugin(nplugin.NPluginProto):
 NPLUGIN_ID = 8
 NPLUGIN_NAME = "MS Teams"

 def __init__(self,nindex): # general init
  nplugin.NPluginProto.__init__(self,nindex)
  self.server = "webhook.office.com"
  self.port = 443
  self.passw = ""
  self.fullurl = ""
  self.chatid = ""
  self.body=""     # template

 def getuniquename(self):
  fullurl = ""
  if self.fullurl !="":
   furl = self.fullurl.replace("//","/")
   try:
    fa = furl.split("/")
    fullurl = fa[1]
   except:
    pass
  else:
   fullurl = self.server
  return fullurl

 def plugin_init(self,enableplugin=None):
  nplugin.NPluginProto.plugin_init(self,enableplugin)
  if self.passw=="*****":
   self.passw=""
  self.initialized = False
  if self.fullurl != "" and self.enabled:
    self.initialized = True

 def webform_load(self): # create html page for settings
  ws.addFormTextBox("Teams channel Webhook URL","fullurl",self.fullurl,512)
  ws.addHtml("<TR><TD>Body:<TD><textarea name='body' rows='5' cols='80' size=255 wrap='off'>")
  ws.addHtml(str(self.body))
  ws.addHtml("</textarea>")
  ws.addFormNote("SSL is currently broken in WROOM, plugin will not work without PSRAM!")
  return True

 def webform_save(self,params): # process settings post reply
  self.fullurl = ws.arg("fullurl",params)
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
  try:
   jdata = {'text': str(message) }
   urlstr = str(self.fullurl)
  except Exception as e:
   misc.addLog(pglobals.LOG_LEVEL_ERROR,"Teams notification: "+str(e))
   return False
  misc.addLog(pglobals.LOG_LEVEL_INFO,"Sending Teams notification")
  return self.urlpost(urlstr,jdata)

 def urlpost(self,url,postdata):
  gc.collect()
  try:
   headers = {'Content-type': 'application/json'}
   response = urequests.post(url, json=postdata, headers=headers)
   return True
  except Exception as e:
   misc.addLog(pglobals.LOG_LEVEL_ERROR,"Controller: "+self.getuniquename()+" connection failed "+str(e))
   return False

 def msgparse(self,ostr):
      cl, st = commands.parseruleline(ostr)
      if st=="CMD":
          resstr=str(cl)
      else:
          resstr=str(ostr)
      return resstr
