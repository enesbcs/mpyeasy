import gc
import pglobals

HTML_SYMBOL_WARNING = "&#9888;"
TASKS_PER_PAGE = 12
TXBuffer = ""
navMenuIndex = 0
_HEAD = False
_TAIL = True
INT_MIN = -2147483648
INT_MAX = 2147483647

def arg(argname,parent):
 return (argname in parent and parent[argname] or '')

def getWebPageTemplateDefault(tmplName):
  tmpl = ""
  file = open(pglobals.fpath+"templ/"+tmplName+".txt","r")
  try:
   tmpl = file.read()
  except:
    tmpl = ""
  if tmpl == "":
    file = open(pglobals.fpath+"templ/TmplStd.txt","r")
    try:
     tmpl = file.read()
    except:
      tmpl = ""
  return tmpl

def getWebPageTemplateVar( varName ):
  global TXBuffer, navMenuIndex
#  print(5,misc.get_memory(),varName)
  import settings
  import pglobals
  if (varName == "name"):
    TXBuffer += settings.Settings["Name"]
  elif (varName == "unit"):
    TXBuffer += str(settings.Settings["Unit"])
  elif (varName == "menu"):
    TXBuffer2 = []
    TXBuffer2.append("<div class='menubar'>")
    for i in range(len(pglobals.gpMenu)):
      TXBuffer2.append("<a class='menu")
      if (i == navMenuIndex):
        TXBuffer2.append(" active")
      TXBuffer2.append("' href='")
      TXBuffer2.append(pglobals.gpMenu[i][1])
      TXBuffer2.append("'>")
      TXBuffer2.append(pglobals.gpMenu[i][0])
      TXBuffer2.append("</a>")
    TXBuffer2.append("</div>")
    TXBuffer += ''.join(TXBuffer2)
    TXBuffer2 = []

  elif (varName == "logo"):
    pass

  elif (varName == "css"):
    try:
      file = open("www/defaultu.css","r") # compat /
      TXBuffer += "<link rel=\"stylesheet\" type=\"text/css\" href=\"defaultu.css\">"
      file.close()
    except:
      pass

  elif (varName == "js"):
    TXBuffer += (
                  "<script><!--\n"
                  "function dept_onchange(frmselect) {frmselect.submit();}"
                  "\n//--></script>")
  else:
    pass
#  print(6,misc.get_memory())

def sendHeadandTail(tmplName, Tail = False):
  global TXBuffer
  pageTemplate = ""
  #int indexStart, indexEnd;
  #String varName;  //, varValue;
  gc.collect() # compat
  pageTemplate = getWebPageTemplateDefault(tmplName)
  if (Tail):
    contentpos = pageTemplate.find("{{content}}")
    TXBuffer += pageTemplate[11+contentpos:]
  else:
    indexStart = pageTemplate.find("{{")
    while (indexStart >= 0):
      TXBuffer += pageTemplate[0:indexStart]
      pageTemplate = pageTemplate[indexStart:]
      indexEnd = pageTemplate.find("}}")
      if (indexEnd > 0):
        varName = pageTemplate[2:indexEnd]
        pageTemplate = pageTemplate[(indexEnd + 2):]
        varName.lower();

        if (varName == "content"): # is var == page content?
          break #;  // send first part of result only
        elif (varName == "error"):
          getErrorNotifications()
        else:
          getWebPageTemplateVar(varName)
      else:
        pageTemplate = pageTemplate[2:]
      indexStart = pageTemplate.find("{{")
  pageTemplate = ""
  varName =""
  gc.collect() # compat
  
def getErrorNotifications():
 return False

def addButton(url, label):
 global TXBuffer
 TXBuffer += "<a class='button link' href='{0}'>{1}</a>".format(url,label)

def addWideButton(url, label, color):
 global TXBuffer
 TXBuffer += "<a class='button link wide{0}' href='{1}'>{2}</a>".format(color,url,label)

def addFormHeader(header1, header2=""):
  global TXBuffer
  if header2 == "":
   TXBuffer += "<TR><TD colspan='2'><h2>{0}</h2>".format(header1)
  else:
   TXBuffer += "<TR><TH>{0}<TH>{1}".format(header1,header2)

def addTextBox(fid, value, maxlength):
  global TXBuffer
  TXBuffer += "<input class='wide' type='text' name='{0}' id='{1}' maxlength='{2}' value='{3}'>".format(fid,fid,maxlength,value)

def addFormTextBox(label, fid, value, maxlength):
  addRowLabel(label)
  addTextBox(fid, value, maxlength)

def addRowLabel(label):
  global TXBuffer
  TXBuffer += "<TR><TD>{0}:<TD>".format(label)

