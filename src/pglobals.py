PROGNAME = "mPyEasy"
BUILD   = 10005
PROGVER = str(BUILD)[:1]+"."+str(BUILD)[1:2]+"."+str(BUILD)[2:]

gpMenu = []
gpMenu.append(['\u2302 Main','.'])
gpMenu.append(['\u2699 Config','config'])
gpMenu.append(['\U0001f4ac Controllers','controllers'])
gpMenu.append(['\U0001f4cc Hardware','hardware'])
gpMenu.append(['\U0001f50c Devices','devices'])
gpMenu.append(['\u26dc Rules','rules'])
gpMenu.append(['\u2709 Notifications','notifications'])
gpMenu.append(['\U0001f527 Tools','tools'])

webLoggedIn = False
wifiSetup = False
fpath = ""
#fpath="/"

deviceselector = [[0,0,"- None -"]]
controllerselector = [[0,0,"- None -"]]
notifierselector = [[0,0,"- None -"]]

NODE_TYPE_ID_ESP_EASY_STD        =   1
NODE_TYPE_ID_RPI_EASY_STD        =   5
NODE_TYPE_ID_ESP_EASYM_STD       =  17
NODE_TYPE_ID_ESP_EASY32_STD      =  33
NODE_TYPE_ID_ARDUINO_EASY_STD    =  65
NODE_TYPE_ID_NANO_EASY_STD       =  81
NODE_TYPE_ID_ATMEGA_EASY_LORA    =  97

LOG_LEVEL_ERROR                  =   1
LOG_LEVEL_INFO                   =   2
LOG_LEVEL_DEBUG                  =   3
LOG_LEVEL_DEBUG_MORE             =   4
LOG_LEVEL_DEBUG_DEV              =   9

LOG_MAXLINES                     = 120

DEVICES_MAX                      = 60
TASKS_MAX                        = 32

CONTROLLER_MAX                   =  3
NOTIFICATION_MAX                 =  2
VARS_PER_TASK                    =  4
PLUGIN_MAX                       = DEVICES_MAX
PLUGIN_CONFIGVAR_MAX             =   8
PLUGIN_CONFIGFLOATVAR_MAX        =   4
PLUGIN_CONFIGLONGVAR_MAX         =   4
PLUGIN_EXTRACONFIGVAR_MAX        =   8
CPLUGIN_MAX                      =  16
NPLUGIN_MAX                      =   4
UNIT_MAX                         = 128
RULES_TIMER_MAX                  =   4
SYSTEM_TIMER_MAX                 =   0
SYSTEM_CMD_TIMER_MAX             =   0
RULES_MAX_SIZE                   = 8192
RULES_MAX_NESTING_LEVEL          =   4
RULESETS_MAX                     =   4
RULES_BUFFER_SIZE                =  64

RULE_USER     = 65530 # user defined event
RULE_SYSTEM   = 65531 # System#Boot MQTT#Connected MQTT#Disconnected
RULE_CLOCK    = 65532 # Clock#Time=
RULE_TIMER    = 65533 # Rules#Timer=

DEVICE_TYPE_SINGLE               =   1  # connected through 1 datapin
DEVICE_TYPE_DUAL                 =   2  # connected through 2 datapins
DEVICE_TYPE_TRIPLE               =   3  # connected through 3 datapins
DEVICE_TYPE_QUAD                 =   4  # connected through 4 datapins
DEVICE_TYPE_ANALOG               =  10  # AIN/tout pin
DEVICE_TYPE_I2C                  =  20  # connected through I2C
DEVICE_TYPE_SPI                  =  30  # connected through SPI
DEVICE_TYPE_DUMMY                =  99  # Dummy device, has no physical connection
DEVICE_TYPE_BLE                  = 120  # BLE connected device
DEVICE_TYPE_SER                  = 150  # Serial

SENSOR_TYPE_NONE                 =  0
SENSOR_TYPE_SINGLE               =  1
SENSOR_TYPE_TEMP_HUM             =  2
SENSOR_TYPE_TEMP_BARO            =  3
SENSOR_TYPE_TEMP_HUM_BARO        =  4
SENSOR_TYPE_DUAL                 =  5
SENSOR_TYPE_TRIPLE               =  6
SENSOR_TYPE_QUAD                 =  7
SENSOR_TYPE_TEMP_EMPTY_BARO      =  8
SENSOR_TYPE_SWITCH               = 10
SENSOR_TYPE_DIMMER               = 11
SENSOR_TYPE_LONG                 = 20
SENSOR_TYPE_WIND                 = 21
SENSOR_TYPE_TEXT                 = 101

NODE_TYPE_ID = NODE_TYPE_ID_ESP_EASY32_STD

FILE_RULES        = "data/rules1.dat"
