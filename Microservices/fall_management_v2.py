# 1st. Read information from device connectors (waist accelerometer and pressure) via MQTT
# 2nd. Check if:
#   pressure is between 4.9-5.1 (pressure)
#   last stop peak 1.69-1.71 (waist)
# 3rd. If both conditions are detected, then a falling is happening
# 4th. Send the data to the statistics manager
# 5th. Send a message to the Telebot if a fall is detected

import time
import paho.mqtt.client as PahoMQTT
import json

class fall_management():
    
    def __init__ (self, patientID, port, broker, topic):

        self.clientID = str(patientID)
        self.port = port
        self.broker = broker
        self.topic = topic
        self._paho_mqtt = PahoMQTT.Client(self.clientID, True)
        self._paho_mqtt.on_connect = self.MyOnConnect
        self._paho_mqtt.on_message = self.MyOnMessage

        self.bn = "marta/ParkinsonHelper/" + self.clientID

        self.structure = {"bn": self.bn +"/fall_manager",
                "e":
                    [
                        {
                            "n":self.topic,
                            "u":"bool",
                            "t":"",
                            "v":"",
                        }
                    ]
        }

    def MyOnConnect(self, paho_mqtt, user_data, flags, rc):
            pass

    def MyOnMessage(self, paho_mqtt, user_data, msg):
        sensor_info = json.loads(msg.payload)

        if(sensor_info["e"][0]["n"] == "TimeLastPeak"):
            waist_freq = sensor_info["e"][0]["v"]
            self.structure["e"][0]["t"] = time.time()
            self.structure["e"][0]["v"] = 0
            if (waist_freq >= 1.69) and (waist_freq <= 1.71):
                self.structure["e"][0]["v"] = 1
                print ("Stop at " + str(time.time()) + "s")

        elif(sensor_info["e"][0]["n"] == "FeetPressure"):
            pressure = sensor_info["e"][0]["v"]
            self.structure["e"][0]["t"] = time.time()
            self.structure["e"][0]["v"] = 0
            if (pressure >= 4.9) and (pressure <= 5.1):
                self.structure["e"][0]["v"] = 1
                print ("Pressure lying at " + str(time.time()) + "s")
            
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
    waist_topic = '/sensors/waist_acc'
    pressure_topic = '/sensors/pressure'
    telebot_topic = '/telebot/wrist_acc'
    thingspeak_topic = '/thingspeak/wrist_acc'

    #start of MQTT connection
    waist_fm = fall_management(clientID, port, broker, waist_topic)
    pressure_fm = fall_management(clientID, port, broker, pressure_topic)
    telebot_sender = fall_management(clientID, port, broker, telebot_topic)
    thingspeak_sender = fall_management(clientID, port, broker, thingspeak_topic)

    waist_fm.start()
    
    while True:
        time.sleep(5)
        if (waist_fm.structure["e"][0]["v"] == 1) and (pressure_fm.structure["e"][0]["v"] == 1):
            fall_flag = 1
        else:
            fall_flag = 0

        msg = {"bn": waist_fm.bn +"/fall_manager",
                "e":
                    [
                        {
                            "n":"fall_manager",
                            "u":"bool",
                            "t":time.time(),
                            "v":fall_flag,
                        }
                    ]
        }
        # MQTT to communicate with telebot and statistics manager
        telebot_sender.publisher(json.dumps(msg))
        thingspeak_sender.publisher(json.dumps(msg))

    
