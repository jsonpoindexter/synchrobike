#include "painlessMesh.h"

#define   MESH_PREFIX     "whateverYouLike"
#define   MESH_PASSWORD   "somethingSneaky"
#define   MESH_PORT       5555

painlessMesh  mesh;

#include <ESP8266TrueRandom.h>

//#define FASTLED_ESP8266_DMA // Use ESP8266'a DMA (GPIO3 / Commonly RX)
                            // WS281x LEDs must be unplugged while uploading sketch
#include <FastLED.h>

#if FASTLED_VERSION < 3001000
#error "Requires FastLED 3.1 or later; check github for latest code."
#endif

#define LED_PIN     13 // This pin is ignorred when using FASTLED_ESP8266_DMA
#define NUM_LEDS    75
#define BRIGHTNESS  64
#define LED_TYPE    WS2811
#define COLOR_ORDER GRB
CRGB leds[NUM_LEDS];

#define HOLD_PALETTES_X_TIMES_AS_LONG 10 // Seconds

CRGBPalette16 currentPalette(CRGB::Black);
CRGBPalette16 targetPalette(OceanColors_p);
TBlendType    currentBlending;  // NOBLEND or LINEARBLEND 

static int16_t dist;  // A random number for our noise generator.
uint16_t xscale = 30;  // Wouldn't recommend changing this on the fly, or the animation will be really blocky.
uint16_t yscale = 30;  // Wouldn't recommend changing this on the fly, or the animation will be really blocky.
uint8_t maxChanges = 24;  // Value for blending between palettes.

boolean force_direction_change = false;
boolean force_pallet_change = false;

uint8_t direction_change; // How many seconds to wait before animation scroll direction to change
uint8_t pallette_change; // How many seconds to wait before animation scroll direction to change

// Define variables used by the sequences.
uint8_t  thisfade = 8;                     // How quickly does it fade? Lower = slower fade rate.
int       thishue = 192;                   // Starting hue.
uint8_t   thisinc = 2;                     // Incremental value for rotating hues
uint8_t   thissat = 255;                   // The saturation, where 255 = brilliant colours.
uint8_t   thisbri = 255;                   // Brightness of a sequence. Remember, max_bright is the overall limiter.
int       huediff = 256;                   // Range of random #'s to use for hue


uint8_t firework_eased   = 0;
uint8_t firework_count   = 0;
uint8_t firework_lerpVal = 0;


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

  // all types on
//mesh.setDebugMsgTypes( ERROR | MESH_STATUS | CONNECTION | SYNC | COMMUNICATION | GENERAL | MSG_TYPES | REMOTE ); 
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

  targetPalette = CRGBPalette16(CHSV(random(0,255), 255, random(128,255)),
                                CHSV(random(0,255), 255, random(128,255)),
                                CHSV(random(0,255), 192, random(128,255)),
                                CHSV(random(0,255), 255, random(128,255)));
  
  dist = random16(mesh.getNodeId()); // A semi-random number for our noise generator
  
}

void loop() {
  mesh.update();
  
  EVERY_N_MILLISECONDS(15) {
    showLEDs();
  }
  EVERY_N_MILLISECONDS(1000) {
    printf("s: %d\n", getSecond());
  }
}

uint8_t prev_second = 0;
uint8_t prev_millis = 0;
uint8_t prev_direction_time = 0;

bool direction = rand() % 2;

int16_t getMillis(){
    return (mesh.getNodeTime() / 1000);
}

int16_t getSecond(){
    return (mesh.getNodeTime() / 1000000);
}

int16_t getMinute(){
    return ((mesh.getNodeTime() / 1000000) / 60);
}

// Array of animation functions to play through.
typedef void (*SimplePatternList[])();
SimplePatternList _animations = {
  fillNoise, confettiNoise, sparkles, firework
};

// Index of the current animation.
int _currentAnimation = 0;

// Generate the animation ever (ms)
void showLEDs(){
  int timeOnAnimation = 20.0;
  int numberOfAnimations = sizeof(_animations) / sizeof(_animations[0]);
  int animation = (getSecond() / timeOnAnimation) % numberOfAnimations;
    
  if (animation != _currentAnimation){
    _currentAnimation = animation;
    Serial.printf("animation: %u\n", _currentAnimation);
    
    // Do any animation-specific reset here.
    
    firework_eased = 0;
    firework_count = 0;
    firework_lerpVal = 0;
  }

  _animations[_currentAnimation]();
  FastLED.show();
}

void fillNoise() {
  nblendPaletteTowardPalette(currentPalette, targetPalette, maxChanges);
  changePalette();
  fillnoise8();
}

void confettiNoise() {
  changePalette();
  nblendPaletteTowardPalette(currentPalette, targetPalette, maxChanges);
  confettiNoise8();
}

void sparkles() {
  // Sparkles, single color 
  changePalette();
  nblendPaletteTowardPalette(currentPalette, targetPalette, maxChanges);
  thisinc=1;
  thishue=0;
  thissat=255;
  thisfade=2;
  huediff=128;
  confetti();
}

void showPallet() {
  changePalette();
  for (int i = 0; i < NUM_LEDS; i++) {
    int index = 255 / NUM_LEDS * i;
    leds[i] = ColorFromPalette(targetPalette, index, 255, LINEARBLEND);  
  }
}

