#!/usr/bin/python3
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import os
import serial
import struct
import math

def get_esp_port():
  return serial.Serial('/dev/ttyUSB0', baudrate=9600, timeout=3.0)

INFLUX_SERIES = os.environ['INFLUX_SERIES']
INFLUX_BUCKET = os.environ['INFLUX_BUCKET']
INFLUX_ORG = os.environ['INFLUX_ORG']

def get_write_api():
  url = os.environ['INFLUX_URL']
  token = os.environ['INFLUX_TOKEN']
  print(f'connecting to {url} at org={INFLUX_ORG} ')
  client = InfluxDBClient(url=url, token=token, org=INFLUX_ORG)
  return client.write_api(write_options=SYNCHRONOUS)

def upload(write_api, point):
  write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)

if __name__ == '__main__':
  print('starting up')
  port = get_esp_port()
  write_api = get_write_api()

  # Continuously read measurements from ESP32 board.
  while True:
    temp_bytes = port.read(4)
    temp = struct.unpack('f', temp_bytes)# little endian
    if math.isnan(temp):
      print('failed checksum')
    else:
      print(f'uploading temperature: {temp}ºC')
      p = Point('workplace')\
            .field("temperature", temp)\
      upload(write_api, p)
