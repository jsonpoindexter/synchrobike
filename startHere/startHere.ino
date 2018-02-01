#include <LinkedList.h>
#include <unordered_map>
#include <array>

//************************************************************
// this is a simple example that uses the easyMesh library
//
// 1. blinks led once for every node on the mesh
// 2. blink cycle repeats every BLINK_PERIOD
// 3. sends a silly message to every node on the mesh at a random time betweew 1 and 5 seconds
// 4. prints anything it recieves to Serial.print
//
//
//************************************************************

#include <painlessMesh.h>

// some gpio pin that is connected to an LED...
// on my rig, this is 5, change to the right number of your LED.
#define   LED             2       // GPIO number of connected LED, ON ESP-12 IS GPIO2

#define   BLINK_PERIOD    3000 // milliseconds until cycle repeat
#define   BLINK_DURATION  100  // milliseconds LED is on for

#define   MESH_SSID       "whateverYouLike"
#define   MESH_PASSWORD   "somethingSneaky"
#define   MESH_PORT       5555

painlessMesh  mesh;
bool calc_delay = false;

/******* INIT LEDS *******/
#include "FastLED.h"

#define NUM_LEDS 72
#define DATA_PIN 13 //D7

#define BRIGHTNESS  64

// Define the array of leds
std::array<CRGB, NUM_LEDS> leds;

struct Node {
  uint8_t  angle;
  CRGB color;
};

std::unordered_map<int32_t, Node> nodes;

void showNodes(){
  EVERY_N_MILLISECONDS(10)
  {
    for (auto& i : nodes) {
      auto& node = i.second;
      auto& nodeId = i.first;
      
      auto lead_dot = map(triwave8(node.angle), 0, 255, 0, NUM_LEDS - 1);
      node.angle = node.angle + 1;
     
      leds.at(lead_dot) = node.color;
    }
    
    fadeToBlackBy(leds.data(), NUM_LEDS, 32);
  }
  FastLED.show();
}

void addNode(int nodeId, int brightness){
 
  // Node newNode;
  // newNode.angle = random(0, 255);
  // newNode.color =  ColorFromPalette(RainbowColors_p, nodeId, brightness, LINEARBLEND);
  nodes.emplace(nodeId, Node { 
    angle: random(0, 255),
    color: ColorFromPalette(RainbowColors_p, nodeId, brightness, LINEARBLEND) 
  });
}

//
////glitter effect
//void addGlitter( int chanceOfGlitter) {
//  for( int i = 0; i < chanceOfGlitter; i++) {
//    int led = random16(NUM_LEDS);
//    leds[led] = CRGB::White;
//    leds[led].fadeToBlackBy( 16 );
//  }
//}

void setup() {
  Serial.begin(115200);

  pinMode(LED, OUTPUT);

  //mesh.setDebugMsgTypes( ERROR | MESH_STATUS | CONNECTION | SYNC | COMMUNICATION | GENERAL | MSG_TYPES | REMOTE ); // all types on
  //mesh.setDebugMsgTypes(ERROR | DEBUG | CONNECTION | COMMUNICATION);  // set before init() so that you can see startup messages
  //mesh.setDebugMsgTypes(ERROR | DEBUG | CONNECTION);  // set before init() so that you can see startup messages

  mesh.init(MESH_SSID, MESH_PASSWORD, MESH_PORT);
  
  mesh.onChangedConnections(&changedConnectionCallback);

  //randomSeed(analogRead(A0));

  FastLED.addLeds<WS2812B, DATA_PIN, RGB>(leds.data(), NUM_LEDS);

  FastLED.show();

  addNode(mesh.getNodeId(), 255);
  
}

void loop() {
  mesh.update();
  showNodes();
}

void receivedCallback(uint32_t from, String & msg) {
//  Serial.printf("startHere: Received from %u msg=%s\n", from, msg.c_str());
}

void changedConnectionCallback() {
  nodes = {};
   addNode(mesh.getNodeId(), 255);
  for (auto& node : mesh.getNodeList()) {
    addNode(node, BRIGHTNESS);
  }
}

