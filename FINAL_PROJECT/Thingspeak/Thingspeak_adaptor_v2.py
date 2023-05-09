import json
import paho.mqtt.client as PahoMqtt
import time
import datetime
import threading
import requests
import cherrypy
from pathlib import Path
P = Path(__file__).parent.absolute()
loop_flag = 1
time_flag = 1
CHERRY_CONF = str(P / "cherrypyconfing")
FILE = P / "conf.json"

def ts_publish(list,field,write_api,ts_url):
    """Take a list of jsons and publish them via REST on ThingSpeak."""
    field_reading={'api_key':str(write_api),'field'+ str(field):list}
    ts_url
    header_f={'Content_type':'application/json'}
    request=requests.post(ts_url,field_reading,header_f)
    request.close()

def publish_flag(cnt,field,ts_url,write_api):
    field_reading={'api_key':str(write_api),'field'+ str(field):cnt}
    header_f={'Content_type':'application/json'}
    request=requests.post(ts_url,field_reading,header_f)
    request.close()

def read_file(filename):
    """Read json file to get catalogURL, port, topic and ThingSpeak URL."""
    with open(filename, "r") as f:
        data = json.loads(f.read())
        url = data["ip"]
        topic = data["baseTopic"]
        port = data["port"]
        ts_url = data["thingspeakURL"]
        return (url, port, topic, ts_url)

def Broker(url,port):
    string="http://"+url+":"+port+"/broker"
    broker=requests.get(string)
    broker_ip=json.loads(broker.text)["IP"]
    mqtt_port=json.loads(broker.text)["mqtt_port"]
    return(broker_ip,mqtt_port)
    

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


class MySubscriber(object):
    """MQTT subscriber."""

    def __init__(self, clientID, topic, broker_ip):
        """Initialise MQTT client."""
        self.clientID = clientID
        self.topic = topic
        self.messageBroker = broker_ip
        self._paho_mqtt = PahoMqtt.Client(self.clientID,False)
        self._paho_mqtt.on_connect = self.my_on_connect
        self._paho_mqtt.on_message = self.my_on_message_received

    def start(self):
        """Start subscriber."""
        self._paho_mqtt.connect(self.messageBroker,1883)
        self._paho_mqtt.loop_start()
        self._paho_mqtt.subscribe(self.topic, 2)
        print("Subscribed to the topic: " + self.topic)
    
    def stop(self):
        """Stop subscriber."""
        self._paho_mqtt.unsubscribe(self.topic)
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()

    def my_on_connect(self, rc,clientID, topic, broker_ip):
        #print("S - Connected to  - Result code:" (self.messageBroker,rc))
        pass
    def send_data(self):
        """Take data from database, empty the database, return data."""
        data = self.db.list_data
        self.db.reset()
        return data


    def my_on_message_received(self, msg,clientID, broker_ip):
        
        (self.url, self.port, self.topic, self.ts_url) = read_file(FILE)
        #read the message coming from the message_broker and upload data depending on the topic 
        msg.payload = msg.payload.decode("utf-8")
        message = json.loads(msg.payload)
        print(message)
        Patient = message['bn']
        print(Patient)
        # Ask catalog for patientID from patient
        #string = "http://" + self.url + ":" + self.port + "/info/" + Patient
        #info_d = json.loads(requests.get(string).text)
        #patientID = info_d["patientID"]

        #thingspeakID="2055330"
        write_api="3D509BA5PQ8SQ4EU"
    
        cont_tremor=0
        cont_fall=0
        cont_freezing=0
        # Update values in the database.
        for i in message["e"]:
            if i["n"] == 'alive':
                pass
            else:
                topic = i["n"]
                if topic == "tremor_manager":
                    value = i["v"]
                    if value == 1:
                        cont_tremor= cont_tremor+1
                        field=4
                        publish_flag(cont_tremor,field,self.ts_url,write_api)
                elif topic == "fall_manager":
                    value = i["v"]
                    if value == 1:
                        cont_fall= cont_fall+1
                        field=5
                        publish_flag(cont_fall,field,self.ts_url,write_api)
                elif topic == "freezing_manager":
                    value = i["v"]
                    if value == 1:
                        cont_freezing= cont_freezing+1
                        field=6
                        publish_flag(cont_freezing,field,self.ts_url,write_api)
                elif topic=="WaistAccStats":
                    value=i["v"]
                    field=1
                    ts_publish(value,field,write_api,self.ts_url)
                elif topic=="WristAccStats":
                    value=i["v"]
                    field=2
                    ts_publish(value,field,write_api,self.ts_url)
                elif topic=="FeetPressureStats":
                    value=i["v"]
                    field=3
                    ts_publish(value,field,write_api,self.ts_url)


class Data(threading.Thread):

    def __init__(self, ThreadID,name):
        threading.Thread.__init__(self)
        self.ThreadID=ThreadID
        self.name=name
        (self.url, self.port, self.topic, self.ts_url) = read_file(FILE)
        (self.broker_ip,self.mqtt_port) = Broker(self.url,self.port)

    def run(self):
        sub=MySubscriber("Thingspeak",self.topic,self.broker_ip)
        sub.start()  

#restfull part to take data from thingspeak

class CherryThread(threading.Thread):
    """Thread to run CherryPy webserver."""

    def __init__(self, ThreadID, name):
        """Initialise thread widh ID and name."""
        threading.Thread.__init__(self)
        self.ThreadID = ThreadID
        self.name = name
        (self.url, self.port, self.topic, self.ts_url) = read_file(FILE)
        (self.broker_ip, mqtt_port) = Broker(self.url, self.port)
        self.mqtt_port = int(mqtt_port)

    def run(self):
        """Run thread."""
        try:
            cherrypy.tree.mount(WebServer(), '/', config=CHERRY_CONF)
            cherrypy.config.update(CHERRY_CONF)
            cherrypy.engine.start()
            cherrypy.engine.block()
        except KeyboardInterrupt:
            print("Stopping the engine")
            return

class WebServer():
    """CherryPy webserver.
    It is used to take data from thingspeak and send them to the control strategies.
    Ex: we want to know the statistics of patient 1 of latest 5 hours.
    Adaptor takes info from thingspeak and send back to strategies a json.
    """

    exposed = True

    @cherrypy.tools.json_out()
    def GET(self, *uri, **params):
        i=1 #to be implemented 

def main ():
    thread1 = Data(1, "Data")
    thread1.start()
    thread2 = Timer(2, "Timer")
    thread2.start()
    #therad3= CherryThread(3, "Cherrypy")
    #therad3.start()

if __name__== "__main__":
    
    main()