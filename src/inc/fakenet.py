#Unit for PC debugging with Python3
STA_IF = 0
AP_IF = 1
ETH_CLOCK_GPIO0_IN=0
ETH_CLOCK_GPIO16_OUT=16
ETH_CLOCK_GPIO17_OUT=17
PHY_LAN8720=0
PHY_TLK110=1
PHY_IP101=2

class WLAN():

  def __init__(self,t1=None,t2=None):
   self.a = True

  def isconnected(self):
   return self.a

  def connect(self,p1,p2):
   self.a = True

  def disconnect(self):
   self.a = False

  def active(self,a):
   self.a = a

  def config(self,essid=None,password=None,authmode=0):
   return "00"

  def ifconfig(self):
   return ['127.0.0.1']
