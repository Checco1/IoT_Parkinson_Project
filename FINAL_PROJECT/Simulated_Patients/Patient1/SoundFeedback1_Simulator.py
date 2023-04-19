import json
import time
from MyMQTT import *
import cherrypy
import requests

class UpdatingCheck():
    exposed = True
    def __init__(self, url) -> None:
        self.url = url

    def GET(self):
        #Answering to the updating check every 300 s
        answer={
            "active": True
        }
        return(json.dumps(answer))
        

class RetrievePatientInfo():
    exposed = True
    def __init__(self, url):
        self.url = url

    def GetTopic(self,patientID): #localhost:8080/info/p_1
        request=self.url+"/info/p_"+str(patientID)
        response = requests.get(request)
        response_json=response.json()
        for device in response_json["devices"]:
            if device["deviceID"]=="soundfeedback1":
                for service in device["Services"]:
                    if service["serviceType"] == "MQTT":
                        self.topics= {"activation":str(service["topic"]["activation"]),
                                      "update_check": str(service["topic"]["update_check"])}
                
        return(self.topics)
    
    def GetSettings(self): #to get broker and port
        request=self.url+"/broker"
        response = requests.get(request)
        return(response.json())

class SFSimulator():
    def __init__(self, dbsID, topic_activation, topic_update, broker, port):
        self.dbsID = dbsID
        self.topic_activation=topic_activation
        self.topic_update=topic_update
        self.client = MyMQTT("SF1",broker,port,self)
        self.sf_activation = False
        self.sf_timeUpdate = 0
        self.message={"bn": "sf1_update",
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
        if self.sf_activation == True:
            print("SF for patient 1 already activated!")
        else:
            self.sf_activation= True
            print(f"The microservice has started the activation with the topic {topic}")
            self.t_activation=time.time()

    def Update(self):
        self.message["e"][0]["timeStamp"]=time.time()
        print(self.topic_update)
        print(self.message)
        self.client.myPublish(self.topic_update,self.message)
        print("Update published!")

if __name__ == "__main__":

    #Initialization
    print("The actuator SoundFeedback1 is not active")

    #Retrieve MQTT info (topics and settings) from patient.json
    patientID = 1
    info=RetrievePatientInfo("http://localhost:8080")
    topic=info.GetTopic(patientID)
    topic_activation = topic["activation"]
    topic_update = topic["update_check"]
    settings=info.GetSettings()
    broker = settings["IP"]
    port = int(settings["mqtt_port"])

    #Start the simulator
    soundfeedback1=SFSimulator("soundfeedback1",  topic_activation, topic_update, broker, port)
    soundfeedback1.client.start()
    soundfeedback1.client.mySubscribe(topic_activation)
    start=time.time()


    while True:
        soundfeedback1.sf_timeUpdate=time.time()-start
        if soundfeedback1.sf_timeUpdate>250:
            soundfeedback1.Update()
            start=time.time()

        if soundfeedback1.sf_activation==True:
            if (soundfeedback1.t_activation-time.time())>10:
                soundfeedback1.sf_activation=False
                #this condition simulate the deactivation of the SF after 10 seconds