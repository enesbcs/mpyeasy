import pglobals
import settings
import misc
try:
 import utime
 from machine import Pin, PWM
except:
 pass # do not load
import commands
from inc.upyrtttl.rtttl import RTTTL

commandlist = ["gpio","pwm","pulse","tone","rtttl","servo"]

hiddenpins = 0

def is_pin_analog(pin):
    res = (int(pin) in [0,2,4,12,13,14,15,25,26,27,32,33,34,35,36,39])
    return res

def is_pin_touch(pin):
    res = (int(pin) in [0,2,4,12,13,14,15,27,32,33])
    return res

def is_pin_valid(pin):
    global hiddenpins
    res = (int(pin) in [0,1,2,3,4,5,12,13,14,15,16,17,18,19,21,22,23,25,26,27,32,33,34,35,36,39])
    if hiddenpins==1:
     if (int(pin) in [9,10,37,38]):
      return True
    return res

def is_pin_dac(pin):
    res = (int(pin) in [25,26])
    return res

def is_pin_pwm(pin):
    global hiddenpins
    res = (int(pin) in [0,1,2,3,4,5,12,13,14,15,16,17,18,19,21,22,23,25,26,27,32,33])
    if hiddenpins==1:
     if (int(pin) in [9,10]):
      return True
    return res

def syncvalue(bcmpin,value):
 for x in range(0,len(settings.Tasks)):
  if (settings.Tasks[x]) and type(settings.Tasks[x]) is not bool: # device exists
   if (settings.Tasks[x].enabled):
     if (settings.Tasks[x].pluginid==29) and (settings.Tasks[x].taskdevicepin[0]==bcmpin): # output on specific pin
      settings.Tasks[x].uservar[0] = value
      if settings.Tasks[x].valuenames[0]!= "":
       commands.rulesProcessing(settings.Tasks[x].taskname+"#"+settings.Tasks[x].valuenames[0]+"="+str(value),pglobals.RULE_USER)
      settings.Tasks[x].plugin_senddata()
      break

