import gc
import misc
import sys
import esp_os
from microWebSrv import MicroWebSrv #22k
import pglobals

@MicroWebSrv.route('/')
@MicroWebSrv.route('/','GET')
@MicroWebSrv.route('/generate_204')
def handle_root(httpClient, httpResponse):
 if httpClient.GetRequestMethod()=="GET":
  responsearr = httpClient.GetRequestQueryParams()
 else:
  responsearr  = httpClient.ReadRequestPostedFormData()
 try:
  import webserver_root
  webserver_root.handle_root(httpResponse,responsearr)
  del sys.modules['webserver_root']
 except Exception as e:
  misc.addLog(pglobals.LOG_LEVEL_ERROR, "Webserver root error: "+str(e))
 gc.collect()

@MicroWebSrv.route('/config')
@MicroWebSrv.route('/config','POST')
def handle_config(httpClient, httpResponse):
 if httpClient.GetRequestMethod()=="GET":
  responsearr = httpClient.GetRequestQueryParams()
 else:
  responsearr  = httpClient.ReadRequestPostedFormData()
 try:
  import webserver_config
  webserver_config.handle_config(httpResponse,responsearr)
  del sys.modules['webserver_config']
 except Exception as e:
  misc.addLog(pglobals.LOG_LEVEL_ERROR, "Webserver config error: "+str(e))
 gc.collect()

@MicroWebSrv.route('/controllers')
@MicroWebSrv.route('/controllers','GET')
@MicroWebSrv.route('/controllers','POST')
def handle_controllers(httpClient, httpResponse):
 if httpClient.GetRequestMethod()=="GET":
  responsearr = httpClient.GetRequestQueryParams()
 else:
  responsearr  = httpClient.ReadRequestPostedFormData()
 try:
  import webserver_contr
  webserver_contr.handle_controllers(httpResponse,responsearr)
  del sys.modules['webserver_contr']
 except Exception as e:
  misc.addLog(pglobals.LOG_LEVEL_ERROR, "Webserver controller error: "+str(e))
 gc.collect()

@MicroWebSrv.route('/devices')
@MicroWebSrv.route('/devices','GET')
@MicroWebSrv.route('/devices','POST')
def handle_devices(httpClient, httpResponse):
 if httpClient.GetRequestMethod()=="GET":
  responsearr = httpClient.GetRequestQueryParams()
 else:
  responsearr  = httpClient.ReadRequestPostedFormData()
 gc.collect()
 taskIndex = ("index" in responsearr and responsearr["index"] or '')
 taskIndexNotSet = (taskIndex == 0) or (taskIndex == '')
 try:
  if taskIndexNotSet:
   import webserver_devlist
   webserver_devlist.handle_devices(httpResponse,responsearr)
   del sys.modules['webserver_devlist']
  else:
   import webserver_dev
   webserver_dev.handle_devices(httpResponse,responsearr)
   del sys.modules['webserver_dev']
 except Exception as e:
  misc.addLog(pglobals.LOG_LEVEL_ERROR, "Webserver devices error: "+str(e))
 gc.collect()

@MicroWebSrv.route('/hardware')
@MicroWebSrv.route('/hardware','GET')
@MicroWebSrv.route('/hardware','POST')
def handle_hw(httpClient, httpResponse):
 if httpClient.GetRequestMethod()=="GET":
  responsearr = httpClient.GetRequestQueryParams()
 else:
  responsearr  = httpClient.ReadRequestPostedFormData()
 try:
  import webserver_hw
  webserver_hw.handle_hw(httpResponse,responsearr)
  del sys.modules['webserver_hw']
 except Exception as e:
  misc.addLog(pglobals.LOG_LEVEL_ERROR, "Webserver hardware error: "+str(e))
 gc.collect()

@MicroWebSrv.route('/sysinfo')
def handle_sysinfo(httpClient, httpResponse):
 try:
  import webserver_sysinfo
  webserver_sysinfo.handle_sysinfo(httpResponse)
  del sys.modules['webserver_sysinfo']
 except Exception as e:
  misc.addLog(pglobals.LOG_LEVEL_ERROR, "Webserver sysinfo error: "+str(e))
 gc.collect()

