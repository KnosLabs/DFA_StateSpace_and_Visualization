#include <Wire.h>

#define MODULE_ID 4

//Pin layout
  const int selectPins[4] = {0, 1, 2, 3};
  const int z = 7; 

  const int bendPin = 6;
  const int outputPorts[3] = {8, 9, 10};

//Input Ports
 int ID1A[4] = {0, 0, 1, 0};
 int ID1B[4] = {1, 0, 1, 0}; 
 int ID2A[4] = {0, 0, 0, 0}; 
 int ID2B[4] = {1, 0, 0, 0};
 int ID3A[4] = {0, 1, 0, 0};
 int ID3B[4] = {1, 1, 0, 0};

 int* inputPorts[6] = {ID1A, ID1B, ID2A, ID2B, ID3A, ID3B};

//Air solenoids 
  int airIn[4] = {0, 1, 1, 0};
  int airOut[4] = {1, 1, 1, 0};

//Locking Connectors (Motor drivers)
  int Unlock1[4] = {1, 0, 1, 1};
  int Lock1[4] = {0, 1, 1, 1};
  int Unlock2[4] = {1, 0, 0, 1};
  int Lock2[4] = {0, 1, 0, 1};
  int Unlock3[4] = {1, 1, 0, 1};
  int Lock3[4] = {0, 0, 1, 1};
  int test[4] = {1, 1, 1, 1};
  
  int* locking[3] = {Lock1, Lock2, Lock3};
  int* unlocking[3] = {Unlock1, Unlock2, Unlock3};

int attemptCount[6] = {0};

volatile bool dataReceived = false;
volatile int receivedData = 0;

int8_t inputData[4] = {0, 0, 0, 0};    //Receiving ports and bend angle
bool pairMode[3] = {false, false, false};

bool connectedBlue[6] = {false}; //
bool connectedRed[3] = {false};

volatile int angle = 0;

int binaryArray[4];

bool controlMode = false;
int command;

void setup() {
  Serial.begin(9600);
  Wire.begin(MODULE_ID);
  Wire.onRequest(requestEvent);
  Wire.onReceive(receiveEvent);

  for (int i=0; i<3; i++) {
    pinMode(outputPorts[i], INPUT);
  }

  for (int i=0; i<4; i++) {
    pinMode(selectPins[i], OUTPUT);
    digitalWrite(selectPins[i], LOW);
  }

  pinMode(bendPin, INPUT);
}

void loop() {
//Reads signals on received on digital pins
  for (int i = 1; i < 4; i++) {
    setPins(inputPorts[i*2-2]);
    readPort(z, i*2-2);
  }
  
//Write actuator and port data to sending ports
 for (int i = 0; i < 3; i++){
    writePort(outputPorts[i], i + 4, i);
  }

//Print actuator data
  Serial.print("Actuator Data: ");
  for (int i=0; i<4; i++){
    Serial.print(inputData[i]);
    Serial.print(", ");
  }
  Serial.println();

  readAngle();

  while(controlMode){}  //If commands are being sent, wait to continue
  delay(100);
  //boardTest();
}






