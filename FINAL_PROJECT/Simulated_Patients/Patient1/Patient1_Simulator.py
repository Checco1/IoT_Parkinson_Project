import matplotlib.pyplot as plt
import numpy as np
import time
from MyMQTT import *

class RetrieveData():

    def __init__(self, patientID,broker,port,baseTopic):

        self.baseTopic=baseTopic
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

            self.message["bn"]="/waist_acc"+str(self.patientID)
            self.message["e"][0]["measureType"] = "TimeLastPeak"
            self.message["e"][0]["unit"] = "s"
            self.message["e"][0]["timeStamp"] = int(time.time())
            self.message["e"][0]["value"] = float(self.waist_acc[i])
            self.topic=self.baseTopic+self.message["bn"]    #the topic is /ParkinsonHelper/patient1/waist_acc1
            self.client.myPublish(self.topic,self.message)

            self.message["bn"]="/wrist_acc"+str(self.patientID)
            self.message["e"][0]["measureType"] = "MeanFrequencyAcceleration"
            self.message["e"][0]["unit"] = "Hz"
            self.message["e"][0]["timeStamp"] = int(time.time())
            self.message["e"][0]["value"] = float(self.wrist_acc[i])
            self.topic=self.baseTopic+self.message["bn"]    #the topic is /ParkinsonHelper/patient1/wrist_acc1
            self.client.myPublish(self.topic,self.message)

            self.message["bn"]="/pressure"+str(self.patientID)
            self.message["e"][0]["measureType"] = "FeetPressure"
            self.message["e"][0]["unit"] = "kg"
            self.message["e"][0]["timeStamp"] = int(time.time())
            self.message["e"][0]["value"] = float(self.pressure[i])
            self.topic=self.baseTopic+self.message["bn"]    #the topic is /ParkinsonHelper/patient1/pressure1
            self.client.myPublish(self.topic,self.message)
            time.sleep(2)
            print("Published!")
        

if __name__ == "__main__":
    
    conf=json.load(open("settings.json"))
    patientID = 1
    broker = conf["broker"]
    port = conf["port"]
    baseTopic = conf["baseTopic"]+'/patient'+str(patientID)
    data=RetrieveData(patientID,broker,port,baseTopic)
    data.ReadTXT()
    data.start()
    data.SendData()
    data.stop()


