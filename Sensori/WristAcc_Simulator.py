import random
import time

## E' il publisher!!

class WristSimulator():

    def __init__(self,patientID,sensorID) -> None:

        self.bn = "marta/ParkinsonHelper/"
        self.patientID=patientID

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


if __name__ == "__main__":

    patientID = input("Insert patient's ID: ")
    sensorID = patientID
    sensor=WristSimulator(patientID,sensorID)
    print("Insert which situation you want to simulate: ")
    print("- Freezing")
    print("- Falling")
    print("- Tremor")
    situation = input("--> ")

    if situation == "Freezing" or situation == "Falling":
        risultato = sensor.NormalWristGenerator()
        print("Wrist accelerometer: "+str(risultato))
    elif situation == "Tremor":
        risultato = sensor.TremorGenerator()
        print("Wrist accelerometer: "+str(risultato))
    else:
        print("Wrong simulation name: retry")

    


