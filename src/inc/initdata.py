import os

favicon = b'\x00\x00\x01\x00\x01\x00\x10\x10\x00\x00\x01\x00 \x00h\x04\x00\x00\x16\x00\x00\x00(\x00\x00\x00\x10\x00\x00\x00 \x00\x00\x00\x01\x00 \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00+++\xff}}y\xff\xc8\xc9\xc4\xff\xc8\xc8\xc7\xff\xc8\xc8\xc6\xff\xc9\xca\xc7\xff\xc9\xca\xc7\xff\xc7\xc7\xc6\xff\xc8\xc8\xc7\xff\xc7\xc7\xc6\xff\xc7\xc7\xc6\xff\xc7\xc7\xc6\xff\xca\xc8\xc7\xff\xc4\xc3\xc2\xffvus\xff\x19\x19\x19\xffdca\xff\xec\xe6\xfa\xff\xc3\xb2\xeb\xff\xff\xff\xff\xff\xff\xff\xff\xff\xdb\xd1\xf3\xff\xd4\xc7\xf0\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xfe\xff\xfe\xff\xd6\xf0\xe3\xff\xe6\xf6\xee\xff\xff\xff\xff\xffssq\xff\xbe\xbd\xb9\xff\xbf\xab\xec\xff/\x00\xc3\xff\xad\x95\xe3\xff\xff\xff\xff\xff\x9f\x83\xe1\xff4\x00\xc4\xff\xbf\xad\xea\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xa7\xdf\xc5\xffD\xbd\x87\xffI\xbf\x8a\xff\xe6\xf6\xee\xff\xc2\xc1\xc1\xff\xc9\xc8\xc6\xff\xff\xff\xff\xff\xb8\xa3\xe6\xff3\x00\xc4\xff\xac\x94\xe1\xff\xff\xff\xff\xff\x91q\xdc\xff3\x00\xc4\xff\xcc\xbd\xed\xff\xff\xff\xff\xff\xff\xff\xff\xff\x92\xd8\xb9\xffK\xc0\x8c\xffD\xbd\x87\xff\xd7\xf0\xe4\xff\xc8\xc7\xc6\xff\xc9\xc8\xc5\xff\xff\xff\xff\xff\xff\xff\xff\xff\xab\x93\xe3\xff2\x00\xc4\xff\xac\x94\xe3\xff\xff\xff\xff\xff\x92r\xde\xff4\x00\xc4\xff\xbf\xac\xea\xff\xff\xff\xff\xff\xe8\xf6\xef\xff\x92\xd9\xb9\xff\xa7\xdf\xc5\xff\xfe\xff\xfe\xff\xc6\xc6\xc5\xff\xca\xca\xc5\xff\xda\xcf\xf3\xff\x9e\x83\xe1\xff\xff\xff\xff\xff\xb9\xa6\xe6\xff2\x00\xc4\xff\xab\x93\xe1\xff\xff\xff\xff\xff\x92q\xdc\xff3\x00\xc4\xff\xcd\xbe\xed\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xc7\xc7\xc5\xff\xca\xca\xc5\xff\xc5\xb3\xee\xff5\x00\xc4\xff\x95w\xdf\xff\xff\xff\xff\xff\xaa\x92\xe3\xff2\x00\xc4\xff\xac\x94\xe3\xff\xff\xff\xff\xff\x92r\xde\xff3\x00\xc4\xff\xbf\xac\xea\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xc6\xc6\xc5\xff\xc8\xc7\xc4\xff\xff\xff\xff\xff\xce\xbf\xee\xff;\x02\xc6\xff\x84b\xd9\xff\xff\xff\xff\xff\xba\xa7\xe7\xff2\x00\xc4\xff\xab\x93\xe1\xff\xff\xff\xff\xff\x92q\xdc\xff4\x00\xc4\xff\xcc\xbd\xed\xff\xff\xff\xff\xff\xff\xff\xff\xff\xc6\xc6\xc5\xff\xc7\xc6\xc4\xff\xff\xff\xff\xff\xff\xff\xff\xff\xb9\xa4\xe8\xff9\x00\xc5\xff\x96x\xdf\xff\xff\xff\xff\xff\xaa\x91\xe3\xff2\x00\xc4\xff\xac\x94\xe3\xff\xff\xff\xff\xff\x92r\xde\xff3\x00\xc4\xff\xbf\xad\xea\xff\xff\xff\xff\xff\xc6\xc6\xc5\xff\xc8\xc8\xc4\xff\xc2\xaf\xec\xffxP\xd5\xff\xff\xff\xff\xff\xcf\xc1\xee\xff:\x01\xc5\xff\x84a\xd9\xff\xff\xff\xff\xff\xba\xa7\xe7\xff2\x00\xc4\xff\xab\x93\xe1\xff\xff\xff\xff\xff\x91q\xdc\xff4\x00\xc4\xff\xd4\xc7\xf0\xff\xc9\xca\xc6\xff\xc8\xc7\xc3\xff\xcd\xbe\xf0\xff?\x08\xc7\xff\x87d\xda\xff\xff\xff\xff\xff\xb9\xa4\xe8\xff:\x01\xc5\xff\x96x\xdf\xff\xff\xff\xff\xff\xaa\x92\xe3\xff2\x00\xc4\xff\xac\x94\xe3\xff\xff\xff\xff\xff\x9e\x82\xe1\xff\xdb\xd1\xf3\xff\xc9\xc9\xc6\xff\xc6\xc5\xc2\xff\xff\xff\xff\xff\xda\xd0\xf3\xffA\n\xc8\xffqG\xd4\xff\xff\xff\xff\xff\xcf\xc1\xee\xff9\x00\xc5\xff\x84b\xd9\xff\xff\xff\xff\xff\xb9\xa6\xe6\xff2\x00\xc4\xff\xac\x94\xe1\xff\xff\xff\xff\xff\xff\xff\xff\xff\xc6\xc6\xc5\xff\xc6\xc5\xc3\xff\xff\xff\xff\xff\xff\xff\xff\xff\xc6\xb6\xed\xffA\n\xc8\xff\x87d\xda\xff\xff\xff\xff\xff\xb9\xa4\xe8\xff;\x02\xc6\xff\x95w\xdf\xff\xff\xff\xff\xff\xab\x93\xe3\xff2\x00\xc4\xff\xac\x95\xe3\xff\xff\xff\xff\xff\xc6\xc6\xc5\xff\xb9\xb9\xb6\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xda\xd0\xf3\xff?\x08\xc7\xffyQ\xd5\xff\xff\xff\xff\xff\xce\xbf\xee\xff5\x00\xc4\xff\x9e\x83\xe1\xff\xff\xff\xff\xff\xb5\x9f\xe7\xff/\x00\xc3\xff\xc4\xb3\xeb\xff\xc6\xc7\xc2\xffa`^\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xcd\xbe\xf1\xff\xc2\xaf\xec\xff\xff\xff\xff\xff\xff\xff\xff\xff\xc5\xb3\xee\xff\xdb\xcf\xf3\xff\xff\xff\xff\xff\xff\xff\xff\xff\xc0\xac\xec\xff\xec\xe6\xfa\xffyyu\xff***\xffbb`\xff\xbb\xba\xb8\xff\xc7\xc6\xc4\xff\xc6\xc6\xc3\xff\xc8\xc8\xc3\xff\xc8\xc8\xc4\xff\xc6\xc5\xc2\xff\xc6\xc6\xc2\xff\xc8\xc8\xc3\xff\xc8\xc7\xc4\xff\xc6\xc5\xc3\xff\xc6\xc6\xc3\xff\xba\xba\xb6\xff]\\Z\xff$$$\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
defaultu = b"* {\n font-family: sans-serif;\n font-size: 12pt;\n margin: 0px;\n padding: 0px;\n box-sizing: border-box;\n}\nh1 {\n font-size: 16pt;\n color: #25333C;\n margin: 8px 0;\n font-weight: bold;\n}\nh2 {\n font-size: 12pt;\n margin: 0 -4px;\n padding: 6px;\n background-color: #444;\n color: #FFF;\n font-weight: bold;\n}\nh3 {\n font-size: 12pt;\n margin: 16px -4px 0 -4px;\n padding: 4px;\n background-color: #EEE;\n color: #444;\n font-weight: bold;\n}\nh6 {\n font-size: 10pt;\n color: #25333C;\n}\n.button {\n margin: 4px;\n padding: 4px 16px;\n background-color: #25333C;\n color: #FFF;\n text-decoration: none;\n border-radius: 4px;\n border: none;\n}\n.button.link {\n}\n.button.link.wide {\n display: inline-block;\n width: 99%;\n text-align: center;\n}\n.button.link.red {\n background-color: red;\n color:yellow;\n}\n.button.help {\n padding: 2px 4px;\n border-style: solid;\n border-width: 1px;\n border-color: gray;\n border-radius: 50%;\n}\n.button:hover {\n background: #369;\n}\ninput, select, textarea {\n margin: 4px;\n padding: 4px 8px;\n border-radius: 4px;\n background-color: #eee;\n border-style: solid;\n border-width: 1px;\n border-color: gray;\n}\ninput:hover {\n background-color: #ccc;\n}\ninput.wide {\n max-width: 500px;\n width:80%;\n}\ninput.widenumber {\n max-width: 500px;\n width:100px;\n}\n#selectwidth {\n max-width: 500px;\n width:80%;\n padding: 4px 8px;\n}\nselect:hover {\n background-color: #ccc;\n}\n.container {\n display: block;\n padding-left: 35px;\n margin-left: 4px;\n margin-top: 0px;\n position: relative;\n cursor: pointer;\n font-size: 12pt;\n -webkit-user-select: none;\n -moz-user-select: none;\n -ms-user-select: none;\n user-select: none;\n}\n.container input {\n position: absolute;\n opacity: 0;\n cursor: pointer;\n}\n.checkmark {\n position: absolute;\n top: 0;\n left: 0;\n height: 25px;\n width: 25px;\n background-color: #eee;\n border-style: solid;\n border-width: 1px;\n border-color: gray;\n border-radius: 4px;\n}\n.container:hover input ~ .checkmark {\n background-color: #ccc;\n}\n.container input:checked ~ .checkmark {\n background-color: #25333C;\n}\n.checkmark:after {\n content: \'\';\n position: absolute;\n display: none;\n}\n.container input:checked ~ .checkmark:after {\n display: block;\n}\n.container .checkmark:after {\n left: 7px;\n top: 3px;\n width: 5px;\n height: 10px;\n border: solid white;\n border-width: 0 3px 3px 0;\n -webkit-transform: rotate(45deg);\n -ms-transform: rotate(45deg);\n transform: rotate(45deg);\n}\n.container2 {\n display: block;\n padding-left: 35px;\n margin-left: 9px;\n margin-bottom: 20px;\n position: relative;\n cursor: pointer;\n font-size: 12pt;\n -webkit-user-select: none;\n -moz-user-select: none;\n -ms-user-select: none;\n user-select: none;\n}\n.container2 input {\n position: absolute;\n opacity: 0;\n cursor: pointer;\n}\n.dotmark {\n position: absolute;\n top: 0;\n left: 0;\n height: 26px;\n width: 26px;\n background-color: #eee;\n border-style: solid;\n border-width: 1px;\n border-color: gray;\n border-radius: 50%;\n}\n.container2:hover input ~ .dotmark {\n background-color: #ccc;\n}\n.container2 input:checked ~ .dotmark {\n background-color: #25333C;\n}\n.dotmark:after {\n content: \'\';\n position: absolute;\n display: none;\n}\n.container2 input:checked ~ .dotmark:after {\n display: block;\n}\n.container2 .dotmark:after {\n top: 8px;\n left: 8px;\n width: 8px;\n height: 8px;\n border-radius: 50%;\n background: white;\n}\n#toastmessage {\n visibility: hidden;\n min-width: 250px;\n margin-left: -125px;\n background-color: #25333C;\n color: #fff;\n text-align: center;\n border-radius: 4px;\n padding: 16px;\n position: fixed;\n z-index: 1;\n left: 282px;\n bottom: 30%;\n font-size: 17px;\n border-style: solid;\n border-width: 1px;\n border-color: gray;\n}\n#toastmessage.show {\n visibility: visible;\n -webkit-animation: fadein 0.5s, fadeout 0.5s 2.5s;\n animation: fadein 0.5s, fadeout 0.5s 2.5s;\n}\n@-webkit-keyframes fadein {\n from {\n  bottom: 20%;\n  opacity: 0;\n }\n to {\n  bottom: 30%;\n  opacity: 0.9;\n }\n}\n@keyframes fadein {\n from {\n  bottom: 20%;\n  opacity: 0;\n }\n to {\n  bottom: 30%;\n  opacity: 0.9;\n }\n}\n@-webkit-keyframes fadeout {\n from {\n  bottom: 30%;\n  opacity: 0.9;\n }\n to {\n  bottom: 0;\n  opacity: 0;\n }\n}\n@keyframes fadeout {\n from {\n  bottom: 30%;\n  opacity: 0.9;\n }\n to {\n  bottom: 0;\n  opacity: 0;\n }\n}\n.level_0 {\n color: #F1F1F1;\n}\n.level_1 {\n color: #FCFF95;\n}\n.level_2 {\n color: #9DCEFE;\n}\n.level_3 {\n color: #A4FC79;\n}\n.level_4 {\n color: #F2AB39;\n}\n.level_9 {\n color: #FF5500;\n}\n.logviewer {\n color: #F1F1F1;\n background-color: #272727;\n font-family: \'Lucida Console\', Monaco, monospace;\n height:  400px;\n max-width: 1000px;\n width: 80%;\n padding: 4px 8px;\n overflow: auto;\n border-style: solid;\n border-color: gray;\n}\ntextarea {\n max-width: 1000px;\n width:80%;\n padding: 4px 8px;\n}\ntextarea:hover {\n background-color: #ccc;\n}\ntable.normal th {\n padding: 6px;\n background-color: #444;\n color: #FFF;\n border-color: #888;\n font-weight: bold;\n}\ntable.normal td {\n padding: 4px;\n height: 30px;\n}\ntable.normal tr {\n padding: 4px;\n}\ntable.normal {\n color: #000;\n width: 100%;\n min-width: 420px;\n border-collapse: collapse;\n}\ntable.multirow th {\n padding: 6px;\n background-color: #444;\n color: #FFF;\n border-color: #888;\n font-weight: bold;\n}\ntable.multirow td {\n padding: 4px;\n text-align: center;\n height: 30px;\n}\ntable.multirow tr {\n padding: 4px;\n}\ntable.multirow tr:nth-child(even) {\n background-color: #DEE6FF;\n}\ntable.multirow {\n color: #000;\n width: 100%;\n min-width: 420px;\n border-collapse: collapse;\n}\n.note {\n color: #444;\n font-style: italic;\n}\n.headermenu {\n position: fixed;\n top: 0;\n left: 0;\n right: 0;\n height: 90px;\n padding: 8px 12px;\n background-color: #F8F8F8;\n border-bottom: 1px solid #DDD;\n z-index: 1;\n}\n.apheader {\n padding: 8px 12px;\n background-color: #F8F8F8;\n}\n.bodymenu {\n margin-top: 96px;\n}\n.menubar {\n position: inherit;\n top: 55px;\n}\n.menu {\n float: left;\n padding: 4px 16px 8px 16px;\n color: #444;\n white-space: nowrap;\n border: solid transparent;\n border-width: 4px 1px 1px;\n border-radius: 4px 4px 0 0;\n text-decoration: none;\n}\n.menu.active {\n color: #000;\n background-color: #FFF;\n border-color: #25333C #DDD #FFF;\n}\n.menu:hover {\n color: #000;\n background: #DEF;\n}\n.menu_button {\n display: none;\n}\n.on {\n color: green;\n}\n.off {\n color: red;\n}\n.div_l {\n float: left;\n}\n.div_r {\n float: right;\n margin: 2px;\n padding: 1px 10px;\n border-radius: 4px;\n background-color: #080;\n color: white;\n}\n.div_br {\n clear: both;\n}\n.alert {\n padding: 20px;\n background-color: #f44336;\n color: white;\n margin-bottom: 15px;\n}\n.closebtn {\n margin-left: 15px;\n color: white;\n font-weight: bold;\n float: right;\n font-size: 22px;\n line-height: 20px;\n cursor: pointer;\n transition: 0.3s;\n}\n.closebtn:hover {\n color: black;\n}\nsection {\n overflow-x: auto;\n width: 100%;\n}\n@media screen and (max-width: 960px) {\n header:hover .menubar {\n  display: block;\n }\n .menu_button {\n  display: block;\n  text-align: center;\n }\n .bodymenu {\n  margin-top: 0px;\n }\n .menubar {\n  display: none;\n  top: 0px;\n  position: relative;\n  float: left;\n  width: 100%;\n }\n .headermenu {\n  position: relative;\n  height: auto;\n  float: left;\n  width: 100%;\n  padding: 5px;\n  z-index: 1;\n }\n .headermenu h1 {\n  padding: 8px 12px;\n }\n .headermenu  a {\n  text-align: center;\n  width: 100%;\n  padding:7px 10px;\n  height: auto;\n  border: 0px;\n  border-radius:0px;\n }\n ;\n}"
tmplstd = b"<!DOCTYPE html><html lang=\'en\'>\n<head>\n  <meta charset=\'utf-8\'/>\n  <title>{{name}}</title>\n  <meta name=\'viewport\' content=\'width=device-width, initial-scale=1.0\'>\n  {{js}}\n  {{css}}\n</head>\n<body class=\'bodymenu\'>\n  <span class=\'message\' id=\'rbtmsg\'></span>\n  <header class=\'headermenu\'>\n <h1>mpyEasy: {{name}} {{logo}}</h1><div class=\'menu_button\'>&#9776;</div><BR>\n {{menu}}\n  </header>\n  <section>\n  <span class=\'message error\'>\n  {{error}}\n  </span>\n  {{content}}\n  </section>\n  <footer>\n <br>\n <h6>Made by <a href=\'http://bitekmindenhol.blog.hu\' style=\'font-size: 15px; text-decoration: none\'>NS Tech</a>. - Designed by <a href=\'http://www.letscontrolit.com\' style=\'font-size: 15px; text-decoration: none\'>www.letscontrolit.com</a></h6>\n  </footer>\n</body></html>"
tmplap  = b"<!DOCTYPE html><html lang=\'en\'>\r\n<head>\r\n<meta charset=\'utf-8\'/>\r\n<meta name=\'viewport\' content=\'width=device-width, initial-scale=1.0\'>\r\n<title>{{name}}</title>\r\n{{css}}\r\n</head>\r\n<body>\r\n<header class=\'apheader\'>\r\n<h1>Welcome to mpyEasy AP</h1>\r\n</header>\r\n<section>\r\n<span class=\'message error\'>\r\n{{error}}\r\n</span>\r\n{{content}}\r\n</section>\r\n<footer>\r\n<br>\r\n<h6>Made by <a href=\'http://bitekmindenhol.blog.hu\' style=\'font-size: 15px; text-decoration: none\'>NS Tech</a>. - Designed by <a href=\'http://www.letscontrolit.com\' style=\'font-size: 15px; text-decoration: none\'>www.letscontrolit.com</a></h6>\r\n</footer>\r\n</body>\r\n\r\n"

def run():
 global favicon, defaultu, tmplstd, tmplap
 if 'data' not in os.listdir():
  try:
   os.mkdir('data')
   os.mkdir('www')
   os.mkdir('templ')
  except:
   pass
  try:
   file = open("www/favicon.ico","wb")
   file.write(favicon)
   file.close()
  except:
   pass
  try:
   file = open("www/defaultu.css","wb")
   file.write(defaultu)
   file.close()
  except:
   pass
  try:
   file = open("templ/TmplStd.txt","wb")
   file.write(tmplstd)
   file.close()
  except:
   pass
  try:
   file = open("templ/TmplAP.txt","wb")
   file.write(tmplap)
   file.close()
  except:
   pass
