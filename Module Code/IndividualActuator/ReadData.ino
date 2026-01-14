//Write ports
void writePort(int port, int portNum, int idx) {
  // Check if port is connected via update from control module
  if(connectedRed[portNum-4]){
    pinMode(port, OUTPUT);
    digitalWrite(port, HIGH);
  }

  else{
  //Seaching for device on port
  pinMode(port, INPUT_PULLDOWN);
  attachInterrupt(digitalPinToInterrupt(port), pairingMode, CHANGE);


  // Checks to see if actuator should go into pairing mode
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
      connectedBlue[idx] = true;
      attemptCount[idx] = 0;
      Serial.println("Reading High on port");
      return;
    } 
    
    else {
      attemptCount[idx]++;    
      if(attemptCount[idx] == 5){    //Attempts to restablish module connection before reseting data
        if(connectedBlue[idx ^ 1] == false){   
          inputData[idx/2] = 0;       //Only sets inputData to 0 if both pins on connector are not occupied
        }
        attemptCount[idx] = 0;
        connectedBlue[idx] = false;
      }

    }

    if(connectedBlue[idx] == false){
      pinMode(port, OUTPUT);
      digitalWrite(port, HIGH);
      delay(50);
      digitalWrite(port, LOW);

      pinMode(port, INPUT_PULLDOWN);
      delay(70);

      if(digitalRead(port)==HIGH){
        delay(100);
        if(inputData[idx/2] == 0){
            Serial.print("Receiving on ... ");
            Serial.println(idx/2+1);
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
                connectedBlue[idx] = true;
                Serial.print("Recieved on port ");
                Serial.print(idx/2);
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
    else{
      pairMode[i] = false;
    }
  }
}

void readAngle(){
  int bendValue = analogRead(bendPin);
  angle = map(bendValue, 660, 1023, 0, 100);
  inputData[3] = angle;
}

void decodeData(int data){
  int connectorNumber = data & 0x07; // Lower 3 bits are connector number
  int actuatorID = (data >> 3) & 0x1F; // Upper 5 bits are actuator ID

    Serial.print("Received data - Actuator ID: ");
    Serial.print(actuatorID);
    Serial.print(", Connector Number: ");
    Serial.println(connectorNumber);
}