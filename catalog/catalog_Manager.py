import json
import cherrypy
import time
import requests
import threading
import paho.mqtt.client as PahoMQTT
from pathlib import Path


P = Path(__file__).parent.absolute()
SERVICE_CATALOG = P / 'service_catalog.json'
RESUORCE_CATALOG = P / 'resource_catalog.json'
PATIENT_CATALOG = P / '../FINAL_PROJECT/patient.json'
CHERRY_CONF = str(P / 'cherrypyconfig')
MAXDELAY = 30

class Catalog(object):
    def __init__(self):
        self.filename_service = SERVICE_CATALOG
        self.filename_resource = RESUORCE_CATALOG
        self.filename_patient = PATIENT_CATALOG
    
    def load_file(self):
        """Load service and resource parts of catalog.
        Load data (service, resource) from json files and get MQTT broker IP
        and MQTT broker port saved on service file.
        """
        loaded = 0
        while not loaded:
            try:
                with open(self.filename_service, "r") as fs:
                    self.service = json.loads(fs.read())
                with open(self.filename_resource, "r") as fd:
                    self.resource = json.loads(fd.read())
                with open(self.filename_patient, "r") as fp:
                    self.patient = json.loads(fp.read())    
                loaded = 1
            except Exception:
                print("Problem in loading catalogs, retrying...")
                time.sleep(.5)

        self.broker_ip = self.service["broker"]["IP"]
        self.mqtt_port = self.service["broker"]["mqtt_port"]

    def write_service(self):
        """Write data on service json file."""
        with open(self.filename_service, "w") as fs:
            json.dump(self.service, fs, ensure_ascii=False, indent=2)
            fs.write("\n")

    def write_resource(self):
        """Write data on resource json file."""
        with open(self.filename_resource, "w") as fd:
            json.dump(self.resource, fd, ensure_ascii=False, indent=2)
            fd.write("\n")

    def write_patient(self):
        """Write data on patient json file."""
        with open(self.filename_patient, "w") as fd:
            json.dump(self.patient, fd, ensure_ascii=False, indent=2)
            fd.write("\n")

    def add_patient(self, patient_json):
        # patient_json will be the body in the POST method
        # Look at the existing patient IDs.
        self.load_file()
        list_id = []

        for p in self.patient["patients_list"]:
            list_id.append(p["patientID"])

        # Generate a new patientID starting from 1 and taking the first free
        # number which is available.
        numID = 1
        new_id = "patient"+str(numID)

        while new_id in list_id:
            numID += 1
            new_id = "patient"+str(numID)

        patient_json["patientID"] = new_id
        print(patient_json)

        self.patient["patients_list"].append(patient_json)
        patient_res_json = {
            "patientID": patient_json["patientID"],
            "device_list": []
        }
        self.resource["patients_list"].append(patient_res_json)
        #self.write_service()
        self.write_patient()
        self.write_resource()

    def add_device(self, device_json, patient):
        """Add a new device in the service catalog.
        The new deviceID is auto-generated.
        """
        self.load_file()

        # Generate list of all deviceID
        #for p in self.patient["patients_list"]:
        #    for d in p["device_list"]:
        #        list_id.append(d["deviceID"])

        # Find specific patient device in service and resource jsons.
        for p in self.patient["patients_list"]:
            if p["patientID"] == patient:
                break

        for pres in self.resource["patients_list"]:
            if pres["patientID"] == patient:
                break

        p["device_list"].append(device_json)

        topic = device_json["Services"]
        topic = topic["topic"]

        device_res_json = {
            "deviceID": device_json["deviceID"],
            "topic": topic,
            "lastUpdate": time.time()
        }
        pres["device_list"].append(device_res_json)

        #self.write_service()
        self.write_patient()
        self.write_resource()

    def add_service(self, service_json , patID):
        """Add a new device in the service catalog.
        The new deviceID is auto-generated.
        """
        self.load_file()

        # Generate list of all deviceID
        #for p in self.patient["patients_list"]:
        #    for d in p["device_list"]:
        #        list_id.append(d["deviceID"])

        # Find specific patient device in service and resource jsons.
        for p in self.patient["patients_list"]:
            if p["patientID"] == patID:
                break
        #self.service[""].append(service_json)
        p["Statistic_services"].append(service_json)
        self.patient["patients_list"].append(p)

        #self.write_service()
        self.write_patient()

    def info(self, ID):
        """Return all information about a patient/device" given an ID."""
        self.load_file()
        for p in self.patient["patients_list"]:
            if p["patientID"] == ID:
                info = {"patientID": ID, "name": p["patientName"],"devices": p["device_list"]}
                return info

            for d in p["device_list"]:
                if d["deviceID"] == ID:
                    info = {"patientID": p["patientID"], "deviceID": ID,
                            "name": p["patientName"], "measureType":d["measureType"],
                            "unit":d[ "unit"], "Services":d["Services"]}
                    return info

        return -1

    def update_device(self, patientID, deviceID, topic):
        """Update timestamp of a device.
        Update timestamp or insert it again in the resource catalog if it has
        expired.
        """
        data = {'deviceID': deviceID, 'topic': topic, 'lastUpdate': time.time()}
        self.load_file()

        for p in self.resource["patients_list"]:
            if p['patientID'] == patientID:
                break

        found = 0
        for d in p['device_list']:
            if d['deviceID'] == deviceID:
                found = 1
                print("Updating %s timestamp." % deviceID)
                d['topic'] = topic
                d['lastUpdate'] = time.time()    

        if not found:  # Insert again the device
        # But first check if device is allowed from the static catalog.
            allowed = 0
            for p2 in self.patient["patients_list"]:
                if p2['patientID'] == patientID:
                    break
                
            for d2 in p2['device_list']:
                if d2['deviceID'] == deviceID:  # In Patient JSON
                    allowed = 1
                    print("%s reconnected!" % deviceID)
                    p['device_list'].append(data)  # In Resource JSON

            if not allowed:
                print("Device %s wants to be updated but it seems to be not present in the catalog, please check." % deviceID)

        self.write_resource()
    
    def remove_old_device(self):
        """Remove old devices whose timestamp is expired.
        Check all the devices whose timestamps are old and remove them from
        the resource catalog.
        """
        self.load_file()

        for p in self.resource["patients_list"]:
            removable = []
            for counter, d in enumerate(p['device_list']):
                #print(counter, d)
                if time.time() - d['lastUpdate'] > MAXDELAY:
                    print("Removing... %s" % (d['deviceID']))
                    removable.append(counter)
            for index in sorted(removable, reverse=True):
                    #print (p['device_list'][index])
                    del p['device_list'][index]

        #print(self.resource)
        self.write_resource()

