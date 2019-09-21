import json
import lib.urequests as requests
from uuid import UUID
import time

class UbirchVisualisation:

    def __init__(self, uuid: UUID, auth: str):
        self.uuid = uuid
        self.__url = 'https://data.dev.ubirch.com/v1/'
        self.__pw = auth
        self.__headers = {'X-Ubirch-Hardware-Id': self.uuid, 'X-Ubirch-Credential': self.__pw}

    def send(self, data_point):
        data = {'date': int(time.time()), 'data': data_point}

        r = requests.post(self.__url, headers=self.__headers, json=data)

        if r.status_code == 200:
            print("Response from {}: {}".format(self.__url, r.content))
        else:
            print("!! request to {} failed with {}: {}".format(self.__url, r.status_code, r.text))
