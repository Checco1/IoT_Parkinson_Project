import matplotlib.pyplot as plt
import numpy as np
import time
from MyMQTT import *
import cherrypy
import requests
from RetrieveInfo import *

class CreatePatient():
    exposed = True
    def __init__(self, url) -> None:
        self.url = url

    def CreatePatient(self):
        self.name = input("Please, enter the patient name and surname: ")
        self.code_f = input("Please enter the code written on your ID card: ")
        request = self.url+"/addp"
        body = {
            "patientName": str(self.name),
            "patientID": "",
            "patientDocument": str(self.code_f),
            "device_list": [],
            "Statistic_services":[]
        }
        print(body)
        requests.post(request, body)
        return self.name, self.code_f

    def CreateDevices(self, name, code_f):
        info = RetrievePatientInfo(self.url)
        self.patientID = info.GetID(name, code_f)
        print(self.patientID)
        numberID=self.patientID.replace("patient","")
        request = self.url+"/addd/"+str(self.patientID)
        
        print(f"Adding devices for patient {name} with ID code {self.patientID}")

        listDevices=["waist_acc","wrist_acc","pressure","dbs","sf"]
        measureTypeList=["TimeLastPeak","MeanFrequency","FeetPressure","Activation","Activation"]
        deviceTypeList=["sensor","sensor","sensor","actuator","actuator"]
        unitList=["s","Hz","kg","bool","bool"]

        print("Mandatory devices: waist_acc, wrist_acc, pressure, dbs and sf.")
        print("Do you want to add other devices?")
        res = input("Y/N: ")
        while res == "Y" or res == "y":
            print("Write the device's name: ")
            deviceName = input("")
            listDevices.append(deviceName)
            print("Write the device's measure type (pressure, heart_rate...): ")
            deviceMeasure = input("")
            measureTypeList.append(deviceMeasure)
            print("Write the device's type (sensor/actuator): ")
            deviceType_inp = input("")
            deviceTypeList.append(deviceType_inp)
            print("Write the unit of the device's measurement (kg, bpm...): ")
            unitDevice = input("")
            unitList.append(unitDevice)

            
            print("Do you want to add new devices?")
            res = input("Y/N: ")

        for device in range(len(listDevices)):
            print(f"Creating the device {listDevices[device]}...")
            self.device= {
                "deviceID": str(listDevices[device])+str(numberID),
                "deviceType": deviceTypeList[device],
                "measureType": measureTypeList[device],
                "unit": unitList[device]
            }
            if deviceTypeList[device] == "sensor":
                self.device["Services"] = {
                    "serviceType": "MQTT",
                    "topic": "ParkinsonHelper/"+self.patientID+"/sensors/"+str(listDevices[device])+str(numberID)
                  }
            elif deviceTypeList[device] == "actuator":
                if "dbs" in str(listDevices[device]):
                    {   
                        "serviceType": "MQTT",
                        "topic": {
                            "activation" : "ParkinsonHelper/"+self.patientID+"/microservices/tremor",
                            "update_check" : "ParkinsonHelper/"+self.patientID+"/actuators/"+str(listDevices[device])+str(numberID)
                        }
                    }
                if "sf" in str(listDevices[device]):
                    {   
                        "serviceType": "MQTT",
                        "topic": {
                            "activation" : "ParkinsonHelper/"+self.patientID+"/microservices/freezing",
                            "update_check" : "ParkinsonHelper/"+self.patientID+"/actuators/"+str(listDevices[device])+str(numberID)
                        }
                    }
                else:
                    print(f"Insert the topic to which the device {listDevices[device]} has to subscribe: ")
                    topicDevice=input(f"ParkinsonHelper/{self.patientID}/")
                    {   
                        "serviceType": "MQTT",
                        "topic": {
                            "activation" : "ParkinsonHelper/"+self.patientID+"/microservices/freezing",
                            "update_check" : "ParkinsonHelper/"+self.patientID+"/actuators/"+str(listDevices[device])+str(numberID)
                        }
                    }

            print(self.device)
            requests.post(request,self.device)
            print(f"Device {listDevices[device]} posted!")

    def CreateStatisticServices(self):

        self.stats = {
            "Statistic_services":[
                {
                  "ServiceName": "TeleBot",
                  "token":"boh",
                  "topic":"ParkinsonHelper/"+self.patientID+"/microservices/fall"

                },
                {
                  "ServiceName": "ThingSpeak",
                  "token":"boh",
                  "topic":[
                    "ParkinsonHelper/"+self.patientID+"/microservices/statistics",
                    "ParkinsonHelper/"+self.patientID+"/microservices/fall",
                    "ParkinsonHelper/"+self.patientID+"/microservices/freezing",
                    "ParkinsonHelper/"+self.patientID+"/microservices/tremor"
                  ]
                }
            ]
        }

        request = self.url+"/adds/"+self.patientID
        requests.post(request, self.stats)