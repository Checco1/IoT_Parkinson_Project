import random
import time
import json
import paho.mqtt.client as PahoMQTT
## E' il publisher!!

class WristSimulator():

    def __init__(self,patientID, port, broker, topic):

        self.clientID = str(patientID)
        self.port = port
        self.broker = broker
        self.topic = topic
        self._paho_mqtt = PahoMQTT.Client(self.clientID, True)
        self._paho_mqtt.on_connect = self.MyOnConnect
        
        self.bn = "marta/ParkinsonHelper/"
        self.patientID=patientID
        self.sensorID = "wrist_acc"+str(patientID)

        self.structure = {"bn": self.bn+str(patientID)+"/wrist_acc"+str(patientID),
                "e":
                    [
                        {
                            "n":"MeanFrequencyAcceleration",
                            "u":"Hz",
                            "t":"",
                            "v":""
                        }
                    ]

        }
    # MQTT methods
    def start(self):
        self._paho_mqtt.connect(self.broker, self.port)
        self._paho_mqtt.loop_start()

    def publisher(self, msg):
        self._paho_mqtt.publish(self.topic, msg, 2)
        print("published: " + str(msg))

    def stop(self):
        self._paho_mqtt.unsubscribe(self.topic)
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()

    def MyOnConnect(self, paho_mqtt, user_data, flags, rc):
            print("connected " + self.topic)
    
    # Simulation methods
    def NormalWristGenerator(self): #for Freezing and Fall generation

        mean_frequency_acc = random.uniform(1,2) #no tremor --> no quick peaks --> low frequency

        self.structure["e"][0]["t"] = int(time.time())
        self.structure["e"][0]["v"] = float(mean_frequency_acc)

        return self.structure
  

    def TremorGenerator(self):

        mean_frequency_acc = random.uniform(4,9) #high frequency --> tremor episode

        self.structure["e"][0]["t"] = int(time.time())
        self.structure["e"][0]["v"] = float(mean_frequency_acc)

        return self.structure

    def Information(self):

        DeviceInf = {
	        "DeviceID" : self.sensorID,
	        "deviceName" : "Wrist Accelerometer "+str(self.patientID),
	        "measureType":"MeanFrequencyAcceleration",
            "availableServices":"MQTT",
            "servicedetails": "To be defined"
        }
        return DeviceInf

if __name__ == "__main__":
    clientID = 'wrist_acc124578963'
    port = 1883
    broker = 'mqtt.eclipseprojects.io'
    wrist_topic = '/sensors/wrist_acc'

    ws = WristSimulator(clientID, port, broker, wrist_topic)
    ws.start()
    for i in range(30):
        time.sleep(5)
        if i in range(3,5):
            state = ws.TremorGenerator()
            
        else:
            state = ws.NormalWristGenerator()

        ws.publisher(json.dumps(state))

    ws.stop()
