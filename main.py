from network import WLAN
from umqtt.simple import MQTTClient
import json
import machine

from azure import generate_sas_token

# load azure configuration
with open("azure.json") as a:
     azure = json.load(a)
endpoint = azure['endpoint']
device_id = azure['name']
key = azure['key']
policy = azure['policy']

# load application config (wifi)
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
print("Time set to: {}".format(rtc.now()))



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
client = MQTTClient(device_id, endpoint, user=username, password=password, ssl=True, port=8883)

client.connect()
topic = "devices/{device_id}/messages/events/".format(device_id=device_id)
client.publish(topic, "test", qos=1)