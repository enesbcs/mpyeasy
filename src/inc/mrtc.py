import inc.uRTC.urtc as urtc
import machine

I2C_RTC = None

def rtcinit(rtype,i2cl,raddress=0x68):
  global I2C_RTC
  if raddress==0:
   maddress = 0x68
  else:
   maddress = raddress
  if I2C_RTC is None:
   try:
    if rtype==1307:
     I2C_RTC = urtc.DS1307(i2cl,address=maddress)
    elif rtype==3231:
     I2C_RTC = urtc.DS3231(i2cl,address=maddress)
    elif rtype==8523:
     I2C_RTC = urtc.PCF8523(i2cl,address=maddress)
   except Exception as e:
    print("rtc ",str(e))#debug
    I2C_RTC = None
    return False
  return True

def setrtctime(timearr=None):
    global I2C_RTC
    try:
     if timearr is None:
      inttime = machine.RTC().datetime() #get time from esp32
     else:
      inttime = timearr
     it = urtc.datetime_tuple(year=inttime[0],month=inttime[1],day=inttime[2],weekday=inttime[3],hour=inttime[4],minute=inttime[5],second=inttime[6])
     I2C_RTC.datetime(it) # set time on RTC
    except Exception as e:
     return False
    return True

def getrtctime():
    global I2C_RTC
    rtime = None
    try:
     rtime = I2C_RTC.datetime() # get time from rtc
    except:
     pass
    return rtime

def setsystime(timearr=None):
    global I2C_RTC
    try:
     if timearr is None:
      tm = I2C_RTC.datetime() # get time from rtc
     else:
      tm = timearr
     machine.RTC().datetime((tm[0], tm[1], tm[2], tm[3], tm[4], tm[5], tm[6],0))
     return True
    except Exception as e:
     return False
