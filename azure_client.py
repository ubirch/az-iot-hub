import json
from binascii import b2a_base64, a2b_base64
from hashlib import sha256
from hmac import HMAC
from time import time
from urllib.parse import urlencode, quote

import urequests as requests

from lib.umqtt.simple import MQTTClient


class AzureClient(MQTTClient):

    def __init__(self):
        # load azure configuration
        with open("azure.json") as a:
            azure = json.load(a)
        self.device_id = azure['name']
        endpoint = azure['endpoint']
        key = azure['key']
        policy = azure['policy']

        self.topic = "devices/{device_id}/messages/events/".format(device_id=self.device_id)

        # configure the URI for authentication (same as HTTP)
        uri = "{hostname}/devices/{device_id}".format(
            hostname=endpoint,
            device_id=self.device_id
        )
        # configure username and password from config
        username = "{hostname}/{device_id}/api-version=2018-06-30".format(
            hostname=endpoint,
            device_id=self.device_id
        )
        sas_token = self._generate_sas_token(uri, key, policy)

        # check if device already exists in registry
        url = 'https://{}?api-version=2018-06-30'.format(uri)
        r = requests.get(url, headers={'Content-Type': 'application/json', 'Authorization': sas_token})
        if r.status_code == 404:  # device is not registered yet
            self._register_device(url, sas_token)  # create new device in Azure IoT hub device registry
        elif r.status_code == 200:
            print("Device registry: {}".format(r.content))
        else:
            raise Exception(
                "!! GET request failed with status code {}: {}".format(r.status_code, r.text))

        # initialize underlying  MQTT client
        super().__init__(self.device_id, endpoint, user=username, password=sas_token, ssl=True, port=8883)

    def _register_device(self, url, sas_token):
        body = '{deviceId: "%s"}' % self.device_id
        r = requests.put(url, headers={'Content-Type': 'application/json', 'Authorization': sas_token}, data=body)
        if r.status_code == 200:
            print("created new identity in IoT hub device registry")
            device_info = json.loads(r.content)
            primary_key = device_info['authentication']['symmetricKey']['primaryKey']
            print("Device primary key: {}".format(primary_key))
        else:
            raise Exception(
                "!! PUT request failed with status code {}: {}".format(r.status_code, r.text))

    def _generate_sas_token(self, uri, key, policy_name="iothubowner", expiry=None):
        # uri = quote(uri, safe='').lower()
        encoded_uri = quote(uri, safe='')

        if expiry is None:
            expiry = time() + 3600
        ttl = int(expiry)

        sign_key = '%s\n%d' % (encoded_uri, ttl)
        signature = b2a_base64(HMAC(a2b_base64(key), sign_key.encode('utf-8'), sha256).digest())

        result = 'SharedAccessSignature ' + urlencode({
            'sr': uri,
            'sig': signature[:-1],
            'se': str(ttl),
            'skn': policy_name
        })

        return result

    def send(self, msg):
        super().publish(self.topic, msg, qos=1)
