// Arduino and KY-015 module

#define DHT11_OUTPUT 14
#define NAN (0.0 / 0.0)

byte measurements[5];  // array to store temp. and humidity values

byte get_value()
{
  byte i = 0;
  byte value = 0;
  for (i = 0; i < 8; i++) {
    while (digitalRead(DHT11_OUTPUT) == LOW); // wait for pin state to be HIGH
    delayMicroseconds(30);          // wait 30 microSeconds
    if (digitalRead(DHT11_OUTPUT) == HIGH)
      value |= (1 << (8 - i));      // save bit value if pin 10 is HIGH
    while (digitalRead(DHT11_OUTPUT) == HIGH); // wait for pin state to be LOW
  }
  return value;
}
// function to get temperature and humidity values from dht11

void dht()
{
  digitalWrite(DHT11_OUTPUT, LOW);  // set pin LOW to start communication with module
  delay(30);              // wait 30 milliSeconds
  digitalWrite(DHT11_OUTPUT, HIGH); // set pin HIGH
  delayMicroseconds(40);  // wait 40 microSeconds
  pinMode(DHT11_OUTPUT, INPUT);     // change pin 10 mode to input
  while (digitalRead(DHT11_OUTPUT) == HIGH);    // wait for pin to be LOW
  delayMicroseconds(80);  // wait for 80 microSeconds
  if (digitalRead(DHT11_OUTPUT) == LOW)
    delayMicroseconds(80); // wait for 80 microSeconds
  for (int i = 0; i < 5; i++) // receive temperature and humidity values
    measurements[i] = get_value();
  pinMode(DHT11_OUTPUT, OUTPUT);    // change pin 10 mode to ouptut
  digitalWrite(DHT11_OUTPUT, HIGH); // set pin 10 to HIGH
}

float dec_to_float(byte *measurement) { // two bytes
  return ((float) measurement[0]) + (((float) measurement[1]) / 10.);
}

void setup() {
  Serial.begin(9600);
  pinMode(DHT11_OUTPUT, OUTPUT);
}

void loop() {
  // get data from module
  dht();

  /*Serial.print("Humdity = ");
  Serial.print(temp_humidity[0], DEC);
  Serial.print(".");
  Serial.print(temp_humidity[1], DEC);
  Serial.println("%");
  Serial.print("Temperature = ");
  Serial.print(temp_humidity[2], DEC);
  Serial.print(".");
  Serial.print(temp_humidity[3], DEC);
  Serial.print(" degC");*/

  byte checksum = measurements[0] + measurements[1] + measurements[2] + measurements[3];
  float values[2] = {NAN, NAN}; // Assume measurement is invalid by default.
  if (checksum == measurements[4]) {
    // Data is valid! Convert it to floating point values.
    float *temp = &values[0], *humidity = &values[1];
    *temp = dec_to_float(&measurements[2]);
    *humidity = dec_to_float(&measurements[0]);
  }
  Serial.write(values, sizeof(values));
  delay(1000);
}
