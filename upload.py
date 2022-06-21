# -*- coding: utf-8 -*-
import subprocess
import serial.tools.list_ports
import os, sys, platform, subprocess, time
from pathlib import Path
from termcolor import colored

platform = platform.system()
home = str(Path.home())

print("Platform: " + platform)
print("Home Dir: " + home)

if platform == 'Linux' or platform == 'Darwin' or platform == 'posix':
    command = home + "/.platformio/penv/bin/platformio"
elif platform == "Windows":
    command = home + "\.platformio\penv\Scripts\platformio.exe"
else:
    sys.exit("os platform " + platform + " unsupported")

# # Test Build sketch
# if platform == 'Linux':
#     command = "/home/jp/arduino/arduino-builder -dump-prefs -logger=machine -hardware /home/jp/arduino/hardware -hardware /home/jp/.arduino15/packages -tools /home/jp/arduino/tools-builder -tools /home/jp/arduino/hardware/tools/avr -tools /home/jp/.arduino15/packages -built-in-libraries /home/jp/arduino/libraries -libraries /home/jp/Arduino/libraries -fqbn=esp8266:esp8266:d1_mini:CpuFrequency=80,UploadSpeed=921600,FlashSize=4M3M -ide-version=10805 -build-path " + build_path + " -warnings=none -build-cache " + build_path + " -prefs=build.warn_data_percentage=75 -prefs=runtime.tools.mkspiffs.path=/home/jp/.arduino15/packages/esp8266/tools/mkspiffs/0.2.0 -prefs=runtime.tools.esptool.path=/home/jp/.arduino15/packages/esp8266/tools/esptool/0.4.12 -prefs=runtime.tools.xtensa-lx106-elf-gcc.path=/home/jp/.arduino15/packages/esp8266/tools/xtensa-lx106-elf-gcc/1.20.0-26-gb404fb9-2 -verbose " + dir_path + "/synchrobike.ino"
# elif platform == 'Darwin' or 'posix':
#     home = os.path.expanduser("~")
#     command = home + "/.platformio/penv/bin/platformio"
# else:
#     sys.exit("os " + platform + " unsupported yet!")
# call(command, shell=True)

# Build Sketch
# if platform == 'Linux':
#     command = "/home/jp/arduino/arduino-builder -dump-prefs -logger=machine -hardware /home/jp/arduino/hardware -hardware /home/jp/.arduino15/packages -tools /home/jp/arduino/tools-builder -tools /home/jp/arduino/hardware/tools/avr -tools /home/jp/.arduino15/packages -built-in-libraries /home/jp/arduino/libraries -libraries /home/jp/Arduino/libraries -fqbn=esp8266:esp8266:d1_mini:CpuFrequency=80,UploadSpeed=921600,FlashSize=4M3M -ide-version=10805 -build-path " + build_path + " -warnings=none -build-cache " + build_path + " -prefs=build.warn_data_percentage=75 -prefs=runtime.tools.mkspiffs.path=/home/jp/.arduino15/packages/esp8266/tools/mkspiffs/0.2.0 -prefs=runtime.tools.esptool.path=/home/jp/.arduino15/packages/esp8266/tools/esptool/0.4.12 -prefs=runtime.tools.xtensa-lx106-elf-gcc.path=/home/jp/.arduino15/packages/esp8266/tools/xtensa-lx106-elf-gcc/1.20.0-26-gb404fb9-2 -verbose " + dir_path + "/synchrobike.ino"
# elif platform == 'Darwin' or 'posix':
#     home = os.path.expanduser("~")
#     command = home + "/.platformio/penv/bin/platformio run --target upload --upload-port "
# else:
#     sys.exit("os " + platform + " unsupported yet!")
# call(command, shell=True)


# Write to devices

serial_devices = serial.tools.list_ports.comports()
successful = []
unsuccessful = []
processes = []
# Itterate serial devices and start parallel platformio build andupload processes
for serial_device in serial_devices:
    port = serial_device.device
    if port !=  "/dev/cu.Bluetooth-Incoming-Port":
        print("Attempting to upload to port: " + port)
        args = " run --target upload --upload-port " + port
        process = subprocess.Popen(command + args, stdout=subprocess.PIPE, shell=True)
        processes.append((process, port))
for process, port in processes:
    (output, err) = process.communicate()
    p_status = process.wait()
    print("Command output : ", output)
    print("Command exit status/return code: ", p_status)
    if p_status > 1:
        unsuccessful.append(port)
    else:
        successful.append(port)
print("=============================== UPLOAD RESULTS ===============================")
print("Successful Devices: " + str(successful))
print("Unsuccessful Devices: " + str(unsuccessful))