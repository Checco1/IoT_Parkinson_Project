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

    def CreatePatient(self):
        #Registering in patient.json and in resource_catalog.json
        post={
            "patientName": "Michael Scott",
            "patientID": "p_1",
            "deviceList": [
              {
                "deviceID": "waist_acc1",
                "deviceType": "sensor",
                "measureType": "TimeLastPeak",
                "unit": "s",
                "Services": [
                  {
                    "serviceType": "MQTT",
                    "topic": "ParkinsonHelper/patient1/sensors/waist_acc1"
                  }
                ]
              },
              {
                "deviceID": "wrist_acc1",
                "deviceType": "sensor",
                "measureType": "MeanFrequency",
                "unit": "Hz",
                "Services": [
                  {
                    "serviceType": "MQTT",
                    "topic": "ParkinsonHelper/patient1/sensors/wrist_acc1"
                  }
                ]
              },
              {
                "deviceID": "pressure1",
                "deviceType": "sensor",
                "measureType": "FeetPressure",
                "unit": "kg",
                "Services": [
                  {
                    "serviceType": "MQTT",
                    "topic": "ParkinsonHelper/patient1/sensors/pressure1"
                  }
                ]
              },
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
              },
              {
                "deviceID": "soundfeedback1",
                "deviceType": "actuator",
                "measureType": "Activation",
                "unit": "bool",
                "Services": [
                  {
                    "serviceType": "MQTT",
                    "topic": "ParkinsonHelper/patient1/actuators/freezing"
                  }
                ]
              }
            ],
            "Statistic_services":[
              {
                "ServiceName": "TeleBot",
                "token":"boh",
                "topic":"ParkinsonHelper/patient1/actuators/fall"

              },
              {
                "ServiceName": "ThingSpeak",
                "token":"boh",
                "topic":[
                  "ParkinsonHelper/patient1/actuators/statistics",
                  "ParkinsonHelper/patient1/actuators/fall",
                  "ParkinsonHelper/patient1/actuators/freezing",
                  "ParkinsonHelper/patient1/actuators/tremor"
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
            if device["deviceType"]=="sensor":
              for service in device["Services"]:
                  if service["serviceType"] == "MQTT":
                      self.topics.update({str(device["deviceID"]):str(service["topic"])})
                
        return(self.topics)
    
    def GetSettings(self): #to get broker and port
        request=self.url+"/broker"
        response = requests.get(request)
        return(response.json())

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

    #def start(self):
    #    self.client.start()
#
    #def stop(self):
    #    self.client.stop()

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

    #Registration in patient.json and in register_catalog.json
    register=Registering("http://localhost:8080")
    #register.UpdateSensors()

    #Retrieve MQTT info (topics and settings) from patient.json
    patientID = 1
    info=RetrievePatientInfo("http://localhost:8080")
    topics=info.GetTopic(patientID)
    settings=info.GetSettings()
    broker = settings["IP"]
    port = int(settings["mqtt_port"])

    print(topics)

    #Retrieve data and publish them
    data=SensorSimulator(patientID,broker,port,topics)
    data.ReadTXT()
    data.client.start()
    data.SendData()

    #End of the service
    data.client.unsubscribe(topics["waist_acc1"])
    data.client.unsubscribe(topics["wrist_acc1"])
    data.client.unsubscribe(topics["pressure1"])
    data.client.stop()