class Webserver(object):
    """CherryPy webserver."""

    exposed = True

    @cherrypy.tools.json_out()
    def GET(self, *uri, **params):
        """Define GET HTTP method for RESTful webserver."""
        cat = Catalog()
        cat.load_file()

        # Get broker info (url, port).
        if uri[0] == 'broker':
            return cat.service["broker"]

        if uri[0] == 'ts':
            return cat.service["thingspeak"]

        # Get Resource catalog json.
        if uri[0] == 'resource':
            return cat.resource

        # Get Service catalog json.
        if uri[0] == 'service':
            return cat.patient["Service_list"]
        
        # Get Patients catolog json
        if uri[0] == 'patient':
            return cat.patient

        # Get all information about a patient/device.
        if uri[0] == 'info':
            ID = uri[1]
            return cat.info(ID)

        # Get reserved information (telegram token or ThingSpeak channel APIs).
        #if uri[0] == 'api':
        #    if uri[1] == 'telegramtoken':
        #        return cat.get_token(APIFILE)
        #
        #    if uri[1] == 'tschannel':
        #        return cat.get_ts_api(APIFILE, uri[2])

    @cherrypy.tools.json_out()
    def POST(self, *uri, **params):
        """Define POST HTTP method for RESTful webserver."""
        # Add new patient.
        if uri[0] == 'addp':
            body = json.loads(cherrypy.request.body.read())  # Read body data
            cat = Catalog()
            print(json.dumps(body))
            cat.add_patient(body)
            return 200
        
        # Add new device.
        if uri[0] == 'addd':
            body = json.loads(cherrypy.request.body.read())  # Read body data
            cat = Catalog()
            print(json.dumps(body))
            cat.add_device(body, uri[1])
            return 200
        
        if uri[0] == 'adds':
            body = json.loads(cherrypy.request.body.read())  # Read body data
            cat = Catalog()
            print(json.dumps(body))
            cat.add_service(body, uri[1])
            return 200

       # if uri[0] == 'update':
       #     if uri[1] == 'user':
       #         body = json.loads(cherrypy.request.body.read())  # Read body
       #         cat = Catalog(JSON_STATIC, JSON_DYNAMIC)
       #         cat.update_user(body["name"], body["chat_id"])

