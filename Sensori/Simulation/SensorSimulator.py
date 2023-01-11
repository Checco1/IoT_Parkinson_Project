import random
import time

## E' il publisher!!

class SensorSimulator():

    def __init__(self,patientID,sensorID) -> None:

        self.bn = "marta/ParkinsonHelper/"
        self.patientID=patientID
        #TimeLastPeak: time from the last peak to the end of the observation window
        #If it is bigger than 1 s --> freezing/fall
        self.waist_acc = {"bn": self.bn+str(patientID)+"/waist_acc"+str(sensorID),
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
        #MeanAcceleration: mean acceleration is usefull to understand if the arm is moved voluntarily
        # (>>0: voluntary contraction, proximal to 0: no movement)

        #MeanFrequencyAcceleration: it is usefull to understand if the patient is trembling
        #(4-9 Hz: tremor, proximal to 0: no tremor)
        self.wrist_acc = {"bn": self.bn+str(patientID)+"/wrist_acc"+str(sensorID),
                "e":
                    [
                        {
                            "measureType":"MeanAcceleration",
                            "unit":"g",
                            "timeStamp":"",
                            "value":""
                        },

                        {
                            "measureType":"MeanFrequencyAcceleration",
                            "unit":"Hz",
                            "timeStamp":"",
                            "value":""
                        }
                    ]

        }
        #Pressure: it is usefull to understand in what position the patient is
        #(70-80: the patient is standing, 30-60: the patient is sitting, proximal to 0: the patient is lying down)
        self.feet_pressure = {"bn": self.bn+str(patientID)+"/pressure"+str(sensorID),
                "e":
                    [
                        {
                            "measureType":"Pressure",
                            "unit":"kg",
                            "timeStamp":"",
                            "value":""
                        }
                    ]

        }

    def FreezingGenerator(self):

        TimeLastPeak = random.gauss(1.7,0.1) #high delta time: freezing episode
        pressure = random.gauss(75,2) #the patient is standing
        mean_acc = random.uniform(0.01,0.1) #no movement
        mean_frequency_acc = random.uniform(1,2) #no tremor --> no quick peaks --> low frequency

        self.waist_acc["e"][0]["timeStamp"] = int(time.time())
        self.waist_acc["e"][0]["value"] = float(TimeLastPeak)

        self.wrist_acc["e"][0]["timeStamp"] = int(time.time())
        self.wrist_acc["e"][0]["value"] = float(mean_acc)

        self.wrist_acc["e"][1]["timeStamp"] = int(time.time())
        self.wrist_acc["e"][1]["value"] = float(mean_frequency_acc)

        self.feet_pressure["e"][0]["timeStamp"] = int(time.time())
        self.feet_pressure["e"][0]["value"] = float(pressure)

        result=[self.waist_acc,self.wrist_acc,self.feet_pressure]

        print("Freezing Simulation")

        return result

    def ErrorSimulation(self):
        #To simulate wrong acquisitions
        TimeLastPeak = random.uniform(10,20) 
        pressure = random.uniform(100,200) 
        mean_acc = random.uniform(2,2.5) 
        mean_frequency_acc = random.uniform(100,20) 

        self.waist_acc["e"][0]["timeStamp"] = int(time.time())
        self.waist_acc["e"][0]["value"] = float(TimeLastPeak)

        self.wrist_acc["e"][0]["timeStamp"] = int(time.time())
        self.wrist_acc["e"][0]["value"] = float(mean_acc)

        self.wrist_acc["e"][1]["timeStamp"] = int(time.time())
        self.wrist_acc["e"][1]["value"] = float(mean_frequency_acc)

        self.feet_pressure["e"][0]["timeStamp"] = int(time.time())
        self.feet_pressure["e"][0]["value"] = float(pressure)

        result=[self.waist_acc,self.wrist_acc,self.feet_pressure]

        print("Error Simulation")

        return result

    def FallGenerator(self):

        TimeLastPeak = random.gauss(1.7,0.1) #high delta time --> no movement
        pressure = random.gauss(5,0.1) #very low pressure (simulate noise or contact with shoes) --> the patient is lying down
        mean_acc = random.uniform(0.01,0.5) #the can move arms or not
        mean_frequency_acc = random.uniform(1,2) #no tremor

        self.waist_acc["e"][0]["timeStamp"] = int(time.time())
        self.waist_acc["e"][0]["value"] = float(TimeLastPeak)

        self.wrist_acc["e"][0]["timeStamp"] = int(time.time())
        self.wrist_acc["e"][0]["value"] = float(mean_acc)

        self.wrist_acc["e"][1]["timeStamp"] = int(time.time())
        self.wrist_acc["e"][1]["value"] = float(mean_frequency_acc)

        self.feet_pressure["e"][0]["timeStamp"] = int(time.time())
        self.feet_pressure["e"][0]["value"] = float(pressure)

        result=[self.waist_acc,self.wrist_acc,self.feet_pressure]
        print("Fall Simulation")

        return result    

    def TremorGenerator(self):

        TimeLastPeak = random.gauss(1.7,0.1) #high delta time --> no movement
        pressure = random.gauss(50,7) #could be every type of pressure from 10 tu 80
        mean_acc = random.uniform(0.01,0.5) #they can move arms or not
        mean_frequency_acc = random.uniform(4,9) #high frequency --> tremor episode

        self.waist_acc["e"][0]["timeStamp"] = int(time.time())
        self.waist_acc["e"][0]["value"] = float(TimeLastPeak)

        self.wrist_acc["e"][0]["timeStamp"] = int(time.time())
        self.wrist_acc["e"][0]["value"] = float(mean_acc)

        self.wrist_acc["e"][1]["timeStamp"] = int(time.time())
        self.wrist_acc["e"][1]["value"] = float(mean_frequency_acc)

        self.feet_pressure["e"][0]["timeStamp"] = int(time.time())
        self.feet_pressure["e"][0]["value"] = float(pressure)

        result=[self.waist_acc,self.wrist_acc,self.feet_pressure]
        print("Fall Simulation")

        return result

    def ImpossibleSituations(self):
        TimeLastPeak = random.gauss(0.5,0.1) #low delta time --> correct gait
        pressure = random.gauss(20,3) #lying down position or sitting position
        mean_acc = random.uniform(0.01,0.5) #they can move arms or not
        mean_frequency_acc = random.uniform(1,9) #any tremor

        self.waist_acc["e"][0]["timeStamp"] = int(time.time())
        self.waist_acc["e"][0]["value"] = float(TimeLastPeak)

        self.wrist_acc["e"][0]["timeStamp"] = int(time.time())
        self.wrist_acc["e"][0]["value"] = float(mean_acc)

        self.wrist_acc["e"][1]["timeStamp"] = int(time.time())
        self.wrist_acc["e"][1]["value"] = float(mean_frequency_acc)

        self.feet_pressure["e"][0]["timeStamp"] = int(time.time())
        self.feet_pressure["e"][0]["value"] = float(pressure)

        result=[self.waist_acc,self.wrist_acc,self.feet_pressure]
        print("Impossible Simulation")
        #patient can't be sitting/lying down and walking correctly

        return result


if __name__ == "__main__":

    patientID = input("Insert patient's ID: ")
    sensorID = patientID
    sensor=SensorSimulator(patientID,sensorID)
    print("Insert which situation you want to simulate: ")
    print("- Freezing")
    print("- Falling")
    print("- Tremor")
    print("- Impossible")
    print("- Errors (not working sensors)")
    situation = input("--> ")
    if situation == "Freezing":
        risultato = sensor.FreezingGenerator()
    elif situation == "Falling":
        risultato = sensor.FallGenerator()
    elif situation == "Tremor":
        risultato = sensor.TremorGenerator()
    elif situation == "Impossible":
        risultato = sensor.ImpossibleSituations()
    elif situation == "Errors":
        risultato = sensor.ErrorSimulation()
    else:
        print("Wrong simulation name: retry")

    print("Waist accelerometer: "+str(risultato[0]))
    print("Wrist accelerometer: "+str(risultato[1]))
    print("Pressure: "+str(risultato[2]))

