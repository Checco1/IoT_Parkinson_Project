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


if __name__ == "__main__":

    patientID = input("Insert patient's ID: ")
    sensorID = patientID
    weight = 75
    sensor=PressureSimulator(patientID,sensorID)
    
    my_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(time.time())))

    res = sensor.Information()
    print(json.dumps(res)) 
    print(my_time)

  #  print("Insert which situation you want to simulate: ")
  #  print("- Freezing")
  #  print("- Falling")
  #  print("- Tremor")
  #  situation = input("--> ")
  #
  #  if situation == "Freezing" or situation == "Tremor":
  #      risultato = sensor.StandingGenerator(weight)
  #      print("Pressure: "+str(risultato))
  #  elif situation == "Fall":
  #      risultato = sensor.LyingGenerator()
  #      print("Pressure: "+str(risultato))
  #  else:
  #      print("Wrong simulation name: retry")