class MySubscriber:
    """MQTT subscriber.
    It subscribes to all topics in order to receive alive messages from sensors
    and update their timestams in the dynamic part of the catalog.
    """

    def __init__(self, clientID, topic, serverIP):
        """Initialise MQTT client."""
        self.clientID = clientID
        self.topic = topic
        self.messageBroker = serverIP
        self._paho_mqtt = PahoMQTT.Client(clientID, False)
        self._paho_mqtt.on_connect = self.my_on_connect
        self._paho_mqtt.on_message = self.my_on_message_received
        self.url = "127.0.0.1"
        self.port = "8080"
        self.smart_topic = ""

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
        """Define custom on_connect function."""
        print("Connected to %s - Result code: %d" % (self.messageBroker, rc))
        self.loop_flag = 0

    def my_on_message_received(self, client, userdata, msg):
        """Define custom on_message function.
        Receives json messages from other devices and get info to update
        old timestamps or insert expired devices.
        """
        msg.payload = msg.payload.decode("utf-8")
        message = json.loads(msg.payload)
        catalog = Catalog()
        devID = message['bn']
        devID = devID.split('/')
        print(message)
        print("\n")
        try:
            for e in message['e']:
                if e['timeStamp'] > 0:
                    string = ('http://' + self.url + ':' + self.port +
                              '/info/' + devID[3])
                    info = json.loads(requests.get(string).text)
                    patientID = devID[1]
                    deviceID = info["deviceID"]
                    for serv in info['Services']:
                        topic = serv['topic']
                    
                    catalog.update_device(patientID, deviceID, topic)
        except Exception:
            pass

# Threads
class First(threading.Thread):
    """Thread to run CherryPy webserver."""

    def __init__(self, ThreadID, name):
        """Initialise thread widh ID and name."""
        threading.Thread.__init__(self)
        self.ThreadID = ThreadID
        self.name = name

    def run(self):
        """Run thread."""
        try:
            cherrypy.tree.mount(Webserver(), '/', config=CHERRY_CONF)
            cherrypy.config.update(CHERRY_CONF)
            cherrypy.engine.start()
            cherrypy.engine.block()

        except KeyboardInterrupt:
            print("Stopping the engine")
            return

class Second(threading.Thread):
    """MQTT Thread.
    Subscribe to MQTT in order to update timestamps of sensors in the dynamic
    part of the catalog.
    """

    def __init__(self, ThreadID, name):
        """Initialise thread widh ID and name."""
        threading.Thread.__init__(self)
        self.ThreadID = ThreadID
        self.name = name

    def run(self):
        """Run thread."""
        cat = Catalog()
        cat.load_file()
        broker_ip = cat.broker_ip
        topic = "ParkinsonHelper/#"
        sub = MySubscriber("Sub1", topic, broker_ip)
        sub.loop_flag = 1
        sub.start()

        while sub.loop_flag:
            print("Waiting for connection...")
            time.sleep(1)

        while True:
            time.sleep(1)

        sub.stop()

class Third(threading.Thread):
    """Old device remover thread.
    Remove old devices which do not send alive messages anymore.
    Devices are removed every five minutes.
    """

    def __init__(self, ThreadID, name):
        """Initialise thread widh ID and name."""
        threading.Thread.__init__(self)
        self.ThreadID = ThreadID
        self.name = self.name

    def run(self):
        """Run thread."""
        time.sleep(MAXDELAY+1)
        while True:
            cat = Catalog()
            cat.remove_old_device()
            time.sleep(MAXDELAY+1)

#Main

def main():
    """Start all threads."""
    thread1 = First(1, "CherryPy")
    thread2 = Second(2, "Updater")
    thread3 = Third(3, "Remover")

    print("> Starting CherryPy...")
    thread1.start()

    time.sleep(1)
    print("\n> Starting MQTT device updater...")
    thread2.start()

    time.sleep(1)
    print("\n> Starting remover...\nDelete old devices every %d seconds."
          % MAXDELAY)
    thread3.start()

if __name__ == '__main__':
    main()