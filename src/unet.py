try:
 import network
except:
 import inc.fakenet as network
import settings
try:
 import machine
except:
 pass
try:
 import utime
except:
 import inc.faketime as utime

_active_mode = 0
_current_ssid  = 0
wifi_sta = None
lan_if = None
_lan_mode = 0

def lan_init():
    global _lan_mode, lan_if
    if _lan_mode==1:
      return True
    try:
     pp = settings.HW['lan-pwr']
     if pp <= -1:
      pp = None
     else:
      pp = machine.Pin(pp)
     lan_if = network.LAN(mdc = machine.Pin(settings.HW['lan-mdc']), mdio = machine.Pin(settings.HW['lan-mdio']), power=pp, phy_type = settings.HW['lan-phy'], phy_addr=settings.HW['lan-addr'], clock_mode=settings.HW['lan-clk'])
     lan_if.active(True)
     if settings.Settings['LDHCP']==False:
          lan_if.ifconfig((settings.Settings['LIP'], settings.Settings['LMask'], settings.Settings['LGW'], settings.Settings['LDNS']))
     else:
          try:
           lan_if.ifconfig('dhcp')
          except:
           pass
     _lan_mode = 1
    except Exception as e:
     print("LAN connection error ",str(e))
     lan_if = None
     _lan_mode = 0

def lan_isconnected():
    global _lan_mode, lan_if
    if _lan_mode==1:
      try:
       if lan_if.isconnected():
        return True
      except:
        return False
    return False

def wifi_sta_mode(ordn=1):
    global _active_mode, _current_ssid, wifi_sta
    try:
     wifi_sta = network.WLAN(network.STA_IF)
    except:
     wifi_sta = None
     _current_ssid = 0
     return False
    _active_mode = (_active_mode | 1)
    forceconn = False
    if wifi_sta.isconnected():
      try:
         if settings.Settings['WDHCP']==False:
          wifi_sta.ifconfig((settings.Settings['WIP'], settings.Settings['WMask'], settings.Settings['WGW'], settings.Settings['WDNS']))
         else:
          wifi_sta.ifconfig('dhcp')
      except Exception as e:
         forceconn = True
    if not wifi_sta.isconnected() or forceconn:
        try:
         wifi_sta.active(True)
         if settings.Settings['WDHCP']==False:
          wifi_sta.ifconfig(config(settings.Settings['WIP'], settings.Settings['WMask'], settings.Settings['WGW'], settings.Settings['WDNS']))
         else:
          wifi_sta.ifconfig('dhcp')
        except Exception as e:
          pass
        _current_ssid = ordn
        try:
         if ordn==1 and settings.Settings['AP1SSID']:
          wifi_sta.connect(settings.Settings['AP1SSID'], settings.Settings['AP1KEY'])
         elif ordn==2 and settings.Settings['AP2SSID']:
          wifi_sta.connect(settings.Settings['AP2SSID'], settings.Settings['AP2KEY'])
        except:
         _current_ssid = 0

def wifi_sta_isconnected():
    global _active_mode, wifi_sta
    try:
     if (_active_mode & 1) == 1:
      wifi_sta = network.WLAN(network.STA_IF)
      if wifi_sta.isconnected():
        return True
    except:
     pass
    return False

def wifi_sta_disconnect(force=False):
    global _active_mode, _current_ssid, wifi_sta
    if ((_active_mode & 1) == 1) or force:
     try:
      wifi_sta = network.WLAN(network.STA_IF)
      wifi_sta.disconnect()
      wifi_sta.active(False)
     except:
      pass
     _current_ssid = 0
     if ((_active_mode & 1) == 1):
      _active_mode = _active_mode - 1

def wifi_ap_mode():
    global _active_mode
    _active_mode = (_active_mode | 2)
    wifi_ap = network.WLAN(network.AP_IF)
    wifi_ap.active(True)
    if settings.Settings["APKEY"]=="":
      amode = 0
    else:
      amode = 4
    wifi_ap.config(essid=settings.Settings["APSSID"],password=settings.Settings["APKEY"],authmode=amode)
    captiveok = False
    try:
     if settings.Settings["APCAPTIVE"]:
        from inc.microdns.microDNSSrv import MicroDNSSrv
        wifi_ap.ifconfig( ('172.217.28.1','255.255.255.0','172.217.28.1','172.217.28.1') )
        if MicroDNSSrv.Create({ '*' : '172.217.28.1' }):
          print("Captive DNS started")
          captiveok = True
        else:
          print("Captive DNS failed")
    except:
     pass
    if captiveok == False:
     wifi_ap.ifconfig( ('192.168.4.1','255.255.255.0','192.168.4.1','192.168.4.1') )

