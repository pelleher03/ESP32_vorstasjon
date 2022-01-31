# Complete project details at https://RandomNerdTutorials.com
try:
  import usocket as socket
except:
  import socket

#Importerer de bibliotekene jeg skal bruke
from time import sleep
from machine import Pin, I2C
import network
import esp
esp.osdebug(None)
import gc
gc.collect()
#Importerer Sensor bibliotekene 
import BME280
import dht
import CCS811

#Sier hvilket nettverk som nettsiden skal settes opp på, og hva passordet til nettverket er
ssid = 'VG3Data'
password = 'Admin:1234'

#Setter opp internett forbindelse
station = network.WLAN(network.STA_IF)
#Om forbindelsen ikke er aktiv skal ESP'en koble seg til på nytt
#Om forbindelsen allerede er aktiv får man beskjed om at forbindelsen allerede er aktiv 
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
    
#Funksjon over hva data og hva som skal vises på nettsiden 
def web_page():
  #Kondigurerer DHT11 sensoren ved å si hvilken pinne den skal bruke
  DHT = dht.DHT11(Pin(13))
  #Lager et I2C objekt ved å sette klokke pinnen og datapinnen 
  i2c = I2C(scl=Pin(22), sda=Pin(21), freq=10000)
  #Konfugurerer BMP280 sensoren med i2c og hvilken modus den skal være i
  bme = BME280.BME280(i2c=i2c)
  #Konfugurerer CCS811 sensoren med I2C og hvilken address den bruker
  ccs_sensor = CCS811.CCS811(i2c=i2c, addr=90)
  #Når ccs811 sensoren er klar vil DHT.sensoren ta en måling
  if ccs_sensor.data_ready():
      DHT.measure()
      #Alt som skal vises på nettsiden må legges inn i HTML variabelen
      #Jeg la til at siden oppdateres hvert 5 sekund, i tilegg byttet jeg ut litt farger for å leke litt med CSS
      #Veridene som er lagt til i HTML dokumentet er Tempratu(DHT og BMP), trykk(BMP), Luftfuktighet(DHT11), eco2 og tvoc(CCS811)
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
              <tr><td>ECo2</td><td><span class="sensor">""" + str(ccs_sensor.eCO2) + """</span></td></tr>
              <tr><td>TVOC</td><td><span class="sensor">""" + str(ccs_sensor.tVOC) + """</span></td></tr>
            </table>
      </body>
</html>"""
      #Returnerer html variabelen når funksjonen er ferdig kjørt 
      return html
    
#Setter opp hvordan og hvilken port som ESP'en skal bruke til å sette opp nettsiden
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

#Alt som ligger inne i while loopen vil kjøre om og om igjen til programmet avbrytes 
while True:
  #Om det er lite minne igjen skal gc(garbage collect slette uviktig data for å frigi minne)
  try:
    if gc.mem_free() < 102000:
      gc.collect()
      
    conn, addr = s.accept()
    conn.settimeout(3.0)
    #Printer ut fra hvilken IP ESP'en får tilkobling fra
    print('Got a connection from %s' % str(addr))
    request = conn.recv(1024)
    conn.settimeout(None)
    request = str(request)
    print('Content = %s' % request)
    #Setter at response skal være lik funksjonen web_page for data og HTMl koden ligger
    response = web_page()
    #Sender dataen ut på nettsiden
    conn.send('HTTP/1.1 200 OK\n')
    conn.send('Content-Type: text/html\n')
    conn.send('Connection: close\n\n')
    conn.sendall(response)
    conn.close()
  #Om det skjern noe feil skal tilkoblingen lokkes
  except OSError as e:
    conn.close()
    print('Connection closed')