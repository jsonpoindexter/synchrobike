# -*- coding: utf-8 -*-
from subprocess import call, check_call
import serial.tools.list_ports
import os, sys, platform, subprocess, time

platform = platform.system()

dir_path = os.path.dirname(os.path.realpath(__file__))
build_path = dir_path + "/build"
print("Operating System: " + platform)
print("Current directory: " + dir_path)
print("Build path: " + build_path)

if not os.path.exists(build_path):
    os.makedirs(build_path)

# Test Build sketch
if platform == 'Linux':
    command = "/home/jp/arduino/arduino-builder -dump-prefs -logger=machine -hardware /home/jp/arduino/hardware -hardware /home/jp/.arduino15/packages -tools /home/jp/arduino/tools-builder -tools /home/jp/arduino/hardware/tools/avr -tools /home/jp/.arduino15/packages -built-in-libraries /home/jp/arduino/libraries -libraries /home/jp/Arduino/libraries -fqbn=esp8266:esp8266:d1_mini:CpuFrequency=80,UploadSpeed=921600,FlashSize=4M3M -ide-version=10805 -build-path " + build_path + " -warnings=none -build-cache " + build_path + " -prefs=build.warn_data_percentage=75 -prefs=runtime.tools.mkspiffs.path=/home/jp/.arduino15/packages/esp8266/tools/mkspiffs/0.2.0 -prefs=runtime.tools.esptool.path=/home/jp/.arduino15/packages/esp8266/tools/esptool/0.4.12 -prefs=runtime.tools.xtensa-lx106-elf-gcc.path=/home/jp/.arduino15/packages/esp8266/tools/xtensa-lx106-elf-gcc/1.20.0-26-gb404fb9-2 -verbose " + dir_path + "/synchrobike.ino"
elif platform == 'Darwin' or 'posix':
    command = "/Applications/Arduino.app/Contents/Java/arduino-builder -dump-prefs -logger=machine -hardware /Applications/Arduino.app/Contents/Java/hardware -hardware /Users/jp/Library/Arduino15/packages -tools /Applications/Arduino.app/Contents/Java/tools-builder -tools¡§ /Applications/Arduino.app/Contents/Java/hardware/tools/avr -tools /Users/jp/Library/Arduino15/packages -built-in-libraries /Applications/Arduino.app/Contents/Java/libraries -libraries /Users/jp/Documents/Arduino/libraries -fqbn=esp8266:esp8266:d1_mini:CpuFrequency=80,UploadSpeed=921600,FlashSize=4M3M -ide-version=10805 -build-path " + build_path + " -warnings=none -build-cache " + build_path + " -prefs=build.warn_data_percentage=75 -prefs=runtime.tools.mkspiffs.path=/Users/jp/Library/Arduino15/packages/esp8266/tools/mkspiffs/0.1.2 -prefs=runtime.tools.esptool.path=/Users/jp/Library/Arduino15/packages/esp8266/tools/esptool/0.4.9 -prefs=runtime.tools.xtensa-lx106-elf-gcc.path=/Users/jp/Library/Arduino15/packages/esp8266/tools/xtensa-lx106-elf-gcc/1.20.0-26-gb404fb9-2 -verbose " + dir_path + "/synchrobike.ino"
else:
    sys.exit("os " + platform + " unsupported yet!")
call(command, shell=True)

# Build Sketch
if platform == 'Linux':
    command = "/home/jp/arduino/arduino-builder -compile -logger=machine -hardware /home/jp/arduino/hardware -hardware /home/jp/.arduino15/packages -tools /home/jp/arduino/tools-builder -tools /home/jp/arduino/hardware/tools/avr -tools /home/jp/.arduino15/packages -built-in-libraries /home/jp/arduino/libraries -libraries /home/jp/Arduino/libraries -fqbn=esp8266:esp8266:d1_mini:CpuFrequency=80,UploadSpeed=921600,FlashSize=4M3M -ide-version=10805 -build-path " + build_path + " -warnings=none -build-cache " + build_path + " -prefs=build.warn_data_percentage=75 -prefs=runtime.tools.mkspiffs.path=/home/jp/.arduino15/packages/esp8266/tools/mkspiffs/0.2.0 -prefs=runtime.tools.esptool.path=/home/jp/.arduino15/packages/esp8266/tools/esptool/0.4.12 -prefs=runtime.tools.xtensa-lx106-elf-gcc.path=/home/jp/.arduino15/packages/esp8266/tools/xtensa-lx106-elf-gcc/1.20.0-26-gb404fb9-2 -verbose " + dir_path + "/synchrobike.ino"
elif platform == 'Darwin' or 'posix':
    command = "/Applications/Arduino.app/Contents/Java/arduino-builder -compile -logger=machine -hardware /Applications/Arduino.app/Contents/Java/hardware -hardware /Users/jp/Library/Arduino15/packages -tools /Applications/Arduino.app/Contents/Java/tools-builder -tools /Applications/Arduino.app/Contents/Java/hardware/tools/avr -tools /Users/jp/Library/Arduino15/packages -built-in-libraries /Applications/Arduino.app/Contents/Java/libraries -libraries /Users/jp/Documents/Arduino/libraries -fqbn=esp8266:esp8266:d1_mini:CpuFrequency=80,UploadSpeed=921600,FlashSize=4M3M -ide-version=10805 -build-path " + build_path + " -warnings=none -build-cache " + build_path + " -prefs=build.warn_data_percentage=75 -prefs=runtime.tools.mkspiffs.path=/Users/jp/Library/Arduino15/packages/esp8266/tools/mkspiffs/0.1.2 -prefs=runtime.tools.esptool.path=/Users/jp/Library/Arduino15/packages/esp8266/tools/esptool/0.4.9 -prefs=runtime.tools.xtensa-lx106-elf-gcc.path=/Users/jp/Library/Arduino15/packages/esp8266/tools/xtensa-lx106-elf-gcc/1.20.0-26-gb404fb9-2 -verbose " + dir_path + "/synchrobike.ino"
else:
    sys.exit("os " + platform + " unsupported yet!")
check_call(command, shell=True)

processes = set()

# Write to devices
serial_devices = serial.tools.list_ports.comports()
connected = []
for serial_device in serial_devices:
    connected.append(serial_device.device)
    port = serial_device.device
    if platform == 'Linux':
        command = "/home/jp/.arduino15/packages/esp8266/tools/esptool/0.4.12/esptool -vv -cd nodemcu -cb 921600 -cp " + port + " -ca 0x00000 -cf " + build_path + "/synchrobike.ino.bin"
    elif platform == 'Darwin' or 'posix':
        command = "/Users/jp/Library/Arduino15/packages/esp8266/tools/esptool/0.4.9/esptool -vv -cd nodemcu -cb 921600 -cp " + port + " -ca 0x00000 -cf " + build_path + "/synchrobike.ino.bin"
    else:
        sys.exit("os " + platform + " unsupported yet!")
    call(command, shell=True)
print("Connected COM ports: " + str(connected))
