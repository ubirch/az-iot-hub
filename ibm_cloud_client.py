import json

from lib.umqtt.simple import MQTTClient


class IBMClient(MQTTClient):

    def __init__(self):

        # load ibm configuration
        with open("ibm_cloud.json") as a:
            ibm_cloud = json.load(a)
        orga_ID = ibm_cloud['orgaID']
        device_type = ibm_cloud['deviceType']
        self.device_id = ibm_cloud['deviceID']
        auth_method = "use-token-auth"
        auth_token = ibm_cloud['authToken']

        client_id = "d:{org}:{type}:{device}".format(org=orga_ID, type=device_type, device=self.device_id)
        url = "{org}.messaging.internetofthings.ibmcloud.com".format(org=orga_ID)

        # initialize underlying  MQTT client
        super().__init__(client_id, url, user=auth_method, password=auth_token, port=1883)

    def send(self, msg, event_name="default"):
        topic = "iot-2/evt/{evt}/fmt/json".format(evt=event_name)

        super().publish(topic, msg, qos=1)