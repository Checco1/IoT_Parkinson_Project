# 1st. Read information from device connectors (waist accelerometer and pressure) via MQTT
# 2nd. Check if:
#   pressure is between 4.9-5.1 (pressure)
#   last stop peak 1.69-1.71 (waist)
# 3rd. If both conditions are detected, then a falling is happening
# 4th. Send the data to the actuators

import time
import paho.mqtt.client as PahoMQTT
import json
from info_provider import *
import requests

class fall_management():
    
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

        self.structure = {"bn": self.bn +"/fall_manager",
                "e":
                    [
                        {
                            "n":"fall_manager",
                            "u":"bool",
                            "t":"",
                            "v":"",
                        }
                    ]
        }

    def MyOnConnect(self, paho_mqtt, user_data, flags, rc):
            pass

    def MyOnMessage(self, paho_mqtt, user_data, msg):
        sensor_info = json.loads(msg.payload)
        print(sensor_info)
        if(sensor_info["e"][0]["n"] == "TimeLastPeak"):
            waist_freq = sensor_info["e"][0]["v"]
            self.structure["e"][0]["t"] = sensor_info["e"][0]["t"]
            self.structure["e"][0]["v"] = 0
            if (waist_freq >= 1.69) and (waist_freq <= 1.71):
                self.structure["e"][0]["v"] = 1
                print ("Stop at " + str(sensor_info["e"][0]["t"]) + "s")

        elif(sensor_info["e"][0]["n"] == "FeetPressure"):
            pressure = sensor_info["e"][0]["v"]
            self.structure["e"][0]["t"] = sensor_info["e"][0]["t"]
            self.structure["e"][0]["v"] = 0
            if (pressure >= 4.9) and (pressure <= 5.1):
                self.structure["e"][0]["v"] = 1
                print ("Pressure lying at " + str(sensor_info["e"][0]["t"]) + "s")
            
        #print(str(self.structure))
        return self.structure

    def start(self):
        self._paho_mqtt.connect(self.broker, self.port)
        self._paho_mqtt.loop_start()

    def subscriber(self):
        topics = []
        for i in range(len(self.topic)):
            topics.append((self.topic[i],2))
        self._paho_mqtt.subscribe(topics)
        #print('Subscribed to' + self.topic)

    def publisher(self, msg):
        self._paho_mqtt.publish(self.actuators_topic, msg, 2)
        print("published: " + str(msg) + " on " + self.actuators_topic)

    def stop(self):
        self._paho_mqtt.unsubscribe(self.topic)
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()

if __name__ == "__main__":

    microserviceID = 'fall147852' 
    nclients = 2 ######### WE SHOULD HAVE A SETTING DESCRIBING HOW MANY CLIENTS DO WE HAVE

    waist_topic = []
    pressure_topic = []
    actuators_topic = []
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
        ####### IF THE LAST PARAMETER DEPENDS ON THE CLIENT NUMBER, THE WILDCARD IS WORTHLESS###

        pressure_topic_args = sensor_topics["pressure"+str(i)].split('/')
        pressure_topic =pressure_topic_args[0]+'/+/'+pressure_topic_args[2]+'/'+pressure_topic_args[3]

        sensors = [waist_topic, pressure_topic]
        # get client's actuators
        uri_actuators = 'http://localhost:9090/get_topics/Statistic_services/patient' + str(i)
        actuators_topics= requests.get(uri_actuators).json()["TeleBot"]
        
        # Creating as many instances as clients, so they can comunicate with their corresponding actuator
        tm.append(fall_management(microserviceID, port, broker, sensors, actuators_topics))
        tm[i-1].start()
        tm[i-1].subscriber()

    # Creation of the MQTT message to send to the actuators
    while True:
        time.sleep(2)
        for i in range(len(tm)):
            tm[i].publisher(json.dumps(tm[i].structure))
