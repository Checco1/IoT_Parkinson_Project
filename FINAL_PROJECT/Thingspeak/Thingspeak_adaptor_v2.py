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
import ast
from pathlib import Path

P = Path(__file__).parent.absolute()
loop_flag = 1
time_flag = 1
FILE = P / "conf.json"


# Functions
def data_publish(list, url):
    """Take a list of jsons and publish them via REST on ThingSpeak using post method."""
    #url=url + f"?api_key={write_api}"
    for item in list:
        print("Publishing:")
        print(json.dumps(item))
        bulk_resp = requests.post(url, data=item)
        while( bulk_resp.status_code != 202 ):
            time.sleep(1)
            bulk_resp = requests.post(url, data=item)


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
    """broker_ip = "test.mosquitto.org"
    mqtt_port = 1883"""
    string = "http://"+url+":"+port+"/broker"
    broker=requests.get(string)
    broker_ip=json.loads(broker.text)["IP"]
    mqtt_port=json.loads(broker.text)["mqtt_port"]
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

class Database(object):
    """Manage a database with data from sensors.
    Create the database, collect data for 15 sec and then publish the data on thingspeak in a json format.
    """

    def __init__(self):
        """Initialise database with an empty list."""
        self.list_ID = []
        self.list_bulk = []

        # Current time in ISO format
        now = time.time()
        self.created_at = datetime.datetime.utcfromtimestamp(now).isoformat()

    def create(self, patientID, write_api):
        """Create a new patient given the patientID and api_key.
        Check if there is a patient with the same id, if not create a new one.
        """
        for patient in self.list_ID:
            if patient["patientID"] == patientID:
                return # The patient is already in the database 

        self.list_bulk.append(self.create_new(write_api))
        self.list_ID.append({"patientID":patientID, "Write_Api" : write_api, "Waist_key" : False, "Wirst_key" : False, "Pressure_key" : False})

    def create_new(self, write_api):
        """Create a new json with writeAPI and timestamp (ISO 8601).
        create a new channel (patient)"""
        bulk_msg = {
            "write_api_key" : str(write_api),
            "updates": []
        }
        return bulk_msg

    def update_data(self, write_api, fieldID, msg):
        """Append or update field and value to the current json."""
        
        cnt = 0

        for bulk in self.list_bulk:
            if bulk["write_api_key"] == write_api:
                break
        
        for data in json.loads(msg["value"]):
            if bulk != []:  
                if len(bulk["updates"]) == 15:
                    bulk["updates"][cnt].update({fieldID:data})
                    cnt += 1
                    
                else:
                    timestamp = json.loads(msg["valueTimestamps"])[cnt]
                    t = datetime.datetime.utcfromtimestamp(timestamp).isoformat()
                    bulk["updates"].append({"created_at" : t, "field1" : "", "field2" : "", "field3" : ""})
                    bulk["updates"][cnt][fieldID] = data
                    cnt += 1

            else:
                timestamp = json.loads(msg["valueTimestamps"])[cnt]
                t = datetime.datetime.utcfromtimestamp(timestamp).isoformat()
                bulk["updates"].append({"created_at" : t, "field1" : "", "field2" : "", "field3" : ""})
                bulk["updates"][cnt][fieldID] = data
                cnt += 1

    def update_key(self, PatientID, fieldID):

        for patient in self.list_ID:
            if patient["patientID"] == PatientID:
                break
        
        patient[fieldID] = True

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
        self.key_waist=0
        self.key_wirst=0
        self.key_pressure=0
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
        print("S - Connected to %s - Result code: %d" % (self.messageBroker, rc))
        loop_flag = 0 #become 0 because the system is connected

    def send_data(self):
        """Send data and then reset lists."""
        data = self.db.list_data
        
        print(data)
        
        self.db.reset()
        return data

    def my_on_message_received(self, client, userdata, msg):
        """Define custom on_message function."""
        # Read conf.json file
        (self.url, self.port, self.topic, self.ts_url) = read_file(FILE)
        # Decode received message and find devID and patient
        message = json.loads(msg.payload.decode("utf-8"))
        #print(message)
        devID = message['bn']
        devID = devID.split('/')
        
        patientID=devID[0]

            # Update values in the database.
            #self.db.create(patientID, str(write_api))
                # Ask catalog the write_api of the thingspeak channel for that specific patientID.
        string = "http://" + self.url + ":" + self.port + "/info/" + patientID
        info = json.loads(requests.get(string).text)
        if info != -1:
            for service in info["Statistic_services"]:
                if service["ServiceName"] == "ThingSpeak":
                    channel_id = service["Channel_ID"]
                    write_api = service["WriteApi"]
                    read_api = service["ReadApi"]
                    local_url = service["URL"]
                    break

        i = message["e"][0]
        
        MeasureType = i["measureType"]
        if MeasureType == "fall_manager":
            value = i["value"]
            if value == 1:

                req = "https://api.thingspeak.com/channels/" + str(channel_id) + "/fields/" + "4" + ".json?api_key=" + read_api + "&results=8000"
                resp = json.loads(requests.get(req).text)
                total_fall = 1

                if resp["feeds"] != []:
                    for entry in resp["feeds"]:
                        if entry["field4"] != None:
                            total_fall += 1

                now = time.time()
                created_at = datetime.datetime.utcfromtimestamp(now).isoformat()

                msg = {
                    "api_key": write_api, 
                    "created_at": created_at, 
                    "field4": total_fall
                }

                fall_r = requests.post(self.ts_url, msg)
                while (fall_r.status_code != 200):
                    time.sleep(1)
                    fall_r = requests.post(self.ts_url, msg)
                print(f"Fall Occurred and sended on ThingSpeak!, {write_api}")

        elif MeasureType == "tremor_manager":
            value = i["value"]
            if value == 1:

                req = "https://api.thingspeak.com/channels/" + str(channel_id) + "/fields/" + "5" + ".json?api_key=" + read_api + "&results=8000"
                resp = json.loads(requests.get(req).text)
                total_tremor = 1

                if resp["feeds"] != []:
                    for entry in resp["feeds"]:
                        if entry["field5"] != None: 
                            total_tremor += 1

                now = time.time()
                created_at = datetime.datetime.utcfromtimestamp(now).isoformat()

                msg = {
                    "api_key": write_api, 
                    "created_at": created_at, 
                    "field5": total_tremor
                }

                tremor_r = requests.post(self.ts_url, msg)
                while(tremor_r.status_code != 200):
                    time.sleep(1)
                    tremor_r = requests.post(self.ts_url, msg)
                print(f"Tremor Occurred and sended on ThingSpeak! {write_api}")

        elif MeasureType == "freezing_manager":
            value = i["value"]
            if value == 1:

                req = "https://api.thingspeak.com/channels/" + str(channel_id) + "/fields/" + "6" + ".json?api_key=" + read_api + "&results=8000"
                resp = json.loads(requests.get(req).text)
                total_freezing = 1

                if resp["feeds"] != []:
                    for entry in resp["feeds"]:
                        if entry["field6"] != None: 
                            total_freezing += 1

                now = time.time()
                created_at = datetime.datetime.utcfromtimestamp(now).isoformat()

                msg = {
                    "api_key": write_api, 
                    "created_at": created_at, 
                    "field6": total_freezing
                }

                frezee_r = requests.post(self.ts_url, msg)
                while(frezee_r.status_code != 200):
                    time.sleep(1)
                    frezee_r = requests.post(self.ts_url, msg)
                print(f"Freezing Occurred and sended on ThingSpeak! {write_api}")
                    
        elif MeasureType == "WaistAccStats":
            field = "field1"
            self.db.create(patientID, write_api)
            self.db.update_data(str(write_api), field, i)
            self.db.update_key(patientID,"Waist_key")
                        
        elif MeasureType == "WristAccStats":
            field = "field2"
            self.db.create(patientID, write_api)
            self.db.update_data(str(write_api), field, i)
            self.db.update_key(patientID,"Wirst_key")
                
        elif MeasureType == "PressureStats":
            field = "field3"
            self.db.create(patientID, write_api)
            self.db.update_data(str(write_api), field, i)
            self.db.update_key(patientID,"Pressure_key")

        for person in self.db.list_ID:
            if person["Waist_key"] == True & person["Wirst_key"] == True & person["Pressure_key"] == True:
                person["Waist_key"] = False
                person["Wirst_key"] = False
                person["Pressure_key"] = False
                for data in self.db.list_bulk:
                    if person["Write_Api"] == data["write_api_key"]:
                        string = "http://" + self.url + ":" + self.port + "/info/" + patientID
                        info = json.loads(requests.get(string).text)
                        for service in info["Statistic_services"]:
                            if service["ServiceName"] == "ThingSpeak":
                                channel_id = service["Channel_ID"]
                        ts = f"https://api.thingspeak.com/channels/{channel_id}/bulk_update.json"
                        da = json.dumps(data)
                        #print(ts)
                        #print(da)
                        headers = {'Content-Type': 'application/json'}
                        res = requests.post(ts,da,headers=headers)
                        while(res.status_code != 202):
                            time.sleep(1)
                            res = requests.post(ts,da,headers=headers)
                        print("Bulk Update OK!")
                        data["updates"].clear()    

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
        sub = MySubscriber("J", self.topic, self.broker_ip)
        sub.start()

        while True:
            time.sleep(1)

            #while time_flag == 0: 
            """# wait untill the time_flag becomes 1, so every 15 sec except the first cycle that we have
                global time_flag = 1"""
            #    time.sleep(0.1)

            # waiting for the connection. when the system is connected to the broker, loop_flag becomes false
            #while loop_flag:
                #print("Waiting for connection...")
                #time.sleep(0.1)

            # Collecting data for 15 seconds. it stops when the time_flag becomes 0 (so after 15 sec)
           # while time_flag == 1:
            #    time.sleep(0.1)

            # Publish json data on thingspeak. Different patient=different channel
            #print(self.ts_url)
            #data_publish(sub.send_data(), self.ts_url)
        

