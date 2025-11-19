#include <Wire.h>

#define MODULE_ID 2

//Correct pin layout
const int selectPins[4] = {0, 1, 2, 3};
const int z = 7; 

const int bendPin = 6;
const int outputPorts[3] = {8, 9, 10};


//Temp pin assignments
/*const int selectPins[4] = {4, 6, 8, 9};
const int z = 5; 

const int bendPin = 1;
const int outputPorts[3] = {2, 3, 10};*/

//INPUT PORTS
 int ID1A[4] = {0, 0, 1, 0};
 int ID1B[4] = {1, 0, 1, 0}; 
 int ID2A[4] = {0, 0, 0, 0}; 
 int ID2B[4] = {1, 0, 0, 0};
 int ID3A[4] = {1, 1, 0, 0};
 int ID3B[4] = {0, 1, 0, 0};


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

//Local configuration matrix
volatile bool dataReceived = false;
volatile int receivedData = 0;

int incomingMatrix[3];   

int8_t inputData[4] = {0, 0, 0, 0};    //Receiving ports and bend angle
bool pairMode[3] = {false, false, false};

bool connected[6] = {false, false, false, false, false, false};

volatile int angle = 0;

int binaryArray[4];

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
//disconnect(0);
 //connect(2);
 //connect(2);


}

void loop() {
//Check all input and output ports for signal 
for (int i = 0; i < 6; i++) {
    setPins(inputPorts[i]);
    readPort(z, i);
  }
  
 for (int i = 0; i < 3; i++){
    writePort(outputPorts[i], i + 4, i);
  }

  readAngle();
  Serial.print("Angle: ");
  Serial.println(angle);
  delay(100);
  //boardTest();
}


void setPins(int input[4]){
  for(int i=0; i<4; i++){
    digitalWrite(selectPins[i], input[i] == 1 ? HIGH : LOW);
  }
}


//Write ports
void writePort(int port, int portNum, int idx) {
  // Check if port is connected via update from control module
  if(connected[portNum-1]){
    pinMode(port, OUTPUT);
    digitalWrite(port, HIGH);
  }

  else{
  //Seaching for device on port
  pinMode(port, INPUT_PULLDOWN);
  attachInterrupt(digitalPinToInterrupt(port), pairingMode, CHANGE);


// Check to see if actuator should go into pairing mode
  if(pairMode[idx] == true){
    detachInterrupt(digitalPinToInterrupt(port));

    int startTime = millis();
    Serial.print("In pairing mode on port ");
    Serial.println(idx + 4);

    Serial.println("Entering Paring Mode");
    while(digitalRead(port) == LOW){
      if(millis() - startTime > 5000){
        pairMode[idx] = false;
        return;
      }
    }

  pinMode(port, OUTPUT);
  delay(75);
  digitalWrite(port, HIGH);
  delay(75);
  digitalWrite(port, LOW);
  delay(50);

  //Combine port number and actuator data
  int data = (portNum & 0x07) | ((MODULE_ID & 0x1F) << 3); 
  Serial.print("Sending data: ");
  Serial.println(data);

  //Send data bitwise
  for (int i = 0; i < 8; i++) {
    digitalWrite(port, (data & (1 << i)) ? HIGH : LOW);
    delay(75); 
  }

    //Set pin to high
    digitalWrite(port, HIGH);
    pairMode[idx] = false;
   }
  }
}

// Read Ports
void readPort(int port, int idx) {
    //Stop reading process if actuator data is already read and detected
    pinMode(z, INPUT_PULLDOWN);
    delay(20);

    if(digitalRead(port) == HIGH){
      connected[idx] = true;
      return;
    } else {
      connected[idx] = false;
      inputData[idx%2] == 0;
    }

    if(connected[idx] == false){
      pinMode(port, OUTPUT);
      digitalWrite(port, HIGH);
      delay(50);
      digitalWrite(port, LOW);

      pinMode(port, INPUT_PULLDOWN);
      delay(70);

      if(digitalRead(port)==HIGH){
        delay(100);
        if(inputData[idx%2] == 0){
            Serial.print("Receiving on ... ");
            Serial.println(idx);
            receivedData = 0;
            for (int j = 0; j < 8; j++) { 
              if (digitalRead(port) == HIGH) {
                receivedData |= (1 << j);
              }
              delay(75);
            }
            //Initiates locking
            if(receivedData != 0){
                connect(idx/2);
                Serial.print("Recieved on port ");
                Serial.print(port/2);
                Serial.print(" ");
                Serial.println(receivedData);
            }

          //Switches data sign depending on port received on
            if(idx%2 == 1){
              receivedData = -1 * receivedData;
            }
            inputData[idx/2] = receivedData;
        }
          //decodeData(receivedData);
      
      }
    }
}

void pairingMode() {
  for(int i = 0; i < 3; i++){
    if(digitalRead(outputPorts[i]) == HIGH){
      pairMode[i] = true;
    }
  }
}

void decodeData(int data){
  int connectorNumber = data & 0x07; // Lower 3 bits are connector number
  int actuatorID = (data >> 3) & 0x1F; // Upper 5 bits are actuator ID

    Serial.print("Received data - Actuator ID: ");
    Serial.print(actuatorID);
    Serial.print(", Connector Number: ");
    Serial.println(connectorNumber);
}

void connect(int motor){
    for(int i = 0; i < 10; i++) {
        setPins(unlocking[motor]);
        analogWrite(z, 100);
        delay(75);
        setPins(locking[motor]);
        analogWrite(z, 255);
        delay(150);
        analogWrite(z, 0);
      }
}

void disconnect(int motor){
    for(int i = 0; i < 10; i++) {
        setPins(locking[motor]);
        analogWrite(z, 100);
        delay(75);
        setPins(unlocking[motor]);
        analogWrite(z, 255);
        delay(150);
        analogWrite(z, 0);
      }
}

void requestEvent() {
  Wire.write(MODULE_ID); // Send the actuator ID first
  for (int i = 0; i < 3; i++) {
    Serial.println(inputData[i]);
    Wire.write(inputData[i]); // Send each data in the array
  }
}

void receiveEvent(int numByte){
  int i = 3;
  while (Wire.available()) {
    int readData = Wire.read();
    if (readData == 1) {
      connected[i] = true;
    } else {
      connected[i] = false;
    }
    i++;
  }
}

void readAngle(){
  int bendValue = analogRead(bendPin);
  angle = map(bendValue, 660, 1023, 0, 100);
  inputData[3] = angle;
}


void resetPins(){
  for(int i=0; i<4; i++){
    digitalWrite(selectPins[i], LOW);
  }
}


void boardTest(){  //iterates over all pins on the multiplexer
   for (int i = 0; i < 16; i++) {
    String binary = String(i, BIN);
    while (binary.length() < 4) {
      binary = "0" + binary;
    }
    for (int j = 0; j < 4; j++) {
      binaryArray[j] = binary.charAt(j) - '0';  // Convert char to int
    }
    setPins(binaryArray);
    digitalWrite(z, HIGH);
    delay(1500);
    digitalWrite(z, LOW);

    Serial.print("Active Pin: ");
    Serial.println(i);
  }

  for (int k = 0; k < 3; k++){
      Serial.print("Output Port: ");
      Serial.println(4+k);
      digitalWrite(outputPorts[k], HIGH);
      delay(1500);
      digitalWrite(outputPorts[k], LOW);
    }

  readAngle();
  Serial.print("Angle: ");
  Serial.println(angle);

   
}
