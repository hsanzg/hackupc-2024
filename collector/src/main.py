#!/usr/bin/python3
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import os
import serial
import random
import struct
import math

def get_esp_port():
  return serial.Serial('/dev/ttyUSB0', baudrate=9600, timeout=3.0)

INFLUX_SERIES = os.getenv('INFLUX_SERIES')
INFLUX_BUCKET = os.getenv('INFLUX_BUCKET')
INFLUX_ORG = os.getenv('INFLUX_ORG')
USE_FAKE_DATA = os.getenv('USE_FAKE_DATA') == 'yes'
SHOULD_UPLOAD = INFLUX_SERIES is not None

def get_write_api():
  url = os.getenv('INFLUX_URL')
  token = os.getenv('INFLUX_TOKEN')
  print(f'connecting to {url} at org={INFLUX_ORG} ')
  client = InfluxDBClient(url=url, token=token, org=INFLUX_ORG)
  return client.write_api(write_options=SYNCHRONOUS)

def upload(write_api, point):
  write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)

if __name__ == '__main__':
  print('starting up')
  if USE_FAKE_DATA:
    print('uploading random data')
    random.seed(2024)
  else:
    port = get_esp_port()
  if SHOULD_UPLOAD:
    write_api = get_write_api()

  # Continuously read measurements from ESP32 board.
  while True:
    if USE_FAKE_DATA:
      temp = random.uniform(22, 24)
      humidity = random.uniform(40, 50)
      sound = random.uniform(0, 255)
    else:
      measurement_bytes = port.read(12)
      temp, humidity, sound = struct.unpack('fff', measurement_bytes)# little endian
    if math.isnan(temp):
      assert(math.isnan(humidity))
      print('failed checksum')
    else:
      print(f'uploading temperature: {temp}ºC, hum {humidity}%, sound {sound}')
      if SHOULD_UPLOAD:
        p = Point('workplace')\
              .field('temperature', temp)\
              .field('humidity', humidity)\
              .field('sound', sound)
        upload(write_api, p)