@MicroWebSrv.route('/blescanner')
def handle_blescan(httpClient, httpResponse):
 try:
  import webserver_blescan
  webserver_blescan.handle_blescan(httpResponse)
  del sys.modules['webserver_blescan']
 except Exception as e:
  misc.addLog(pglobals.LOG_LEVEL_ERROR, "Webserver blescan error: "+str(e))
 gc.collect()

@MicroWebSrv.route('/i2cscanner')
def handle_i2cscan(httpClient, httpResponse):
 try:
  import webserver_i2cscan
  webserver_i2cscan.handle_i2cscan(httpResponse)
  del sys.modules['webserver_i2cscan']
 except Exception as e:
  misc.addLog(pglobals.LOG_LEVEL_ERROR, "Webserver i2cscan error: "+str(e))
 gc.collect()

@MicroWebSrv.route('/wifiscanner')
def handle_wifiscan(httpClient, httpResponse):
 try:
  import webserver_wifiscan
  webserver_wifiscan.handle_wifiscan(httpResponse)
  del sys.modules['webserver_wifiscan']
 except Exception as e:
  misc.addLog(pglobals.LOG_LEVEL_ERROR, "Webserver wifiscan error: "+str(e))
 gc.collect()

@MicroWebSrv.route('/sysvars')
def handle_sysvars(httpClient, httpResponse):
 try:
  import webserver_sysvars
  webserver_sysvars.handle_sysvars(httpResponse)
  del sys.modules['webserver_sysvars']
 except Exception as e:
  misc.addLog(pglobals.LOG_LEVEL_ERROR, "Webserver sysvars error: "+str(e))
 gc.collect()

@MicroWebSrv.route('/log')
def handle_log(httpClient, httpResponse):
 try:
  import webserver_log
  webserver_log.handle_log(httpResponse)
  del sys.modules['webserver_log']
 except Exception as e:
  misc.addLog(pglobals.LOG_LEVEL_ERROR, "Webserver log error: "+str(e))
 gc.collect()

@MicroWebSrv.route('/tools')
@MicroWebSrv.route('/tools','POST')
def handle_tools(httpClient, httpResponse):
 if httpClient.GetRequestMethod()=="GET":
  responsearr = httpClient.GetRequestQueryParams()
 else:
  responsearr  = httpClient.ReadRequestPostedFormData()
 try:
  import webserver_tools
  webserver_tools.handle_tools(httpResponse,responsearr)
  del sys.modules['webserver_tools']
 except Exception as e:
  misc.addLog(pglobals.LOG_LEVEL_ERROR, "Webserver tools error: "+str(e))
 gc.collect()

@MicroWebSrv.route('/rules')
@MicroWebSrv.route('/rules','GET')
@MicroWebSrv.route('/rules','POST')
def handle_rules(httpClient, httpResponse):
 if httpClient.GetRequestMethod()=="GET":
  responsearr = httpClient.GetRequestQueryParams()
 else:
  responsearr  = httpClient.ReadRequestPostedFormData()
 try:
  import webserver_rules
  webserver_rules.handle_rules(httpResponse,responsearr)
  del sys.modules['webserver_rules']
 except Exception as e:
  misc.addLog(pglobals.LOG_LEVEL_ERROR, "Webserver rules error: "+str(e))
 gc.collect()

@MicroWebSrv.route('/advanced')
@MicroWebSrv.route('/advanced','GET')
@MicroWebSrv.route('/advanced','POST')
def handle_adv(httpClient, httpResponse):
 if httpClient.GetRequestMethod()=="GET":
  responsearr = httpClient.GetRequestQueryParams()
 else:
  responsearr  = httpClient.ReadRequestPostedFormData()
 try:
  import webserver_adv
  webserver_adv.handle_adv(httpResponse,responsearr)
  del sys.modules['webserver_adv']
 except Exception as e:
  misc.addLog(pglobals.LOG_LEVEL_ERROR, "Webserver adv error: "+str(e))
 gc.collect()

