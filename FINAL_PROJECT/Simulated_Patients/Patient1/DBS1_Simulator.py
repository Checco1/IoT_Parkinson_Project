import json
import time
from MyMQTT import *

class DBS():
    def __init__(self, dbsID, baseTopic, broker, port):
        self.dbsID = dbsID
        self.baseTopic=baseTopic
        self.client = MyMQTT("DeviceConnector",broker,port,self)
        self.dbs_activation = False

    def start(self):
        self.client.start()
        self.client.mySubscribe(self.topic)

    def stop(self):
        self.client.stop()

    def notify(self, topic, msg):
        d = json.loads(msg)
        client = d["bn"]
        if self.dbs_activation == True:
            print("DBS for patient 1 already activated!")
        else:
            self.dbs_activation= True
            print(f"The microservice {client} has started the activation with the topic {topic}")
            self.t_activation=time.time()

if __name__ == "__main__":
    conf=json.load(open("settings.json"))
    broker = conf["broker"]
    port = conf["port"]
    patientID = 1
    baseTopic = conf["baseTopic"]
    topic = baseTopic+"/patient"+str(patientID)+"7dbs_activation"
    dbs1=DBS("DBS1", topic, broker, port)
    dbs1.start()

    while True:
        if (dbs1.t_activation-time.time())>120:
            dbs1.dbs_activation=False
            #this condition simulate the deactivation of the DBS after
            #a certain amount of time (in reality, it would be a larger
            #range)