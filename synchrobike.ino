#include "painlessMesh.h"

#define   MESH_PREFIX     "whateverYouLike"
#define   MESH_PASSWORD   "somethingSneaky"
#define   MESH_PORT       5555

painlessMesh  mesh;

#include <ESP8266TrueRandom.h>

#define FASTLED_ESP8266_DMA // Use ESP8266'a DMA (GPIO3 / Commonly RX)
                            // WS281x LEDs must be unplugged while uploading sketch
#include <FastLED.h>
#define FASTLED_ESP8266_DMA


#if FASTLED_VERSION < 3001000
#error "Requires FastLED 3.1 or later; check github for latest code."
#endif

#define LED_PIN     13
#define NUM_LEDS    100
#define BRIGHTNESS  64
#define LED_TYPE    WS2811
#define COLOR_ORDER GRB
CRGB leds[NUM_LEDS];

// 1 = 5 sec per palette
// 2 = 10 sec per palette
// etc
#define HOLD_PALETTES_X_TIMES_AS_LONG 30

CRGBPalette16 currentPalette(CRGB::Black);
CRGBPalette16 targetPalette(OceanColors_p);
TBlendType    currentBlending;                                // NOBLEND or LINEARBLEND 
 
static int16_t dist;                                          // A random number for our noise generator.
uint16_t xscale = 30;                                         // Wouldn't recommend changing this on the fly, or the animation will be really blocky.
uint16_t yscale = 30;                                         // Wouldn't recommend changing this on the fly, or the animation will be really blocky.
uint8_t maxChanges = 24;                                      // Value for blending between palettes.
boolean force_change = false;

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
    force_change = true;
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

//  randomSeed(mesh.getNodeId());  // This will cause a semi-random pallet to be created on first boot.
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


uint8_t prev_second_hand = 0;
uint8_t prev_millisecond_hand = 0;
uint8_t prev_direction_time = 0;

bool direction = rand() % 2;

void showAnimations(){
  int current_time = mesh.getNodeTime();
//  randomSeed(current_time / 100000);

  // Generate the animation ever (ms)
  uint8_t millisecond_hand = (current_time / 10000 % 60); // enter every 10ms
  if (prev_millisecond_hand != millisecond_hand) {    
    nblendPaletteTowardPalette(currentPalette, targetPalette, maxChanges);      // AWESOME palette blending capability.
    fillnoise8();                                                               // Update the LED array with noise at the new location
    prev_millisecond_hand = millisecond_hand;
    FastLED.show();
  }

//  // change direction every random (s);
//  uint8_t direction_time = (current_time / 10000000 % 60) / direction_change;
//  if((prev_direction_time != direction_time) || force_change) {
//    Serial.printf("SYNCHROBIKE: directionChange has been reached: %u\n", direction_time);
//    direction = random(0,255) % 2;
//    direction_change = random(5,6);
//    prev_direction_time = direction_time;
//    force_change = false;
//  }

  // change color pallet every random (s)
  
//  uint8_t second_hand = (current_time / 1000000 % 60) / 6;
 uint8_t second_hand = ((current_time / 1000000)  % 60) / HOLD_PALETTES_X_TIMES_AS_LONG;
  if ((prev_second_hand != second_hand) || force_change) {
    randomSeed(second_hand);
    Serial.printf("SYNCHROBIKE: change color pallets: %u\n", second_hand);
    targetPalette = CRGBPalette16(CHSV(random(0,255), 255, random(128,255)), CHSV(random(0,255), 255, random(128,255)), CHSV(random(0,255), 192, random(128,255)), CHSV(random(0,255), 255, random(128,255)));
    prev_second_hand = second_hand;
    force_change = false;
  }
}
 
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

