from subprocess import call, check_call
import serial.tools.list_ports

import os 
dir_path = os.path.dirname(os.path.realpath(__file__))
build_path = dir_path + "/build"
print(dir_path)
print(build_path)

# Build sketch
command = "/Applications/Arduino.app/Contents/Java/arduino-builder -dump-prefs -logger=machine -hardware /Applications/Arduino.app/Contents/Java/hardware -hardware /Users/jp/Library/Arduino15/packages -tools /Applications/Arduino.app/Contents/Java/tools-builder -tools /Applications/Arduino.app/Contents/Java/hardware/tools/avr -tools /Users/jp/Library/Arduino15/packages -built-in-libraries /Applications/Arduino.app/Contents/Java/libraries -libraries /Users/jp/Documents/Arduino/libraries -fqbn=esp8266:esp8266:d1_mini:CpuFrequency=80,UploadSpeed=921600,FlashSize=4M3M -ide-version=10805 -build-path " + build_path + " -warnings=none -build-cache " + build_path + " -prefs=build.warn_data_percentage=75 -prefs=runtime.tools.mkspiffs.path=/Users/jp/Library/Arduino15/packages/esp8266/tools/mkspiffs/0.1.2 -prefs=runtime.tools.esptool.path=/Users/jp/Library/Arduino15/packages/esp8266/tools/esptool/0.4.9 -prefs=runtime.tools.xtensa-lx106-elf-gcc.path=/Users/jp/Library/Arduino15/packages/esp8266/tools/xtensa-lx106-elf-gcc/1.20.0-26-gb404fb9-2 -verbose " + dir_path + "/synchrobike.ino"
call(command, shell=True) 

command = "/Applications/Arduino.app/Contents/Java/arduino-builder -compile -logger=machine -hardware /Applications/Arduino.app/Contents/Java/hardware -hardware /Users/jp/Library/Arduino15/packages -tools /Applications/Arduino.app/Contents/Java/tools-builder -tools /Applications/Arduino.app/Contents/Java/hardware/tools/avr -tools /Users/jp/Library/Arduino15/packages -built-in-libraries /Applications/Arduino.app/Contents/Java/libraries -libraries /Users/jp/Documents/Arduino/libraries -fqbn=esp8266:esp8266:d1_mini:CpuFrequency=80,UploadSpeed=921600,FlashSize=4M3M -ide-version=10805 -build-path " + build_path + " -warnings=none -build-cache " + build_path + " -prefs=build.warn_data_percentage=75 -prefs=runtime.tools.mkspiffs.path=/Users/jp/Library/Arduino15/packages/esp8266/tools/mkspiffs/0.1.2 -prefs=runtime.tools.esptool.path=/Users/jp/Library/Arduino15/packages/esp8266/tools/esptool/0.4.9 -prefs=runtime.tools.xtensa-lx106-elf-gcc.path=/Users/jp/Library/Arduino15/packages/esp8266/tools/xtensa-lx106-elf-gcc/1.20.0-26-gb404fb9-2 -verbose " + dir_path + "/synchrobike.ino"
check_call(command, shell=True) 

list = serial.tools.list_ports.comports()
connected = []
for element in list:
   connected.append(element.device)
   port = element.device
   command = "/Users/jp/Library/Arduino15/packages/esp8266/tools/esptool/0.4.9/esptool -vv -cd nodemcu -cb 921600 -cp " + port + " -ca 0x00000 -cf " + build_path + "/synchrobike.ino.bin"
   call(command, shell=True) 
print("Connected COM ports: " + str(connected))
