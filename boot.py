try:
  import usocket as socket
except:
  import socket
import time
from machine import Pin, I2c
import network
import esp
esp.osdebug(None)
import gc
gc.collect()

i2c = I2C(scl=Pin(22), sda=Pin(21), freq=10000)
ssid = 'VG3Data'
password = 'Admin:1234'

station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
  pass

print('Connection successful')
print(station.ifconfig())
