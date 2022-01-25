# Complete project details at https://RandomNerdTutorials.com
try:
  import usocket as socket
except:
  import socket
  
from time import sleep
from machine import Pin, I2C
import network
import esp
esp.osdebug(None)

import gc
gc.collect()

import BME280
import dht
import CCS811

ssid = 'VG3Data'
password = 'Admin:1234'

station = network.WLAN(network.STA_IF)
if not station.isconnected():
    station.active(True)
    station.connect(ssid, password)

    while station.isconnected() == False:
      pass

    print('Connection successful')
    print(station.ifconfig())
else:
    print('Already is connected!')
    print(station.ifconfig())
    


# Complete project details at https://RandomNerdTutorials.com

def web_page():
  DHT = dht.DHT11(Pin(13))
  i2c = I2C(scl=Pin(22), sda=Pin(21), freq=10000)
  bme = BME280.BME280(i2c=i2c)
  sensor = CCS811.CCS811(i2c=i2c, addr=90)
  if sensor.data_ready():
      DHT.measure()
      html = """
<html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta http-equiv="refresh" content="5">
        <link rel="icon" href="data:,">
        <style>
            body { text-align: center; background-color: rgb(69, 75, 79); font-family: "Trebuchet MS", Arial;}
            H1 {color: rgb(227, 245, 64)}
            table { border-collapse: collapse; width:35%; margin-left:auto; margin-right:auto; }
            th { padding: 12px; background-color: #0043af; color: white; }
            tr { border: 1px solid #ddd; padding: 12px; }
            tr:hover { background-color: #9c9a9a;}
            td { border: none; padding: 12px; color: white; background-color: #bcbcbc;}
            .sensor { color:white; font-weight: bold; background-color: #bcbcbc; padding: 1px;}
        </style>
      </head>
      <body>
          <h1>ESP with BME280</h1>
            <table>
              <tr><th>MEASUREMENT</th><th>VALUE</th></tr>
              <tr><td>Temp. Celsius(DHT11)</td><td><span class="sensor">""" + str(DHT.temperature()) + "C" +"""</span></td></tr>
              <tr><td>Temp. Celsius</td><td><span class="sensor">""" + str(bme.temperature) + """</span></td></tr>
              <tr><td>Pressure</td><td><span class="sensor">""" + str(bme.pressure) + """</span></td></tr>
              <tr><td>Humidity</td><td><span class="sensor">""" + str(DHT.humidity()) + "%" + """</span></td></tr>
              <tr><td>ECo2</td><td><span class="sensor">""" + str(sensor.eCO2) + """</span></td></tr>
              <tr><td>TVOC</td><td><span class="sensor">""" + str(sensor.tVOC) + """</span></td></tr>
            </table>
      </body>
</html>"""
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