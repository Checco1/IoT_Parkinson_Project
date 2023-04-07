import json
import time
from MyMQTT import *
import cherrypy
import requests

class Registering():
    exposed = True
    def __init__(self, url) -> None:
        self.url = url

    def AddingDBS(self):
        #Registering dbs1 in patient.json and in resource_catalog.json
        post={
            "patientName": "Michael Scott",
            "patientID": "p_1",
            "deviceList": [
              {
                "deviceID": "dbs1",
                "deviceType": "actuator",
                "measureType": "Activation",
                "unit": "bool",
                "Services": [
                  {
                    "serviceType": "MQTT",
                    "topic": "ParkinsonHelper/patient1/actuators/tremor"
                  }
                ]
              }
            ]
        }
        requests.post(self.url, post)
        pass

class RetrievePatientInfo():
    exposed = True
    def __init__(self, url):
        self.url = url

    def GetTopic(self,patientID): #localhost:8080/info/p_1
        self.topics={}
        request=self.url+"/info/p_"+str(patientID)
        response = requests.get(request)
        response_json=response.json()
        for device in response_json["devices"]:
            if device["deviceType"]=="actuator":
                for service in device["Services"]:
                    if service["serviceType"] == "MQTT":
                        self.topics.update({str(device["deviceID"]):str(service["topic"])})
                
        return(self.topics)
    
    def GetSettings(self): #to get broker and port
        request=self.url+"/broker"
        response = requests.get(request)
        return(response.json())

class DBSSimulator():
    def __init__(self, dbsID, topic, broker, port):
        self.dbsID = dbsID
        self.topic=topic
        self.client = MyMQTT("DeviceConnector",broker,port,self)
        self.dbs_activation = False

    #def start(self):
    #    self.client.start()
    #    self.client.mySubscribe(self.topic)
#
    #def stop(self):
    #    self.client.stop()

    def notify(self, topic, msg):
        d = json.loads(msg)
        client = d["bn"]
        if self.dbs_activation == True:
            print("DBS for patient 1 already activated!")
        else:
            self.dbs_activation= True
            print(f"The microservice has started the activation with the topic {topic}")
            self.t_activation=time.time()

if __name__ == "__main__":

    #Registering to the patient.json and to register_catalog.json
    register = Registering("http://localhost:8080")
    register.AddingDBS()

    #Retrieve MQTT info (topics and settings) from patient.json
    patientID = 1
    info=RetrievePatientInfo("http://localhost:8080")
    topic=info.GetTopic(patientID)["dbs1"]
    settings=info.GetSettings()
    broker = settings["IP"]
    port = int(settings["mqtt_port"])

    #Start the simulator
    dbs1=DBSSimulator("DBS1", topic, broker, port)
    dbs1.client.start()
    dbs1.client.mySubscribe(topic)

    while True:
        if (dbs1.t_activation-time.time())>120:
            dbs1.dbs_activation=False
            #this condition simulate the deactivation of the DBS after
            #a certain amount of time (in reality, it would be a larger
            #range)