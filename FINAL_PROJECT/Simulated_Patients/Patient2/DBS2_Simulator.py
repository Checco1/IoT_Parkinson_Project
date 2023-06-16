import json
import time
from MyMQTT import *
import cherrypy
import requests
        

class RetrievePatientInfo():
    exposed = True
    def __init__(self, url):
        self.url = url

    def GetTopic(self,patientID): #localhost:8080/info/patient1
        request=self.url+"/info/"+str(patientID)
        response = requests.get(request)
        response_json=response.json()
        for device in response_json["devices"]:
            if device["deviceID"]=="dbs2":
                for service in device["Services"]:
                    if service["serviceType"] == "MQTT":
                        self.topics= {"activation":str(service["topic"]["activation"]),
                                      "update_check": str(service["topic"]["update_check"])}
                
        return(self.topics)
    
    def GetSettings(self): #to get broker and port
        request=self.url+"/broker"
        response = requests.get(request)
        return(response.json())

class DBSSimulator():
    def __init__(self, dbsID, topic_activation, topic_update, broker, port):
        self.dbsID = dbsID
        self.topic_activation=topic_activation
        self.topic_update=topic_update
        self.client = MyMQTT("DBS2",broker,port,self)
        self.t_activation=time.time()
        self.dbs_activation = False
        self.message={"bn": "patient2/dbs2",
                "e":
                    [
                        {
                            "measureType":"Activation",
                            "unit":"bool",
                            "timeStamp":"",
                            "value":"True"
                        }
                    ]

        }

    def notify(self, topic, msg):
        d = json.loads(msg)
        client = d["bn"]
        if self.dbs_activation == True:
            print("DBS for patient 2 already activated!")
        else:
            self.dbs_activation= True
            print(f"The microservice has started the activation with the topic {topic}")
            self.t_activation=time.time()

    def Update(self):
        self.message["e"][0]["timeStamp"]=time.time()
        print(self.message)
        self.client.myPublish(self.topic_update,self.message)
        print("Update published!")



if __name__ == "__main__":

    #Initialization
    print("The actuator DBS2 is not active")

    #Retrieve MQTT info (topics and settings) from patient.json
    patientID = "patient1"
    info=RetrievePatientInfo("http://localhost:8080")
    topic=info.GetTopic(patientID)
    topic_activation = topic["activation"]
    topic_update = topic["update_check"]
    settings=info.GetSettings()
    broker = settings["IP"]
    port = int(settings["mqtt_port"])

    #Start the simulator
    dbs1=DBSSimulator("DBS2", topic_activation, topic_update, broker, port)
    dbs1.client.start()
    dbs1.client.mySubscribe(topic_activation)
    start=time.time()

    while True:
        #Update every 250 seconds sending an MQTT message to catalog_Manager
        dbs_timeUpdate=time.time()-start
        if dbs_timeUpdate>25:
            dbs1.Update()
            start=time.time()

        if dbs1.dbs_activation==True and abs(dbs1.t_activation-time.time())>5:
            print("The DBS has been deactivated!")
            dbs1.dbs_activation=False
            #this condition simulate the deactivation of the DBS after
            #a certain amount of time (in reality, it would be a larger
            #range)