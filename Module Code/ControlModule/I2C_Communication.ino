void requestData(int actuatorID) {
  Wire.requestFrom(actuatorID, NUM_INPUT_PORTS); 

  if (Wire.available()) {
    int receivedActuatorID = Wire.read(); 
    if (receivedActuatorID != actuatorID) {
      Serial.print("Warning: Expected actuator ID ");
      Serial.print(actuatorID);
      Serial.print(" but received ");
      Serial.println(receivedActuatorID);
      return;
    }

    for (int i = 0; i < NUM_INPUT_PORTS; i++) {
      if (Wire.available()) {
        int data = Wire.read();
        configurationMatrix[receivedActuatorID - 1][i] = data; 
        present = true;
      }
    }
  } else {
      for (int i = 0; i < NUM_INPUT_PORTS; i++) {
        configurationMatrix[actuatorID - 1][i] = 0;
    }
  }
}

void updateConfigArrays(){
   int configMatrix[MAX_ACTUATORS][3] = {0};
   controlPresent = false;

   for (int i = 0; i < MAX_ACTUATORS; i++) {
    for (int j = 0; j < 3; j++) {
      int value = configurationMatrix[i][j];
      if (value == 0){
        continue;
      }

       if (abs(value) == 1){
        controlPresent = true;
        continue;
      } 

      int portID = value & 0x07; // Lower 3 bits are connector number
      int actuatorID = (value >> 3) & 0x1F;

      if (portID < 4 || portID > 6 || actuatorID < 1 || actuatorID > MAX_ACTUATORS) {
        Serial.print("Error: Invalid portID ");
        Serial.print(portID);
        Serial.print(" or actuatorID ");
        Serial.print(actuatorID);
        continue; 
      }

      configMatrix[actuatorID-1][portID - 4] = 1;
    }
   }
       
    for (int ID = 1; ID <= MAX_ACTUATORS; ID++){
        Wire.beginTransmission(ID);
        Wire.write('u'); // 'u' indicated configuration Update matrix 
        for(int port_idx = 0; port_idx < 3; port_idx++){
          int connectedState = configMatrix[ID - 1][port_idx];
          Wire.write(connectedState);
        }
        byte result = Wire.endTransmission();
        if (result != 0) {
          continue; // Skip to next actuator
        }

        Serial.print("Updating Matrix");
    }
  
}