import pglobals
import settings
import gc
try:
 import utime
except:
 import inc.faketime as utime
import re

SystemLog = []
start_time = utime.time()

def WebLog(lvl,logstamp,line):
   global SystemLog
   if len(SystemLog)>pglobals.LOG_MAXLINES:
      tvar = []
      for i in range(0,10):
         SystemLog[i]=SystemLog[pglobals.LOG_MAXLINES-10+i]
      SystemLog = tvar
   SystemLog.append({  "t":logstamp,"l":line,"lvl":lvl})

def addLog(loglevel, line):
   lstamp = strtime(1)#str(utime.ticks_ms())
   if int(loglevel)<=int(settings.AdvSettings["webloglevel"]):
      WebLog(loglevel,lstamp,line)
   if int(loglevel)<=int(settings.AdvSettings["consoleloglevel"]):
    if loglevel==pglobals.LOG_LEVEL_ERROR:
     lstamp += ": !"
    else:
     lstamp += ": "
    print(lstamp+line)

def getuptime(form=0):
  global start_time
  upts = int(utime.time()-start_time)
  if form==1:
   days, remainder = divmod(upts, 86400)
   hours, remainder2 = divmod(remainder, 3600)
   minutes, seconds  = divmod(remainder2,60)
   upts = "{0} days {1} hours {2} minutes".format(days,hours,minutes)
  elif form==2:
   upts = int(upts / 60)
  return upts

def formatnum(num,decimal):
 res = ""
 try:
  decimal = int(decimal)
 except:
  decimal=0
 try:
  num=float(num)
 except:
  pass
 if decimal<0:
  res = str(num)
 else:
  nformat = "{0:."+str(decimal)+"f}"
  try:
   res = nformat.format(num)
  except:
   res = num
 return res

def strtime(ttype=0): #0:ymd hms 1:hms
 try:
  ret = utime.localtime()
 except:
  pass
 rv = ""
 try:
  if ttype==0:
   rv = '{:04}-{:02}-{:02} {:02}:{:02}:{:02}'.format(ret[0],ret[1],ret[2],ret[3],ret[4],ret[5])
  elif ttype==1:
   rv = '{:02}:{:02}:{:02}'.format(ret[3],ret[4],ret[5])
  else:
   rv = str(ret)
 except Exception as e:
   print(e)
   rv = str(ret)
 return rv

def get_battery_value():
 bval = 255
 try:
  if settings.AdvSettings["battery"]["enabled"]:
   bval = float(settings.Tasks[int(settings.AdvSettings["battery"]["tasknum"])].uservar[int(settings.AdvSettings["battery"]["taskvaluenum"])])
  else:
   bval = 255
 except:
  bval = 255
 if bval!=255:
  if bval<0:
   bval = 0
  elif bval>100:
   bval = 100
 return bval

def findall(restr,tstr): #missing from mpy regex
 fok = True
 tstr2 = tstr
 res = []
 while fok:
  m = re.search(restr,tstr2)
  if m is not None:
   rstr = m.group(1)
   if rstr not in res:
    res.append(rstr)
   tstr2 = tstr2.replace(m.group(0),"")
  else:
   fok = False
 return res

def mvtoarr(mv,rtype): # convert bloody memoryview to bytearray or array for human beings
     if rtype==0:
      resarr = bytearray()
     elif rtype==1:
      resarr = []
     for i in range(len(mv)):
      try:
       resarr.append(mv[i])
      except:
       pass
     return resarr
