#include "FastLED.h"

// How many leds in your strip?
#define NUM_LEDS 72

// For led chips like Neopixels, which have a data line, ground, and power, you just
// need to define DATA_PIN.  For led chipsets that are SPI based (four wires - data, clock,
// ground, and power), like the LPD8806 define both DATA_PIN and CLOCK_PIN
#define DATA_PIN 13

// Define the array of leds
CRGB leds[NUM_LEDS];

#define MAX_BALLS 256

int node_count = 0;

struct Ball {
  uint32_t id;
  uint8_t  angle;
  CRGB color;
  uint8_t speed;
};
typedef struct Ball Ball;

Ball balls[MAX_BALLS];

void initBall(){
  balls[0].id = 1234;
  balls[0].angle = 0;
  balls[0].color = CRGB(0,0,255);
  balls[0].speed = random(1,5);
  node_count++;
}

void addBall(){
  balls[node_count].id = random();
  balls[node_count].angle = 0;
  balls[node_count].color = CRGB(random(0,255),random(0,255),random(0,255));
  balls[node_count].speed = random(1,5);
  node_count++;
}

void removeBall(){
  if(node_count > 1){
    node_count--;
  }
}


void setup() {
  Serial.begin(9600); 
  FastLED.addLeds<WS2812B, DATA_PIN, RGB>(leds, NUM_LEDS);
  randomSeed(analogRead(0));
  initBall();
}

int lead_dot = 0;

long previousMillis = 0;        // will store last time LED was updated
long interval = 2000;           // interval at which to blink (milliseconds)

void loop() 
{

  unsigned long currentMillis = millis();
  if(currentMillis - previousMillis > interval) {
    previousMillis = currentMillis;
    if (random() % 2){
       addBall();  
    } else {
      removeBall();
    }
  }
  
  EVERY_N_MILLISECONDS(10)
  {
    for (int i = 0; i < node_count; i++){
      uint8_t lead_dot = map(triwave8(balls[i].angle), 0, 255, 0, NUM_LEDS - 1);
      
      balls[i].angle = balls[i].angle + 1;
      leds[lead_dot] = balls[i].color;
     
    }
     fadeToBlackBy(leds, NUM_LEDS, 32);
  }

  FastLED.show();

}
