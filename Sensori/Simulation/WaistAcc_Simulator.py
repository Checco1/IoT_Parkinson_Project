import random
import time

## E' il publisher!!

class WaistSimulator():

    def __init__(self,patientID) -> None:

        self.bn = "marta/ParkinsonHelper/"
        self.patientID=patientID
        self.sensorID = "waist_acc"+str(patientID)

        self.structure = {"bn": self.bn+str(patientID)+"/waist_acc"+str(patientID),
                "e":
                    [
                        {
                            "measureType":"TimeLastPeak",
                            "unit":"s",
                            "timeStamp":"",
                            "value":""
                        }
                    ]

        }
        

    def NormalWalkGenerator(self): #for Freezing and Fall generation

        TimeLastPeak = random.gauss(0.7,0.01) #high delta time: freezing episode

        self.structure["e"][0]["timeStamp"] = int(time.time())
        self.structure["e"][0]["value"] = float(TimeLastPeak)

        return self.structure
  

    def StopGenerator(self):

        TimeLastPeak = random.gauss(1.7,0.01) #high delta time: freezing episode

        self.structure["e"][0]["timeStamp"] = int(time.time())
        self.structure["e"][0]["value"] = float(TimeLastPeak)

        return self.structure

    def Information(self):

        DeviceInf = {
	        "DeviceID" : self.sensorID,
	        "deviceName" : "Waist Accelerometer "+str(self.patientID),
	        "measureType":"TimeLastPeak",
            "availableServices":"MQTT",
            "servicedetails": "To be defined"
        }
        return DeviceInf
