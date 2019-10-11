import json
import time
from uuid import UUID

import machine
from LIS2HH12 import LIS2HH12
from LTR329ALS01 import LTR329ALS01
from MPL3115A2 import MPL3115A2, ALTITUDE
from SI7006A20 import SI7006A20
from network import WLAN
from pysense import Pysense

# azure client
from azure_client import AzureClient
# IBM client
from ibm_cloud_client import IBMClient

# generate device UUID
uuid = UUID(b'UBIR'+ 2*machine.unique_id())
print("** UUID   : "+str(uuid)+"\n")

# load application config
with open('config.json') as c:
    config = json.load(c)

print("connecting to wifi")
wlan = WLAN(mode=WLAN.STA)
wlan.connect(config['ssid'], auth=(WLAN.WPA2, config['pass']), timeout=5000)
while not wlan.isconnected():
    machine.idle()
print("Connected to Wifi\n")

# Set time
print("Setting time")
rtc = machine.RTC()
rtc.ntp_sync("pool.ntp.org")
while not rtc.synced():
    machine.idle()
print("Time set to: {}".format(rtc.now())+"\n")

# create Azure client
azure = AzureClient()

# create IBM Cloud client (MQTT) and connect
ibm = IBMClient()

py = Pysense()
# Returns height in meters. Mode may also be set to PRESSURE, returning a value in Pascals
mp = MPL3115A2(py, mode=ALTITUDE)
si = SI7006A20(py)
lt = LTR329ALS01(py)
li = LIS2HH12(py)

while True:
    try:
        #get new data
        temperature = mp.temperature()
        humidity = si.humidity()
        light = lt.light()
        voltage = py.read_battery_voltage()

        # micropython does not support writing compact, sorted json
        fmt = """{{"deviceId":"{}","humidty":{:.3f},"light0":{},"light1":{},"temperature":{:.3f},"time":{},"voltage":{:.3f}}}"""
        message = fmt.format(azure.device_id, humidity, light[0], light[1], temperature, int(time.time()), voltage)

        # send data to IoT hub
        print("** sending measurements to Azure IoT hub ...")
        azure.send(message)

        # send data to IBM cloud
        print("** sending measurements to IBM cloud ...")
        ibm.send(message)

        print("** done\n")

    except Exception as e:
        import sys
        sys.print_exception(e)

    finally:
        time.sleep(60)
