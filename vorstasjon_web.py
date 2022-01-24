try:
  import usocket as socket
except:
  import socket

from machine import Pin, I2C
import time
import network
import esp
import dht
import CCS811
from bmp280 import *
esp.osdebug(None)
import gc
gc.collect()

i2c = I2C(scl=Pin(22), sda=Pin(21), freq=10000)
ssid = 'VG3Data'
password = 'Admin:1234'

station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
  pass

print('Connection successful')
print(station.ifconfig())

def web_page():
  DHT = dht.DHT11(Pin(13))
  i2c = I2C(scl=Pin(22), sda=Pin(21))
  sensor = CCS811.CCS811(i2c=i2c, addr=90)
  bmp = BMP280(i2c, use_case=BMP280_CASE_WEATHER)
  time.sleep(1)
  
  html = """<html><head><meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="data:,"><style>body { text-align: center; font-family: "Trebuchet MS", Arial;}
  table { border-collapse: collapse; width:35%; margin-left:auto; margin-right:auto; }
  th { padding: 12px; background-color: #0043af; color: white; }
  tr { border: 1px solid #ddd; padding: 12px; }
  tr:hover { background-color: #bcbcbc; }
  td { border: none; padding: 12px; }
  .sensor { color:white; font-weight: bold; background-color: #bcbcbc; padding: 1px;
  </style></head><body><h1>ESP with BME280</h1>
  <table><tr><th>MEASUREMENT</th><th>VALUE</th></tr>
  <tr><td>Temp DH11. Celsius</td><td><span class="sensor">""" + str(DHT.temperature()) + """</span></td></tr>
  <tr><td>Humidity</td><td><span class="sensor">""" + str(DHT.humidity()) + """</span></td></tr>
  <tr><td>Temp. Celsius</td><td><span class="sensor">""" + str(bmp.temperature) + """</span></td></tr>
  <tr><td>Temp. Fahrenheit</td><td><span class="sensor">""" + str(round((bmp.read_temperature()/100.0) * (9/5) + 32, 2))  + """F</span></td></tr>
  <tr><td>Pressure</td><td><span class="sensor">""" + str(bmp.pressure) + """</span></td></tr>
  <tr><td>eCO2</td><td><span class="sensor">""" + str(sensor.eCO2) + """</span></td></tr>
  <tr><td>tVOC</td><td><span class="sensor">""" + str(sensor.tVOC) + """</span></td></tr>
</body></html>"""
  return html

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

while True:
  try:
    if gc.mem_free() < 102000:
      gc.collect()
    conn, addr = s.accept()
    conn.settimeout(3.0)
    print('Got a connection from %s' % str(addr))
    request = conn.recv(1024)
    conn.settimeout(None)
    request = str(request)
    print('Content = %s' % request)
    response = web_page()
    conn.send('HTTP/1.1 200 OK\n')
    conn.send('Content-Type: text/html\n')
    conn.send('Connection: close\n\n')
    conn.sendall(response)
    conn.close()
  except OSError as e:
    conn.close()
    print('Connection closed')