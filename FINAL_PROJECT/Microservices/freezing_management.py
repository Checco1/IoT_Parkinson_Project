# 1st. Read information from device connectors (waist accelerometer) via MQTT
# 2nd. Check if last stop peak 1.69-1.71 (waist accelerometer)
# 3rd. If the condition is happening, freezing is occuring
# 4th . Send the data to the actuators

import time
import paho.mqtt.client as PahoMQTT
import json
from info_provider import *
import requests


# MQTT connection class
class freezing_management():

    def __init__ (self, patientID, port, broker, topic):

        self.clientID = str(patientID)
        self.port = port
        self.broker = broker
        self.topic = topic
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

        return self.structure

    def start(self):
        self._paho_mqtt.connect(self.broker, self.port)
        self._paho_mqtt.loop_start()

    def subscriber(self):
        self._paho_mqtt.subscribe(self.topic, 2)
        print('Subscribed to' + self.topic)

    def publisher(self, msg):
        self._paho_mqtt.publish(self.topic, msg, 2)
        print("published: " + str(msg))

    def stop(self):
        self._paho_mqtt.unsubscribe(self.topic)
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()


if __name__ == "__main__":

    microserviceID = 'freezing147852' 
    nclients = 2 #This is just to try
    port = 1883
    broker = 'mqtt.eclipseprojects.io'
    actuators_topic = '/actuators/freezing' # Removing
    
    waist_topic = []

    # Get info about port and broker




    # Get the dictionary with all the clients and their sensors
    for i in range(1, nclients):
        uri = 'http://localhost:9090/get_topics/sensor/patient' + str(i) #
        sensor_topics= requests.get(uri).json()
        waist_topic_args = sensor_topics["waist_acc"+str(i)].split('/')
        waist_topic.append(waist_topic_args[0]+'/+/'+waist_topic_args[2]+'/'+waist_topic_args[3])

    # Get the dictionary with all the clients and their actuators
    #for i in range(1, nclients):
    #    uri = 'http://localhost:9090/get_topics/actuator/patient' + str(i) + '/soundfeedback'
    #    actuators_topics= requests.get(uri).json()
    #    soundfeedback_topic_args = actuators_topics["soundfeedback"+str(i)].split('/')
    #    soundfeedback_topic.append(soundfeedback_topic_args[0]+'/+/'+soundfeedback_topic_args[2]+'/'+soundfeedback_topic_args[3])

    # --------MQTT subscriber communication-----------
    tm = freezing_management(microserviceID, port, broker, waist_topic)
    tm.start()
    tm.subscriber()
    
    
    # Get the dictionary with all the clients and their actuators
    # We should get the patient depending on the callback
    actuators = freezing_management(microserviceID, port, broker, actuators_topic)

    # Creation of the MQTT message to send to the actuators
    while True:
        time.sleep(2)
        actuators.publisher(json.dumps(tm.structure))

        
