#include <LinkedList.h>
#include <unordered_map>
#include <unordered_set>
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

std::unordered_map<uint32_t, Node> nodes;
std::list<uint32_t> mesh_nodes;

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
  nodes.emplace(nodeId, Node { 
    angle: random(0, 255),
    color: ColorFromPalette(RainbowColors_p, nodeId, brightness, LINEARBLEND) 
  });
}

void setup() {
  Serial.begin(115200);

  pinMode(LED, OUTPUT);
  mesh.init(MESH_SSID, MESH_PASSWORD, MESH_PORT);
  
  mesh.onChangedConnections(&changedConnectionCallback);

  FastLED.addLeds<WS2812B, DATA_PIN, RGB>(leds.data(), NUM_LEDS);

  FastLED.show();

  addNode(mesh.getNodeId(), 255);
  
}

void loop() {
  mesh.update();
  showNodes();
}


void changedConnectionCallback() {
  auto current_nodes = mesh.getNodeList();

  std::unordered_set<uint32_t> existing_node_ids{current_nodes.begin(), current_nodes.end()};
  existing_node_ids.insert(mesh.getNodeId());
  
  Serial.println("*** connection change***");
  // 1. A node that is not in nodes will be in mesh.getNodeId()
  // 2. a node that is in mesh.getNodeId() will not be in  

  Serial.printf("mesh.getNodeList().size: %i\n", mesh_nodes.size());
  Serial.printf("nodes.size: %i\n", nodes.size());
  
  for (auto& node : current_nodes) {
    if (nodes.find(node) == nodes.end()) {
      Serial.println("New node found");
      addNode(node, BRIGHTNESS);
    } else {
      Serial.println("Not a new node");
    }
  }

  for(auto it = nodes.begin(); it != nodes.end(); ) {
    // If this node ID is NOT in mesh_nodes, erase
    if (existing_node_ids.find(it->first) == existing_node_ids.end()) {
      it = nodes.erase(it);
    } else {
      it++;
    }
  }
  
}

