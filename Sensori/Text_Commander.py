import matplotlib.pyplot as plt
import numpy as np
import time

class RetrieveData():

    def __init__(self,patientID,sensorID):

        self.pressure=[]
        self.wrist_acc=[]
        self.waist_acc=[]

        self.bn = "marta/ParkinsonHelper/"
        self.message={"bn": self.bn+str(patientID)+"/pressure"+str(sensorID),
                "e":
                    [
                        {
                            "measureType":"",
                            "unit":"",
                            "timeStamp":"",
                            "value":""
                        }
                    ]

        }


    def ReadTXT(self):
        f_p = open("pressure.txt","r")
        f_waist = open("waist_acc.txt","r")
        f_wrist = open("wrist_acc.txt","r")

        for line in f_p:
            self.pressure.append(float(line.strip('\n')))
        for line in f_waist:
            self.waist_acc.append(float(line.strip('\n')))
        for line in f_wrist:
            self.wrist_acc.append(float(line.strip('\n')))

        f_p.close()
        f_waist.close()
        f_wrist.close()
    
    def PlotGraphs(self):
        plt.figure()
        plt.subplot(311)
        plt.plot(np.arange(0,len(self.wrist_acc)*2,2),self.wrist_acc,'r')
        plt.ylim(0,10)
        plt.ylabel("Mean wrist frequency (Hz)")
        plt.xlabel("time (s)")
        plt.title("Wrist Accelerometer")
        plt.subplot(312)
        plt.plot(np.arange(0,len(self.waist_acc)*2,2),self.waist_acc,'b')
        plt.ylim(0,2)
        plt.ylabel("Time from last peak (s)")
        plt.xlabel("time (s)")
        plt.title("Waist Accelerometer")
        plt.subplot(313)
        plt.plot(np.arange(0,len(self.pressure)*2,2),self.pressure,'g')
        plt.ylim(0,max(self.pressure)+10)
        plt.ylabel("pressure (kg)")
        plt.xlabel("time (s)")
        plt.title("Pressure sensor")
        plt.tight_layout()
        plt.show()

    def SendData(self):
        for i in range(len(self.waist_acc)):

            self.message["e"][0]["measureType"] = "TimeLastPeak"
            self.message["e"][0]["unit"] = "s"
            self.message["e"][0]["timeStamp"] = int(time.time())
            self.message["e"][0]["value"] = float(self.waist_acc[i])
            print(self.message)

            self.message["e"][0]["measureType"] = "MeanFrequencyAcceleration"
            self.message["e"][0]["unit"] = "Hz"
            self.message["e"][0]["timeStamp"] = int(time.time())
            self.message["e"][0]["value"] = float(self.wrist_acc[i])
            print(self.message)

            self.message["e"][0]["measureType"] = "FeetPressure"
            self.message["e"][0]["unit"] = "kg"
            self.message["e"][0]["timeStamp"] = int(time.time())
            self.message["e"][0]["value"] = float(self.pressure[i])
            print(self.message)
            time.sleep(2)
        

if __name__ == "__main__":
    
    patientID = input ("Insert patient's ID: ")
    data=RetrieveData(patientID,patientID)
    data.ReadTXT()
    data.SendData() #this has to be translated in MQTT

