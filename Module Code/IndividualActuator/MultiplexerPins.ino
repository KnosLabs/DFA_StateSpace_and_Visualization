void setPins(int input[4]){
  for(int i=0; i<4; i++){
    digitalWrite(selectPins[i], input[i] == 1 ? HIGH : LOW);
  }
}

void resetPins(){
  for(int i=0; i<4; i++){
    digitalWrite(selectPins[i], LOW);
  }
}