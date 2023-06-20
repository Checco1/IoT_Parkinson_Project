# 1. Get connection info (broker, port, ...) by REST
# 2. Get topic info by REST
# 3. Read information from device connectors (waist accelerometer) via MQTT
# 4. Check if last stop peak 1.69-1.71 (waist accelerometer). If the condition is 
#   happening, freezing is occuring
# 5 . Send the data to the corresponding soundeedback actuator

import time
import paho.mqtt.client as PahoMQTT
import json
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
        

        self.bn = "ParkinsonHelper"
        self.structure = {"bn": self.bn +"/freezing_manager",
                "e":
                    [
                        {
                            "measureType": "freezing_manager",
                            "unit":"bool",
                            "timeStamp":time.time(),
                            "value": True,
                        }
                    ]

        }
        self.listOfPatients = [{"waistFlag" : 0, "pressureFlag": 0}]*512
        self.sentFlag = ['OFF']*512
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
        patientNumber = int(self.receivedPatientID.replace("patient", ''))
        waistSensorName = "waist_acc" + str(patientNumber)
        pressureSensorName = "pressure" + str(patientNumber)
        self.structure["bn"] = self.receivedPatientID + '/freezing_manager'
        if(self.receivedActuator == waistSensorName):
            print(sensor_info)
            waist_time = sensor_info["e"][0]["value"]
            self.structure["e"][0]["timeStamp"] = sensor_info["e"][0]["timeStamp"]
            if (waist_time >= 1.5): #and (waist_time <= 1.71): #must check if time last peak is > 1.5
                print("Waist acceleration is too high")
                self.listOfPatients[patientNumber]["waistFlag"] = 1
            else:
                 self.listOfPatients[patientNumber]["waistFlag"] = 0

        elif(self.receivedActuator == pressureSensorName):
            print(sensor_info)
            pressure = sensor_info["e"][0]["value"]
            self.structure["e"][0]["timeStamp"] = sensor_info["e"][0]["timeStamp"]
            if (pressure > 30):
                print ("Pressure over 30 detected at " + str(sensor_info["e"][0]["timeStamp"]) + "s")
                self.listOfPatients[patientNumber]["pressureFlag"] = 1
            else:
                 self.listOfPatients[patientNumber]["pressureFlag"] = 0
           
        if(self.receivedActuator == waistSensorName or self.receivedActuator == pressureSensorName):
            if (self.sentFlag[patientNumber] == 'OFF'):
                if (self.listOfPatients[patientNumber]["waistFlag"] == 1 and self.listOfPatients[patientNumber]["pressureFlag"] == 1):
                    self.sentFlag[patientNumber] = 'SEND_COMMAND'
                    print("Freezing situation at " + str(sensor_info["e"][0]["timeStamp"]))
                    self.publisher(json.dumps(self.structure))
                    self.listOfPatients[patientNumber]["pressureFlag"] = 0
                    self.listOfPatients[patientNumber]["waistFlag"] = 0
            elif(self.sentFlag[patientNumber] == 'SEND_COMAND'):
                if (self.listOfPatients[patientNumber]["waistFlag"] == 1 or self.listOfPatients[patientNumber]["pressureFlag"] == 1):
                    self.sentFlag[patientNumber] = 'KEEPS_FREEZING'
                elif(self.listOfPatients[patientNumber]["waistFlag"] == 0 and self.listOfPatients[patientNumber]["pressureFlag"] == 0):
                    self.sentFlag[patientNumber] = 'OFF'
            else:
                if(self.listOfPatients[patientNumber]["waistFlag"] == 0 and self.listOfPatients[patientNumber]["pressureFlag"] == 0):
                    self.sentFlag[patientNumber] = 'OFF'

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

    microserviceID = 'freezing147852' 
    uri_broker = 'http://localhost:8080/broker'
    uri_sensor = 'http://localhost:8080/info/patient1' 

    waist_topic = []
    actuators_topics = []

    # Get info about port and broker
    settings = requests.get(uri_broker).json()
    port = int(settings["mqtt_port"])
    broker = settings["IP"]
    
    # get client's sensors (for now I can retrieve this this way, but maybe it is better to have the waist topic already defined.)
    
    client_info= requests.get(uri_sensor).json()
    waist_acc_ID = "waist_acc1"
    soundfeedback_ID = "sf1"
    
    for d in range(len(client_info["devices"])):
                if client_info["devices"][d]["deviceID"] == waist_acc_ID:
                    waist_topic_p_1 = client_info["devices"][d]["Services"][0]["topic"]
                if client_info["devices"][d]["deviceID"] == soundfeedback_ID:
                    soundfeedback_topic_p_1 = client_info["devices"][d]["Services"][0]["topic"]["activation"]

    waist_topic_args = waist_topic_p_1.split('/')
    waist_topic =waist_topic_args[0]+'/+/'+waist_topic_args[2]+'/#'

    sf_topic_args = soundfeedback_topic_p_1.split('/')
    sf_topic = sf_topic_args[0] +"/PATIENT_ID/" + sf_topic_args[2] + "/" + sf_topic_args[3]
    tm = freezing_management(microserviceID, port, broker, waist_topic, sf_topic)
    tm.start()
    tm.subscriber()

    # Creation of the MQTT message to send to the actuators
    while True:
        pass

        
