from network import WLAN
from umqtt.simple import MQTTClient
import os
import time
import machine
import json
from uuid import UUID
import binascii

import pycom
from pysense import Pysense
from LIS2HH12 import LIS2HH12
from SI7006A20 import SI7006A20
from LTR329ALS01 import LTR329ALS01
from MPL3115A2 import MPL3115A2, ALTITUDE, PRESSURE

# ubirch client
from ubirch import UbirchClient

# Cumulocity API
from c8y.http_client import C8yHTTPClient as C8yClient

from azure import generate_sas_token

# generate device UUID
uuid = UUID(b'UBIR'+ 2*machine.unique_id())
print("** UUID   : "+str(uuid)+"\n")

# load azure configuration
with open("azure.json") as a:
    azure = json.load(a)
endpoint = azure['endpoint']
device_id = azure['name']
key = azure['key']
policy = azure['policy']

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


# configure the URI for authentication (same as HTTP)
uri = "{hostname}/devices/{device_id}".format(
    hostname=endpoint,
    device_id=device_id
)
# configure username and password from config
username = "{hostname}/{device_id}/api-version=2018-06-30".format(
    hostname=endpoint,
    device_id=device_id
)
password = generate_sas_token(uri, key, policy)

# create MQTT client
client = MQTTClient(device_id, endpoint, user=username,
                    password=password, ssl=True, port=8883)

client.connect()
topic = "devices/{device_id}/messages/events/".format(device_id=device_id)

# create Cumulocity client (bootstraps)
uname = os.uname()
c8y = C8yClient(uuid, dict(config['bootstrap']), {
    "name": str(uuid),
    "c8y_IsDevice": {},
    "c8y_Hardware": {
        "model": uname.machine + "-" + config['type'],
        "revision": uname.release + "-" + uname.version,
        "serialNumber": str(uuid)
    }
})

ubirch = UbirchClient(uuid, c8y.get_auth()) #, "demo")

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
        fmt = """{{"deviceId":"{}","humidty":{:.3f},"light":[{},{}],"temperature":{:.3f},"time":{},"voltage":{:.3f}}}"""
        message = fmt.format(device_id, humidity, light[0], light[1], temperature, int(time.time()), voltage)

        # send data to IoT Hub
        print("** sending measurements ...")
        client.publish(topic, message, qos=1)

        # send data certificate (UPP) to UBIRCH
        print("** sending measurement certificate ...")
        ubirch.send(message)

        print("** done\n")

    except Exception as e:
        import sys
        sys.print_exception(e)

    finally:
        time.sleep(30)
