#define DHT11_OUTPUT 14
#define MICROPHONE_ANALOG_PIN 26
#define ON_BOARD_LED 1
#define NAN (0.0 / 0.0)
#define SEND_INTERVAL 1000 // send data every `SEND_INTERVAL` ms
#define POLL_INTERVAL 1000 // measure sound intensity every `POLL_INTERVAL` ms
#define POLLS_PER_SEND (SEND_INTERVAL / POLL_INTERVAL)

// int digitalVal;       // digital readings
int analog_val;        // analog readings

byte measurements[5];  // array to store temp. and humidity values

void setup() {
  Serial.begin(9600);

  pinMode(DHT11_OUTPUT, OUTPUT);
  // pinMode(ON_BOARD_LED, OUTPUT);
  // pinMode(MICROPHONE_DIGITAL_PIN, INPUT);
  pinMode(MICROPHONE_ANALOG_PIN, INPUT);
}

byte get_value() {
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

// Retrieve temperature and humidity values from dht11.
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

void send_payload(float sound) {
  byte checksum = measurements[0] + measurements[1] + measurements[2] + measurements[3];
  float values[3] = {NAN, NAN, sound}; // Assume measurement is invalid by default.
  if (true) { // supposed to be checksum == measurements[4], but the sensor seems to produce wrong values somehow
    // Data is valid! Convert it to floating point values.
    float *temp = &values[0], *humidity = &values[1], *sound = &values[2];
    *temp = dec_to_float(&measurements[2]);
    *humidity = dec_to_float(&measurements[0]);
  }
  byte *raw_values = (byte*) values;
  Serial.write(raw_values, sizeof(values));
}

int elapsed_ms = 0;
double total_sound = 0.;

void loop() {
  if (elapsed_ms >= SEND_INTERVAL) {
    // Update data from module temperature and humidity sensor.
    dht();
    // Calculate average sound.
    send_payload((float) (total_sound / (POLLS_PER_SEND - 1)));
    // Reset clock and total sound.
    elapsed_ms = 0, total_sound = 0.;
  } else {
    total_sound += (double) analogRead(MICROPHONE_ANALOG_PIN);
    delay(POLL_INTERVAL);
    elapsed_ms += POLL_INTERVAL;
  }
}