def addFormNumericBox(label, fid, value, minv=INT_MIN, maxv=INT_MAX):
  addRowLabel(label)
  addNumericBox(fid, value, minv, maxv)

def addNumericBox(fid, value, minv=INT_MIN, maxv=INT_MAX):
  global TXBuffer
  TXBuffer += "<input class='widenumber' type='number' name='{0}'".format(fid)
  if (minv != INT_MIN):
    TXBuffer += " min={0}".format(minv)
  if (maxv != INT_MAX):
    TXBuffer += " max={0}".format(maxv)
  TXBuffer += " value={0}>".format(value)

def addSubmitButton(value = "Submit", name="Submit"):
  global TXBuffer
  TXBuffer += "<input class='button link' type='submit' value='{0}' name='{1}'><div id='toastmessage'></div><script type='text/javascript'>toasting();</script>".format(value,name)

def getControllerSymbol(indexs):
  ret = "<p style='font-size:20px'>&#"
  ret += str(10102+int(indexs))
  ret += ";</p>"
  return ret

def addEnabled(enabled):
  global TXBuffer
  if (enabled):
    TXBuffer += "<span class='enabled on'>&#10004;</span>"
  else:
    TXBuffer += "<span class='enabled off'>&#10060;</span>"

def addSelector_Head(fid, reloadonchange):
  global TXBuffer
  TXBuffer += "<select id='selectwidth' name='{0}'".format(fid)
  if (reloadonchange):
    TXBuffer += " onchange='return dept_onchange(frmselect)'>"
  TXBuffer += ">"

def addSelector_Item(option, sindex, selected, disabled, attr=""):
  global TXBuffer
  TXBuffer += "<option value={0}".format(sindex)
  if (selected):
    TXBuffer += " selected"
  if (disabled):
    TXBuffer += " disabled"
  if (attr and attr.length() > 0):
    TXBuffer += " {0}".format(attr)
  TXBuffer += ">{0}</option>".format(option)

def addSelector_Foot():
  global TXBuffer
  TXBuffer += "</select>"

def addFormCheckBox(label, fid, checked):
  addRowLabel(label)
  addCheckBox(fid, checked)

def addCheckBox(fid, checked):
  global TXBuffer
  TXBuffer += "<label class='container'>&nbsp;<input type='checkbox' id='{0}' name='{1}'".format(fid,fid)
  if (checked):
    TXBuffer += " checked"
  TXBuffer += "><span class='checkmark'></span></label>"

def addFormSeparator(clspan):
 global TXBuffer
 TXBuffer += "<TR><TD colspan='{0}'><hr>".format(clspan)

def addFormPasswordBox(label, fid, password, maxlength):
  global TXBuffer
  addRowLabel(label);
  TXBuffer += "<input class='wide' type='password' name='{0}' maxlength={1} value='".format(fid,maxlength)
  if (password != ""):
    TXBuffer += "*****"
  TXBuffer += "'>"

def addFormSubHeader(header):
  global TXBuffer
  TXBuffer += "<TR><TD colspan='2'><h3>{0}</h3>".format(header)

def addFormPinSelect(label,fid,choice,pfilter=0):
  addRowLabel(label)
  addPinSelect(False,fid,choice,pfilter)

def addPinSelect(fori2c,name,choice,pfilter=0):
  global TXBuffer
  import settings
  addSelector_Head(name,False)
  addSelector_Item("None",-1,None,False,"")
  try:
   import inc.lib_gpiohelper as gpiohelper
   for x in range(0,40):
    valid = False
    if pfilter==0:
     if gpiohelper.is_pin_valid(x): #all
      valid = True
    elif pfilter==1:
      if gpiohelper.is_pin_pwm(x): #out/pwm
       valid = True
    elif pfilter==2:
      if gpiohelper.is_pin_analog(x): #ana
       valid = True
    elif pfilter==4:
      if gpiohelper.is_pin_touch(x): #tch
       valid = True
    elif pfilter==8:
      if gpiohelper.is_pin_dac(x): #dac
       valid = True
    if valid:
     oname = "GPIO-{0}".format(str(x))
     try:
      amode = 0
      pf = False
      for p in range(len(settings.Pinout)):
       if settings.Pinout[p]['p']==x:
        amode = settings.Pinout[p]['m']
        pf = True
        break
      if amode==9 and pf:
       oname += " - {0}".format(settings.Pinout[p]['d'])
      elif amode>0:
       oname += " - {0}".format(settings.PinStates[amode])
     except Exception as e:
      print(e)
     addSelector_Item(oname,x,(str(choice)==str(x)),False,"")
  except:
   pass
  addSelector_Foot()

