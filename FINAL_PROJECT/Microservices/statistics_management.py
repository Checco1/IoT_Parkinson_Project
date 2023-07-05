# 1st. Read information from device connectors (waist and wrist accelerometer and pressure) via MQTT
# 2nd. Gets the data sent by all the sensors and stores it
# 3rd. Calculates the average and standard deviation for the last 15 measures (last 30 seconds)
# 4th. Sends the statistics to the thingspeak adaptor

import time
import datetime
import paho.mqtt.client as PahoMQTT
import json
import numpy as np
from numpy_ringbuffer import RingBuffer
import requests
from pathlib import Path

P = Path(__file__).parent.absolute()
CONF = P / 'statistics_conf.json'

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
                            "unit":"[]",
                            "timeStamp":"",
                            "value":"",
                            "valueTimestamps" : ""
                        }
                    ]
        }

        self.listOfPatientsTimeStamps = [
                                            {       
                                                "waistTimeStamp" : [15], 
                                                "wristTimeStamp": [15], 
                                                "pressureTimeStamp": [15]
                                            }
                                        ]*512
        self.listOfPatients = [
                                    {
                                        "waistBuffer" : [15], 
                                        "wristBuffer": [15], 
                                        "pressureBuffer": [15]
                                    }
                                ]*512
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
        now = time.time()
        if(self.receivedActuator == waistSensorName):
            waist_freq = sensor_info["e"][0]["value"]
            waist_timestamp = str(datetime.datetime.utcfromtimestamp(now).isoformat())

            self.listOfPatients[patientNumber]["waistBuffer"].append(waist_freq)
            self.listOfPatientsTimeStamps[patientNumber]["waistTimeStamp"].append(waist_timestamp)

            if (len(self.listOfPatients[patientNumber]["waistBuffer"]) == 15):
                self.structure["bn"] = self.sensor_id      
                self.structure["e"][0]["measureType"] = "WaistAccStats"
                self.structure["e"][0]["timeStamp"] = sensor_info["e"][0]["timeStamp"]
                self.structure["e"][0]["value"] = str(self.listOfPatients[patientNumber]["waistBuffer"])
                self.structure["e"][0]["valueTimestamps"] = str(self.listOfPatientsTimeStamps[patientNumber]["waistTimeStamp"])
                # Remove the content of the buffer
                self.listOfPatients[patientNumber]["waistBuffer"].clear()
                self.listOfPatientsTimeStamps[patientNumber]["waistTimeStamp"].clear()
                self.publisher(json.dumps(self.structure))

        elif(self.receivedActuator == wristSensorName):
            wrist_freq = sensor_info["e"][0]["value"]
            wrist_timestamp = str(datetime.datetime.utcfromtimestamp(now).isoformat())

            self.listOfPatients[patientNumber]["wristBuffer"].append(wrist_freq)
            self.listOfPatientsTimeStamps[patientNumber]["wristTimeStamp"].append(wrist_timestamp)

            if (len(self.listOfPatients[patientNumber]["wristBuffer"]) == 15): 
                self.structure["bn"] = self.sensor_id      
                self.structure["e"][0]["measureType"] = "WristAccStats"
                self.structure["e"][0]["timeStamp"] = sensor_info["e"][0]["timeStamp"]
                self.structure["e"][0]["value"] = str(self.listOfPatients[patientNumber]["wristBuffer"])
                self.structure["e"][0]["valueTimestamps"] = str(self.listOfPatientsTimeStamps[patientNumber]["wristTimeStamp"])

                # Remove the content of the buffer
                self.listOfPatients[patientNumber]["wristBuffer"].clear()
                self.listOfPatientsTimeStamps[patientNumber]["wristTimeStamp"].clear()

                self.publisher(json.dumps(self.structure))

        elif(self.receivedActuator == pressureSensorName):
            pressure = sensor_info["e"][0]["value"]
            pressure_timestamp = str(datetime.datetime.utcfromtimestamp(now).isoformat())
           
            self.listOfPatients[patientNumber]["pressureBuffer"].append(pressure)
            self.listOfPatientsTimeStamps[patientNumber]["pressureTimeStamp"].append(pressure_timestamp)

            if (len(self.listOfPatients[patientNumber]["pressureBuffer"]) == 15):  
                self.structure["bn"] = self.sensor_id    
                self.structure["e"][0]["measureType"] = "PressureStats"
                self.structure["e"][0]["timeStamp"] = sensor_info["e"][0]["timeStamp"]
                self.structure["e"][0]["value"] = str(self.listOfPatients[patientNumber]["pressureBuffer"])
                self.structure["e"][0]["valueTimestamps"] = str(self.listOfPatientsTimeStamps[patientNumber]["pressureTimeStamp"])

                
                # Remove the content of the buffer
                self.listOfPatients[patientNumber]["pressureBuffer"].clear()
                self.listOfPatientsTimeStamps[patientNumber]["pressureTimeStamp"].clear()
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
        print("published: " + str(msg) + " on " + topic + "\n")

    def stop(self):
        self._paho_mqtt.unsubscribe(self.topic)
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()

    

if __name__ == "__main__":
     # Open microservice's configuration file
    try:
        with open(CONF, "r") as fs:
             conf_file = json.loads(fs.read())
    except Exception:
         print("Problem in loading catalog")

    # Get info about port and broker
    microserviceID = conf_file["microservice_ID"]
    settings = requests.get(conf_file["broker_uri"]).json()
    port = int(settings["mqtt_port"])
    broker = settings["IP"]

    # Get client's sensors
    while (True):
        client_info= requests.get(conf_file["information_uri"]).json()
        if (client_info != -1):
            time.sleep(5)
            break
        else:
            print("No patients registered yet, retrying in 10s...")
        time.sleep(10)
    
    sensorID = conf_file["sensor_ID"]
    
    for d in range(len(client_info["devices"])):
                if client_info["devices"][d]["deviceID"] == sensorID:
                    sensor = client_info["devices"][d]["Services"][0]["topic"]

    sensor_args = sensor.split('/')
    sensor_topic =sensor_args[0]+'/+/'+sensor_args[2]+'/#'

    actuators_topics = conf_file["microservice_topic"]

    tm = statistics_management(microserviceID, port, broker, sensor_topic, actuators_topics)
    tm.start()
    tm.subscriber()

    while True:
        pass
   