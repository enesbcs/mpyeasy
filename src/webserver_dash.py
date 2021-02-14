import webserver_global as ws
import settings
import unet

def handle_dash(httpResponse,responsearr):
  try:
   ws.navMenuIndex=7
   ws.TXBuffer = ""
   httpResponse.WriteResponseOk(
        headers = ({'Cache-Control': 'no-cache'}),
        contentType = 'text/html',
        contentCharset = 'UTF-8',
        content = "" )

   dashtask = None
   for t in range(0,len(settings.Tasks)):
     if (settings.Tasks[t] and (type(settings.Tasks[t]) is not bool)):
      try:
       if settings.Tasks[t].enabled:
        if settings.Tasks[t].pluginid==212:
         dashtask = settings.Tasks[t]
         break
      except:
       pass
   ws.TXBuffer =""
   if (dashtask is not None) and (dashtask.taskdevicepluginconfig[2]):
    ws.sendHeadandTail("TmplStd",ws._HEAD)
    ws.TXBuffer += "<link rel='stylesheet' href='/dash.css'>"
   else:
    ws.TXBuffer += "<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'/><link rel='stylesheet' href='/dash.css'></head><body>"

   if (dashtask is not None) and (len(dashtask.celldata)>0):
    astr = ""
    estr = ""
    vstr = ""
    if int(dashtask.taskdevicepluginconfig[0])>1 and int(dashtask.taskdevicepluginconfig[0])<7:
     astr = " tab"+str(dashtask.taskdevicepluginconfig[0])
    ws.addHtml("<table width='100%' class='tab "+astr+"'>")
    offs = 0
    for r in range(int(dashtask.taskdevicepluginconfig[1])):
     httpResponse._write(ws.TXBuffer,strEncoding='UTF-8')
     ws.TXBuffer = ""
     if offs>=len(dashtask.celldata):
      break
     ws.addHtml("<tr>")
     for c in range(int(dashtask.taskdevicepluginconfig[0])):
      if offs>=len(dashtask.celldata):
       break
      ws.addHtml("<td>")
      offs = (r * int(dashtask.taskdevicepluginconfig[0])) + c
      try:
       dtype = int(dashtask.celldata[offs]["type"])
       tid = str(dashtask.celldata[offs]["data"])
       estr += '"'+tid+'",'
       ti = tid.split("_")
       tasknum = int(ti[0])
       valnum  = int(ti[1])
       vstr += '"'+ str(settings.Tasks[tasknum].uservar[valnum]) +'",'
       try:
        namestr = str(dashtask.celldata[offs]["name"])
       except:
         namestr = ""
       if namestr.strip() == "":
        namestr = str(settings.Tasks[tasknum].gettaskname())+"#"+str(settings.Tasks[tasknum].valuenames[valnum])
       ws.addHtml("<div class='div_d' id='valuename_"+ str(tid) + "'>"+ namestr + "</div>")
      except:
       dtype = -1
      try:
        udata = str(dashtask.celldata[offs]["unit"])
      except:
        udata = ""
      if dtype == 0:
       ws.addHtml("<div class='textval' id='value_"+str(tid)+ "'>"+ str(settings.Tasks[tasknum].uservar[valnum]) +"</div>")
      elif dtype == 1:
       ws.addHtml("<div class='centered'><input type='checkbox' id='value_"+str(tid)+ "' class='state' disabled='disabled'/><label for='value_"+str(tid)+ "' class='toggleWrapper'><div class='toggle'></div></label></div>")
      elif dtype == 2:
       ws.addHtml("<div class='switch'><input id='value_"+str(tid)+ "' class='cmn-toggle cmn-toggle-round' type='checkbox' onchange='cboxchanged(this)'><label for='value_"+str(tid)+ "'></label></div>")
      elif dtype == 3:
       try:
         umin = float(dashtask.celldata[offs]["min"])
       except:
         umin = 0
       try:
         umax = float(dashtask.celldata[offs]["max"])
       except:
         umax = 100
       ws.addHtml("<div style='width:100%'><meter id='value_"+str(tid)+ "' min='"+str(umin)+"' max='"+str(umax)+"' value='" + str(settings.Tasks[tasknum].uservar[valnum]) + "' class='meter'></meter>")
       sval = umin
       stepval = (umax-umin)/5
       ws.addHtml("<ul id='scale'><li style='width: 10%'><span></span></li>")
       while sval < (umax-stepval):
        sval = sval + stepval
        ws.addHtml("<li><span id='scale'>"+str(sval)+"</span></li>")
       ws.addHtml("<li style='width: 10%'><span id='scale'></span></li></ul></div>")
      elif dtype == 4:
       ws.addHtml("<div class='gauge' id='value_"+str(tid)+ "'><div class='gauge__body'><div class='gauge__fill'></div><div class='gauge__cover'></div></div></div>")
      elif dtype == 5:
       try:
         umin = float(dashtask.celldata[offs]["min"])
       except:
         umin = 0
       try:
         umax = float(dashtask.celldata[offs]["max"])
       except:
         umax = 100
       ws.addHtml("<input type='range' min='" +str(umin) +"' max='"+ str(umax) +"' value='" + str(settings.Tasks[tasknum].uservar[valnum]) + "' class='slider' id='value_"+str(tid)+ "' onchange='sselchanged(this)' oninput='this.nextElementSibling.value = this.value'>")
       ws.addHtml("<output>"+ str(settings.Tasks[tasknum].uservar[valnum]) +"</output>")
      elif dtype == 6:
       ws.addHtml("<div class='box'><select name='value_"+str(tid)+ "' id='value_"+str(tid)+ "' onchange='sselchanged(this)'>")
       optionnames = []
       if "," in dashtask.celldata[offs]["optionnames"]:
        optionnames = dashtask.celldata[offs]["optionnames"].split(",")
       elif ";" in dashtask.celldata[offs]["optionnames"]:
        optionnames = dashtask.celldata[offs]["optionnames"].split(",")
       options = []
       if "," in dashtask.celldata[offs]["options"]:
        options = dashtask.celldata[offs]["options"].split(",")
       elif ";" in dashtask.celldata[offs]["options"]:
        options = dashtask.celldata[offs]["options"].split(",")
       ol = len(optionnames)
       if ol> len(options):
        ol = len(options)
       for o in range(ol):
        ws.addHtml("<option value='"+ str(options[o]) +"'>"+ str(optionnames[o])  +"</option>")
       ws.addHtml("</select></div>")
      else:
        ws.addHtml("&nbsp;")
      if udata.strip() != "":
        ws.addHtml(textparse(udata))
      ws.addHtml("</td>")
     ws.addHtml("</tr>")
    ws.addHtml("</table>")
    ws.addHtml('<script type="text/javascript" src="/dash.js"></script>')
    ws.addHtml("<script>var elements=["+estr+"]; var values=["+vstr+"];")
    offs = (dashtask.taskdevicepluginconfig[0] * dashtask.taskdevicepluginconfig[1])
    pstr = ""
    for o in range(offs):
     if "min" in dashtask.celldata[o]:
      pstr += "[" + str(dashtask.celldata[o]["min"]) + "," + str(dashtask.celldata[o]["max"]) + "],"
     else:
      pstr += '[0,100],'
    ws.addHtml('var props=['+str(pstr)+'];')
    ws.addHtml("var ownurl='http://" + str(unet.get_ip())+":80';")
    ws.addHtml("refreshDatas();setInterval(function(){ getDatas(); }, "+ str(dashtask.interval*1000) +");</script>")
   else:
    ws.TXBuffer += "<p>Setup dashboard first!"
   if dashtask.taskdevicepluginconfig[2]:
    ws.sendHeadandTail("TmplStd",ws._TAIL)
   else:
    ws.TXBuffer += "</body></html>"
   httpResponse._write(ws.TXBuffer,strEncoding='UTF-8')
   ws.TXBuffer = ""
  except Exception as e:
   print("Config error, try to delete and recreate task!",e)
  return ws.TXBuffer

