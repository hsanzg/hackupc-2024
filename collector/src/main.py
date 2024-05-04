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

USE_FAKE_DATA = os.getenv('USE_FAKE_DATA') == 'yes'
url = os.getenv('INFLUX_URL')
token = os.getenv('INFLUX_TOKEN')
org = os.getenv('INFLUX_ORG')
bucket = os.getenv('INFLUX_BUCKET')

def get_write_api():
    client = InfluxDBClient(url=url, token=token, org=org)
    write_api = client.write_api()
    return write_api

def upload(write_api, point):
  write_api.write(bucket=bucket, org=org, record=point)

if __name__ == '__main__':
  print('starting up')
  if True:
    random.seed(2024)
  else:
    port = get_esp_port()
  write_api = get_write_api()

  while True:
    if True:
      temp = random.uniform(22, 24)
      humidity = random.uniform(40, 50)
    else:
      measurement_bytes = port.read(8)
      temp, humidity = struct.unpack('f', measurement_bytes)# little endian
    if math.isnan(temp):
      assert(math.isnan(humidity))
      print('failed checksum')
    else:
      print(f'uploading temperature: {temp}ºC and hum {humidity}')
      p = Point('workplace')\
            .field('temperature', temp)\
            .field('humidity', humidity)
      upload(write_api, p)
