import matplotlib.pyplot as plt
import numpy as np
from WaistAcc_Simulator import *
from WristAcc_Simulator import *
from Pressure_Simulator import *



if __name__ == "__main__":

    wrist_cycle = np.zeros(30)
    waist_cycle = np.zeros(30)
    pressure_cycle = np.zeros(30)

    patientID = input("Insert patient's ID: ")
    weight = 75
    wrist_Acc=WristSimulator(patientID)
    waist_Acc=WaistSimulator(patientID)
    pressure=PressureSimulator(patientID)
    print("Insert which situation you want to simulate: ")
    print("- Freezing")
    print("- Falling")
    print("- Tremor")
    print("- T+Fr (Tremor+Freezing)")
    print("- Fr+Fa (Freezing+Falling)")
    print("- T+Fa (Tremor+Falling)")
    situation = input("--> ")
    if situation == "Freezing":
        for i in range(30):
            if i in range(15,17):
                wrist_cycle[i] = wrist_Acc.NormalWristGenerator()["e"][0]["value"]
                waist_cycle[i] = waist_Acc.StopGenerator()["e"][0]["value"]
                pressure_cycle[i] = pressure.StandingGenerator(weight)["e"][0]["value"]
            else:
                wrist_cycle[i] = wrist_Acc.NormalWristGenerator()["e"][0]["value"]
                waist_cycle[i] = waist_Acc.NormalWalkGenerator()["e"][0]["value"]
                pressure_cycle[i] = pressure.StandingGenerator(weight)["e"][0]["value"]
    elif situation == "Falling":
        for i in range(30):
            if i == 15 or i == 25:
                wrist_cycle[i] = wrist_Acc.NormalWristGenerator()["e"][0]["value"]
                waist_cycle[i] = waist_Acc.StopGenerator()["e"][0]["value"]
                pressure_cycle[i] = pressure.LyingGenerator()["e"][0]["value"]
            elif i in range(16,25):
                wrist_cycle[i] = wrist_Acc.NormalWristGenerator()["e"][0]["value"]
                waist_cycle[i] = 2
                pressure_cycle[i] = pressure.LyingGenerator()["e"][0]["value"]
            else:
                wrist_cycle[i] = wrist_Acc.NormalWristGenerator()["e"][0]["value"]
                waist_cycle[i] = waist_Acc.NormalWalkGenerator()["e"][0]["value"]
                pressure_cycle[i] = pressure.StandingGenerator(weight)["e"][0]["value"]
    elif situation == "Tremor":
        for i in range(30):
            if i in range(15,17):
                wrist_cycle[i] = wrist_Acc.TremorGenerator()["e"][0]["value"]
                waist_cycle[i] = waist_Acc.NormalWalkGenerator()["e"][0]["value"]
                pressure_cycle[i] = pressure.StandingGenerator(weight)["e"][0]["value"]
            else:
                wrist_cycle[i] = wrist_Acc.NormalWristGenerator()["e"][0]["value"]
                waist_cycle[i] = waist_Acc.NormalWalkGenerator()["e"][0]["value"]
                pressure_cycle[i] = pressure.StandingGenerator(weight)["e"][0]["value"]
    elif situation == "T+Fr":
        for i in range(30):
            if i in range(13,15):
                wrist_cycle[i] = wrist_Acc.TremorGenerator()["e"][0]["value"]
                waist_cycle[i] = waist_Acc.NormalWalkGenerator()["e"][0]["value"]
                pressure_cycle[i] = pressure.StandingGenerator(weight)["e"][0]["value"]
            elif i in range(15,17):
                wrist_cycle[i] = wrist_Acc.TremorGenerator()["e"][0]["value"]
                waist_cycle[i] = waist_Acc.StopGenerator()["e"][0]["value"]
                pressure_cycle[i] = pressure.StandingGenerator(weight)["e"][0]["value"]
            else:
                wrist_cycle[i] = wrist_Acc.NormalWristGenerator()["e"][0]["value"]
                waist_cycle[i] = waist_Acc.NormalWalkGenerator()["e"][0]["value"]
                pressure_cycle[i] = pressure.StandingGenerator(weight)["e"][0]["value"]
    elif situation == "Fr+Fa":
        for i in range(30):
            if i in range(13,15):
                wrist_cycle[i] = wrist_Acc.NormalWristGenerator()["e"][0]["value"]
                waist_cycle[i] = waist_Acc.StopGenerator()["e"][0]["value"]
                pressure_cycle[i] = pressure.StandingGenerator(weight)["e"][0]["value"]
            elif i == 15 or i == 25:
                wrist_cycle[i] = wrist_Acc.NormalWristGenerator()["e"][0]["value"]
                waist_cycle[i] = waist_Acc.StopGenerator()["e"][0]["value"]
                pressure_cycle[i] = pressure.LyingGenerator()["e"][0]["value"]
            elif i in range(16,25):
                wrist_cycle[i] = wrist_Acc.NormalWristGenerator()["e"][0]["value"]
                waist_cycle[i] = 2
                pressure_cycle[i] = pressure.LyingGenerator()["e"][0]["value"]
            else:
                wrist_cycle[i] = wrist_Acc.NormalWristGenerator()["e"][0]["value"]
                waist_cycle[i] = waist_Acc.NormalWalkGenerator()["e"][0]["value"]
                pressure_cycle[i] = pressure.StandingGenerator(weight)["e"][0]["value"]
    elif situation == "T+Fa":
        for i in range(30):
            if i in range(13,15):
                wrist_cycle[i] = wrist_Acc.TremorGenerator()["e"][0]["value"]
                waist_cycle[i] = waist_Acc.NormalWalkGenerator()["e"][0]["value"]
                pressure_cycle[i] = pressure.StandingGenerator(weight)["e"][0]["value"]
            elif i == 15 :
                wrist_cycle[i] = wrist_Acc.TremorGenerator()["e"][0]["value"]
                waist_cycle[i] = waist_Acc.StopGenerator()["e"][0]["value"]
                pressure_cycle[i] = pressure.LyingGenerator()["e"][0]["value"]
            elif i in range(15,19):
                wrist_cycle[i] = wrist_Acc.TremorGenerator()["e"][0]["value"]
                waist_cycle[i] = 2
                pressure_cycle[i] = pressure.LyingGenerator()["e"][0]["value"]
            elif i in range(19,25):
                wrist_cycle[i] = wrist_Acc.NormalWristGenerator()["e"][0]["value"]
                waist_cycle[i] = 2
                pressure_cycle[i] = pressure.LyingGenerator()["e"][0]["value"]
            elif i == 25 :
                wrist_cycle[i] = wrist_Acc.NormalWristGenerator()["e"][0]["value"]
                waist_cycle[i] = waist_Acc.StopGenerator()["e"][0]["value"]
                pressure_cycle[i] = pressure.LyingGenerator()["e"][0]["value"]    
            else:
                wrist_cycle[i] = wrist_Acc.NormalWristGenerator()["e"][0]["value"]
                waist_cycle[i] = waist_Acc.NormalWalkGenerator()["e"][0]["value"]
                pressure_cycle[i] = pressure.StandingGenerator(weight)["e"][0]["value"]
    else:
        print("Wrong simulation name: retry")

    ##Printing all the values (1 minute acquisition)
    #print("Wrist acc:")
    #for i in range(len(wrist_cycle)):
    #    print(wrist_cycle[i])
    #print("Waist acc:")
    #for i in range(len(waist_cycle)):
    #    print(waist_cycle[i])
    #print("Pressure:")
    #for i in range(len(pressure_cycle)):
    #    print(pressure_cycle[i])

    plt.figure()
    plt.subplot(311)
    plt.plot(np.arange(0,60,2),wrist_cycle,'r')
    plt.ylim(0,10)
    plt.ylabel("Mean wrist frequency (Hz)")
    plt.xlabel("time (s)")
    plt.title("Wrist Accelerometer")
    plt.subplot(312)
    plt.plot(np.arange(0,60,2),waist_cycle,'b')
    plt.ylim(0,2)
    plt.ylabel("Time from last peak (s)")
    plt.xlabel("time (s)")
    plt.title("Waist Accelerometer")
    plt.subplot(313)
    plt.plot(np.arange(0,60,2),pressure_cycle,'g')
    plt.ylim(0,weight+10)
    plt.ylabel("pressure (kg)")
    plt.xlabel("time (s)")
    plt.title("Pressure sensor")
    plt.tight_layout()
    plt.show()

