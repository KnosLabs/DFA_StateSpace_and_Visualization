void receiveCommands(){
  if(Serial.available()) {
    while (Serial.available()) {
      int angle = 0;
      int ports[3] = {0};

      String line = Serial.readStringUntil('\n');
      line.trim();

      String parts[4];
      int idx = 0;
      int start = 0;
      for (int i = 0; i < line.length(); i++) {
        if (line.charAt(i) == ',') {
          parts[idx++] = line.substring(start, i);
          start = i + 1;
        }
      }
      parts[idx] = line.substring(start);

      double time = parts[0].toDouble();   
      int module = parts[1].toInt();   
      String action = parts[2];   
      int value = parts[3].toInt();

      if (action == "inflate") {
          angle = value;
      } else if (action == "connect") {
          ports[value - 1] = 1;
      } else if (action == "disconnect") {
          ports[value - 1] = -1;
      } else {
          Serial.println("Invalid command received");
      }
      commandBuffer[commandCount++] = {time, module, {ports[0], ports[1], ports[2]}, angle};
    }
    Serial.println("Commands have been received.");
  }
}

void runCommand(){
  unsigned long start = millis();
  for (int i = 0; i < commandCount; i++) {
    while (millis() - start < commandBuffer[i].time) {
      // wait until scheduled time
    }
    sendModuleCommand(commandBuffer[i]);
  }
}

void sendModuleCommand(Command cmd) {
    Wire.beginTransmission(cmd.module);  
    Wire.write("c");                    
    for (int i = 0; i < 3; i++) {
      Wire.write(cmd.ports[i]); // Send each data in the array
    } 
    Wire.write(cmd.angle);
    Wire.endTransmission();

    Serial.print("Sent command to module ");
    Serial.print(cmd.module);
    Serial.print(" angle=");
    Serial.println(cmd.angle);
}    
