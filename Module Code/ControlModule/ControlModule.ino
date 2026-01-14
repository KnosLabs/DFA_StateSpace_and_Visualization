#include <Wire.h>

// Constants
#define NUM_INPUT_PORTS 4 
#define MAX_ACTUATORS 5

const int port = 6;   //Digital ID Pin
bool pairMode = false;  
bool controlPresent = false;
bool present = false;
int count = 0;

int configurationMatrix[MAX_ACTUATORS][NUM_INPUT_PORTS] = {0}; 
int commandMatrix[MAX_ACTUATORS][NUM_INPUT_PORTS];

struct Command {
  unsigned long time;
  int module;   
  int ports[3];                    
  int angle;            
};


#define MAX_COMMANDS 50
Command commandBuffer[MAX_COMMANDS];
int commandCount = 0;

unsigned long startTime;

void writePort(int, int);

void setup() {
  Serial.begin(9600);
  Wire.begin(); //Master
}

void loop() {
  // If actuator detect, send control module signal (1)
  writePort(port, 1);

  //Request configuration data from Actuators by ID
  for (int actuatorID = 1; actuatorID <= MAX_ACTUATORS; actuatorID++) {
    requestData(actuatorID);
    delay(200); 
  }

  updateConfigArrays();
  //sendMatrix();

  receiveCommands();
  if (commandBuffer){
    runCommand();
  }
  //}
  printConfigurationMatrix();
  delay(200);
}




