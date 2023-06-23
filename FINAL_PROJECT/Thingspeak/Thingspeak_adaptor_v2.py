
"""ThingSpeak adaptor.
It collects SenML-formatted json files from sensors via MQTT and publish them
on ThingSpeak every 15 seconds.
"""
import json
import paho.mqtt.client as PahoMQTT
import time
import datetime
import threading
import requests
import cherrypy
from pathlib import Path

P = Path(__file__).parent.absolute()
loop_flag = 1
time_flag = 1
#CHERRY_CONF = str(P / "cherrypyconf")
FILE = P / "conf.json"


# Functions
def data_publish(list, url):
    """Take a list of jsons and publish them via REST on ThingSpeak using post method."""
    for item in list:
        print("Publishing:")
        print(json.dumps(item))
        requests.post(url, data=item)


def read_file(filename):
    """Read json file to get catalogURL, port, topic and ThingSpeak URL."""
    with open(filename, "r") as f:
        data = json.load(f)
        url = data["ip"]
        topic = data["baseTopic"]
        port = data["port"]
        ts_url = data["thingspeakURL"]
        return url, port, topic, ts_url


def broker_info(url, port):
    broker_ip = "test.mosquitto.org"
    mqtt_port = 1883
    return broker_ip, mqtt_port


# Classes
class Timer(threading.Thread):
    """15-second timer.
    It is used to prevent publishing on ThingSpeak too often.
    """

    def __init__(self, ThreadID, name):
        """Initialise thread widh ID and name."""
        threading.Thread.__init__(self)
        self.ThreadID = ThreadID
        self.name = self.name

    def run(self):
        """Run thread."""
        global time_flag
        while True:
            time_flag = 1  # Start timer.
            time.sleep(15)  # Wait 15 seconds.
            time_flag = 0  # Stop timer.
            time.sleep(1)  # 1-sec cooldown.

# Threads
class SendData(threading.Thread):
    """ Data are collected for 15 seconds and then published.
    So we call the class MySubscriber and the methods
    """

    def __init__(self, ThreadID, name):
        """Initialise thread widh ID and name."""
        threading.Thread.__init__(self)
        self.ThreadID = ThreadID
        self.name = name
        (self.url, self.port, self.topic, self.ts_url) = read_file(FILE)
        (self.broker_ip, mqtt_port) = broker_info(self.url, self.port)
        self.mqtt_port = int(mqtt_port)

    def run(self):
        """Run thread."""
        global time_flag

        # Start subscriber.
        sub = MySubscriber("Thingspeak", self.topic, self.broker_ip)
        sub.start()

        while True:

            while time_flag == 0: 
                """# wait untill the time_flag becomes 1, so every 15 sec except the first cycle that we have
                global time_flag = 1"""
                time.sleep(.1)

            # waiting for the connection. when the system is connected to the broker, loop_flag becomes false
            while loop_flag:
                print("Waiting for connection...")
                time.sleep(.01)

            # Collecting data for 15 seconds. it stops when the time_flag becomes 0 (so after 15 sec)
            while time_flag == 1:
                time.sleep(.1)

            # Publish json data on thingspeak. Different patient=different channel
            data_publish(sub.send_data(), self.ts_url)


class Database(object):
    """Manage a database with data from sensors.
    Create the database, collect data for 15 sec and then publish the data on thingspeak in a json format.
    """

    def __init__(self):
        """Initialise database with an empty list."""
        self.list_ID = []
        self.list_data = []

        # Current time in ISO format
        now = time.time()
        self.created_at = datetime.datetime.utcfromtimestamp(now).isoformat()

    def create(self, patientID, write_api):
        """Create a new patient given the patientID and api_key.
        Check if there is a patient with the same id, if not create a new one.
        """
        if patientID in self.list_ID:
            pass  # The patient is already in the database.

        else:
            
            self.list_data.append(self.create_new(write_api))
            self.list_ID.append(patientID)

    def create_new(self, write_api):
        """Create a new json with writeAPI and timestamp (ISO 8601).
        create a new channel (patient)"""
        data = {
            "write_api": write_api,
            "created_at": self.created_at,
        }
        return data

    def update_data(self, write_api, fieldID, value):
        """Append or update field and value to the current json."""
        print("Collected: field%s=%s (%s)" % (str(fieldID), value, write_api))
        up = {
                "field" + str(fieldID): value,
             }

        cnt = 0

        for data in self.list_data:
            if data["write_api"] == write_api:
                self.list_data[cnt].update(up)
            cnt += 1 

    def reset(self):
        """Reset lists and time."""
        self.list_ID = []
        self.list_data = []
        now = time.time()
        self.created_at = datetime.datetime.utcfromtimestamp(now).isoformat()


