#include "painlessMesh.h"

#define   MESH_PREFIX     "whateverYouLike"
#define   MESH_PASSWORD   "somethingSneaky"
#define   MESH_PORT       5555

painlessMesh  mesh;

#include <ESP8266TrueRandom.h>

#define FASTLED_ESP8266_DMA // Use ESP8266'a DMA (GPIO3 / Commonly RX)
                            // WS281x LEDs must be unplugged while uploading sketch
#include <FastLED.h>

#if FASTLED_VERSION < 3001000
#error "Requires FastLED 3.1 or later; check github for latest code."
#endif

#define LED_PIN     13 // This pin is ignorred when using FASTLED_ESP8266_DMA
#define NUM_LEDS    50
#define BRIGHTNESS  64 // 0 - 255
#define LED_TYPE    WS2811
#define COLOR_ORDER GRB
CRGB leds[NUM_LEDS];

#define HOLD_PALETTES_X_TIMES_AS_LONG 10 // Seconds

CRGBPalette16 currentPalette(CRGB::Black);
CRGBPalette16 targetPalette(OceanColors_p);
TBlendType    currentBlending;                                // NOBLEND or LINEARBLEND 
 
static int16_t dist;                                          // A random number for our noise generator.
uint16_t xscale = 30;                                         // Wouldn't recommend changing this on the fly, or the animation will be really blocky.
uint16_t yscale = 30;                                         // Wouldn't recommend changing this on the fly, or the animation will be really blocky.
uint8_t maxChanges = 24;                                      // Value for blending between palettes.
boolean force_direction_change = false;
boolean force_pallet_change = false;

uint8_t direction_change; // How many seconds to wait before animation scroll direction to change
uint8_t pallette_change; // How many seconds to wait before animation scroll direction to change

void receivedCallback( uint32_t from, String &msg ) {
  Serial.printf("SYSTEM: Received from %u msg=%s\n", from, msg.c_str());
}

void newConnectionCallback(uint32_t nodeId) {
    Serial.printf("SYSTEM: New Connection, nodeId = %u\n", nodeId);
}

void changedConnectionCallback() {
    Serial.printf("SYSTEM: Changed connections %s\n",mesh.subConnectionJson().c_str());
}

void nodeTimeAdjustedCallback(int32_t offset) {
    Serial.printf("SYSTEM: Adjusted time %u. Offset = %d\n", mesh.getNodeTime(),offset);
    force_direction_change = true;
    force_pallet_change = true;
}

void setup() {
  Serial.begin(115200);

//mesh.setDebugMsgTypes( ERROR | MESH_STATUS | CONNECTION | SYNC | COMMUNICATION | GENERAL | MSG_TYPES | REMOTE ); // all types on
  mesh.setDebugMsgTypes( ERROR | STARTUP );  // set before init() so that you can see startup messages

  mesh.init( MESH_PREFIX, MESH_PASSWORD, MESH_PORT );
  mesh.onReceive(&receivedCallback);
  mesh.onNewConnection(&newConnectionCallback);
  mesh.onChangedConnections(&changedConnectionCallback);
  mesh.onNodeTimeAdjusted(&nodeTimeAdjustedCallback);
  
  FastLED.addLeds<LED_TYPE, LED_PIN, COLOR_ORDER>(leds, NUM_LEDS).setCorrection( TypicalLEDStrip );
  FastLED.setBrightness(  BRIGHTNESS );

  set_max_power_in_volts_and_milliamps(5, 500);               // FastLED Power management set at 5V, 500mA.
  
  randomSeed(ESP8266TrueRandom.random());
  direction_change = random(5,10); // How many seconds to wait before animation scroll direction to change
  pallette_change = random(4,8); // How many seconds to wait before animation scroll direction to change

  targetPalette = CRGBPalette16(CHSV(random(0,255), 255, random(128,255)), CHSV(random(0,255), 255, random(128,255)), CHSV(random(0,255), 192, random(128,255)), CHSV(random(0,255), 255, random(128,255)));
  
  dist = random16(mesh.getNodeId()); // A semi-random number for our noise generator
  
}

void loop() {
  mesh.update();
  showAnimations();
}

int previous_seed = 0;
uint8_t prev_second_hand = 0;
uint8_t prev_millisecond_hand = 0;
uint8_t prev_direction_time = 0;

bool direction = rand() % 2;

