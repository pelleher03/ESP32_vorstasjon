from machine import Pin, I2C
import time
import dht
import CCS811
from bmp280 import *

DHT = dht.DHT11(Pin(13))

def main():
    i2c = I2C(scl=Pin(22), sda=Pin(21))
    sensor = CCS811.CCS811(i2c=i2c, addr=90)
    bmp = BMP280(i2c, use_case=BMP280_CASE_WEATHER)
    time.sleep(1)
    
    while True:
        if sensor.data_ready():
            DHT.measure()
            print('eCO2: %d ppm, TVOC: %d ppb' % (sensor.eCO2, sensor.tVOC))
            print("temperatur:", DHT.temperature(), "luftfuktighet:", DHT.humidity())
            print("temp: ", bmp.temperature)
            print("pressure: ", bmp.pressure)
            print("")
            time.sleep(1)
main()