class MySubscriber(object):
    """MQTT subscriber."""

    def __init__(self, clientID, topic, serverIP):
        """Initialise MQTT client."""
        self.clientID = clientID
        self.topic = topic
        self.messageBroker = serverIP
        self._paho_mqtt = PahoMQTT.Client(clientID, False)
        self._paho_mqtt.on_connect = self.my_on_connect
        self._paho_mqtt.on_message = self.my_on_message_received
        self.cont_tremor=0
        self.cont_fall=0
        self.cont_freezing=0
        self.db = Database()

    def start(self):
        """Start subscriber."""
        self._paho_mqtt.connect(self.messageBroker, 1883)
        self._paho_mqtt.loop_start()
        self._paho_mqtt.subscribe(self.topic, 2)

    def stop(self):
        """Stop subscriber."""
        self._paho_mqtt.unsubscribe(self.topic)
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()

    def my_on_connect(self, client, userdata, flags, rc):
        
        global loop_flag
        print("S - Connected to %s - Result code: %d" % (self.messageBroker,
                                                         rc))
        loop_flag = 0 #become 0 because the system is connected

    def send_data(self):
        """Send data and then reset lists."""
        data = self.db.list_data
        self.db.reset()
        return data

    def my_on_message_received(self, client, userdata, msg):
        """Define custom on_message function."""
        # Read conf.json file
        (self.url, self.port, self.topic, self.ts_url) = read_file(FILE)

        # Decode received message and find devID and patient
        message = json.loads(msg.payload.decode("utf-8"))
        print(message)
        devID = message['bn']
        devID = devID.split('/')
        
        patientID=devID[0]
        # Ask catalog the thingspeakID for that specific patientID.

        #string = "http://" + self.url + ":" + self.port + "/info/" + patientID
        #info = json.loads(requests.get(string).text)
        #thingspeakID = info['thingspeakID']

        # Ask catalog the APIs for that ThingSpeak ID.

        #string = ("http://" + self.url + ":" + self.port +  str(thingspeakID))
        #info = json.loads(requests.get(string).text)
        #write_api = info["writeAPI"]

        write_api = "3D509BA5PQ8SQ4EU"

        # Update values in the database.
        self.db.create(patientID, str(write_api))

        for i in message["e"]:
            if i["measureType"] == 'alive':
                pass
            else:
                topic = i["measureType"]
                if topic == "tremor_manager":
                    value = i["value"]
                    if value == 1:
                        self.cont_tremor += 1
                        values=self.cont_tremor
                        field = 4
                        self.db.update_data(str(write_api), field, values)
                        
                elif topic == "fall_manager":
                    value = i["value"]
                    if value == 1:
                        self.cont_fall += 1
                        values=self.cont_fall
                        field = 5
                        self.db.update_data(str(write_api), field, values)
                        
                elif topic == "freezing_manager":
                    value = i["value"]
                    if value == 1:
                        self.cont_freezing += 1
                        values=self.cont_freezing
                        field = 6
                        self.db.update_data(str(write_api), field, values)
                        
                elif topic == "WaistAccStats":
                    value = float(i["value"])
                    print(value)
                    #field=1
                    #std =float(i["value"]["std"])
                    #values=[mean,std]
                    values=value.mean()
                    field=2
                    self.db.update_data(str(write_api), field, values)
                    
                elif topic == "WristAccStats":
                    value = float(i["value"])
                    print(value)
                    #std =float(i["value"]["std"])
                    #fieldM=7
                    #values=[mean,std]
                    values=value.mean()
                    field = 8
                    self.db.update_data(str(write_api), field, values)
                    
                elif topic == "FeetPressureStats":
                    value = float(i["value"])
                    print(value)
                    values=value.mean()
                    field=3
                    self.db.update_data(str(write_api), field, values)
                    #std =float(i["value"]["std"])
                    #values=[mean,std]
                    #fieldS = 9  
                    
                    
                #self.db.update_data(str(write_api), field, values)






if __name__ == "__main__":
    thread1 = SendData(1, "SendData")
    thread1.start()
    thread2 = Timer(2, "Timer")
    thread2.start()
    #thread3 = CherryThread(3, "CherryServer")
    #thread3.start()
