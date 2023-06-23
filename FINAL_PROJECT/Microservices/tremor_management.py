# 1st. Read information from device connectors (wrist accelerometer) via MQTT
# 2nd. Check if the frequency of the accelerometer is between 4 - 9 Hz
# 3rd. If the frequency is in that range for a period of time, a tremor is occuring
# 4th . Send the data to the actuators

import time
import paho.mqtt.client as PahoMQTT
import json
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
        self.sensor_id = "default"
        self.receivedPatientID = "default"
        self.receivedActuator = "default"
        self.sentFlag = ['OFF']*512

        self.bn = "ParkinsonHelper"

        self.structure = {"bn": self.bn +"/tremor_manager",
                "e":
                    [
                        {
                            "measureType":"tremor_manager",
                            "unit":"bool",
                            "timeStamp":time.time(),
                            "value": True,
                        }
                    ]

        }
        
    def MyOnConnect(self, paho_mqtt, user_data, flags, rc):
            pass

    def MyOnMessage(self, paho_mqtt, user_data, msg):
        sensor_info = json.loads(msg.payload)
        self.sensor_id = sensor_info["bn"]
        sensorParameters = self.sensor_id.split('/')
        self.receivedPatientID = sensorParameters[0]
        self.receivedActuator = sensorParameters[1]
        patientNumber = int(self.receivedPatientID.replace("patient", ''))
        sensor_name = "wrist_acc" + str(patientNumber)

        self.structure["bn"] = self.receivedPatientID + '/tremor_manager'
        if(self.receivedActuator == sensor_name):
            print(sensor_info)
            wrist_freq = sensor_info["e"][0]["value"]
            self.structure["e"][0]["timeStamp"] = sensor_info["e"][0]["timeStamp"]
            if (wrist_freq >= 4):
                if (self.sentFlag[patientNumber] == 'OFF'):
                    self.sentFlag[patientNumber] = 'KEEPS_TREMBLING'
                    print ("Tremor situation at " + str(sensor_info["e"][0]["timeStamp"]) + "s")
                    self.publisher(json.dumps(self.structure))

            else:
                 self.sentFlag[patientNumber] = 'OFF'
                 
                

        return self.structure

    def start(self):
        self._paho_mqtt.connect(self.broker, self.port)
        self._paho_mqtt.loop_start()

    def subscriber(self):
        self._paho_mqtt.subscribe(self.topic, 2)
        print('Subscribed to ' + self.topic)

    def publisher(self, msg):
        topic = self.actuators_topic.replace( "PATIENT_ID", self.receivedPatientID)
        self._paho_mqtt.publish(topic, msg, 2)
        print("published: " + str(msg) + " on " + self.actuators_topic)

    def stop(self):
        self._paho_mqtt.unsubscribe(self.topic)
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()


if __name__ == "__main__":

    microserviceID = 'tremor147852' 
    uri_broker = 'http://localhost:8080/broker'
    uri_sensor = 'http://localhost:8080/info/patient1'

    # Get info about port and broker
    settings = requests.get(uri_broker).json()
    port = int(settings["mqtt_port"])
    broker = settings["IP"]

    # get client's sensors 
    client_info= requests.get(uri_sensor).json()
    wrist_acc_ID = "wrist_acc1"
    dbs_ID = "dbs1"

    for d in range(len(client_info["devices"])):
                if client_info["devices"][d]["deviceID"] == wrist_acc_ID:
                    wrist_topic_p_1 = client_info["devices"][d]["Services"][0]["topic"]
                if client_info["devices"][d]["deviceID"] == dbs_ID:
                    dbs_topic_p_1 = client_info["devices"][d]["Services"][0]["topic"]["activation"]


    wrist_topic_args = wrist_topic_p_1.split('/')
    wrist_topic =wrist_topic_args[0]+'/+/'+wrist_topic_args[2]+'/#'
    
    dbs_topic_args = dbs_topic_p_1.split('/')
    dbs_topic = dbs_topic_args[0] + "/PATIENT_ID/" + dbs_topic_args[2] + '/' + dbs_topic_args[3]
    print(dbs_topic)
    tm = tremor_management(microserviceID, port, broker, wrist_topic, dbs_topic)
    tm.start()
    tm.subscriber()

    # Creation of the MQTT message to send to the actuators
    while True:
        pass
