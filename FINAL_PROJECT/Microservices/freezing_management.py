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
        self.sensor_id = "def"


        self.bn = "ParkinsonHelper"

        self.structure = {"bn": self.bn +"/freezing_manager",
                "e":
                    [
                        {
                            "measureType": "freezing_manager",
                            "unit":"bool",
                            "timeStamp":time.time(),
                            "value": 0,
                        }
                    ]

        }
        
    def MyOnConnect(self, paho_mqtt, user_data, flags, rc):
            pass

    def MyOnMessage(self, paho_mqtt, user_data, msg):
        sensor_info = json.loads(msg.payload)
        print(sensor_info)
        self.sensor_id = sensor_info["bn"]
        if(sensor_info["e"][0]["measureType"] == "TimeLastPeak"):
            waist_time = sensor_info["e"][0]["value"]
            self.structure["e"][0]["timeStamp"] = sensor_info["e"][0]["timeStamp"]
            self.structure["e"][0]["value"] = 0
            if (waist_time >= 1.69) and (waist_time <= 1.71):
                self.structure["e"][0]["value"] = 1
                print ("Freezing situation at " + str(sensor_info["e"][0]["timeStamp"]) + "s")
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

    microserviceID = 'freezing147852' 

    waist_topic = []
    actuators_topics = []

    # Get info about port and broker
    uri_broker = 'http://localhost:8080/broker'
    settings = requests.get(uri_broker).json()
    port = int(settings["mqtt_port"])
    broker = settings["IP"]

    # Get the dictionary with all the clients and their sensors and actuators
    
    # get client's sensors 
    uri_sensor = 'http://localhost:8080/info/patient1' 
    client_info= requests.get(uri_sensor).json()
    waist_acc_ID = "waist_acc1"
    soundfeedback_ID = "soundfeedback1"
    for d in range(len(client_info["devices"])):
                if client_info["devices"][d]["deviceID"] == waist_acc_ID:
                    waist_topic_p_1 = client_info["devices"][d]["Services"][0]["topic"]
                if client_info["devices"][d]["deviceID"] == soundfeedback_ID:
                    soundfeedback_topic_p_1 = client_info["devices"][d]["Services"][0]["topic"]


    waist_topic_args = waist_topic_p_1.split('/')
    waist_topic =waist_topic_args[0]+'/+/'+waist_topic_args[2]+'/#'

    # Creating as many instances as clients, so they can comunicate with their corresponding actuator
    tm = freezing_management(microserviceID, port, broker, waist_topic, soundfeedback_topic_p_1)
    tm.start()
    tm.subscriber()

    # Creation of the MQTT message to send to the actuators
    while True:
        pass

        
