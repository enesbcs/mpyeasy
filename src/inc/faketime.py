#Unit for debugging with Python3
import time as Time

def ticks_diff(val1,val2):
 return val1-val2

def ticks_ms():
 return (Time.time()*1000)

def time():
 return Time.time()

def ticks_add(base,dif):
 return base+dif

def sleep_ms(interval):
 Time.sleep(interval/1000)

def localtime():
 return Time.localtime()
