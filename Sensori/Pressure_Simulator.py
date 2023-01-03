import random
import time
import json

## E' il publisher!!

class PressureSimulator():

    def __init__(self,patientID,sensorID) -> None:

        self.bn = "marta/ParkinsonHelper/"
        self.patientID=patientID
        self.sensorID = "pressure"+str(sensorID)
        self.structure = {"bn": self.bn+str(patientID)+"/pressure"+str(sensorID),
                "e":
                    [
                        {
                            "measureType":"FeetPressure",
                            "unit":"Kg",
                            "timeStamp":"",
                            "value":""
                        }
                    ]

        }
        

    def StandingGenerator(self, weight):

        pressure = random.uniform(weight-1,weight) #the patient is standing

        self.structure["e"][0]["timeStamp"] = int(time.time())
        self.structure["e"][0]["value"] = float(pressure)

        return self.structure
  

    def LyingGenerator(self):

        pressure = random.gauss(5,0.1)

        self.structure["e"][0]["timeStamp"] = int(time.time())
        self.structure["e"][0]["value"] = float(pressure)

        return self.structure

    def Information(self):

        DeviceInf = {
	        "DeviceID" : self.sensorID,
	        "deviceName" : "Pressure Sensor "+str(sensorID),
	        "measureType":"FeetPressure",
            "availableServices":"MQTT",
            "servicedetails": "To be defined"
        }
        return DeviceInf
