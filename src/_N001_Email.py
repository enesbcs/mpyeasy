import nplugin
import pglobals
import misc
import webserver_global as ws
import commands
try:
 import inc.uMail.umail as umail
except:
 print("uMail not found")

class Plugin(nplugin.NPluginProto):
 NPLUGIN_ID = 1
 NPLUGIN_NAME = "Email (SMTP)"

 def __init__(self,nindex): # general init
  nplugin.NPluginProto.__init__(self,nindex)
  self.server = "0.0.0.0"
  self.port = 25 #25/465
  self.security = 0 # 0:plain,1:ssl
  self.sender = ""
  self.receiver = ""
  self.login  = ""
  self.passw = ""
  self.subject ="" # template
  self.body=""     # template

 def getuniquename(self):
  return self.server

 def plugin_init(self,enableplugin=None):
  nplugin.NPluginProto.plugin_init(self,enableplugin)
  if self.passw=="*****":
   self.passw=""

 def webform_load(self): # create html page for settings
  ws.addFormTextBox("Server","server",self.server,64)
  options = ["Plain","SSL"]
  optionvalues = [0,1]
  ws.addFormSelector("Protocol","security",len(options),options,optionvalues,None,self.security)
  ws.addFormNumericBox("Port","port",self.port,1,65535)
  ws.addFormTextBox("Sender","sender",self.sender,64)
  ws.addFormTextBox("Receiver","receiver",self.receiver,64)
  ws.addFormTextBox("SMTP login name","login",self.login,64)
  ws.addFormPasswordBox("STMP password","passw",self.passw,64)
  ws.addFormTextBox("Subject","subject",self.subject,64)
  ws.addHtml("<TR><TD>Body:<TD><textarea name='body' rows='5' cols='80' size=512 wrap='off'>")
  ws.addHtml(str(self.body))
  ws.addHtml("</textarea>")
  return True

 def webform_save(self,params): # process settings post reply
  self.server = ws.arg("server",params)
  par1 = ws.arg("security",params)
  try:
   par1= (int(par1)==1)
  except:
   par1= False
  self.security=par1
  par1 = ws.arg("port",params)
  try:
   par1=int(par1)
  except:
   par1=25
  if par1<1 or par1>65534:
   par1=25
  self.port=par1
  self.sender   = ws.arg("sender",params)
  self.receiver = ws.arg("receiver",params)
  self.login    = ws.arg("login",params)
  passw = ws.arg("passw",params)
  if "**" not in passw:
   self.passw = passw
  self.subject = ws.arg("subject",params)
  self.body    = ws.arg("body",params)
  return True

 def notify(self,pmsg=""):
  if self.initialized==False or self.enabled==False:
    return False
  if self.sender=="" or self.receiver=="":
    return False
  if self.server=="0.0.0.0" or self.server=="":
    return False
  if pmsg=="":
    message = str(self.mailparse(self.body))
  else:
    message = str(self.mailparse(pmsg))
  try:
   smtp = umail.SMTP(self.server, self.port, ssl=self.security)
   if self.login!="" and self.passw!="":
    smtp.login(self.login, self.passw)
   smtp.to(self.receiver)
   smtp.write("From: {0}\r\n".format(self.sender))
   smtp.write("To: {0}\r\n".format(self.receiver))
   smtp.write("Content-Type: text/plain; charset=utf-8\r\nSubject: {0}\r\n\r\n".format(self.subject))
   smtp.write("{0}\n".format(message)) #smtp.write("{0}\n".format(message.encode("utf8")))
   smtp.send()
   smtp.quit()
   misc.addLog(pglobals.LOG_LEVEL_INFO,"Mail sent!")
   return True
  except Exception as e:
   misc.addLog(pglobals.LOG_LEVEL_ERROR,str(e))
   return False

 def mailparse(self,ostr):
      cl, st = commands.parseruleline(ostr)
      if st=="CMD":
          resstr=str(cl)
      else:
          resstr=str(ostr)
      return resstr
