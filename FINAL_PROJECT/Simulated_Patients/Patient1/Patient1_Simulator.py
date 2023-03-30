import matplotlib.pyplot as plt
import numpy as np
import time
from MyMQTT import *
import cherrypy
import requests

class Registering():
    exposed = True
    def __init__(self, url) -> None:
        self.url = url

    def UpdateSensors(self):
        #do something for the registration in the RegisterCatalog
        post={
            "waist_acc1": "active",
            "wrist_acc1": "active",
            "pressure1": "active",
            "lastUpdate": time.time()
        }
        requests.post(self.url, post)
        pass

class RetrievePatientInfo():
    exposed = True
    def __init__(self, url):
        self.url = url

    def GetTopic(self,patientID): #localhost:8080/get_topics/sensor/patient1
        request=self.url+"/get_topics/sensor/patient"+str(patientID)
        response = requests.get(request)
        return(response.json())
    
    def GetSettings(self): #to get broker and port
        request=self.url+"/get_settings"
        response = requests.get(request)
        return(response.json())

class RetrieveData():

    def __init__(self, patientID,broker,port,topics):

        self.topics=topics
        self.publish_topic= ""
        self.client = MyMQTT("DeviceConnector",broker,port,None)
        self.message={"bn": "",
                "e":
                    [
                        {
                            "measureType":"",
                            "unit":"",
                            "timeStamp":"",
                            "value":""
                        }
                    ]

        }

        self.pressure=[]
        self.wrist_acc=[]
        self.waist_acc=[]
        self.patientID = patientID

    def ReadTXT(self):
        f_p = open("pressure"+str(self.patientID)+".txt","r")
        f_waist = open("waist_acc"+str(self.patientID)+".txt","r")
        f_wrist = open("wrist_acc"+str(self.patientID)+".txt","r")

        for line in f_p:
            self.pressure.append(float(line.strip('\n')))
        for line in f_waist:
            self.waist_acc.append(float(line.strip('\n')))
        for line in f_wrist:
            self.wrist_acc.append(float(line.strip('\n')))

        f_p.close()
        f_waist.close()
        f_wrist.close()

    def start(self):
        self.client.start()

    def stop(self):
        self.client.stop()

    def SendData(self):
        for i in range(len(self.waist_acc)):

            self.message["bn"]="/patient1/sensor/waist_acc1"
            self.message["e"][0]["measureType"] = "TimeLastPeak"
            self.message["e"][0]["unit"] = "s"
            self.message["e"][0]["timeStamp"] = int(time.time())
            self.message["e"][0]["value"] = float(self.waist_acc[i])
            self.publish_topic=self.topics["waist_acc1"]
            print(self.publish_topic)
            self.client.myPublish(self.publish_topic,self.message)

            self.message["bn"]="/patient1/sensor/wrist_acc1"
            self.message["e"][0]["measureType"] = "MeanFrequencyAcceleration"
            self.message["e"][0]["unit"] = "Hz"
            self.message["e"][0]["timeStamp"] = int(time.time())
            self.message["e"][0]["value"] = float(self.wrist_acc[i])
            self.publish_topic=self.topics["wrist_acc1"]
            print(self.publish_topic)
            self.client.myPublish(self.publish_topic,self.message)

            self.message["bn"]="/patient1/sensor/pressure1"
            self.message["e"][0]["measureType"] = "FeetPressure"
            self.message["e"][0]["unit"] = "kg"
            self.message["e"][0]["timeStamp"] = int(time.time())
            self.message["e"][0]["value"] = float(self.pressure[i])
            self.publish_topic=self.topics["pressure1"]
            print(self.publish_topic)
            self.client.myPublish(self.publish_topic,self.message)
            time.sleep(2)
            print("Published!")
        

if __name__ == "__main__":

    #### URL MUST NOT BE THERE ####

    register=Registering("http://localhost:8080")
    #register.UpdateSensors()
    patientID = 1
    info=RetrievePatientInfo("http://localhost:8080")
    topics=info.GetTopic(patientID)
    settings=info.GetSettings()
    broker = settings["broker"]
    port = int(settings["port"])

    print("Topic: ", topics)
    print("Broker: ", broker)
    print("Port: ", port)

    data=RetrieveData(patientID,broker,port,topics)
    data.ReadTXT()
    data.start()
    data.SendData()
    data.stop()


