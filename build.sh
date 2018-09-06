#!/bin/bash

# Clone dependencies
repos=( 
    "https://github.com/marvinroger/ESP8266TrueRandom"
    "https://github.com/coryking/FastLED"
    "https://gitlab.com/painlessMesh/painlessMesh.git"
    "https://github.com/bblanchon/ArduinoJson"
    "https://github.com/arkhipenko/TaskScheduler"
    "https://github.com/me-no-dev/ESPAsyncTCP"
    "https://github.com/me-no-dev/AsyncTCP"
)
cd lib
for repo in "${repos[@]}"
do 
    git clone $repo
done

cd ..

# Build and Upload
python3 upload.py