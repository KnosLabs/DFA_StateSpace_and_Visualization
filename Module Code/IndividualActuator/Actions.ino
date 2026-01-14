

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

void actuate(int inputAngle, int duration = 4*1000){
  unsigned long start = millis();
  unsigned long timeout = 10000; // 10 seconds
  int allowedError = 10;

  readAngle();
  if (inputAngle == 1) {
    setPins(airIn);
    digitalWrite(z, HIGH);
    delay(duration);
    digitalWrite(z, LOW);
  } 
  else if (inputAngle == 0){
    setPins(airOut);
    digitalWrite(z, HIGH);
    delay(duration);
    digitalWrite(z, LOW);
  } 
  else if (inputAngle > 0){
    setPins(airIn);
    digitalWrite(z, HIGH);
    
    while(true){
      readAngle();
      if (abs(inputAngle - angle) < allowedError){
        break;
      }
      delay(200);

      if (millis() - start >= timeout) {
        digitalWrite(z, LOW);
        break; // exit after timeout
      }
    }
  }
}