void requestEvent() {
  Wire.write(MODULE_ID); // Send the actuator ID first
  for (int i = 0; i < 4; i++) {
    Wire.write(inputData[i]); // Send each data in the array
  }
  Serial.println("Data sent to command module.");
}

void receiveEvent(int numByte){
  char cmd = Wire.read();
  if (cmd == 'u') {
    for (int i = 3; i < 6 && Wire.available(); i++) {
      connectedRed[i] = (Wire.read() == 1);
    }
  }

  if (cmd == 'c') {
    controlMode = true;
    bool connection = false;
    for (int i = 0; i < 4 && Wire.available(); i++){
      command = Wire.read();
      if (command == 1 && i != 3){
        connect(i);
        break;
      }
      else if (command == -1 && i != 3){
        disconnect(i);
        break;
      }
      else if (i == 3){
        actuate(command);
        break;
      }
      else {
        continue;
      }
    }
  }

  if (cmd == 'q'){
    controlMode = false;
  }
}