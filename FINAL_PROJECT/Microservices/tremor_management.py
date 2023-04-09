# 1st. Read information from device connectors (wrist accelerometer) via MQTT
# 2nd. Check if the frequency of the accelerometer is between 4 - 9 Hz
# 3rd. If the frequency is in that range for a period of time, a tremor is occuring
# 4th . Send the data to the actuators

import time
import paho.mqtt.client as PahoMQTT
import json
from info_provider import *
import requests

class tremor_management():

    def __init__ (self, patientID, port, broker, topic, actuators_topic):

        self.clientID = str(patientID)
        self.port = port
        self.broker = broker
        self.topic = topic
        self.actuators_topic = actuators_topic
        self._paho_mqtt = PahoMQTT.Client(self.clientID, True)
        self._paho_mqtt.on_connect = self.MyOnConnect
        self._paho_mqtt.on_message = self.MyOnMessage


        self.bn = "marta/ParkinsonHelper/" + self.clientID

        self.structure = {"bn": self.bn +"/tremor_manager",
                "e":
                    [
                        {
                            "n":"tremor_manager",
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
        print(sensor_info)
        if(sensor_info["e"][0]["n"] == "MeanFrequencyAcceleration"):
            wrist_freq = sensor_info["e"][0]["v"]
            self.structure["e"][0]["t"] = sensor_info["e"][0]["t"]
            self.structure["e"][0]["v"] = 0
            if (wrist_freq >= 4) and (wrist_freq <= 9):
                self.structure["e"][0]["v"] = 1
                print ("Tremor situation at " + str(sensor_info["e"][0]["t"]) + "s")

        print(str(self.structure))
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

    microserviceID = 'tremor147852' 
    nclients = 2 ######### WE SHOULD HAVE A SETTING DESCRIBING HOW MANY CLIENTS DO WE HAVE

    wrist_topic = []
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
        wrist_topic_args = sensor_topics["wrist_acc"+str(i)].split('/')
        wrist_topic =wrist_topic_args[0]+'/+/'+wrist_topic_args[2]+'/'+wrist_topic_args[3]
        ####### IF THE LAST PARAMETER DEPENDS ON THE CLIENT NUMBER, THE WILDCARD IS WORTHLESS###

        # get client's actuators
        uri_actuators = 'http://localhost:9090/get_topics/actuator/patient' + str(i) + '/soundfeedback'
        actuators_topics= requests.get(uri_actuators).json()["soundfeedback"+str(i)]
        
        # Creating as many instances as clients, so they can comunicate with their corresponding actuator
        tm.append(tremor_management(microserviceID, port, broker, wrist_topic, actuators_topics))
        tm[i-1].start()
        tm[i-1].subscriber()

    # Creation of the MQTT message to send to the actuators
    while True:
        time.sleep(2)
        for i in range(len(tm)):
            tm[i].publisher(json.dumps(tm[i].structure))
