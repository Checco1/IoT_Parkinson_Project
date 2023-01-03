import random
import time

## E' il publisher!!

class WristSimulator():

    def __init__(self,patientID,sensorID) -> None:

        self.bn = "marta/ParkinsonHelper/"
        self.patientID=patientID
        self.sensorID = "wrist_acc"+str(sensorID)

        self.structure = {"bn": self.bn+str(patientID)+"/wrist_acc"+str(sensorID),
                "e":
                    [
                        {
                            "measureType":"MeanFrequencyAcceleration",
                            "unit":"Hz",
                            "timeStamp":"",
                            "value":""
                        }
                    ]

        }
        

    def NormalWristGenerator(self): #for Freezing and Fall generation

        mean_frequency_acc = random.uniform(1,2) #no tremor --> no quick peaks --> low frequency

        self.structure["e"][0]["timeStamp"] = int(time.time())
        self.structure["e"][0]["value"] = float(mean_frequency_acc)

        return self.structure
  

    def TremorGenerator(self):

        mean_frequency_acc = random.uniform(4,9) #high frequency --> tremor episode

        self.structure["e"][0]["timeStamp"] = int(time.time())
        self.structure["e"][0]["value"] = float(mean_frequency_acc)

        return self.structure

    def Information(self):

        DeviceInf = {
	        "DeviceID" : self.sensorID,
	        "deviceName" : "Wrist Accelerometer "+str(sensorID),
	        "measureType":"MeanFrequencyAcceleration",
            "availableServices":"MQTT",
            "servicedetails": "To be defined"
        }
        return DeviceInf