void showAnimations(){
  int current_time = mesh.getNodeTime();


  // Generate the animation ever (ms)
  int millisecond_hand = (current_time / 10000 % 60); // enter every 10ms
  if (prev_millisecond_hand != millisecond_hand) {   
    nblendPaletteTowardPalette(currentPalette, targetPalette, maxChanges);      // AWESOME palette blending capability.
//    fillnoise8();
    confetti(); // Update the LED array with noise at the new location
    prev_millisecond_hand = millisecond_hand;
    FastLED.show();
  }

  // change direction every random (s);
  int direction_time = current_time / 10000000 / direction_change;
  if((prev_direction_time != direction_time) || force_direction_change) {
    randomSeed(direction_time);
    Serial.printf("SYNCHROBIKE: directionChange has been reached: %u\n", direction_time);
    direction = random(0,255) % 2;
    direction_change = random(5,6);
    prev_direction_time = direction_time;
    force_direction_change = false;
  }

  // change color pallet every random (s)
 int second_hand = (current_time / 1000000) / HOLD_PALETTES_X_TIMES_AS_LONG;
  if ((prev_second_hand != second_hand) || force_pallet_change) {
    randomSeed(second_hand);
    Serial.printf("SYNCHROBIKE: change color pallets: %u\n", second_hand);
    targetPalette = CRGBPalette16(CHSV(random(0,255), 255, random(128,255)), CHSV(random(0,255), 255, random(128,255)), CHSV(random(0,255), 192, random(128,255)), CHSV(random(0,255), 255, random(128,255)));
    prev_second_hand = second_hand;
    force_pallet_change = false;
    changeConfetti();
  }
}

/* =============== NOISE ANIMATION =============== */
 
void fillnoise8() {
  for(int i = 0; i < NUM_LEDS; i++) {                                      // Just ONE loop to fill up the LED array as all of the pixels change.
    uint8_t index = inoise8(0, dist+i* yscale) % 255;               // Get a value from the noise function. I'm using both x and y axis.
    leds[i] = ColorFromPalette(currentPalette, index, 255, LINEARBLEND);   // With that value, look up the 8 bit colour palette value and assign it to the current LED.
  }
  if (direction){ // Moving along the distance (that random number we started out with). Vary it a bit with a sine wave.
    dist += beatsin8(10,1,4, mesh.getNodeTime());                        
  } else {
    dist -= beatsin8(10,1,4, mesh.getNodeTime()); 
  }
}

/* =============== CONFETTI ANIMATION =============== */
// Define variables used by the sequences.
uint8_t  thisfade = 8;                                        // How quickly does it fade? Lower = slower fade rate.
int       thishue = 50;                                       // Starting hue.
uint8_t   thisinc = 1;                                        // Incremental value for rotating hues
uint8_t   thissat = 100;                                      // The saturation, where 255 = brilliant colours.
uint8_t   thisbri = 255;                                      // Brightness of a sequence. Remember, max_bright is the overall limiter.
int       huediff = 256;                                      // Range of random #'s to use for hue
uint8_t thisdelay = 5;

void confetti() {                                             // random colored speckles that blink in and fade smoothly
    fadeToBlackBy(leds, NUM_LEDS, thisfade);                    // Low values = slower fade.
//    random16_set_seed((mesh.getNodeTime() / 1000));
    int pos = random16(NUM_LEDS);                               // Pick an LED at random.
    leds[pos] += CHSV((thishue + random16(huediff))/4 , thissat, thisbri);  // I use 12 bits for hue so that the hue increment isn't too quick.
    thishue = thishue + thisinc;                                // It increments here.
}


void changeConfetti() {                                             // A time (rather than loop) based demo sequencer. This gives us full control over the length of each sequence.
//    uint8_t secondHand = (mesh.getNodeTime() / 1000000) %
//                         15;                // IMPORTANT!!! Change '15' to a different value to change duration of the loop.
//    static uint8_t lastSecond = 99;                             // Static variable, means it's only defined once. This is our 'debounce' variable.
//    if (lastSecond != secondHand) {                             // Debounce to make sure we're not repeating an assignment.
//        lastSecond = secondHand;
//        switch (secondHand) {
//            case 0:
                thisinc = 1;
                thishue = 192;
                thissat = 255;
                thisfade = 18;
                huediff = 256;
//                break;  // You can change values here, one at a time , or altogether.
//            case 5:
//                thisinc = 2;
//                thishue = 128;
//                thisfade = 8;
//                huediff = 64;
//                break;
//            case 10:
//                random16_set_seed((mesh.getNodeTime() / 1000000) / HOLD_PALETTES_X_TIMES_AS_LONG);
//                thisinc = 1;
//                thishue = random(255);
//                thisfade = 1;
//                huediff = 16;
//                break;      // Only gets called once, and not continuously for the next several seconds. Therefore, no rainbows.
//            case 15:
//                break;                                                                // Here's the matching 15 for the other one.
//        }
//    }
}


