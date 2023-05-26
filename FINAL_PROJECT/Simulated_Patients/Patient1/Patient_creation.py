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
            "patientDocument": str(self.code_f),
            "device_list": [],
            "Statistic_services":[]
        }
        body = json.dumps(body)
        requests.post(request, body)
        return self.name, self.code_f

    def CreateDevices(self, name, code_f):
        info = RetrievePatientInfo(self.url)
        self.patientID = info.GetID(name, code_f)
        numberID=self.patientID.replace("patient","")
        request = self.url+"/addd/"+str(self.patientID)
        
        print(f"Adding devices for patient {name} with ID code {self.patientID}")
        correct = 0
        while correct == 0:
            print("Insert the name of the device to add.")
            print("The devices: waist_acc, wrist_acc and pressure are mandatory.")
            print("Separate them with a comma (,): ")
            stringDevices = input("")
            if "waist_acc" in stringDevices and "wrist_acc" in stringDevices and "pressure" in stringDevices:
                correct = 1
            else:
                print("Devices waist_acc, wrist_acc and pressure not present or misspelled")

        listDevices = stringDevices.split(",")

        for device in listDevices:
            correct = 0
            while correct == 0:
                deviceType = input(f"Enter the type of device for {device} (sensor/actuator): ")
                if deviceType == "sensor" or deviceType == "actuator":
                    correct = 1
                else:
                    print("Device type must be 'sensor' or 'actuator'.")
            measureType = input(f"Enter the type of measure for {device} (TimeLastPeak, MeanFrequenct, FeetPressure...): ")
            unit = input(f"Enter the unit of the measurement for {device} (s, Hz, Kg): ")
            print("Creating the device...")
            self.device= {
                "deviceID": str(device)+str(numberID),
                "deviceType": deviceType,
                "measureType": measureType,
                "unit": unit
            }
            if deviceType == "sensor":
                self.device["Services"] = {
                    "serviceType": "MQTT",
                    "topic": "ParkinsonHelper/"+self.patientID+"/sensors/waist_acc"+numberID
                  }
            elif deviceType == "actuator":
                {   
                      "serviceType": "MQTT",
                      "topic": {
                        "activation" : "ParkinsonHelper/"+self.patientID+"/microservices/tremor",
                        "update_check" : "ParkinsonHelper/"+self.patientID+"/actuators/dbs"+numberID
                      }
                }

            print(self.device)
            requests.post(request,self.device)
            print(f"Device {device} posted!")

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