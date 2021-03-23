[![Release downloads](https://img.shields.io/github/downloads/enesbcs/mpyeasy/total.svg)]() [![Code size](https://img.shields.io/github/languages/code-size/enesbcs/mpyeasy)]() [![Last commit](https://img.shields.io/github/last-commit/enesbcs/mpyeasy)]()

# To support the development you can:
- Be a patron at [Patreon](https://www.patreon.com/enesbcs)
- Buy a [coffee](https://ko-fi.com/I3I5UT4H)
- Donate by [PayPal](https://www.paypal.me/rpieasy)
- Adding Python code by [Pull Request](https://github.com/enesbcs/mpyeasy/pulls)

# mPyEasy

Easy MultiSensor device based on ESP32 &amp; MicroPython

Based on MicroPython and ESP32 this project tries to mimic the magnificent [ESPEasy](https://www.letscontrolit.com/wiki/index.php/ESPEasy) project functions. Python code is backported from RPIEasy.
Main goal is to create a multisensor device, that can be install and setup quickly.

Tested with ESP32 WROVER and WROOM modules with 4MB flash.

:warning:THIS IS A BETA TEST VERSION!:warning:

Expect major changes in later versions that may cause incompatibility with earlier versions!

# Installation

1/ Recommended method to write the firmware binary to the flash directly. It will run on either WROOM or WROVER variants.

  Download image from: https://github.com/enesbcs/mpyeasy/releases/

- Erase flash at first time on ESP32:

  `esptool.py --port /dev/ttyUSB0 erase_flash`
- Write firmware:

  `esptool.py --port /dev/ttyUSB0 write_flash -z 0x1000 firmware.bin`

2/ MicroPython source code from the src directory can be copied to the flash onto a WROVER module with 4MB PSRAM! 
Without PSRAM it will run out of memory, i warned you!

https://github.com/enesbcs/mpyeasy/tree/main/src

# Setup

- Connect to mpyEasy WIFI AP with configesp password.
- Setup your own wifi data at http://192.168.4.1/config
- Search it on your own network and configure at the obtained dhcp IP with a web browser.

(LAN module can be enabled at the Hardware page, then configure it on the Config page, if settings are correct it will work after reboot.)

# Update

1/ If using the recommended firmware binary, the OTA function is available in the webGUI. OTA will only work with MicroPython images where APP partition starts on 0xF000. Release files in this repository looks like this. If used in OTA, the program will automatically skip the first 0xF000 bytes and upload only the APP partition from the binary, to the next free OTA partition of the ESP32 flash. This is the reason why the flashable FACTORY release and the OTA version is the same.

2/ In case the source py files written to the Flash of the device, OTA will not work, source files needs to be updated manually. (Either by REPL or manual FTP)

# Compiling

To create firmware image from python sources, follow instructions for compiling standard MicroPython and add mPyEasy source to micropython/ports/esp32/modules subdirectory before "make" command.

https://github.com/micropython/micropython/tree/master/ports/esp32

https://blog.horan.hk/micropythonesp32.html