void changePalette(){
  // change color pallet every random (s)
  int second = getSecond() / HOLD_PALETTES_X_TIMES_AS_LONG;
  if ((prev_second != second) || force_pallet_change) {
    Serial.printf("Change color pallet %u\n", second);
    randomSeed(second);

    // Color picker: https://alloyui.com/examples/color-picker/hsv

    uint8_t seedColor = random(0,255);
    targetPalette = CRGBPalette16(
      // First pick a random color.
      CHSV(seedColor, 255, random(200,255)),
      // A brighter white version of that color.
      CHSV(seedColor, 196, random(128,255)),
      // First split complementary color with random vibrance (darker).
      CHSV(hueMatch(seedColor, 6), 255, random(64,255)),
      // Second split complementary color with random vibrance (darker).
      CHSV(hueMatch(seedColor, 7), 255, random(64,255)));

    prev_second = second;
    force_pallet_change = false;
  }
}

uint8_t hueMatch(uint8_t hue, uint8_t SchemeNumber) {
  //1 : Analog -
  //2 : Analog +  
  //3 : Triad Color -
  //4 : Triad Color +
  //5 : Complementary
  //6 : Complementary -
  //7 : Complementary +
  
  switch (SchemeNumber) {
    case 1: return hue-21;
        break; 
    case 2: return hue+21;
        break; 
    case 3: return hue-85;
        break; 
    case 4: return hue+85;
        break; 
    case 5: return hue+127;
        break; 
    case 6: return hue+106;
        break; 
    case 7: return hue-106;
        break; 
    }
}

/* =============== NOISE ANIMATION =============== */

void fillnoise8() {
  // Just ONE loop to fill up the LED array as all of the pixels change.
  for(int i = 0; i < NUM_LEDS; i++) {
    // Get a value from the noise function. I'm using both x and y axis.
    uint8_t index = inoise8(0, dist+i* yscale) % 255;
    // With that value, look up the 8 bit colour palette value and assign it to the current LED.
    leds[i] = ColorFromPalette(currentPalette, index, 255, LINEARBLEND);
  }
  if (direction){ // Moving along the distance (that random number we started out with). Vary it a bit with a sine wave.
    dist += beatsin8(10,1,4, mesh.getNodeTime());                        
  } else {
    dist -= beatsin8(10,1,4, mesh.getNodeTime()); 
  }
}

void changeDirection(){
    // change direction every random (s);
    int direction_time = getSecond() / direction_change;
    if((prev_direction_time != direction_time) || force_direction_change) {
        randomSeed(direction_time);
        direction = random(0,255) % 2;
        direction_change = random(5,6);
        prev_direction_time = direction_time;
        force_direction_change = false;
    }
}

/* =============== CONFETTI ANIMATION =============== */


void confetti() {                                             // random colored speckles that blink in and fade smoothly
    fadeToBlackBy(leds, NUM_LEDS, thisfade);                    // Low values = slower fade.
    int pos = random16(NUM_LEDS); 
    leds[pos] = ColorFromPalette(currentPalette,  thishue + random16(huediff)/4, thisbri, currentBlending);
    thishue = thishue + thisinc;                                   // It increments here.
}

void confettiNoise8(){
    fadeToBlackBy(leds, NUM_LEDS, thisfade);   
    int pos = random16(NUM_LEDS);          
    uint8_t index = inoise8(0, dist+pos* yscale) % 255;
    leds[pos] = ColorFromPalette(currentPalette, index, thisbri, currentBlending);
    dist += beatsin8(10,1,4, millis());       
}

/* =============== FIREWORK ANIMATION =============== */

void firework() {
  changePalette();

  // Start with easeInVal at 0 and then go to 255 for the full easing.
  firework_eased = easeOutQuart(firework_count / 255.0) * 255; //ease8InOutCubic(count);
  firework_count++;

  // Map it to the number of LED's you have.
  firework_lerpVal = lerp8by8(0, NUM_LEDS, firework_eased);

  uint8_t index = inoise8(0, dist + firework_lerpVal * yscale) % 255;
  // With that value, look up the 8 bit colour palette value and assign it to the current LED.
  leds[firework_lerpVal] = ColorFromPalette(targetPalette, index, 255, LINEARBLEND);
  leds[firework_lerpVal].maximizeBrightness();

  fadeToBlackBy(leds, NUM_LEDS, 16);  // 8 bit, 1 = slow fade, 255 = fast fade

//  if (count > 225) {
//    for (int i = NUM_LEDS - 20; i < NUM_LEDS; i++) {
//      index = inoise8(0, dist + lerpVal * yscale) % 255;
//      leds[i] = ColorFromPalette(CRGBPalette16(CHSV(0, 255, 255),
//                                               CHSV(40, 255, random(225, 255)),
//                                               CHSV(80, 255, random(225, 255)),
//                                               CHSV(140, 255, 255)), index, 255, LINEARBLEND);
////      leds[i].fadeToBlackBy(1);
//    }
//  }
  
}

float easeOutQuart(float t) {
  return 1-(--t)*t*t*t;
} 

float easeOutQuint(float t) {
  return 1+(--t)*t*t*t*t;
}
