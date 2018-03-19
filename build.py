from subprocess import call
import serial.tools.list_ports
list = serial.tools.list_ports.comports()
connected = []
for element in list:
    connected.append(element.device)
    port = element.device
    command = "/Users/jp/Library/Arduino15/packages/esp8266/tools/esptool/0.4.9/esptool -vv -cd nodemcu -cb 921600 -cp " + port + " -ca 0x00000 -cf /var/folders/y7/dlk34nfs5m358ftdcp69d9zm0000gn/T/arduino_build_822067/sync_animations.ino.bin"
    call(command, shell=True) 
print("Connected COM ports: " + str(connected))