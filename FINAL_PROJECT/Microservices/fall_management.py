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
        self.flag_waist = 0
        self.flag_pressure = 0

    def MyOnConnect(self, paho_mqtt, user_data, flags, rc):
            pass

    def MyOnMessage(self, paho_mqtt, user_data, msg):
        sensor_info = json.loads(msg.payload)
        print(sensor_info)
        self.bn = ["/ParkinsonHelper/fall_manager/"  + sensor_info["bn"]]
        
        if(sensor_info["e"][0]["measureType"] == "TimeLastPeak"):
            waist_freq = sensor_info["e"][0]["value"]
            self.structure["e"][0]["timeStamp"] = sensor_info["e"][0]["timeStamp"]
            self.structure["e"][0]["value"] = 0
            if (waist_freq >= 1.69) and (waist_freq <= 1.71):
                self.structure["e"][0]["value"] = 1
                print ("Stop at " + str(sensor_info["e"][0]["timeStamp"]) + "s")
                self.flag_waist = 1

        elif(sensor_info["e"][0]["measureType"] == "FeetPressure"):
            pressure = sensor_info["e"][0]["value"]
            self.structure["e"][0]["timeStamp"] = sensor_info["e"][0]["timeStamp"]
            self.structure["e"][0]["value"] = 0
            if (pressure >= 4.9) and (pressure <= 5.1):
                self.structure["e"][0]["value"] = 1
                print ("Pressure lying at " + str(sensor_info["e"][0]["timeStamp"]) + "s")
                self.flag_pressure = 1
                 
        if (self.flag_waist==1 and self.flag_pressure==1):
            print("Fall situation at " + str(sensor_info["e"][0]["timeStamp"]))
            self.publisher(json.dumps(self.structure))
            self.flag_waist = 0
            self.flag_pressure = 0

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
    
    waist_topic = []
    pressure_topic = []
    actuators_topic = []

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
    pressure_ID = "pressure1"
    for d in range(len(client_info["devices"])):
                if client_info["devices"][d]["deviceID"] == waist_acc_ID:
                    waist_topic_p_1 = client_info["devices"][d]["Services"][0]["topic"]
                if client_info["devices"][d]["deviceID"] == pressure_ID:
                    pressure_topic_p_1 = client_info["devices"][d]["Services"][0]["topic"]

    waist_topic_args = waist_topic_p_1.split('/')
    waist_topic =waist_topic_args[0]+'/+/'+waist_topic_args[2]+'/#'
    pressure_topic_args = pressure_topic_p_1.split('/')
    pressure_topic =pressure_topic_args[0]+'/+/'+pressure_topic_args[2]+'/#'

    sensors = [waist_topic, pressure_topic]
    # get client's actuators
    #=================ASK ABOUT TELEBOT'S URI=============
    #uri_actuators = 'http://localhost:8080/get_topics/Statistic_services/patient1'
    #actuators_topics= requests.get(uri_actuators).json()["TeleBot"]
    actuators_topics = "ParkinsonHelper/patient1/actuator/fall"
    # Creating as many instances as clients, so they can comunicate with their corresponding actuator
    tm = fall_management(microserviceID, port, broker, sensors, actuators_topics)
    tm.start()
    tm.subscriber()

    # Creation of the MQTT message to send to the actuators
    while True:
        pass
