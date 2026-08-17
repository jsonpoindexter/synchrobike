# Synchrobike

Synchronized LED color palettes and animations over a wireless node mesh.

The project runs on Wemos D1 Mini boards and keeps WS281x LED animations aligned
across nearby bikes or other mobile installations.

[Video preview](https://github.com/jsonpoindexter/synchrobike/blob/7a36adf7c99e19d84d8cd89cc18fcecfbe31a66b/IMG_6202.mov)

## Hardware

- 5V phone battery bank
- USB-to-Micro-USB cable
- [50 WS281x 5V pixels](https://www.aliexpress.com/item/50-Pcs-string-12mm-WS2811-2811-IC-RGB-LED-Pixels-Module-String-Light-Black-Wire-cable/1854864234.html)
- [Wemos D1 Mini](https://www.wemos.cc/en/latest/d1/d1_mini.html)
- Male 3-pin JST connector
- 5m telescopic fishing rod

## Software setup

Python 3.11 and Git are required. Create a virtual environment and install the
pinned PlatformIO and upload-tool dependencies:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows, activate the environment with `.venv\Scripts\activate`.

All firmware libraries and the ESP8266 platform are pinned in `platformio.ini`;
do not clone dependencies into `lib/` manually.

## Build

On macOS or Linux:

```sh
./build.sh
```

On any supported platform:

```sh
pio run -e d1_mini
```

Additional PlatformIO arguments can be passed through the build script, for
example `./build.sh -v` or `./build.sh -t clean`.

## Upload and monitor

Inspect serial devices before uploading:

```sh
python upload.py --list-ports
```

The uploader automatically selects USB serial devices, builds once, and uploads
to the selected devices in parallel:

```sh
python upload.py --upload
```

Use repeatable `--port` arguments when automatic discovery is too broad or when
testing command construction:

```sh
python upload.py --upload --port /dev/cu.usbserial-1 --port /dev/cu.usbserial-2
python upload.py --upload --port /dev/cu.usbserial-1 --dry-run
```

On macOS, iTerm2 can open or reuse one monitor pane per device. Enable iTerm2's
Python API first, then run:

```sh
python upload.py --upload --monitor
```

Run `python upload.py --help` for retry, concurrency, environment, and split
options.

> **Important:** Unplug the LEDs from the Wemos D1 Mini while uploading. The LED
> data line uses GPIO3/RX, and upload traffic can turn all LEDs on at full
> brightness, potentially overloading the board or USB port.

## Wiring

| WS281x | Wemos D1 Mini |
| --- | --- |
| Digital In (DI) | GPIO3 / RX |
| Ground | Ground |
| 5V / VCC | 5V |

Power the Wemos D1 Mini through its Micro-USB port with a 5V battery bank. Peak
power usage is approximately 350–500mA at full brightness.

## Range

Two nodes have synchronized successfully at 180m line-of-sight.

## Pinout

![Wemos D1 Mini pinout](https://www.projetsdiy.fr/wp-content/uploads/2016/05/esp8266-wemos-d1-mini-gpio-pins.jpg)
