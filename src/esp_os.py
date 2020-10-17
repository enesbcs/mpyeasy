try:
 import machine
 import esp
 import esp32
 import gc
except:
 pass

#esp.osdebug(None) #nodebug

def getfreq():
 try:
  f = machine.freq()
 except:
  f = 0
 return f

def setfreq(freq):
 try:
  machine.freq(freq)
 except:
  pass

def getstorage():
 try:
  s = esp.flash_size()
 except:
  s = 0
 return s

def read_cpu_temp():
 tc = 0
 try:
  tf = esp32.raw_temperature()
  tc = (tf-32.0)/1.8
 except:
  tc = 0
 return tc

def get_memory():
  ret = {'f':0,'u':0,'t':0}
  f = False
  try:
   gc.collect()
   ret['f'] = gc.mem_free()
   ret['u'] = gc.mem_alloc()
   ret['t'] = ret['u'] + ret['f']
  except:
   f = True
  if f: # try other ways
   try:
    import resource
    ret['u']= resource.getrusage(resource.RUSAGE_SELF)[2] * 1024
   except:
    pass
   try:
    import os
    ret['t'] = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')
    ret['f']  = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_AVPHYS_PAGES')
   except:
    pass
  return ret

def FreeMem():
  try:
   gc.collect()
   ret = gc.mem_free()
  except:
   ret = -1
  if ret==-1:
   ret = get_memory()['f']
  return ret

def psRamFound():
 found = False
 try:
  import esp32
  mi = get_memory()
  if int(mi['t'] ) > 300000:
   found = True
 except:
  pass
 return found

def reboot():
  try:
   machine.reset()
  except:
   pass

def getid():
  try:
   return machine.unique_id()
  except:
   return False
