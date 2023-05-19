# 1st. Read information from device connectors (waist and wrist accelerometer and pressure) via MQTT
# 2nd. Gets the data sent by all the sensors and stores it
# 3rd. Calculates the average and standard deviation for the last 15 measures (last 30 seconds)
# 4th. Sends the statistics to the thingspeak adaptor

import time
import paho.mqtt.client as PahoMQTT
import json
import numpy as np
from numpy_ringbuffer import RingBuffer
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

        self.bn = "ParkinsonHelper/" + self.clientID

        self.structure = {"bn": self.bn +"/statistics_manager",
                "e":
                    [
                        {
                            "measureType":"statistics_manager",
                            "unit":"[mean, std]",
                            "timeStamp":"",
                            "value":"",
                        }
                    ]
        }

        self.waist_buffer = RingBuffer(15, float)
        self.wrist_buffer = RingBuffer(15, float)
        self.pressure_buffer = RingBuffer(15, float)

    def MyOnConnect(self, paho_mqtt, user_data, flags, rc):
            pass

    # ============Send the whole buffer===================
    def MyOnMessage(self, paho_mqtt, user_data, msg):
        sensor_info = json.loads(msg.payload)
        #print(sensor_info)
        if(sensor_info["e"][0]["measureType"] == "TimeLastPeak"):
            waist_freq = sensor_info["e"][0]["value"]
            self.waist_buffer.append(waist_freq)
            v = {"mean" : np.mean(self.waist_buffer),
                 "std" : np.std(self.waist_buffer),
                 "measurements" : str(self.waist_buffer._arr)
                 }
            self.structure["e"][0]["measureType"] = "WaistAccStats"
            self.structure["e"][0]["timeStamp"] = sensor_info["e"][0]["timeStamp"]
            self.structure["e"][0]["value"] = v

        elif(sensor_info["e"][0]["measureType"] == "MeanFrequencyAcceleration"):
            wrist_freq = sensor_info["e"][0]["value"]
            self.wrist_buffer.append(wrist_freq)
            v = {"mean" : np.mean(self.wrist_buffer),
                 "std" : np.std(self.wrist_buffer),
                 "measurements" : str(self.wrist_buffer._arr)
                 }
            self.structure["e"][0]["measureType"] = "WristAccStats"
            self.structure["e"][0]["timeStamp"] = sensor_info["e"][0]["timeStamp"]
            self.structure["e"][0]["value"] = v

        elif(sensor_info["e"][0]["measureType"] == "FeetPressure"):
            pressure = sensor_info["e"][0]["value"]
            self.pressure_buffer.append(pressure)
            v = {"mean" : np.mean(self.pressure_buffer),
                 "std" : np.std(self.pressure_buffer),
                 "measurements" : str(self.pressure_buffer._arr)
                 }
            self.structure["e"][0]["measureType"] = "FeetPressureStats"
            self.structure["e"][0]["timeStamp"] = sensor_info["e"][0]["timeStamp"]
            self.structure["e"][0]["value"] = v
        
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
    uri_broker = 'http://localhost:8080/broker'
    settings = requests.get(uri_broker).json()
    print(settings)
    port = int(settings["mqtt_port"])
    broker = settings["IP"]

    # Get the dictionary with all the clients and their sensors and actuators
    
    # get client's sensors 
    uri_sensor = 'http://localhost:8080/info/patient1'
    client_info= requests.get(uri_sensor).json()
    waist_acc_ID = "waist_acc1"

    for d in range(len(client_info["devices"])):
                if client_info["devices"][d]["deviceID"] == waist_acc_ID:
                    waist_topic_p_1 = client_info["devices"][d]["Services"][0]["topic"]
               
    topic_args = waist_topic_p_1.split('/')
    sensors =topic_args[0]+'/+/'+topic_args[2]+'/'+ '#'
    ####### IF THE LAST PARAMETER DEPENDS ON THE CLIENT NUMBER, THE WILDCARD IS WORTHLESS###

    # get client's actuators
    #==================ASK ABOUT THINGSPEAK'S URI=============
    uri_actuators = 'http://localhost:8080/ts'
    actuators_topics = "ParkinsonHelper/patient1/actuator/statistics"

    # Creating as many instances as clients, so they can comunicate with their corresponding actuator
    tm = statistics_management(microserviceID, port, broker, sensors, actuators_topics)
    tm.start()
    tm.subscriber()

    # Creation of the MQTT message to send to the actuators
    while True:
        pass
   