
#include <IRremote.hpp>



const uint16_t kIrLed = 25;




String incomingString = "";



void setup() {
  Serial.begin(115200);
  //Serial.setTimeout(0.5);
  IrSender.begin(kIrLed);
  IrSender.enableIROut(38);

}

void loop() {

  if (Serial.available()) {
    incomingString = Serial.readStringUntil('[');  // Read until '['
    incomingString = Serial.readStringUntil(']');  // Read until ']'

    int newLength = incomingString.toInt();
    uint16_t newRawData[newLength] = {};
    String newVals = Serial.readStringUntil(',');
    for (int i = 0; i < newVals.length(); i++) {
      int intVal = newVals.substring(i, i + 1).toInt() * 700;
      newRawData[i] = intVal;
    }
    IrSender.sendRaw(newRawData, newLength, 38);  // Send a raw data capture at 38kHz.
    Serial.println("IR signal sent to pin 25");  // Print a message indicating IR signal sent
    delay(3);


  }




}

