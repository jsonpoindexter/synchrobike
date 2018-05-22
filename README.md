# synchrobike
Synchronized LED across bike lights

The goal of this project is to synchronize amazing LED animations and colors across countless wiresless LED nodes.

Range: I was able to successfully sync two nodes at a distance of 180m before running out of line of sight.
Current code 

## Current Status:
Sudo-randomly generated noise LED animation, color pallets, and animation direction sync with all nodes connected to the mesh network.

## Planned Features:
* Synchronized LED animations across mesh nodes.
* Animation(s) for when a new node is added to the mesh.
* Well documented DIY instructions.

## Components
* [5V AA Battery Holder](https://www.aliexpress.com/item/Plastic-On-Off-Switch-4-x-1-5V-AA-Battery-Case-Holder-w-Cap-Black/32791164112.html?spm=2114.search0104.3.100.25bd57e7QmYioq&ws_ab_test=searchweb0_0,searchweb201602_3_10065_10344_10130_10068_10324_10342_10547_10325_10343_10546_10340_10548_10341_10545_10084_10617_10083_10616_10618_10615_10307_10313_10059_10534_100031_10103_441_10624_442_10623_10622_10621_10620_10142,searchweb201603_1,ppcSwitch_4&algo_expid=12c610c0-542a-4a46-a529-61155310b292-14&algo_pvid=12c610c0-542a-4a46-a529-61155310b292&priceBeautifyAB=2) ($1)
* [50pc 12mm WS281x 5v](https://www.aliexpress.com/item/50-Pcs-string-12mm-WS2811-2811-IC-RGB-LED-Pixels-Module-String-Light-Black-Wire-cable/1854864234.html?spm=2114.search0104.3.2.6a988a44u9URvr&ws_ab_test=searchweb0_0,searchweb201602_3_10065_10344_10130_10068_10324_10342_10547_10325_10343_10546_10340_10548_10341_10545_10084_10617_10083_10616_10618_10615_10307_10313_10059_10534_100031_10103_441_10624_442_10623_10622_10621_10620_10142,searchweb201603_1,ppcSwitch_4&algo_expid=81ef6b16-d8b9-4240-9a2a-7512ddce5816-0&algo_pvid=81ef6b16-d8b9-4240-9a2a-7512ddce5816&priceBeautifyAB=2) ($10)
* [WEMOS D1 Mini](https://wiki.wemos.cc/products:d1:d1_mini) ($3.70)
* [5M Fishing Rod](https://www.aliexpress.com/item/AZJ-Brand-Wholesale-2-1-7-2M-Stream-Fishing-Rod-Glass-Fiber-Telescopic-Fishing-Rod-Ultra/32794897069.html) ($8.30)


Total Estimated Cost: $23

## Setup
1. Setup Arduino IDE for the ESP8266 (Wemos D1 Mini):  https://github.com/esp8266/Arduino
2. Install Arduino library dependencies:
    * FastLED (EPS8266 DMA Fork): https://github.com/coryking/FastLED  -*this fixes flickering caused by interupts on the ESP8226 and the WS281x's* 

   * painlessMesh: https://gitlab.com/painlessMesh/painlessMesh
        * And any painlessMesh dependencies: https://gitlab.com/painlessMesh/painlessMesh#dependencies
3. Connect the WS281x to the Wemos D1 Mini:

| **WS281x**        |   **Wemos D1 Mini**| 
| :-------------: |:-------------: |
| Digital In (DI) | GPIO3 (Rx)
| Ground      | Ground       |
| 5v / Vcc | 5v       |

4. Connect your power source's 5v and Ground to the **WS2811x's dedicated 5v and Ground cables that are separate from the JST connectors.**  
   
## Pinout

![Wemos D1 Mini Pinout](https://www.projetsdiy.fr/wp-content/uploads/2016/05/esp8266-wemos-d1-mini-gpio-pins.jpg)

Syncing Animations:
- [x] https://github.com/atuline/FastLED-Demos/blob/master/one_sine_pal_demo/one_sine_pal_demo.ino
- [ ] Lightning bolt
- [ ] Sparkles / Twinkle
- [ ] More to come!
