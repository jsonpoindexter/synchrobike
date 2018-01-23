#include "FastLED.h"

// How many leds in your strip?
#define NUM_LEDS 72

// For led chips like Neopixels, which have a data line, ground, and power, you just
// need to define DATA_PIN.  For led chipsets that are SPI based (four wires - data, clock,
// ground, and power), like the LPD8806 define both DATA_PIN and CLOCK_PIN
#define DATA_PIN 13

// Define the array of leds
CRGB leds[NUM_LEDS];

class Ball
{
  // Class Member Variables
  // These are initialized at startup
  public: uint8_t  angle;
  public: CRGB color;    // milliseconds of off-time

  // Constructor - initializes the member variables and state
  public:
  Ball(uint8_t  initAngle, CRGB initColor)
  {
    angle = initAngle;
    color = initColor;   
  }
};


Ball balls[] = {
  Ball(random(0, 255),CRGB( random(0, 255), random(0, 255), random(0, 255))),
  Ball(random(0, 255),CRGB( random(0, 255), random(0, 255), random(0, 255))),
  Ball(random(0, 255),CRGB( random(0, 255), random(0, 255), random(0, 255))),
  Ball(random(0, 255),CRGB( random(0, 255), random(0, 255), random(0, 255))),
  Ball(random(0, 255),CRGB( random(0, 255), random(0, 255), random(0, 255))),
  Ball(random(0, 255),CRGB( random(0, 255), random(0, 255), random(0, 255))),
};

void setup() {
  Serial.begin(9600); 
  FastLED.addLeds<WS2812B, DATA_PIN, RGB>(leds, NUM_LEDS);
  randomSeed(analogRead(0));
  initBalls();
}

int lead_dot = 0;
uint8_t  angle = 0;

void loop() 
{
  
  EVERY_N_MILLISECONDS(10)
  {
    for (int i = 0; i < sizeof(balls) / sizeof(Ball); i++){
      uint8_t lead_dot = map(triwave8(balls[i].angle), 0, 255, 0, NUM_LEDS - 1);
      
      balls[i].angle = balls[i].angle + 1;
      leds[lead_dot] = balls[i].color;
      fadeToBlackBy(leds, NUM_LEDS, 32);
    }
  }

  FastLED.show();

  Serial.println(balls[0].angle);

}

void initBalls(){
  for (int i = 0; i < sizeof(balls) / sizeof(Ball); i++){
    balls[i].angle = random(0, 255);
    balls[i].color = CRGB( random(0, 255), random(0, 255), random(0, 255));
  }
}

