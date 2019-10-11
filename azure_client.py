import json
from binascii import b2a_base64, a2b_base64
from hashlib import sha256
from hmac import HMAC
from time import time
from urllib.parse import urlencode, quote

import urequests as requests


def _get_device_key(r):
    """
    get the device primary key
    :param r: the http request response from IoT hub device registry
    :return: the primary symmetric authentication key of the registered device
    """
    device_info = json.loads(r.content)
    return device_info['authentication']['symmetricKey']['primaryKey']


class AzureClient:
    API_VERSION = '2016-02-03'

    def __init__(self):
        # load azure configuration
        with open("azure.json") as a:
            azure = json.load(a)
        self.device_id = azure['name']
        self.endpoint = azure['endpoint']
        self.key = azure['key']
        self.policy = azure['policy']

        # configure the URI for authentication
        self.uri = "{hostname}/devices/{device_id}".format(
            hostname=self.endpoint,
            device_id=self.device_id
        )

        # generate a SAS token from URI, shared access key and policy name
        sas_token = self._generate_sas_token(self.uri, self.key, self.policy)

        # check if device already exists in registry and register if not
        register_url = "https://{uri}?api-version={version}".format(
            uri=self.uri,
            version=self.API_VERSION
        )
        r = requests.get(register_url, headers={'Content-Type': 'application/json', 'Authorization': sas_token})
        if r.status_code == 404:  # device is not registered yet
            r.close()
            self.device_key = self._register_device(register_url, sas_token)
        elif r.status_code == 200:
            print("Device already registered: {}".format(r.text))
            self.device_key = _get_device_key(r)
        else:
            raise Exception(
                "!! GET request failed with status code {}: {}".format(r.status_code, r.text))

        # generate URL for device to cloud messaging
        self.message_url = "https://{uri}/messages/events?api-version={version}".format(
            uri=self.uri,
            version=self.API_VERSION
        )

    def _register_device(self, url, sas_token):
        """
        create new device identity in Azure IoT hub device registry
        """
        body = '{deviceId: "%s"}' % self.device_id
        r = requests.put(url, headers={'Content-Type': 'application/json', 'Authorization': sas_token}, data=body)
        if r.status_code == 200:
            print("Registered device at hub: {}".format(r.text))
            return _get_device_key(r)
        else:
            raise Exception(
                "!! Device not registered. Request failed with status code {}: {}".format(r.status_code, r.text))

    def _generate_sas_token(self, uri, key, policy_name, valid_secs=10):
        # uri = quote(uri, safe='').lower()
        encoded_uri = quote(uri, safe='')

        expiry = time() + valid_secs
        ttl = int(expiry)

        sign_key = '%s\n%d' % (encoded_uri, ttl)
        signature = b2a_base64(HMAC(a2b_base64(key), sign_key.encode('utf-8'), sha256).digest())

        token = 'SharedAccessSignature ' + urlencode({
            'sr': uri,
            'sig': signature[:-1],
            'se': str(ttl),
            'skn': policy_name
        })
        return token

    def send(self, msg: str):
        # generate a new SAS token for every message to make sure it's still valid
        sas_token = self._generate_sas_token(self.uri, self.key, self.policy)

        r = requests.post(self.message_url, headers={'Authorization': sas_token}, data=msg)
        if r.status_code == 204:
            r.close()
        else:
            raise Exception(
                "!! request to {} failed with status code {}: {}".format(self.message_url, r.status_code, r.text))
