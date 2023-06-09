
import json
import threading
import time
import datetime
import requests
from pathlib import Path
from paho.mqtt.client import Client as MqttClient


P = Path(__file__).parent.absolute()

FILE = P / "conf.json"

loop_flag = 1
time_flag = 1

class Timer(threading.Thread):
    """15-second timer.
    It is used to prevent publishing on ThingSpeak too often.
    """

    def __init__(self):
        """Initialize the timer thread."""
        threading.Thread.__init__(self)

    def run(self):
        """Run the timer thread."""
        global time_flag
        while True:
            time_flag = 1  # Start timer.
            time.sleep(15)  # Wait 15 seconds.
            time_flag = 0  # Stop timer.
            time.sleep(1)  # 1-sec cooldown.


class MySubscriber():
    """MQTT subscriber."""

    def __init__(self, clientID, topic, broker_ip):
        """Initialize the MQTT subscriber."""
        self.clientID = clientID
        self.topic = topic
        self.messageBroker = broker_ip
        self._paho_mqtt = MqttClient(self.clientID, False)
        self._paho_mqtt.on_connect = self.my_on_connect
        self._paho_mqtt.on_message = self.my_on_message_received

    def start(self):
        """Start the MQTT subscriber."""
        self._paho_mqtt.connect(self.messageBroker, 1883)
        self._paho_mqtt.loop_start()
        self._paho_mqtt.subscribe(self.topic, 2)
        print("Subscribed to the topic: " + self.topic)
    
    def stop(self):
        """Stop the MQTT subscriber."""
        self._paho_mqtt.unsubscribe(self.topic)
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()

    def my_on_connect(self, client, userdata, flags, rc):
        """Handle MQTT connection event."""
        pass

    def my_on_message_received(self, client, userdata, msg):
        """Handle received MQTT message."""
        (url, port, topic, ts_url) = read_file(FILE)
        print(topic)
        message = json.loads(msg.payload.decode("utf-8"))
        print(message)
        Patient_topic = message['bn']
        print(Patient_topic)
        write_api = "3D509BA5PQ8SQ4EU"
        cont_tremor = 0
        cont_fall = 0
        cont_freezing = 0
        
        #if Patient["e"][0]=="fall_manager":
        for i in message["e"]:
            if i["measureType"] == 'alive':
                pass
            else:
                topic = i["measureType"]
                if topic == "tremor_manager":
                    value = i["value"]
                    if value == 1:
                        cont_tremor += 1
                        field = 4
                        publish_flag(cont_tremor, field, ts_url, write_api)
                elif topic == "fall_manager":
                    value = i["value"]
                    if value == 1:
                        cont_fall += 1
                        field = 5
                        publish_flag(cont_fall, field, ts_url, write_api)
                elif topic == "freezing_manager":
                    value = i["value"]
                    if value == 1:
                        cont_freezing += 1
                        field = 6
                        publish_flag(cont_freezing, field, ts_url, write_api)
                elif topic == "WaistAccStats":
                    mean = i["value"]["mean"]
                    field=1
                    ts_publish_m(mean, field, write_api, ts_url)
                    std =i["value"]["std"]
                    field=2
                    ts_publish_s(std, field, write_api, ts_url)
                elif topic == "WristAccStats":
                    mean = i["value"]["mean"]
                    std =i["value"]["std"]
                    field=7
                    ts_publish_m(mean, field, write_api, ts_url)
                    field = 8
                    ts_publish_s(std, field, write_api, ts_url)
                elif topic == "FeetPressureStats":
                    mean = i["value"]["mean"]
                    field=3
                    ts_publish_m(mean, field, write_api, ts_url)
                    std =i["value"]["std"]
                    field = 9
                    ts_publish_s(std, field, write_api, ts_url)


def ts_publish_m(mean, field, write_api, ts_url): #publish the mean of the sensors
    """Publish data via REST on ThingSpeak."""
    field_reading = {'api_key': str(write_api), 'field' + str(field): mean}
    headers_f = {'Content-Type': 'application/json'}
    response = requests.post(ts_url,field_reading, headers_f)
    response.close()

def ts_publish_s(std, field, write_api, ts_url): #publish the standard deviation of the sensors
    """Publish data via REST on ThingSpeak."""
    field_reading = {'api_key': str(write_api), 'field' + str(field): std}
    headers_f = {'Content-Type': 'application/json'}
    response = requests.post(ts_url,field_reading, headers_f)
    response.close()


def publish_flag(cnt, field, ts_url, write_api):
    """Publish flag count via REST on ThingSpeak."""
    print("ciao")
    field_reading = {'api_key': str(write_api), 'field' + str(field): cnt}
    headers = {'Content-Type': 'application/json'}
    response = requests.post(ts_url,field_reading, headers)
    print(response)
    response.close()


def read_file(filename):
    """Read JSON file to get catalogURL, port, topic, and ThingSpeak URL."""
    with open(filename, "r") as f:
        data = json.load(f)
        url = data["ip"]
        topic = data["baseTopic"]
        port = data["port"]
        ts_url = data["thingspeakURL"]
        return url, port, topic, ts_url


class Data(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        (self.url, self.port, self.topic, self.ts_url) = read_file(FILE)
        (self.broker_ip, self.mqtt_port) = Broker(self.url, self.port)

    def run(self):
        sub = MySubscriber("Thingspeak", self.topic, self.broker_ip)
        sub.start()


def Broker(url, port):
    broker_ip = "test.mosquitto.org"
    mqtt_port = 1883
    return broker_ip, mqtt_port


def main():
    thread1 = Data()
    thread1.start()
    thread2 = Timer()
    thread2.start()


if __name__ == "__main__":
    main()
