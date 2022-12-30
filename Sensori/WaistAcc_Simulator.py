import random
import time

## E' il publisher!!

class WaistSimulator():

    def __init__(self,patientID,sensorID) -> None:

        self.bn = "marta/ParkinsonHelper/"
        self.patientID=patientID

        self.structure = {"bn": self.bn+str(patientID)+"/waist_acc"+str(sensorID),
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


if __name__ == "__main__":

    patientID = input("Insert patient's ID: ")
    sensorID = patientID
    sensor=WaistSimulator(patientID,sensorID)
    print("Insert which situation you want to simulate: ")
    print("- Freezing")
    print("- Falling")
    print("- Tremor")
    situation = input("--> ")

    if situation == "Tremor":
        risultato = sensor.NormalWalkGenerator()
        print("Waist accelerometer: "+str(risultato))
    elif situation == "Freezing" or situation == "Fall":
        risultato = sensor.StopGenerator()
        print("Waist accelerometer: "+str(risultato))
    else:
        print("Wrong simulation name: retry")

    