def wifi_ap_stop(force=False):
   global _active_mode
   if ((_active_mode & 2) == 2) or force:
    wifi_ap = network.WLAN(network.AP_IF)
    wifi_ap.active(False)
    if ((_active_mode & 2) == 2):
     _active_mode = _active_mode - 2

def get_ip(nm=""):
   global _active_mode, _lan_mode, lan_if
   wlan = None
   if nm=="STA":
     try:
      wlan = network.WLAN(network.STA_IF)
     except:
      return '0.0.0.0'
   elif nm=="AP":
     try:
      if (_active_mode & 2) == 2:
       wlan = network.WLAN(network.AP_IF)
     except:
      return '0.0.0.0'         
   elif nm=="LAN":
      wlan = lan_if
   else:
    if (_lan_mode==1):
      wlan = lan_if
    elif (_active_mode & 1) == 1:
      wlan = network.WLAN(network.STA_IF)
    elif (_active_mode & 2) == 2:
      wlan = network.WLAN(network.AP_IF)
    else:
      return '0.0.0.0'
   try:
    ipstr = wlan.ifconfig()[0]
   except:
    ipstr = '0.0.0.0'
   return ipstr

def get_rssi():
    global _active_mode, wifi_sta
    if (_active_mode & 1) == 1:
      wifi_sta = network.WLAN(network.STA_IF)
      try:
       return wifi_sta.status('rssi')
      except:
       pass
    return -100

def get_ssid():
    global _active_mode
    result = ""
    try:
     if (_active_mode & 1) == 1:
       wlan = network.WLAN(network.STA_IF)
     elif (_active_mode & 2) == 2:
      wlan = network.WLAN(network.AP_IF)
     else:
       return ''
     result = wlan.config('essid')
    except:
     pass
    return result

def get_mac(nm=""):
   global _active_mode, _lan_mode, lan_if
   result = ""
   wlan = None
   try:
    if nm=="STA":
      wlan = network.WLAN(network.STA_IF)
    elif nm=="AP":
      wlan = network.WLAN(network.AP_IF)
    elif nm=="LAN":
      wlan = lan_if
    else:
     if _lan_mode==1:
      wlan = lan_if
     elif (_active_mode & 1) == 1:
      wlan = network.WLAN(network.STA_IF)
     elif (_active_mode & 2) == 2:
      wlan = network.WLAN(network.AP_IF)
     else:
      return ""
    a = wlan.config('mac')
    result = '{:02x}:{:02x}:{:02x}:{:02x}:{:02x}:{:02x}'.format(a[0],a[1],a[2],a[3],a[4],a[5])
   except:
     return ""
   return result

def setntp(ntpserver, timezone):
   res = False
   try:
    import ntptime
    ntptime.host = ntpserver
    t = ntptime.time()
    tm = utime.gmtime(t+(timezone*60))
    machine.RTC().datetime((tm[0], tm[1], tm[2], tm[6] + 1, tm[3], tm[4], tm[5], 0))
    res = True
   except:
    res = False
   return res

def get_net_const(cname):
 if cname=="clk":
   return [network.ETH_CLOCK_GPIO0_IN, network.ETH_CLOCK_GPIO16_OUT, network.ETH_CLOCK_GPIO17_OUT]
 elif cname=="c0i":
   return network.ETH_CLOCK_GPIO0_IN
 elif cname=="c16o":
  try:
   return network.ETH_CLOCK_GPIO16_OUT
  except:
   return -1
 elif cname=="c17o":
  try:
   return network.ETH_CLOCK_GPIO17_OUT
  except:
   return -1
 elif cname=="phy":
   return [-1,network.PHY_LAN8720, network.PHY_TLK110, network.PHY_IP101]
 elif cname=="8720":
   return network.PHY_LAN8720
 elif cname=="110":
   return network.PHY_TLK110
 elif cname=="101":
   return network.PHY_IP101
