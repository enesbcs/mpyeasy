import webserver_global as ws
import settings
import inc.lib_gpiohelper as gpiohelp
import esp_os
import unet
try:
 import inc.libhw as libhw
except:
 pass

def handle_hw(httpResponse,responsearr):
  ws.navMenuIndex=3
  ws.TXBuffer = ""
  httpResponse.WriteResponseOk(
        headers = ({'Cache-Control': 'no-cache'}),
        contentType = 'text/html',
        contentCharset = 'UTF-8',
        content = "" )
  method = ws.arg("method",responsearr)
  saved = ws.arg("Submit",responsearr)
  if (saved):
   try:
    tvar = int(ws.arg('freq',responsearr))
    esp_os.setfreq(tvar)
    settings.HW['freq']=int(tvar)
    settings.HW['psram-cs']= int(ws.arg('psram-cs',responsearr))
    settings.HW['psram-clk']= int(ws.arg('psram-clk',responsearr))
   except:
    pass
   iname=""
   tname=""
   try:
    for i in range(2):
     iname = "i2c{0}".format(i)
     settings.HW[iname] = (ws.arg(iname,responsearr) == "on")
     if settings.HW[iname]:
       tname = iname+"-freq"
       settings.HW[tname] = int(ws.arg(tname,responsearr))
       tname = iname+"-sda"
       settings.HW[tname] = int(ws.arg(tname,responsearr))
       tname = iname+"-scl"
       settings.HW[tname] = int(ws.arg(tname,responsearr))
   except:
    pass
   try:
    if 'spic' in responsearr:
     iname = 'spic'
     settings.HW[iname] = (ws.arg(iname,responsearr) == "on")
     tname = iname+"-clk"
     settings.HW[tname] = int(ws.arg(tname,responsearr))
     tname = iname+"-mosi"
     settings.HW[tname] = int(ws.arg(tname,responsearr))
     tname = iname+"-miso"
     settings.HW[tname] = int(ws.arg(tname,responsearr))
     tname = iname+"-baud"
     settings.HW[tname] = int(ws.arg(tname,responsearr))
   except:
    pass
   try:
    for i in range(1,3):
      iname = "spi{0}".format(i)
      if 'spic' in responsearr:
       settings.HW[iname] = False
      else:
       settings.HW[iname] = (ws.arg(iname,responsearr) == "on")
      if settings.HW[iname]:
       tname = iname+"-cs"
       settings.HW[tname] = int(ws.arg(tname,responsearr))
       tname = iname+"-baud"
       settings.HW[tname] = int(ws.arg(tname,responsearr))
   except:
    pass
   try:
    for i in range(1,3):
     iname = "uart{0}".format(i)
     settings.HW[iname] = (ws.arg(iname,responsearr) == "on")
     if settings.HW[iname]:
       tname = iname+"-rx"
       settings.HW[tname] = int(ws.arg(tname,responsearr))
       tname = iname+"-tx"
       settings.HW[tname] = int(ws.arg(tname,responsearr))
       tname = iname+"-baud"
       settings.HW[tname] = int(ws.arg(tname,responsearr))
       tname = iname+"-timeout"
       settings.HW[tname] = int(ws.arg(tname,responsearr))
   except:
    pass
   try:
    li = int(ws.arg("lanphy",responsearr))
   except:
    li = -1
   settings.HW["lan-phy"] = li
   if li >-1 and ("lanphy" in responsearr):
    settings.HW["lan-mdc"] = int(ws.arg("lanmdc",responsearr))
    settings.HW["lan-mdio"] = int(ws.arg("lanmdio",responsearr))
    settings.HW["lan-pwr"] = int(ws.arg("lanpwr",responsearr))
    settings.HW["lan-addr"] = int(ws.arg("lanaddr",responsearr))
    settings.HW["lan-clk"] = int(ws.arg("lanclk",responsearr))

   if "p0" in responsearr:
    for p in range(40):
     pv = -1
     try:
      pv = int(ws.arg("p"+str(p),responsearr))
     except:
      pv = -1
     if pv > -1:
      psuc = False
      for ap in range(len(settings.Pinout)):
       if int(settings.Pinout[ap]['p']) == int(p):
        settings.Pinout[ap]['m'] = pv
        psuc = True
        break
      if psuc==False:
        settings.Pinout.append({'p':p,'m':pv})
   settings.savehwsettings()
   settings.savepinout()
   try:
    libhw.initgpio()
   except:
    pass
