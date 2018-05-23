# synchrobike
Synchronized LED across bike lights

The goal of this project is to synchronize amazing LED animations and colors across countless wiresless LED nodes.

Range: I was able to successfully sync two nodes at a distance of 180m before running out of line of sight.
Current code 

## Current Status:
- [x] Sudo-randomly generated noise LED animation, color pallets, and animation direction sync with all nodes connected to the mesh network.
- [ ] Create Hardware and Software sections detailing how components are conected and how to upload sketch to the Wemos D1 Mini.
- [ ] Power section detailing power usage at different brightness and LED count.
- [ ] Include video/gif demo of synchrobike(s) in action.

## Planned Features:
* Synchronized LED animations across mesh nodes.
* Animation(s) for when a new node is added to the mesh.
* Well documented DIY instructions.

## Components
* [5V AA Battery Holder](https://www.aliexpress.com/item/Plastic-On-Off-Switch-4-x-1-5V-AA-Battery-Case-Holder-w-Cap-Black/32791164112.html) ($1)
* [50pc 12mm WS281x 5v](https://www.aliexpress.com/item/50-Pcs-string-12mm-WS2811-2811-IC-RGB-LED-Pixels-Module-String-Light-Black-Wire-cable/1854864234.html) ($10)
* [WEMOS D1 Mini](https://wiki.wemos.cc/products:d1:d1_mini) ($3.70)
* [5M Fishing Rod](https://www.aliexpress.com/item/AZJ-Brand-Wholesale-2-1-7-2M-Stream-Fishing-Rod-Glass-Fiber-Telescopic-Fishing-Rod-Ultra/32794897069.html) ($8.30)
* [Male 3 Pin JST Connector](https://www.aliexpress.com/item/Free-Shipping-10pcs-3pin-JST-Connector-Male-Female-plug-and-socket-connecting-Cable-Wire-for-WS2811/32366522079.html) ($1.40)

Total Estimated Cost: ~$25

## Wemos D1 Mini Setup
1. Setup Arduino IDE for the ESP8266 (Wemos D1 Mini):  https://github.com/esp8266/Arduino
2. Install Arduino library dependencies:
    * FastLED (EPS8266 DMA Fork): https://github.com/coryking/FastLED  -*this fixes flickering caused by interupts on the ESP8226 and the WS281x's* 

   * ESP8266TrueRandom: https://github.com/marvinroger/ESP8266TrueRandom
   
   * painlessMesh: https://gitlab.com/painlessMesh/painlessMesh
        * And any painlessMesh dependencies: https://gitlab.com/painlessMesh/painlessMesh#dependencies
3. Solder a Male JST Connector the WS281x to the Wemos D1 Mini:

| **WS281x**        |   **Wemos D1 Mini**| 
| :-------------: |:-------------: |
| Digital In (DI) | GPIO3 (Rx)
| Ground      | Ground       |
| 5v / Vcc | 5v       |

4. Connect your power source's 5v and Ground to the **WS2811x's dedicated 5v and Ground cables that are separate from the JST connectors.**  

5. Upload `syncrhobike.ino` to the Wemos D1 Mini 

**Note: It is suggested to unplug the LEDs from the Wemos D1 Mini while uploading the sketch. The LEDs being on the RX pin means that they can possibly interfeer with the upload, and will turn a very bright white.**

## Pinout

![Wemos D1 Mini Pinout](https://www.projetsdiy.fr/wp-content/uploads/2016/05/esp8266-wemos-d1-mini-gpio-pins.jpg)