def addUnit(unit):
  global TXBuffer
  TXBuffer += " [{0}]".format(unit)

def addFormSelector(label, fid, optionCount, options, indices, attr, selectedIndex, reloadonchange = False):
  addRowLabel(label)
  addSelector(fid, optionCount, options, indices, attr, selectedIndex, reloadonchange)

def addSelector(fid, optionCount, options, indices, attr, selectedIndex, reloadonchange):
  global TXBuffer
  sindex = 0
  TXBuffer += "<select id='selectwidth' name='{0}'".format(fid)
  if (reloadonchange):
    TXBuffer += " onchange='return dept_onchange(frmselect)'>"
  TXBuffer += ">"
  for x in range(optionCount):
    if (indices):
      sindex = indices[x]
    else:
      sindex = x
    TXBuffer += "<option value={0}".format(sindex)
    if (int(selectedIndex) == int(sindex)):
      TXBuffer += " selected"
    if (attr):
      TXBuffer += " {0}".format(attr[x])
    TXBuffer += ">{0}</option>".format(options[x])
  TXBuffer += "</select>"

def addSelector_Head(fid, reloadonchange):
  global TXBuffer
  TXBuffer += "<select id='selectwidth' name='{0}'".format(fid)
  if (reloadonchange):
    TXBuffer += " onchange='return dept_onchange(frmselect)'>"
  TXBuffer += ">"

def addSelector_Item(option, sindex, selected, disabled, attr=""):
  global TXBuffer
  TXBuffer += "<option value={0}".format(sindex)
  if (selected):
    TXBuffer += " selected"
  if (disabled):
    TXBuffer += " disabled"
  if (attr and attr.length() > 0):
    TXBuffer += " {0}".format(attr)
  TXBuffer += ">{0}</option>".format(option)

def addSelector_Foot():
  global TXBuffer
  TXBuffer += "</select>"

def addFormNote(text):
  global TXBuffer
  TXBuffer += "<TR><TD><TD><div class='note'>Note: {0}</div>".format(text)

def addHtml(html):
 global TXBuffer
 TXBuffer += html

def addCopyButton(value, delimiter, name,dist=""):
  global TXBuffer
  TXBuffer += "<script>function setClipboard"+str(dist)+"() { var clipboard = ''; max_loop = 100; for (var i = 1; i < max_loop; i++){ var cur_id = '"
  TXBuffer += str(value)
  TXBuffer += "_' + i; var test = document.getElementById(cur_id); if (test == null){ i = max_loop + 1;  } else { clipboard += test.innerHTML.replace(/<[Bb][Rr]\\s*\\/?>/gim,'\\n') + '"
  TXBuffer += str(delimiter)
  TXBuffer += "'; } }"
  TXBuffer += "clipboard = clipboard.replace(/<\\/[Dd][Ii][Vv]\\s*\\/?>/gim,'\\n');"
  TXBuffer += "clipboard = clipboard.replace(/<[^>]*>/gim,'');"
  TXBuffer += "var tempInput = document.createElement('textarea'); tempInput.style = 'position: absolute; left: -1000px; top: -1000px'; tempInput.innerHTML = clipboard;"
  TXBuffer += "document.body.appendChild(tempInput); tempInput.select(); document.execCommand('copy'); document.body.removeChild(tempInput); alert('Copied: \"' + clipboard + '\" to clipboard!') }</script>"
  TXBuffer += "<button class='button link' onclick='setClipboard"+str(dist)+"()'>"
  TXBuffer += str(name)
  TXBuffer += "</button>"

def addFormLogLevelSelect(label, sid, choice):
  addRowLabel(label)
  addLogLevelSelect(sid,choice)

def addLogLevelSelect(name,choice):
  options=[]
  optionvalues=[]
  for l in range(0,10):
   lvlname = getLogLevelDisplayString(l)
   if lvlname!="":
    options.append(lvlname)
    optionvalues.append(l)
  addSelector(name, len(options), options, optionvalues, None, choice, False)

def getLogLevelDisplayString(lvl):
 res = ""
 if lvl == 0:
  res = "None"
 elif lvl == pglobals.LOG_LEVEL_ERROR:
  res ="Error"
 elif lvl == pglobals.LOG_LEVEL_INFO:
  res ="Info"
 elif lvl == pglobals.LOG_LEVEL_DEBUG:
  res ="Debug"
 elif lvl == pglobals.LOG_LEVEL_DEBUG_MORE:
  res ="Debug More"
 elif lvl == pglobals.LOG_LEVEL_DEBUG_DEV:
  res ="Debug Developer"
 return res