#  else:
#   settings.loadhwsettings()
#   settings.loadpinout()

  ws.sendHeadandTail("TmplStd",ws._HEAD)
  ws.addHtml("<p><div><a class='menu2' href='hardware'>Main</a> | <a class='menu2' href='hardware?method=i2c'>I2C</a> | <a class='menu2' href='hardware?method=spi'>SPI</a> | <a class='menu2' href='hardware?method=uart'>UART</a> | <a class='menu2' href='hardware?method=lan'>LAN</a></div>")
  ws.TXBuffer += "<form name='frmselect' method='post'><table class='normal'>"
  if method=="":
#   ws.addFormSeparator(3)
   ws.addFormHeader("Main")
   httpResponse._write(ws.TXBuffer,strEncoding='UTF-8')
   ws.TXBuffer = ""
   options = ['80','160','240']
   optionvalues = [80000000, 160000000, 240000000]
   afreq = int(esp_os.getfreq())
   if afreq not in optionvalues:
    optionvalues.append(afreq)
    options.append(str(afreq))
   ws.addFormSelector("Core speed","freq",len(optionvalues),options,optionvalues,None,afreq)
   ws.addUnit('MHz')
   ws.addFormPinSelect("PSRAM-CS",'psram-cs',settings.HW['psram-cs'],1)
   ws.addFormPinSelect("PSRAM-CLK",'psram-clk',settings.HW['psram-clk'],1)
   ws.addFormNote("Set to none only when no PSRAM connected!")
   httpResponse._write(ws.TXBuffer,strEncoding='UTF-8')
   ws.TXBuffer = ""

  if method=="i2c":
   ws.addFormHeader("I2C")
   options = ['100','400']
   optionvalues = [100000, 400000]
   iname = ""
   tname = ""
   for i in range(2):
    iname = "i2c{0}".format(i)
    ws.addFormCheckBox("Enable I2C-"+str(i),iname,settings.HW[iname])
    tname = iname+"-freq"
    ws.addFormSelector("Speed",tname,len(optionvalues),options,optionvalues,None,settings.HW[tname])
    ws.addUnit('kHz')
    tname = iname+"-sda"
    tval = settings.HW[tname]
    if tval<0:
     if i==0:
      tval = 21
     else:
      tval = 16
    ws.addFormPinSelect("SDA",tname,tval,1)
    tname = iname+"-scl"
    tval = settings.HW[tname]
    if tval<0:
     if i==0:
      tval = 22
     else:
      tval = 17
    ws.addFormPinSelect("SCL",tname,tval,1)
   httpResponse._write(ws.TXBuffer,strEncoding='UTF-8')
   ws.TXBuffer = ""

  if method=="spi":
   ws.addFormHeader("SPI")
   options = ['1','5','10','18','20','26','40','48','80']
   optionvalues = [10000000,50000000,10000000,18000000,20000000,26000000,40000000,48000000,80000000]
   for i in range(1,3):
    iname = "spi{0}".format(i)
    ws.addFormCheckBox("Enable Hardware SPI-"+str(i),iname,settings.HW[iname])
    tname = iname+"-baud"
    aspd = settings.HW[tname]
    if aspd<1:
     aspd = 18000000
    ws.addFormSelector("Speed",tname,len(optionvalues),options,optionvalues,None,aspd)
    ws.addUnit("Mhz")
    tname = iname+"-cs"
    tval = settings.HW[tname]
    if tval<0:
     if i==1:
      tval = 15
     else:
      tval = 5
    ws.addFormPinSelect("CS",tname,tval,1)
   try:
    iname = "spic"
    ws.addFormCheckBox("Enable Custom SPI",iname,settings.HW[iname])
    tname = iname+"-baud"
    aspd = settings.HW[tname]
    if aspd<1:
     aspd = 18000000
    ws.addFormSelector("Speed",tname,len(optionvalues),options,optionvalues,None,aspd)
    ws.addUnit("Mhz")
    tname = iname+"-clk"
    ws.addFormPinSelect("CLK",tname,settings.HW[tname],1)
    tname = iname+"-mosi"
    ws.addFormPinSelect("MOSI",tname,settings.HW[tname],1)
    tname = iname+"-miso"
    ws.addFormPinSelect("MISO",tname,settings.HW[tname],0)
   except Exception as e:
    settings.HW[iname] = 0
    settings.HW[iname+"-clk"] = -1
    settings.HW[iname+"-mosi"] = -1
    settings.HW[iname+"-miso"] = -1
    settings.HW[iname+"-baud"] = 0

   httpResponse._write(ws.TXBuffer,strEncoding='UTF-8')
   ws.TXBuffer = ""

  if method=="uart":
   ws.addFormHeader("UART")
   for i in range(1,3):
    iname = "uart{0}".format(i)
    ws.addFormCheckBox("Enable UART-"+str(i),iname,settings.HW[iname])
    tname = iname+"-baud"
    ws.addFormNumericBox("Baud",tname,settings.HW[tname],0,921600)
    tname = iname+"-timeout"
    ws.addFormNumericBox("Timeout",tname,settings.HW[tname],0,50000)
    tname = iname+"-rx"
    tval = settings.HW[tname]
    if tval<0:
     if i==0:
      tval = 9
     else:
      tval = 16
    ws.addFormPinSelect("RX",tname,tval,1)
    tname = iname+"-tx"
    tval = settings.HW[tname]
    if tval<0:
     if i==0:
      tval = 10
     else:
      tval = 17
    ws.addFormPinSelect("TX",tname,tval,1)
   httpResponse._write(ws.TXBuffer,strEncoding='UTF-8')
   ws.TXBuffer = ""

  if method=="lan":
   try:
    optionvalues1 = unet.get_net_const("phy")
    optionvalues2 = unet.get_net_const("clk")
    lanok = True
   except Exception as e:
