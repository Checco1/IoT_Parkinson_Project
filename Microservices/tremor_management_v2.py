# 1st. Read information from device connectors (wrist accelerometer) via MQTT
# 2nd. Check if the frequency of the accelerometer is between 4 - 9 Hz
# 3rd. If the frequency is in that range for a period of time, a tremor is occuring
# 4th . Send the data to the statistics manager
# 5th. Send a message to the ThingSpeak adaptor if a tremor is detected

import time
import paho.mqtt.client as PahoMQTT
import json

class tremor_management():

    def __init__ (self, patientID, port, broker, topic):

        self.clientID = str(patientID)
        self.port = port
        self.broker = broker
        self.topic = topic
        self._paho_mqtt = PahoMQTT.Client(self.clientID, True)
        self._paho_mqtt.on_connect = self.MyOnConnect
        self._paho_mqtt.on_message = self.MyOnMessage


        self.bn = "marta/ParkinsonHelper/" + self.clientID

        self.structure = {"bn": self.bn +"/tremor_manager",
                "e":
                    [
                        {
                            "n":"tremor_manager",
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
        if(sensor_info["e"][0]["n"] == "MeanFrequencyAcceleration"):
            wrist_freq = sensor_info["e"][0]["v"]
            self.structure["e"][0]["t"] = time.time()
            self.structure["e"][0]["v"] = 0
            if (wrist_freq >= 4) and (wrist_freq <= 9):
                self.structure["e"][0]["v"] = 1
                print ("Tremor situation at " + str(time.time()) + "s")

        print(str(self.structure))
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

    clientID = 'tremor_manager147852369'
    port = 1883
    broker = 'mqtt.eclipseprojects.io'
    wrist_topic = '/sensors/wrist_acc'
    telebot_topic = '/telebot/wrist_acc'
    thingspeak_topic = '/thingspeak/wrist_acc'

    #start of MQTT connection
    tm = tremor_management(clientID, port, broker, wrist_topic)
    telebot_sender = tremor_management(clientID, port, broker, telebot_topic)
    thingspeak_sender = tremor_management(clientID, port, broker, thingspeak_topic)
    tm.start()
    tm.subscriber()
    
    #telebot_sender.start()
    #thingspeak_sender.start()
    # Creation of the MQTT message to send to the actuators

    while True:
        time.sleep(5)
    #    time.sleep(5)
        telebot_sender.publisher(json.dumps(tm.structure))
        thingspeak_sender.publisher(json.dumps(tm.structure))

        
