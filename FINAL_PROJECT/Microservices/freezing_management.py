# 1st. Read information from device connectors (waist accelerometer) via MQTT
# 2nd. Check if last stop peak 1.69-1.71 (waist accelerometer)
# 3rd. If the condition is happening, freezing is occuring
# 4th . Send the data to the actuators

import time
import paho.mqtt.client as PahoMQTT
import json

class freezing_management():

    def __init__ (self, patientID, port, broker, topic):

        self.clientID = str(patientID)
        self.port = port
        self.broker = broker
        self.topic = topic
        self._paho_mqtt = PahoMQTT.Client(self.clientID, True)
        self._paho_mqtt.on_connect = self.MyOnConnect
        self._paho_mqtt.on_message = self.MyOnMessage


        self.bn = "marta/ParkinsonHelper/" + self.clientID

        self.structure = {"bn": self.bn +"/freezing_manager",
                "e":
                    [
                        {
                            "n": "freezing_manager",
                            "u":"bool",
                            "t":time.time(),
                            "v": 0,
                        }
                    ]

        }
        
    def MyOnConnect(self, paho_mqtt, user_data, flags, rc):
            pass

    def MyOnMessage(self, paho_mqtt, user_data, msg):
        sensor_info = json.loads(msg.payload)
        if(sensor_info["e"][0]["n"] == "TimeLastPeak"):
            waist_time = sensor_info["e"][0]["v"]
            self.structure["e"][0]["t"] = sensor_info["e"][0]["t"]
            self.structure["e"][0]["v"] = 0
            if (waist_time >= 1.69) and (waist_time <= 1.71):
                self.structure["e"][0]["v"] = 1
                print ("Freezing situation at " + str(sensor_info["e"][0]["t"]) + "s")

        return self.structure

    def start(self):
        self._paho_mqtt.connect(self.broker, self.port)
        self._paho_mqtt.loop_start()

    def subscriber(self):
        self._paho_mqtt.subscribe(self.topic, 2)
        print('Subscribed to' + self.topic)

    def publisher(self, msg):
        self._paho_mqtt.publish(self.topic, msg, 2)
        print("published: " + str(msg))

    def stop(self):
        self._paho_mqtt.unsubscribe(self.topic)
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()


if __name__ == "__main__":

    clientID = 'freezing_manager147852369'
    port = 1883
    broker = 'mqtt.eclipseprojects.io'
    waist_topic = '/sensors/waist_acc'
    actuators_topic = '/actuators/freezing'

    #start of MQTT connection
    tm = freezing_management(clientID, port, broker, waist_topic)
    actuators = freezing_management(clientID, port, broker, actuators_topic)
    tm.start()
    tm.subscriber()
    
    # Creation of the MQTT message to send to the actuators
    while True:
        time.sleep(2)
        actuators.publisher(json.dumps(tm.structure))

        