#    print("LAN failed ",e)#debug
    lanok = False
   if lanok:
    ws.addFormHeader("LAN RMII interface")
    options = ['Disabled','LAN8720','TLK110','IP101']
    ws.addFormSelector("LAN PHY","lanphy",len(optionvalues1),options,optionvalues1,None,settings.HW["lan-phy"])
    options = ['GPIO0 (default)','GPIO16','GPIO17']
    ws.addFormSelector("LAN CLK mode","lanclk",len(optionvalues2),options,optionvalues2,None,settings.HW["lan-clk"])
    ws.addFormNumericBox("PHY Address","lanaddr",settings.HW["lan-addr"],0,0x1F)
    ws.addFormPinSelect("PHY MDC","lanmdc",settings.HW["lan-mdc"],1)
    ws.addFormPinSelect("PHY MDIO","lanmdio",settings.HW["lan-mdio"],1)
    ws.addFormPinSelect("PHY Power enable","lanpwr",settings.HW["lan-pwr"],1)
   httpResponse._write(ws.TXBuffer,strEncoding='UTF-8')
   ws.TXBuffer = ""

  if method=="":
   ws.addHtml("<tr><th>GPIO</th><th>Requested startup state</th><th>Value</th></tr>")
   for p in range(40):
    if gpiohelp.is_pin_valid(p):
     reserved = False
     value = ""
     if settings.HW['psram-cs']==p:
      reserved = True
      value = "PSRAM-CS"
     elif settings.HW['psram-clk']==p:
      reserved = True
      value = "PSRAM-CLK"
     if settings.HW["lan-phy"]>-1:
      cpin = 0
      if unet.get_net_const("c16o")==settings.HW["lan-clk"]:
       cpin = 16
      elif unet.get_net_const("c17o")==settings.HW["lan-clk"]:
       cpin = 17
      if p==settings.HW["lan-mdc"]:
       reserved = True
       value = "LAN MDC"
      elif p==settings.HW["lan-mdio"]:
       reserved = True
       value = "LAN MDIO"
      elif p==settings.HW["lan-pwr"]:
       reserved = True
       value = "LAN PWR"
      elif p==cpin:
       reserved = True
       value = "LAN CLK"
      if p in [22,19,21,26,25,27]:
       reserved = True
       value = "RMII LAN"

     if settings.HW['i2c0']:
      if settings.HW['i2c0-sda']==p:
       reserved = True
       value = "I2C0-SDA"
      elif settings.HW['i2c0-scl']==p:
       reserved = True
       value = "I2C0-SCL"
     if settings.HW['i2c1']:
      if settings.HW['i2c1-sda']==p:
       reserved = True
       value = "I2C1-SDA"
      elif settings.HW['i2c1-scl']==p:
       reserved = True
       value = "I2C1-SCL"
     if settings.HW['uart1']:
      if settings.HW['uart1-rx']==p:
       reserved = True
       value = "UART1-RX"
      elif settings.HW['uart1-tx']==p:
       reserved = True
       value = "UART1-TX"
     if settings.HW['uart2']:
      if settings.HW['uart2-rx']==p:
       reserved = True
       value = "UART2-RX"
      elif settings.HW['uart2-tx']==p:
       reserved = True
       value = "UART2-TX"
     if settings.HW['spi1']: # hspi
      if settings.HW['spi1-cs']==p:
       reserved = True
       value = "SPI1-CS"
      elif p==12:
       reserved = True
       value = "SPI1-MISO"
      elif p==13:
       reserved = True
       value = "SPI1-MOSI"
      elif p==14:
       reserved = True
       value = "SPI1-CLK"
     if settings.HW['spi2']: # vspi
      if settings.HW['spi2-cs']==p:
       reserved = True
       value = "SPI2-CS"
      elif p==19:
       reserved = True
       value = "SPI2-MISO"
      elif p==23:
       reserved = True
       value = "SPI2-MOSI"
      elif p==18:
       reserved = True
       value = "SPI2-CLK"
     if 'spic' in responsearr:
      if settings.HW['spic']: # custom spi
       if settings.HW['spic-clk']==p:
        reserved = True
        value = "SPI-CLK"
       elif settings.HW['spic-miso']==p:
        reserved = True
        value = "SPI-MISO"
       elif settings.HW['spic-mosi']==p:
        reserved = True
        value = "SPI-MOSI"
     if reserved==False:
      if p==1:
       reserved = True
       value = "UART0-TX"
      elif p==3:
       reserved = True
       value = "UART0-RX"
     options = settings.PinStates
     amode = 0
     apin = -1
     nonres = False
     try:
      if str(value).strip()=="":
       nonres = True
     except:
      pass
     try:
      for pin in range(len(settings.Pinout)):
       if int(settings.Pinout[pin]['p']) == int(p):
        if settings.Pinout[pin]['m']==9:
         if nonres:
          settings.Pinout[pin]['m']=0
        amode = settings.Pinout[pin]['m']
        apin = pin
     except Exception as e:
      amode = 0
     if reserved:
      amode = 9
     if reserved and value and value != "":
      svalue = str(value)
     else:
      svalue = ""
     if apin==-1:
      settings.Pinout.append({'p':p,'m':amode,'d':svalue})
     else:
      settings.Pinout[apin] = {'p':p,'m':amode,'d':svalue}
     attr = []
     if amode==9:
      for a in range(9):
       attr.append("DISABLED")
      attr.append("")
     else:
      if p<34:
       for a in range(7):
        attr.append("")
       for a in range(2):
        attr.append("DISABLED")
      else:
       for a in range(2):
        attr.append("")
       for a in range(2,12):
        attr.append("DISABLED")
     optionvalues = [0,1,2,3,4,5,6,7,8,9]
     ws.addHtml("<tr><td align=right>D"+str(p)+"</td><td>")
     try:
      ws.addSelector("p"+str(p),len(options),options,optionvalues,attr,amode,False)
     except Exception as e:
      pass
     ws.addHtml("</td><td>"+str(value)+"</td></tr>")
    httpResponse._write(ws.TXBuffer,strEncoding='UTF-8')
    ws.TXBuffer = ""
  ws.addFormSeparator(3)
  ws.TXBuffer += "<tr><td colspan=3>"
  ws.addSubmitButton()
  ws.addFormNote('WARNING: Some changes needed to reboot after submitting changes!')
  ws.TXBuffer += "</table></form>"
  ws.sendHeadandTail("TmplStd",ws._TAIL)
  httpResponse._write(ws.TXBuffer,strEncoding='UTF-8')
  ws.TXBuffer = ""
