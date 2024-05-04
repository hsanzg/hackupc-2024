void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600); // open the serial port at 9600 bps:
}

void loop() {

  float temp = 3.14;
  byte * ptr = (byte *) &temp;

  Serial.write(ptr, sizeof(float));
  delay(2000);
}