def gpio_commands(cmd):
  res = False
  cmdarr = cmd.split(",")
  cmdarr[0] = cmdarr[0].strip().lower()
  if cmdarr[0] == "gpio":
   pin = -1
   val = -1
   logline = ""
   try:
    pin = int(cmdarr[1].strip())
    val = int(cmdarr[2].strip())
   except:
    pin = -1
   if pin>-1 and val in [0,1]:
    logline = "BCM"+str(pin)+" set to "+str(val)
    misc.addLog(pglobals.LOG_LEVEL_DEBUG,logline)
    suc = False
    try:
     suc = True
     selfpin = Pin(pin,Pin.OUT)
     selfpin.value(val)
     syncvalue(pin,val)
    except Exception as e:
     misc.addLog(pglobals.LOG_LEVEL_ERROR,"BCM"+str(pin)+": "+str(e))
     suc = False
   res = True
  elif cmdarr[0]=="pwm":
   pin = -1
   prop = -1
   logline = ""
   try:
    pin = int(cmdarr[1].strip())
    prop = int(cmdarr[2].strip())
   except:
    pin = -1
    prop = -1
   rfreq = 1000
   try:
    rfreq = int(cmdarr[3].strip())
   except:
    rfreq = 1000
   if pin>-1 and prop>-1:
    suc = False
    try:
     suc = True
     pwmchan = PWM(Pin(pin), freq=rfreq, duty=prop)
     if prop<=0:
       pwmchan.deinit()
     logline = "BCM"+str(pin)+" PWM "+str(prop)+" @ "+str(freq)+"Hz"
     misc.addLog(pglobals.LOG_LEVEL_DEBUG,logline)
    except Exception as e:
     misc.addLog(pglobals.LOG_LEVEL_ERROR,"BCM"+str(pin)+" PWM "+str(e))
     suc = False
   res = True
  elif cmdarr[0]=="pulse":
   pin = -1
   val = -1
   logline = ""
   try:
    pin = int(cmdarr[1].strip())
    val = int(cmdarr[2].strip())
   except:
    pin = -1
   dur = 100
   try:
    dur = int(cmdarr[3].strip())
   except:
    dur = 100
   if pin>-1 and val in [0,1]:
    logline = "BCM"+str(pin)+": Pulse started"
    misc.addLog(pglobals.LOG_LEVEL_DEBUG,logline)
    try:
     selfpin = Pin(pin,Pin.OUT)
     selfpin.value(val)
     utime.sleep_ms(dur)
     selfpin.value(1-val)
    except Exception as e:
     misc.addLog(pglobals.LOG_LEVEL_ERROR,"BCM"+str(pin)+": "+str(e))
     suc = False
    misc.addLog(pglobals.LOG_LEVEL_DEBUG,"BCM"+str(pin)+": Pulse ended")
   res = True

  elif cmdarr[0]=="tone":
   pin  = -1
   freq = -1
   dur  = 0
   gi = -1
   try:
    pin  = int(cmdarr[1].strip())
    freq = int(cmdarr[2].strip())
    dur  = int(cmdarr[3].strip())
   except:
    pin = -1
    freq = -1
    dur = 0
   if pin>-1 and freq>-1 and dur>0:
    suc = False
    try:
     suc = True
     beeper = play_tone(pin,freq,dur)
     beeper.deinit() # stop sound
    except Exception as e:
     misc.addLog(pglobals.LOG_LEVEL_ERROR,"BCM"+str(pin)+" Tone "+str(e))
     suc = False
   res = True

  elif cmdarr[0]=="rtttl":
   cmdarr = cmd.replace(":",",").split(",")
   pin  = -1
   gi = -1
   logline = ""
   try:
    pin  = int(cmdarr[1].strip())
   except:
    pin = -1
   if pin>-1:
    suc = False
    try:
     sp = cmd.find(":")
     if sp > -1:
      play_rtttl(pin,"t"+cmd[sp:])
     suc = True
    except Exception as e:
     misc.addLog(pglobals.LOG_LEVEL_ERROR,str(e))
     suc = False
   res = True

  elif cmdarr[0]=="servo":
   snr  = -1
   pin  = -1
   pos = -1
   logline = ""
   try:
    snr = int(cmdarr[1].strip())
    pin = int(cmdarr[2].strip())
    pos = int(cmdarr[3].strip())
   except:
    snr = -1
    pin = -1
    pos = 0
   if snr>-1 and pin>-1 and pos>0:
    suc = False
    try:
     suc = True
     logline = "BCM"+str(pin)+" to servo "+str(pos)+" angle"
     misc.addLog(pglobals.LOG_LEVEL_DEBUG,logline)
     setservoangle(pin,pos)
    except Exception as e:
     misc.addLog(pglobals.LOG_LEVEL_ERROR,"BCM"+str(pin)+" Servo "+str(e))
     suc = False
   res = True
  return res

def play_tone(pin,rfreq,delay):
  pwmchan = PWM(Pin(pin), freq=rfreq, duty=512)
  utime.sleep_ms(delay)
  return pwmchan

def setservoangle(servopin,angle):
    if angle>= 0 and angle<= 180:
     prop = (angle / 1.8) +20
     try:
       servo = machine.PWM(Pin(servopin),freq=50,duty=prop)
     except:
       misc.addLog(pglobals.LOG_LEVEL_ERROR,"Servo failed for pin "+str(servopin))

def play_rtttl(pin,notestr):
 notes = []
 try:
  notes = RTTTL(notestr)
 except Exception as e:
  misc.addLog(pglobals.LOG_LEVEL_ERROR,"RTTTL parse failed: "+str(e))
  return False
 try:
  pc = None
  for freq, msec in notes.notes():
      pc = play_tone(pin,int(freq),int(msec))
  pc.deinit()
 except Exception as e:
  pass
