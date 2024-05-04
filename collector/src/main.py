#!/usr/bin/python3
import os
import random
import struct
import math
import time
import numpy as np
from numpy import random as rnd

url = os.getenv('INFLUX_URL')
token = os.getenv('INFLUX_TOKEN')
org = os.getenv('INFLUX_ORG')
bucket = os.getenv('INFLUX_BUCKET')
USE_FAKE_DATA = os.getenv('USE_FAKE_DATA') == 'yes'
SHOULD_UPLOAD = url is not None

if not USE_FAKE_DATA:
  import serial

if SHOULD_UPLOAD:
  from influxdb_client import InfluxDBClient, Point
  from influxdb_client.client.write_api import SYNCHRONOUS

def get_write_api():
    client = InfluxDBClient(url=url, token=token, org=org)
    write_api = client.write_api()
    return write_api

def upload(write_api, point):
  write_api.write(bucket=bucket, org=org, record=point)

def get_esp_port():
  return serial.Serial('/dev/ttyUSB0', baudrate=9600)

# Synthetic data parameters
SD_DIFF_FACTOR = 1e-2
BIAS_FACTOR = 1e-4

co2_mean = 700 # ppm
co2_std_dev = 100
co2 = rnd.normal(co2_mean, co2_std_dev)

sound_mean = 45 # dB
sound_std_dev = 4
sound_peak_p = 1 / (30 * 60)
sound = rnd.normal(sound_mean, sound_std_dev)

people_mean = 20
people_std_dev = 5
people_theta = 0
people_theta_delta = (2 * np.pi) / 3600 # have a period of one hour
people_second_scale = 2 * people_std_dev
people = rnd.normal(people_mean, people_std_dev)

def gen_next(mean, std_dev, prev):
  # bias the diff depending on how far we are from the mean.
  norm_diff_mean = BIAS_FACTOR * (prev - mean) / std_dev
  diff = rnd.normal(-norm_diff_mean, std_dev * SD_DIFF_FACTOR)
  return prev + diff

if __name__ == '__main__':
  print('starting up')
  if USE_FAKE_DATA:
    print('using synthetic temp and humidity data')
  else:
    port = get_esp_port()
  if SHOULD_UPLOAD:
    print('uploading to db')
    write_api = get_write_api()

  while True:
    if USE_FAKE_DATA:
      temp = rnd.normal(23, 1)
      humidity = rnd.normal(45, 3)
      time.sleep(1)
    else:
      measurement_bytes = port.read(12) # waits to receive from ESP32.
      temp, humidity, _sound = struct.unpack('fff', measurement_bytes) # little endian

    # Update synthetic data.
    co2 = gen_next(co2_mean, co2_std_dev, co2)
    sound = gen_next(sound_mean, sound_std_dev, sound)
    if rnd.binomial(1, sound_peak_p):
      sound += rnd.normal(2 * sound_std_dev, sound_std_dev / 2)
    people = max(gen_next(people_mean, people_std_dev, people), 0)
    # Add extra noise scale to people.
    people += people_second_scale * np.sin(people_theta)
    people_theta += people_theta_delta

    if math.isnan(temp) or not (-20 < temp < 50) or not (0 < humidity < 100):
      print(f'failed checksum or invalid data (temp={temp}, hum={humidity}, sound={sound}); skipping')
    else:
      print(f'uploading temp={temp}ºC, hum={humidity}%, sound={sound}db, co2={co2}ppm, people={people}')
      if SHOULD_UPLOAD:
        p = Point('workplace')\
              .field('temperature', temp)\
              .field('humidity', humidity)\
              .field('co2', co2)\
              .field('sound', sound)\
              .field('people', np.round(people))
        upload(write_api, p)
