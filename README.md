# synchrobike
Synchronized LED across bike lights

[Link to current animation demo](https://imgur.com/a/bO6bh)

In the video each strip of LEDs is attached to 1 wireless microcontroller (so 3 total in the video). When each one boots up it initially puts a single led 'fish' going back and forth on the strip. The fish's color is derived from a unique hardware ID attached to the wireless device. When the wireless devices connect to each other they share hardware Id's and then automatically add the other devices 'fish' to their strip. 

## Components
* [5V AA Battery Holder](https://www.aliexpress.com/item/Plastic-On-Off-Switch-4-x-1-5V-AA-Battery-Case-Holder-w-Cap-Black/32791164112.html?spm=2114.search0104.3.100.25bd57e7QmYioq&ws_ab_test=searchweb0_0,searchweb201602_3_10065_10344_10130_10068_10324_10342_10547_10325_10343_10546_10340_10548_10341_10545_10084_10617_10083_10616_10618_10615_10307_10313_10059_10534_100031_10103_441_10624_442_10623_10622_10621_10620_10142,searchweb201603_1,ppcSwitch_4&algo_expid=12c610c0-542a-4a46-a529-61155310b292-14&algo_pvid=12c610c0-542a-4a46-a529-61155310b292&priceBeautifyAB=2) ($1)
* [50pc 12mm WS281x 5v](https://www.aliexpress.com/item/50-Pcs-string-12mm-WS2811-2811-IC-RGB-LED-Pixels-Module-String-Light-Black-Wire-cable/1854864234.html?spm=2114.search0104.3.2.6a988a44u9URvr&ws_ab_test=searchweb0_0,searchweb201602_3_10065_10344_10130_10068_10324_10342_10547_10325_10343_10546_10340_10548_10341_10545_10084_10617_10083_10616_10618_10615_10307_10313_10059_10534_100031_10103_441_10624_442_10623_10622_10621_10620_10142,searchweb201603_1,ppcSwitch_4&algo_expid=81ef6b16-d8b9-4240-9a2a-7512ddce5816-0&algo_pvid=81ef6b16-d8b9-4240-9a2a-7512ddce5816&priceBeautifyAB=2) ($10)
* [WEMOS D1 Mini](https://wiki.wemos.cc/products:d1:d1_mini) ($3.70)
* [5M Fishing Rod](https://www.aliexpress.com/item/AZJ-Brand-Wholesale-2-1-7-2M-Stream-Fishing-Rod-Glass-Fiber-Telescopic-Fishing-Rod-Ultra/32794897069.html) ($8.30)


Total Estimated Cost: $23

## Setup
* Setup Arduino IDE for the ESP8266 (Wemos D1 Mini):  https://github.com/esp8266/Arduino
* Arduino Dependencies:
   * painlessMesh: https://gitlab.com/BlackEdder/painlessMesh
   
   * SimpleList: https://github.com/blackhack/ArduLibrariesand 

   * ArduinoJson: https://github.com/bblanchon/ArduinoJson 

![Wemos D1 Mini Pinout](https://www.projetsdiy.fr/wp-content/uploads/2016/05/esp8266-wemos-d1-mini-gpio-pins.jpg)