if __name__ == "__main__":

    """api_key="5LWQ3IHY3DY8TILH"
    url=f"https://api.thingspeak.com/channels.json"
    data={
        "api_key":api_key,
        "field1":"waistStats",
        "field2":"wristStats",
        "field3":"pressureStats",
        "field4":"fall_episodes",
        "field5":"tremor_episode",
        "field6":"freezing_episode"
    }
    response=requests.post(url,json=data)
    if response.status_code==200:
        new_channel=response.json()
        channel_id=new_channel["id"]
        print("New channel added with id: ",channel_id)
    else:
        print("Error in the channel creation")
    url=f"https://api.thingspeak.com/channels/{channel_id}.json"
    params={"api_key":api_key}
    response=requests.get(url,params=params)
    
    channel_info=response.json()
    write_api=channel_info["api_keys"][0]["api_key"]
    read_api=channel_info["api_keys"][1]["api_key"]
    print("Write api: ",write_api)
    print("Read api: ",read_api) """

    thread1 = SendData(1, "SendData")
    thread1.start()
    #thread2 = Timer(2, "Timer")
    #thread2.start()

    """ read values of field od the patient
    read_api="E7JRP689C2U0W11U"
    channelID=2202640
    fieldID=4
    url=f"https://api.thingspeak.com/channels/{channelID}/fields/{fieldID}.json?api_key={read_api}"# gett alla values of the field of the last day
    start_date="2023-06-27"
    end_date="2023-06-27"
    url=f"https://api.thingspeak.com/channels/{channelID}/fields/{fieldID}.json?api_key={read_api}&start={start_date}&end={end_date}"#get data of field of the day
    url=f"https://api.thingspeak.com/channels/{channelID}/fields/{fieldID}.json?api_key={read_api}&result=10" #get last 10 values
    #In the start day and end day, if you specify the hours, you'll get the values of the hours range  
    response=requests.get(url)
    data=response.json()
    feeds = data['feeds']
    
    
    values = [feed[f'field{fieldID}'] for feed in feeds]
    print(values)
    filtered_data = [x for x in values if x is not None ] #to create a list of value without values=None
    
    #print("DATA from field%s = ",(fieldID,data))"""