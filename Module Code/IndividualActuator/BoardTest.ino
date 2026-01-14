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