def textparse(ostr):
      resstr=str(ostr)
      if "{" in resstr or "&" in resstr:
       resstr = resstr.replace("{D}","˚").replace("&deg;","˚")
       resstr = resstr.replace("{<<}","«").replace("&laquo;","«")
       resstr = resstr.replace("{>>} ","»").replace("&raquo;","»")
       resstr = resstr.replace("{u} ","µ").replace("&micro; ","µ")
       resstr = resstr.replace("{E}","€").replace("&euro;","€")
       resstr = resstr.replace("{Y}","¥").replace("&yen;","¥")
       resstr = resstr.replace("{P}","£").replace("&pound;","£")
       resstr = resstr.replace("{c}","¢").replace("&cent;","¢")
       resstr = resstr.replace("{^1}","¹").replace("&sup1;","¹")
       resstr = resstr.replace("{^2}","²").replace("&sup2;","²")
       resstr = resstr.replace("{^3}","³").replace("&sup3;","³")
       resstr = resstr.replace("{1_4}","¼").replace("&frac14;","¼")
       resstr = resstr.replace("{1_2}","½").replace("&frac24;","½")
       resstr = resstr.replace("{3_4}","¾").replace("&frac34;","¾")
       resstr = resstr.replace("{+-}","±").replace("&plusmn;","±")
       resstr = resstr.replace("{x}","×").replace("&times;","×")
       resstr = resstr.replace("{..}","÷").replace("&divide;","÷")
      return resstr
