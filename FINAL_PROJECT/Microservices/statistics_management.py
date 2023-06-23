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

        self.listOfPatients = [{"waistBuffer" : [15], "wristBuffer": [15], "pressureBuffer": [15]}]*512
        self.sensor_id = "default"
        self.receivedPatientID = "default"
        self.receivedActuator = "default"


    def MyOnConnect(self, paho_mqtt, user_data, flags, rc):
            pass


    def MyOnMessage(self, paho_mqtt, user_data, msg):

        sensor_info = json.loads(msg.payload)
        # Retrieve sensor and ID from the "bn field"
        self.sensor_id = sensor_info["bn"]
        sensorParameters = self.sensor_id.split('/')
        self.receivedPatientID = sensorParameters[0]
        self.receivedActuator = sensorParameters[1]

        # Get the numerical ID of the patient
        patientID = self.receivedPatientID
        patientNumber = int(patientID.replace("patient", ''))

        waistSensorName = "waist_acc" + str(patientNumber)
        wristSensorName = "wrist_acc" + str(patientNumber)
        pressureSensorName = "pressure" + str(patientNumber)

        self.structure["bn"] = self.receivedPatientID + '/statistics_manager'
        if(self.receivedActuator == waistSensorName):
            waist_freq = sensor_info["e"][0]["value"]
            self.listOfPatients[patientNumber]["waistBuffer"].append(waist_freq)
            if (len(self.listOfPatients[patientNumber]["waistBuffer"]) == 15):
                self.structure["bn"] = self.sensor_id      
                self.structure["e"][0]["measureType"] = "WaistAccStats"
                self.structure["e"][0]["timeStamp"] = sensor_info["e"][0]["timeStamp"]
                self.structure["e"][0]["value"] = str(self.listOfPatients[patientNumber]["waistBuffer"])
                # Remove the content of the buffer
                self.listOfPatients[patientNumber]["waistBuffer"].clear()
                self.publisher(json.dumps(self.structure))

        elif(self.receivedActuator == wristSensorName):
            wrist_freq = sensor_info["e"][0]["value"]
            self.listOfPatients[patientNumber]["wristBuffer"].append(wrist_freq)
            if (len(self.listOfPatients[patientNumber]["wristBuffer"]) == 15): 
                self.structure["bn"] = self.sensor_id      
                self.structure["e"][0]["measureType"] = "WristAccStats"
                self.structure["e"][0]["timeStamp"] = sensor_info["e"][0]["timeStamp"]
                self.structure["e"][0]["value"] = str(self.listOfPatients[patientNumber]["wristBuffer"])
                # Remove the content of the buffer
                self.listOfPatients[patientNumber]["wristBuffer"].clear()
                self.publisher(json.dumps(self.structure))

        elif(self.receivedActuator == pressureSensorName):
            pressure = sensor_info["e"][0]["value"]
            self.listOfPatients[patientNumber]["pressureBuffer"].append(pressure)
            if (len(self.listOfPatients[patientNumber]["pressureBuffer"]) == 15):  
                self.structure["bn"] = self.sensor_id    
                self.structure["e"][0]["measureType"] = "PressureStats"
                self.structure["e"][0]["timeStamp"] = sensor_info["e"][0]["timeStamp"]
                self.structure["e"][0]["value"] = str(self.listOfPatients[patientNumber]["pressureBuffer"])
                # Remove the content of the buffer
                self.listOfPatients[patientNumber]["pressureBuffer"].clear()
                self.publisher(json.dumps(self.structure))
        
        return self.structure

    def start(self):
        self._paho_mqtt.connect(self.broker, self.port)
        self._paho_mqtt.loop_start()

    def subscriber(self):
        self._paho_mqtt.subscribe(self.topic, 2)
        print('Subscribed to' + self.topic)

    def publisher(self, msg):
        topic = self.actuators_topic.replace( "PATIENT_ID", self.receivedPatientID)
        self._paho_mqtt.publish(topic, msg, 2)
        print("published: " + str(msg) + " on " + topic)

    def stop(self):
        self._paho_mqtt.unsubscribe(self.topic)
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()

    

if __name__ == "__main__":
    microserviceID = 'stats147852' 
    uri_broker = 'http://localhost:8080/broker'
    uri_sensor = 'http://localhost:8080/info/patient1'
    uri_actuators = 'http://localhost:8080/ts'

     # Get info about port and broker
    settings = requests.get(uri_broker).json()
    port = int(settings["mqtt_port"])
    broker = settings["IP"]

    # get client's sensors 
    client_info= requests.get(uri_sensor).json()
    waist_acc_ID = "waist_acc1"

    for d in range(len(client_info["devices"])):
                if client_info["devices"][d]["deviceID"] == waist_acc_ID:
                    waist_topic_p_1 = client_info["devices"][d]["Services"][0]["topic"]
               
    topic_args = waist_topic_p_1.split('/')
    sensors =topic_args[0]+'/+/'+topic_args[2]+'/'+ '#'

    # get client's actuators
    
    actuators_topics = "ParkinsonHelper/PATIENT_ID/microservices/statistics"

    tm = statistics_management(microserviceID, port, broker, sensors, actuators_topics)
    tm.start()
    tm.subscriber()

    # Creation of the MQTT message to send to the actuators
    while True:
        pass
   