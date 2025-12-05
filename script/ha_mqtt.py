import paho.mqtt.client as mqtt
from secrets import *

class mqttPublisher:
    def __init__(self):
        self.host = MQTT_IP
        self.port = 1883
        self.user = MQTT_USER
        self.pwd = MQTT_PWD

        self.client = mqtt.Client(callback_api_version=2)
        self.client.username_pw_set(self.user, self.pwd)

    def connect(self):
        self.client.connect(self.host, self.port, keepalive=60)
        self.client.loop(timeout=0.2)

    def publish_obis(self, name, value):
        topic = f'home/energy/{name}'
        payload = str(value)
        self.client.publish(topic, payload)
        self.client.loop(timeout=0.1)
    
    def disconnect(self):
        self.client.disconnect()

if __name__ == "__main__":
    
    client = mqttPublisher()
    client.connect()
    client.publish_obis("tariff", "T0")
    client.disconnect()
