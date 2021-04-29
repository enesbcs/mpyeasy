#############################################################################
###################### Helper Library for Time functions ####################
#############################################################################
#
# Copyright (C) 2020 by Alexander Nagy - https://bitekmindenhol.blog.hu/
#
import time
import pglobals
import misc
try:
 from machine import Timer
except:
 pass

def get_us_from_sec(sec):
    return sec * 1000

class timer:
 def __init__(self,timerid):
  self.timerid = timerid
  self.state = 0 # 0:off,1:running,2:paused
  self.starttime = 0
  self.pausetime = 0
  self.lefttime  = 0
  self.timer = None
  self.timeractive = False
  self.callback = None
  self.retvalue = [-1,-1]
  self.looping = False
  self.loopcount = 0
  self.maxloops = -1
  self.timeout = 0
  self.laststart = 0

 def addcallback(self,callback):
  self.retvalue = [-1,-1]
  self.callback = callback

 def setretvalue(self,retvalue):
  self.retvalue = retvalue

 def start(self,timeout,usrcall=True,looping=False,maxloops=-1):
#  print("Timer",self.timerid,"started with timeout:",timeout)
  try:
   if self.timer is not None:
    try:
     self.timer.deinit()
    except:
     pass
   self.starttime = time.time()
   self.lefttime  = timeout
   self.state = 1
   self.timeractive = True
   self.looping = looping
   if usrcall or self.timeout==0:
    self.timeout = timeout
    self.maxloops = maxloops
    self.loopcount = 0
   self.loopcount += 1
   self.laststart = time.time()
   self.timer = Timer(self.timerid-1)
   self.timer.init(mode=Timer.ONE_SHOT,period=get_us_from_sec(timeout),callback=self.stop)
  except Exception as e:
   print(e)

 def stop(self,call=True):
#  print("Timer",self.timerid,"stopped")
  self.state = 0
  self.starttime = 0
  self.timeractive = False
  try:
   if self.timer is not None:
    self.timer.deinit()
  except:
   pass
  try:
   if call and self.callback:
    if self.retvalue[0] > -1:
     self.callback(self.timerid,self.retvalue) # callbacks with saved return value
    else:
     self.callback(self.timerid) # call rules with timer id only
  except Exception as e:
   print(e)
  if self.maxloops>-1:
   if self.loopcount>=self.maxloops: #loop count reached
    self.looping = False
  if self.looping and call: #autorestart timer
   self.start(self.timeout,False,True,self.maxloops)
  else:
   self.looping = False

 def pause(self):
  if self.state == 1:
   lefttime = time.time()-self.starttime
#   print("Timer",self.timerid,"runnning paused at",lefttime)
   if lefttime<self.lefttime:
    self.lefttime = self.lefttime - lefttime
    self.state = 2
    try:
     self.timer.deinit()
    except:
     pass

 def resume(self):
  if self.state == 2:
#   print("Timer",self.timerid,"runnning continues for",self.lefttime)
   self.timer = Timer(self.timerid-1)
   self.timer.init(mode=Timer.ONE_SHOT,period=get_us_from_sec(self.lefttime),callback=self.stop)
   self.starttime = time.time()
   self.state = 1
   self.pausetime = 0
   self.timer.start()

Timers = []
for t in range(0,pglobals.RULES_TIMER_MAX):
 Timers.append(timer(t+1))
