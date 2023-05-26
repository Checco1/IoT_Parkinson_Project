import requests
import json

class RetrievePatientInfo():
    exposed = True
    def __init__(self, url):
        self.url = url

    def GetID(self, name, code):
        self.ID=""
        request = self.url+"/patient"
        response = requests.get(request)
        response = response.json()
        for patient in response["patients_list"]:
            if patient["patientName"] == name and patient["patientDocument"] == code:
                self.ID = patient["patientID"]
        return self.ID 

    def GetTopic(self,patientID): #localhost:8080/info/patient1
        self.topics={}
        request=self.url+"/info/"+str(patientID)
        numberID=str(patientID).replace("patient","")
        response = requests.get(request)
        response_json=response.json()
        for device in response_json["devices"]:
            if device["deviceType"]=="sensor":
              for service in device["Services"]:
                  if service["serviceType"] == "MQTT":
                      deviceName = str(device["deviceID"]).replace(numberID,"")
                      self.topics.update({deviceName:str(service["topic"])})
                
        return(self.topics)
    
    def GetSettings(self): #to get broker and port
        request=self.url+"/broker"
        response = requests.get(request)
        return(response.json())