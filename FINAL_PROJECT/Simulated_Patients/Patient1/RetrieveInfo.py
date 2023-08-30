import requests
import json

class RetrievePatientInfo():
    exposed = True
    def __init__(self, url):
        self.url = url

    def GetID(self, name, code):
        print("\n")
        print("Getting ID...")
        self.ID=""
        request = self.url+"/patient"
        response = requests.get(request)
        response = response.json()
        for patient in response["patients_list"]:
            if patient["patientName"] == name and patient["patientDocument"] == code:
                self.ID = patient["patientID"]
        print("Patient ID: ",self.ID)
        return self.ID

    def GetTopic(self,patientID): #localhost:8080/info/patient1
        print("\n")
        print("Getting topics...")
        self.topics={}
        request=self.url+"/info/"+str(patientID)
        numberID=str(patientID).replace("patient","")
        response = requests.get(request)
        response_json=response.json()
        for device in response_json["device_list"]:
            if device["deviceType"]=="sensor":
              for service in device["Services"]:
                  if service["serviceType"] == "MQTT":
                      deviceName = str(device["deviceID"]).replace(numberID,"")
                      self.topics.update({deviceName:str(service["topic"])})
        return(self.topics)
    
    def GetSettings(self): #to get broker and port
        print("\n")
        print("Getting settings...")
        request=self.url+"/broker"
        response = requests.get(request)
        return(response.json())