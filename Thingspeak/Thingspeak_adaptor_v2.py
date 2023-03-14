import json
import paho.mqtt.client as PahoMqtt
import time
import datetime
import threading
import requests
import cherrypy
from pathlib import Path
time_flag=1
loop_flag=1

def ts_publish(list,field,write_api):
    """Take a list of jsons and publish them via REST on ThingSpeak."""
    field_reading={'api_key':str(write_api),'field'+ str(field):list}
    url='https://api.thingspeak.com/update.json'
    header_f={'Content_type':'application/json'}
    request=requests.post(url,field_reading,header_f)
    request.close()

def publish_flag(cnt,field):
    write_api="3D509BA5PQ8SQ4EU"
    field_reading={'api_key':str(write_api),'field'+ str(field):cnt}
    url='https://api.thingspeak.com/update.json'
    header_f={'Content_type':'application/json'}
    request=requests.post(url,field_reading,header_f)
    request.close()
    
    

class Timer(threading.Thread):
    """15-second timer.
    It is used to prevent publishing on ThingSpeak too often.
    """

    def __init__(self, ThreadID, name):
        """Initialise thread widh ID and name."""
        threading.Thread.__init__(self)
        self.ThreadID = ThreadID
        self.name = name

    def run(self):
        """Run thread."""
        global time_flag
        while True:
            time_flag = 1  # Start timer.
            time.sleep(15)  # Wait 15 seconds.
            time_flag = 0  # Stop timer.
            time.sleep(1)  # 1-sec cooldown.

class PatientDatabase(threading.Thread):
    def __init__(self, ThreadID, name):
        """Initialise thread widh ID and name."""
        threading.Thread.__init__(self)
        self.ThreadID = ThreadID
        self.name = name

    def data(self):
        waist_acc=[]
        wrist_acc=[]
        pressure=[]
        self.write_api="3D509BA5PQ8SQ4EU"
    #filewrist="wrist_acc1.txt"
    #filewaist="waist_acc1.txt"
    #filepressure="pressure1.txt"
        flag=0
        time_data = 10
        time_d=0
        while flag==0:
            with open("C:/Users/LUCA/Desktop/POLI/ICT/IOT/IoT_Parkinson_Project/Sensori/Measures_MQTT/wrist_acc1.txt","r")as f:
                while True:
                    wrist=f.readline()
                    wrist_acc.append(wrist)
                    field=1
                    ts_publish(wrist_acc,field,self.write_api)
                    if not wrist:
                        break
            with open(file="C:/Users/LUCA/Desktop/POLI/ICT/IOT/IoT_Parkinson_Project/Sensori/Measures_MQTT/waist_acc1.txt")as f:
                while True:
                    waist=f.readline()
                    waist_acc.append(waist)
                    field=2
                    ts_publish(waist_acc,field,self.write_api)
                    if not waist:
                        break
            with open(file="C:/Users/LUCA/Desktop/POLI/ICT/IOT/IoT_Parkinson_Project/Sensori/Measures_MQTT/pressure1.txt")as f:
                while True:
                    press=f.readline()
                    pressure.append(press)
                    field=3
                    ts_publish(pressure,field,self.write_api)
                    if not press:
                        break
            time_d=time_d+1
            if time_d==time_data:
                flag=1


class MySubscriber():
    """MQTT subscriber."""

    def __init__(self, clientID, mqtt_port, broker_ip, topic):
        """Initialise MQTT client."""
        self.clientID = clientID
        self.topic = topic
        self.port=mqtt_port
        self.messageBroker = broker_ip
        self._paho_mqtt = PahoMqtt.Client(self.clientID,True)
        self._paho_mqtt.on_connect = self.my_on_connect
        self._paho_mqtt.on_message = self.my_on_message_received

    def start(self):
        """Start subscriber."""
        self._paho_mqtt.connect(self.messageBroker)
        self._paho_mqtt.loop_start()
        self._paho_mqtt.subscribe(self.topic, 2)
        print("Subscribed to the topic: " + self.topic)
    
    def stop(self):
        """Stop subscriber."""
        self._paho_mqtt.unsubscribe(self.topic)
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()

        # except:
        #     print("Invalid message type")
        #     pass

    def my_on_connect(self, client, userdata, flags, rc):
        print("S - Connected to %s - Result code: %d" % (self.messageBroker,
                                                         rc))

    def my_on_message_received(self, client, userdata, msg):
        """Define custom on_message function."""
        # Decode received message 
        print("ciao")
        msg.payload = msg.payload.decode()
        message = json.loads(msg.payload)
        print(message)
        Patient = message['bn']

        
        cont_tremor=0
        # Update values in the database.
        for item in message["e"]:
            if item["n"] == 'alive':
                pass
            else:
                topic = item["n"]
                if topic == "tremor_manager":
                    value = item["v"]
                    if value == 1:
                        cont_tremor= cont_tremor+1
                        field=4
                        publish_flag(cont_tremor,field)

if __name__== "__main__":
    
    thread1=PatientDatabase(1, "PatientDatabase")
    thread1.start()
    clientID="ThingSpeak1478523691"
    topic = "/actuators/statistics"
    broker_ip='mqtt.eclipseprojects.io'
    mqtt_port=1883
    my=MySubscriber(clientID, mqtt_port, broker_ip, topic)
    my.start()
    while True:
        pass
    my.stop()
    thread2 = Timer(2, "Timer")
    thread2.start()