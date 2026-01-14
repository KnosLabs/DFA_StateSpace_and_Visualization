void sendMatrix(){
  // Send the matrix to the serial port
  for (int i = 0; i < MAX_ACTUATORS; i++) {
    for (int j = 0; j < NUM_INPUT_PORTS; j++) {
      Serial.print(configurationMatrix[i][j]);
      if (j < NUM_INPUT_PORTS-1) {
        Serial.print(",");  // Separate elements by commas
      }
    }
    Serial.println();  // Newline at the end of each row
  }
  
  delay(100);  
}


void printConfigurationMatrix() {
  Serial.println("Configuration Matrix:");
  for (int i = 0; i < MAX_ACTUATORS; i++) {
    Serial.print("Actuator ");
    Serial.print(i + 1);
    Serial.print(": ");
    for (int j = 0; j < NUM_INPUT_PORTS; j++) {
      Serial.print(configurationMatrix[i][j]);
      Serial.print(" ");
    }
    Serial.println();
  }
}


void zeroMatrix() {
   // Set all values to zero using nested loops
  for (int i = 0; i < MAX_ACTUATORS; i++) {
    for (int j = 0; j < NUM_INPUT_PORTS; j++) {
      configurationMatrix[i][j] = 0;
    }
  }
}

