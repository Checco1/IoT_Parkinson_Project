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
        print("\n")
        print("Welcome to ParkinsonHelper!")
        print("Please, enter the patient name and surname of the new patient: ")
        self.name = input("")
        self.code_f = input("Please enter the code written on the patient's ID card: ")
        request = self.url+"/addp"
        body = {
            "patientName": str(self.name),
            "patientID": "",
            "patientDocument": str(self.code_f),
            "device_list": [],
            "Statistic_services":[]
        }
        print(body)
        body = json.dumps(body)
        requests.post(request, body)
        print("Patient created!")
        return self.name, self.code_f

    def CreateDevices(self, name, code_f):
        print("\n")
        print("Creation of the patient's personal devices.")
        info = RetrievePatientInfo(self.url)
        self.patientID = info.GetID(name, code_f)
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

            
            print("Do you want to add other devices?")
            res = input("Y/N: ")

        for device in range(len(listDevices)):
            print("\n")
            print(f"Creating the device {listDevices[device]}...")
            self.device= {
                "deviceID": str(listDevices[device])+str(numberID),
                "deviceType": deviceTypeList[device],
                "measureType": measureTypeList[device],
                "unit": unitList[device]
            }
            if deviceTypeList[device] == "sensor":
                self.device["Services"] = [{
                    "serviceType": "MQTT",
                    "topic": "ParkinsonHelper/"+self.patientID+"/sensors/"+str(listDevices[device])+str(numberID)
                  }]
            elif deviceTypeList[device] == "actuator":
                if "dbs" in str(listDevices[device]) or str(listDevices[device])=="dbs":
                    self.device["Services"] = [{   
                        "serviceType": "MQTT",
                        "topic": {
                            "activation" : "ParkinsonHelper/"+self.patientID+"/microservices/tremor",
                            "update_check" : "ParkinsonHelper/"+self.patientID+"/actuators/"+str(listDevices[device])+str(numberID)
                        }
                    }]
                elif "sf" in str(listDevices[device]) or str(listDevices[device])=="sf":
                    self.device["Services"] = [{   
                        "serviceType": "MQTT",
                        "topic": {
                            "activation" : "ParkinsonHelper/"+self.patientID+"/microservices/freezing",
                            "update_check" : "ParkinsonHelper/"+self.patientID+"/actuators/"+str(listDevices[device])+str(numberID)
                        }
                    }]
                else:
                    print(f"Insert the topic to which the device {listDevices[device]} has to subscribe: ")
                    topicDevice=input(f"ParkinsonHelper/{self.patientID}/microservices/")
                    self.device["Services"] = [{   
                        "serviceType": "MQTT",
                        "topic": {
                            "activation" : "ParkinsonHelper/"+self.patientID+"/microservices/"+str(topicDevice),
                            "update_check" : "ParkinsonHelper/"+self.patientID+"/actuators/"+str(listDevices[device])+str(numberID)
                        }
                    }]

            print(self.device)
            self.device = json.dumps(self.device)
            requests.post(request,self.device)
            print(f"Device {listDevices[device]} posted!")

    def CreateStatisticServices(self, name, code_f, channel_id, write_api, read_api, url):
        print("\n")
        print(f"Adding mandatory services for the patient {name} with ID code {code_f}")

        info = RetrievePatientInfo(self.url)
        self.patientID = info.GetID(name, code_f)

        self.stats = {

            "Statistic_services":
            [
                {
                "ServiceName": "TeleBot",
                "BotName": "ParkinsonHelperBot",
                "Services": [
                        {
                        "ServiceType": "MQTT",
                        "topic": "ParkinsonHelper/"+self.patientID+"/microservices/fall"
                        }
                    ]
                },
                {
                "ServiceName": "ThingSpeak",
                "Channel_ID": channel_id,
                "URL": url,
                "WriteApi": write_api,
                "ReadApi": read_api,
                "Services": [
                        {
                        "serviceProvider": "Statistic_manager",
                        "serviceType": "MQTT",
                        "topic": "ParkinsonHelper/"+self.patientID+"/microservices/statistics"
                        },
                        {
                        "serviceProvider": "Fall_manager",
                        "serviceType": "MQTT",
                        "topic": "ParkinsonHelper/"+self.patientID+"/microservices/fall"
                        },
                        {
                        "serviceProvider": "Freezing_manager",
                        "serviceType": "MQTT",
                        "topic": "ParkinsonHelper/"+self.patientID+"/microservices/freezing"
                        },
                        {
                        "serviceProvider": "Tremor_manager",
                        "serviceType": "MQTT",
                        "topic": "ParkinsonHelper/"+self.patientID+"/microservices/tremor"
                        }
                    ]
                }
            ]
        }

        self.stats=json.dumps(self.stats)
        request = self.url+"/adds/"+self.patientID
        requests.post(request, self.stats)
        print(self.stats)
        print("Services added!")


    def CreateTSChannel(self, ID):
        api_key="5LWQ3IHY3DY8TILH"
        url=f"https://api.thingspeak.com/channels.json"
        data={
            "api_key":api_key,
            "name":str(ID),
            "field1":"waistStats",
            "field2":"wristStats",
            "field3":"pressureStats",
            "field4":"fall_episodes",
            "field5":"tremor_episode",
            "field6":"freezing_episode"
        }
        response=requests.post(url,json=data)
        if response.status_code==200:
            new_channel=response.json()
            channel_id=new_channel["id"]
            print("New channel added with id: ",channel_id)
        else:
            print("Error in the channel creation")
        url=f"https://api.thingspeak.com/channels/{channel_id}/bulk_update.json"
        params={"api_key":api_key}
        response=requests.get(url,params=params)
        
        channel_info=response.json()
        write_api=channel_info["api_keys"][0]["api_key"]
        read_api=channel_info["api_keys"][1]["api_key"]
        print("Write api: ",write_api)
        print("Read api: ",read_api)

        return channel_id, write_api, read_api, url