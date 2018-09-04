# synchrobike
Synchronized LED color palletes and animations.

The goal of this project is to synchronize amazing LED animations and colors across a wiresless node mesh.

## Components
* 5V Phone Battery Bank
* USB to Micro USB cable
* [50pc 12mm WS281x 5v](https://www.aliexpress.com/item/50-Pcs-string-12mm-WS2811-2811-IC-RGB-LED-Pixels-Module-String-Light-Black-Wire-cable/1854864234.html)
* [WEMOS D1 Mini](https://wiki.wemos.cc/products:d1:d1_mini)
* [Male 3 Pin JST Connector](https://www.aliexpress.com/item/Free-Shipping-10pcs-3pin-JST-Connector-Male-Female-plug-and-socket-connecting-Cable-Wire-for-WS2811/32366522079.html)
* [5M Telescopic Fishing Rod](https://www.aliexpress.com/item/AZJ-Brand-Wholesale-2-1-7-2M-Stream-Fishing-Rod-Glass-Fiber-Telescopic-Fishing-Rod-Ultra/32794897069.html)

## Project Dependencies
* FastLED (EPS8266 DMA Fork): https://github.com/coryking/FastLED  -*this fixes flickering caused by interupts on the ESP8226 and the WS281x's* 

* ESP8266TrueRandom: https://github.com/marvinroger/ESP8266TrueRandom

* painlessMesh: https://gitlab.com/painlessMesh/painlessMesh
    * And any painlessMesh dependencies: https://gitlab.com/painlessMesh/painlessMesh#dependencies


## Wiring
| **WS281x**        |   **Wemos D1 Mini**| 
| :-------------: |:-------------: |
| Digital In (DI) | GPIO3 (Rx)
| Ground      | Ground       |
| 5v / Vcc | 5v       |


## Powering
Power the Wemos D1 Mini through the micro USB port using a 5v mobile phone battery bank. The peak power usage is around 350-500mA on full brightness (255). 

**Note: It is HIGHLY suggested to unplug the LEDs from the Wemos D1 Mini while uploading the sketch. The LEDs being on the RX pin means that they can possibly interfeer with the upload. During upload all connected LEDs will turn white at max brightness which could possibly cause harm to the Wemos D1 Mini and/or the USB port.**

## Range 
I was able to successfully sync two nodes at a distance of 180m before running out of line of sight.

## Pinout

![Wemos D1 Mini Pinout](https://www.projetsdiy.fr/wp-content/uploads/2016/05/esp8266-wemos-d1-mini-gpio-pins.jpg)
