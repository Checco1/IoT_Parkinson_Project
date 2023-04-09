# 1st. Read information from device connectors (waist and wrist accelerometer and pressure) via MQTT
# 2nd. Gets the data sent by all the sensors and stores it
# 3rd. Calculates the average and standard deviation for the last 15 measures (last 30 seconds)
# 4th. Sends the statistics to the thingspeak adaptor

import time
import paho.mqtt.client as PahoMQTT
import json
import numpy as np
from numpy_ringbuffer import RingBuffer

from info_provider import *
import requests


class statistics_management():
    
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

        self.structure = {"bn": self.bn +"/statistics_manager",
                "e":
                    [
                        {
                            "n":"statistics_manager",
                            "u":"[mean, std]",
                            "t":"",
                            "v":"",
                        }
                    ]
        }

        self.waist_buffer = RingBuffer(15, float)
        self.wrist_buffer = RingBuffer(15, float)
        self.pressure_buffer = RingBuffer(15, float)

    def MyOnConnect(self, paho_mqtt, user_data, flags, rc):
            pass

    def MyOnMessage(self, paho_mqtt, user_data, msg):
        sensor_info = json.loads(msg.payload)
        #print(sensor_info)
        if(sensor_info["e"][0]["n"] == "TimeLastPeak"):
            waist_freq = sensor_info["e"][0]["v"]
            self.waist_buffer.append(waist_freq)
            v = [np.mean(self.waist_buffer), np.std(self.waist_buffer)]
            self.structure["e"][0]["n"] = "WaistAccStats"
            self.structure["e"][0]["t"] = sensor_info["e"][0]["t"]
            self.structure["e"][0]["v"] = v

        elif(sensor_info["e"][0]["n"] == "MeanFrequencyAcceleration"):
            wrist_freq = sensor_info["e"][0]["v"]
            self.wrist_buffer.append(wrist_freq)
            v = [np.mean(self.wrist_buffer), np.std(self.wrist_buffer)]
            self.structure["e"][0]["n"] = "WristAccStats"
            self.structure["e"][0]["t"] = sensor_info["e"][0]["t"]
            self.structure["e"][0]["v"] = v

        elif(sensor_info["e"][0]["n"] == "FeetPressure"):
            pressure = sensor_info["e"][0]["v"]
            self.pressure_buffer.append(pressure)
            v = [np.mean(self.pressure_buffer), np.std(self.pressure_buffer)]
            self.structure["e"][0]["n"] = "FeetPressureStats"
            self.structure["e"][0]["t"] = sensor_info["e"][0]["t"]
            self.structure["e"][0]["v"] = v
        
        self.publisher(json.dumps(self.structure))
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
    microserviceID = 'stats147852' 
    nclients = 2 ######### WE SHOULD HAVE A SETTING DESCRIBING HOW MANY CLIENTS DO WE HAVE

    sensors = []
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
        topic_args = sensor_topics["waist_acc"+str(i)].split('/')
        sensors =topic_args[0]+'/'+topic_args[1]+'/'+topic_args[2]+'/'+ '#'
        ####### IF THE LAST PARAMETER DEPENDS ON THE CLIENT NUMBER, THE WILDCARD IS WORTHLESS###

        # get client's actuators
        uri_actuators = 'http://localhost:9090/get_topics/Statistic_services/patient' + str(i)
        actuators_topics= requests.get(uri_actuators).json()["ThingSpeak"].strip('][').split(', ')[0]
        
        # Creating as many instances as clients, so they can comunicate with their corresponding actuator
        tm.append(statistics_management(microserviceID, port, broker, sensors, actuators_topics))
        tm[i-1].start()
        tm[i-1].subscriber()

    # Creation of the MQTT message to send to the actuators
    while True:
        time.sleep(2)
        for i in range(len(tm)):
            tm[i].publisher(json.dumps(tm[i].structure))
   

    ###### OLD ####3
    clientID1 = 'stats_manager1478523691'
    clientID2 = 'stats_manager1478523692'
    clientID3 = 'stats_manager1478523693'
    clientID4 = 'stats_manager1478523694'
    port = 1883
    broker = 'mqtt.eclipseprojects.io'
    waist_topic = '/sensors/waist_acc'
    wrist_topic = '/sensors/wrist_acc'
    pressure_topic = '/sensors/pressure'
    actuators_topic = '/actuators/statistics'

    #start of MQTT connection
    waist_sm = statistics_management(clientID1, port, broker, waist_topic, actuators_topic)
    wrist_sm = statistics_management(clientID2, port, broker, wrist_topic, actuators_topic)
    pressure_sm = statistics_management(clientID3, port, broker, pressure_topic, actuators_topic)

    waist_sm.start()
    wrist_sm.start()
    pressure_sm.start()

    waist_sm.subscriber()
    wrist_sm.subscriber()
    pressure_sm.subscriber()
    
    while True:
        pass


    