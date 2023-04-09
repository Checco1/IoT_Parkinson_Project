# 1. Get connection info (broker, port, ...) by REST
# 2. Get topic info by REST
# 3. Read information from device connectors (waist accelerometer) via MQTT
# 4. Check if last stop peak 1.69-1.71 (waist accelerometer). If the condition is 
#   happening, freezing is occuring
# 5 . Send the data to the corresponding soundeedback actuator

import time
import paho.mqtt.client as PahoMQTT
import json
from info_provider import *
import requests


# MQTT connection class
class freezing_management():

    def __init__ (self, patientID, port, broker, topic, actuators_topic):

        self.clientID = str(patientID)
        self.port = port
        self.broker = broker
        self.topic = topic
        self.actuators_topic = actuators_topic
        self._paho_mqtt = PahoMQTT.Client(self.clientID, True)
        self._paho_mqtt.on_connect = self.MyOnConnect
        self._paho_mqtt.on_message = self.MyOnMessage
        self.sensor_id = "def"


        self.bn = "ParkinsonHelper/" + self.clientID

        self.structure = {"bn": self.bn +"/freezing_manager",
                "e":
                    [
                        {
                            "n": "freezing_manager",
                            "u":"bool",
                            "t":time.time(),
                            "v": 0,
                        }
                    ]

        }
        
    def MyOnConnect(self, paho_mqtt, user_data, flags, rc):
            pass

    def MyOnMessage(self, paho_mqtt, user_data, msg):
        sensor_info = json.loads(msg.payload)
        # I want to identify who is the patient who has sent this, idk if i can identify it with the bn
        self.sensor_id = sensor_info["bn"]
        if(sensor_info["e"][0]["n"] == "TimeLastPeak"):
            waist_time = sensor_info["e"][0]["v"]
            self.structure["e"][0]["t"] = sensor_info["e"][0]["t"]
            self.structure["e"][0]["v"] = 0
            if (waist_time >= 1.69) and (waist_time <= 1.71):
                self.structure["e"][0]["v"] = 1
                print ("Freezing situation at " + str(sensor_info["e"][0]["t"]) + "s")

        self.publisher(json.dumps(tm.structure))
        return self.structure

    def start(self):
        self._paho_mqtt.connect(self.broker, self.port)
        self._paho_mqtt.loop_start()

    def subscriber(self):
        self._paho_mqtt.subscribe(self.topic, 2)
        print('Subscribed to' + self.topic)

    def publisher(self, msg):
        self._paho_mqtt.publish(self.actuators_topic, msg, 2)
        print("published: " + str(msg) + " on " + self.actuators_topic)

    def stop(self):
        self._paho_mqtt.unsubscribe(self.topic)
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()


if __name__ == "__main__":

    microserviceID = 'freezing147852' 
    nclients = 2 ######### WE SHOULD HAVE A SETTING DESCRIBING HOW MANY CLIENTS DO WE HAVE

    waist_topic = []
    actuators_topics = []
    tm = []

    # Get info about port and broker
    uri_settings = 'http://localhost:9090/get_settings'
    settings = requests.get(uri_settings).json()
    port = settings["port"]
    broker = settings["broker"]

    # Get the dictionary with all the clients and their sensors and actuators
    for i in range(1, nclients+1):
        # get client's sensors 
        uri_sensor = 'http://localhost:9090/get_topics/sensor/patient' + str(i) #
        sensor_topics= requests.get(uri_sensor).json()
        waist_topic_args = sensor_topics["waist_acc"+str(i)].split('/')
        waist_topic =waist_topic_args[0]+'/+/'+waist_topic_args[2]+'/'+waist_topic_args[3]
        # get client's actuators
        uri_actuators = 'http://localhost:9090/get_topics/actuator/patient' + str(i) + '/dbs'
        actuators_topics= requests.get(uri_actuators).json()["dbs"+str(i)]
        
        # Creating as many instances as clients, so they can comunicate with their corresponding actuator
        tm.append(freezing_management(microserviceID, port, broker, waist_topic, actuators_topics))
        tm[i-1].start()
        tm[i-1].subscriber()

    # Creation of the MQTT message to send to the actuators
    while True:
        time.sleep(2)
        for i in range(len(tm)):
            tm[i].publisher(json.dumps(tm[i].structure))

        
