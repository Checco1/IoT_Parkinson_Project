import matplotlib.pyplot as plt
import numpy as np
import time
from MyMQTT import *
import cherrypy
import requests
from Patient_creation import *
from RetrieveInfo import *

class SensorSimulator():

    def __init__(self, patientID,broker,port,topics):

        self.topics=topics #dictionary of topics
        self.publish_topic= "" #topic in use
        self.client = MyMQTT("SensorSimulator",broker,port,None)
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
        f_p = open("pressure1.txt","r")
        f_waist = open("waist_acc1.txt","r")
        f_wrist = open("wrist_acc1.txt","r")

        for line in f_p:
            self.pressure.append(float(line.strip('\n')))
        for line in f_waist:
            self.waist_acc.append(float(line.strip('\n')))
        for line in f_wrist:
            self.wrist_acc.append(float(line.strip('\n')))

        f_p.close()
        f_waist.close()
        f_wrist.close()

    def SendData(self):
        for i in range(len(self.waist_acc)):

            self.numID = self.patientID.replace("patient","")
            self.message["bn"]=str(self.patientID)+"/waist_acc"+str(self.numID)
            self.message["e"][0]["measureType"] = "TimeLastPeak"
            self.message["e"][0]["unit"] = "s"
            self.message["e"][0]["timeStamp"] = int(time.time())
            self.message["e"][0]["value"] = float(self.waist_acc[i])
            self.publish_topic=self.topics["waist_acc"]
            print(self.publish_topic)
            self.client.myPublish(self.publish_topic,self.message)

            self.message["bn"]=str(self.patientID)+"/wrist_acc"+str(self.numID)
            self.message["e"][0]["measureType"] = "MeanFrequencyAcceleration"
            self.message["e"][0]["unit"] = "Hz"
            self.message["e"][0]["timeStamp"] = int(time.time())
            self.message["e"][0]["value"] = float(self.wrist_acc[i])
            self.publish_topic=self.topics["wrist_acc"]
            print(self.publish_topic)
            self.client.myPublish(self.publish_topic,self.message)

            self.message["bn"]=str(self.patientID)+"/pressure"+str(self.numID)
            self.message["e"][0]["measureType"] = "FeetPressure"
            self.message["e"][0]["unit"] = "kg"
            self.message["e"][0]["timeStamp"] = int(time.time())
            self.message["e"][0]["value"] = float(self.pressure[i])
            self.publish_topic=self.topics["pressure"]
            print(self.publish_topic)
            self.client.myPublish(self.publish_topic,self.message)
            time.sleep(2)
            print("Published!")
        

if __name__ == "__main__":

    #Registration in patient.json and in register_catalog.json
    register=CreatePatient("http://localhost:8080")
    [name, code] = register.CreatePatient()
    register.CreateDevices(name, code)
    
    #Retrieve MQTT info (topics and settings) from patient.json
    info=RetrievePatientInfo("http://localhost:8080")
    patientID = info.GetID(name, code)
    [channel_id, write_api, read_api, url] = register.CreateTSChannel(patientID)
    register.CreateStatisticServices(name, code, channel_id, write_api, read_api, url)
    topics=info.GetTopic(patientID)
    settings=info.GetSettings()
    broker = settings["IP"]
    port = int(settings["mqtt_port"])

    #Retrieve data and publish them
    data=SensorSimulator(patientID,broker,port,topics)
    data.ReadTXT()
    data.client.start()

    while True:
        data.SendData()

    #End of the service
    data.client.stop()