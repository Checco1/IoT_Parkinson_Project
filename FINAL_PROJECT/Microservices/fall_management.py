# 1st. Read information from device connectors (waist accelerometer and pressure) via MQTT
# 2nd. Check if:
#   pressure is between 4.9-5.1 (pressure)
#   last stop peak 1.69-1.71 (waist)
# 3rd. If both conditions are detected, then a falling is happening
# 4th. Send the data to the actuators

import time
import paho.mqtt.client as PahoMQTT
import json
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

        self.bn = "ParkinsonHelper" 

        self.structure = {"bn": self.bn +"/fall_manager",
                "e":
                    [
                        {
                            "measureType":"fall_manager",
                            "unit":"bool",
                            "timeStamp":"",
                            "value":"",
                        }
                    ]
        }
        self.listOfPatients = [{"waistFlag" : 0, "pressureFlag": 0}]*512
        self.sensor_id = "default"
        self.receivedPatientID = "default"
        self.receivedActuator = "default"

    def MyOnConnect(self, paho_mqtt, user_data, flags, rc):
            pass

    def MyOnMessage(self, paho_mqtt, user_data, msg):
        sensor_info = json.loads(msg.payload)

        self.sensor_id = sensor_info["bn"]
        sensorParameters = self.sensor_id.split('/')
        self.receivedPatientID = sensorParameters[0]
        self.receivedActuator = sensorParameters[1]

        # Get the numerical ID of the patient
        patientID = self.receivedPatientID
        patientID.replace("patient", '')
        patientNumber = int(patientID.replace("patient", ''))
        
        waistSensorName = "waist_acc" + str(patientNumber)
        pressureSensorName = "pressure" + str(patientNumber)

        if(self.receivedActuator == waistSensorName):
            print(sensor_info)
            waist_freq = sensor_info["e"][0]["value"]
            self.structure["e"][0]["timeStamp"] = sensor_info["e"][0]["timeStamp"]
            self.structure["e"][0]["value"] = 0
            if (waist_freq >= 1.5): #and (waist_freq <= 1.71): #must check if time last peak is > 1.5
                self.structure["e"][0]["value"] = 1
                print ("Stop at " + str(sensor_info["e"][0]["timeStamp"]) + "s")
                self.listOfPatients[patientNumber]["waistFlag"] = 1
            else:
                 self.listOfPatients[patientNumber]["waistFlag"] = 0
                

        elif(self.receivedActuator == pressureSensorName):
            print(sensor_info)
            pressure = sensor_info["e"][0]["value"]
            self.structure["e"][0]["timeStamp"] = sensor_info["e"][0]["timeStamp"]
            self.structure["e"][0]["value"] = 0
            if (pressure <= 30):
                self.structure["e"][0]["value"] = 1
                print ("Pressure lying at " + str(sensor_info["e"][0]["timeStamp"]) + "s")
                self.listOfPatients[patientNumber]["pressureFlag"] = 1
            else:
                 self.listOfPatients[patientNumber]["pressureFlag"] = 0
                 
        if (self.listOfPatients[patientNumber]["waistFlag"] == 1 and self.listOfPatients[patientNumber]["pressureFlag"] == 1):
            print("Fall situation at " + str(sensor_info["e"][0]["timeStamp"]))
            self.publisher(json.dumps(self.structure))
            self.listOfPatients[patientNumber]["pressureFlag"] = 0
            self.listOfPatients[patientNumber]["waistFlag"] = 0

        return self.structure

    def start(self):
        self._paho_mqtt.connect(self.broker, self.port)
        self._paho_mqtt.loop_start()

    def subscriber(self):
        self._paho_mqtt.subscribe(self.topic, 2)
        print('Subscribed to' + self.topic)

    def publisher(self, msg):
        topic = self.actuators_topic
        topic.replace( "PATIENT_ID", self.receivedPatientID)
        self._paho_mqtt.publish(self.actuators_topic, msg, 2)
        print("published: " + str(msg) + " on " + self.actuators_topic)

    def stop(self):
        self._paho_mqtt.unsubscribe(self.topic)
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()

if __name__ == "__main__":

    microserviceID = 'fall147852' 
    uri_broker = 'http://localhost:8080/broker'
    uri_sensor = 'http://localhost:8080/info/patient1' 

    waist_topic = []
    pressure_topic = []
    actuators_topic = []

    # Get info about port and broker
    settings = requests.get(uri_broker).json()
    port = int(settings["mqtt_port"])
    broker = settings["IP"]

    # get client's sensors 
    client_info= requests.get(uri_sensor).json()
    waist_acc_ID = "waist_acc1"
    pressure_ID = "pressure1"
    for d in range(len(client_info["devices"])):
                if client_info["devices"][d]["deviceID"] == waist_acc_ID:
                    waist_topic_p_1 = client_info["devices"][d]["Services"][0]["topic"]
                if client_info["devices"][d]["deviceID"] == pressure_ID:
                    pressure_topic_p_1 = client_info["devices"][d]["Services"][0]["topic"]

    waist_topic_args = waist_topic_p_1.split('/')
    sensor_topic =waist_topic_args[0]+'/+/'+waist_topic_args[2]+'/#'
    
    # get client's actuators
    #=================ASK ABOUT TELEBOT'S URI=============
    #uri_actuators = 'http://localhost:8080/get_topics/Statistic_services/patient1'
    #actuators_topics= requests.get(uri_actuators).json()["TeleBot"]
    actuators_topics = "ParkinsonHelper/PATIENT_ID/actuator/fall"
    # Creating as many instances as clients, so they can comunicate with their corresponding actuator
    tm = fall_management(microserviceID, port, broker, sensor_topic, actuators_topics)
    tm.start()
    tm.subscriber()

    # Creation of the MQTT message to send to the actuators
    while True:
        pass
