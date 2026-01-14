
void writePort(int port, int id) {
  //Buffer to allow control module to collect data from modules
  count++;
  if (count != 5){
    return;
  }
  count = 0;

  //Keep high signal constant if control module was detected by a module
  if (controlPresent == true){
    pinMode(port, OUTPUT);
    digitalWrite(port, HIGH);

  } else {
  //Seaching for device on port
  pinMode(port, INPUT_PULLDOWN);
  attachInterrupt(digitalPinToInterrupt(port), pairingMode, CHANGE);

// Check to see if actuator should go into pairing mode
  if(pairMode == true){
    detachInterrupt(digitalPinToInterrupt(port));

    int startTime = millis();

    //Serial.println("Entering Paring Mode");
    while(digitalRead(port) == LOW){
      if(millis() - startTime > 4000){
        pairMode = false;
        return;
      }
    }

  //Handshake
  pinMode(port, OUTPUT);
  delay(75);
  digitalWrite(port, HIGH);
  delay(75);
  digitalWrite(port, LOW);
  delay(50);
  //Serial.print("Sending Data");
  //Send data bitwise
  for (int i = 0; i < 8; i++) {
    digitalWrite(port, (id & (1 << i)) ? HIGH : LOW);
    delay(75); 
  }
    digitalWrite(port, HIGH); //Write high until proven not connected
    pairMode = false;
  }
  }
}

void pairingMode() {
    if(digitalRead(port) == HIGH){
      pairMode = true;
  }
}