@MicroWebSrv.route('/notifications')
@MicroWebSrv.route('/notifications','GET')
@MicroWebSrv.route('/notifications','POST')
def handle_notifications(httpClient, httpResponse):
 if httpClient.GetRequestMethod()=="GET":
  responsearr = httpClient.GetRequestQueryParams()
 else:
  responsearr  = httpClient.ReadRequestPostedFormData()
 try:
  import webserver_notif
  webserver_notif.handle_notif(httpResponse,responsearr)
  del sys.modules['webserver_notif']
 except Exception as e:
  misc.addLog(pglobals.LOG_LEVEL_ERROR, "Webserver notification error: "+str(e))
 gc.collect()

@MicroWebSrv.route('/update')
@MicroWebSrv.route('/update','POST')
def handle_ota(httpClient, httpResponse):
 try:
  import webserver_ota
  if httpClient.GetRequestMethod()=="POST":
   webserver_ota.handle_upload(httpClient, httpResponse)
  else:
   webserver_ota.handle_ota(httpResponse)
  del sys.modules['webserver_ota']
 except Exception as e:
  misc.addLog(pglobals.LOG_LEVEL_ERROR, "Webserver ota error: "+str(e))
 gc.collect()

@MicroWebSrv.route('/dash')
@MicroWebSrv.route('/dash','GET')
@MicroWebSrv.route('/dash','POST')
def handle_dash(httpClient, httpResponse):
 if httpClient.GetRequestMethod()=="GET":
  responsearr = httpClient.GetRequestQueryParams()
 else:
  responsearr  = httpClient.ReadRequestPostedFormData()
 try:
  import webserver_dash
  webserver_dash.handle_dash(httpResponse,responsearr)
  del sys.modules['webserver_dash']
 except Exception as e:
  misc.addLog(pglobals.LOG_LEVEL_ERROR, "Webserver dash error: "+str(e))
 gc.collect()

@MicroWebSrv.route('/control')
@MicroWebSrv.route('/control','GET')
def handle_command(httpClient, httpResponse):
 if httpClient.GetRequestMethod()=="GET":
  responsearr = httpClient.GetRequestQueryParams()
 else:
  responsearr  = httpClient.ReadRequestPostedFormData()
 try:
  import webserver_command
  webserver_command.handle_command(httpResponse,responsearr)
  del sys.modules['webserver_command']
 except Exception as e:
  misc.addLog(pglobals.LOG_LEVEL_ERROR, "Webserver command error: "+str(e))
 gc.collect()

@MicroWebSrv.route('/csv')
@MicroWebSrv.route('/csv','GET')
def handle_csv(httpClient, httpResponse):
 if httpClient.GetRequestMethod()=="GET":
  responsearr = httpClient.GetRequestQueryParams()
 else:
  responsearr  = httpClient.ReadRequestPostedFormData()
 try:
  import webserver_csv
  webserver_csv.handle_csv(httpResponse,responsearr)
  del sys.modules['webserver_csv']
 except Exception as e:
  misc.addLog(pglobals.LOG_LEVEL_ERROR, "Webserver csv error: "+str(e))
 gc.collect()

@MicroWebSrv.route('/json')
@MicroWebSrv.route('/json','GET')
def handle_json(httpClient, httpResponse):
 if httpClient.GetRequestMethod()=="GET":
  responsearr = httpClient.GetRequestQueryParams()
 else:
  responsearr  = httpClient.ReadRequestPostedFormData()
 try:
  import webserver_json
  webserver_json.handle_json(httpResponse,responsearr)
  del sys.modules['webserver_json']
 except Exception as e:
  misc.addLog(pglobals.LOG_LEVEL_ERROR, "Webserver json error: "+str(e))
 gc.collect()

# Starting Webserver entity
WebServer = MicroWebSrv(webPath=pglobals.fpath+'www/')
