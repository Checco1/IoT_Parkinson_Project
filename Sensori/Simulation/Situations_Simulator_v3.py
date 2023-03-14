import matplotlib.pyplot as plt
import numpy as np
import paho.mqtt.client as PahoMQTT
import random
import time
import json
from WaistAcc_Simulator import *
from WristAcc_Simulator import *
from Pressure_Simulator import *
from copy import deepcopy

class sensors_MQTT():

    def __init__(self,patientID, port, broker, topic, sensor):

        self.clientID = str(patientID)
        self.port = port
        self.broker = broker
        self.topic = topic
        self._paho_mqtt = PahoMQTT.Client(self.clientID, True)
        self._paho_mqtt.on_connect = self.MyOnConnect
        
        self.bn = "marta/ParkinsonHelper/"
        self.patientID=patientID

        if sensor == "waist": n = "TimeLastPeak"
        elif sensor == "wrist": n = "MeanFrequencyAcceleration"
        else: n = "FeetPressure"

        self.structure = {"bn": self.bn+str(patientID)+self.topic,
                "e":
                    [
                        {
                            "n": n,
                            "u":"Hz",
                            "t":"",
                            "v":""
                        }
                    ]

        }
    # MQTT methods
    def start(self):
        self._paho_mqtt.connect(self.broker, self.port)
        self._paho_mqtt.loop_start()

    def publisher(self, msg):
        self._paho_mqtt.publish(self.topic, msg, 2)
        print("published: " + str(msg))

    def stop(self):
        self._paho_mqtt.unsubscribe(self.topic)
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()

    def MyOnConnect(self, paho_mqtt, user_data, flags, rc):
            print("connected " + self.topic)

if __name__ == "__main__":

    wrist_cycle = []
    waist_cycle = []
    pressure_cycle = []

    # Generate the simulation:
    patientID = input("Insert patient's ID: ")
    weight = 75
    wrist_Acc=WristSimulator(patientID)
    waist_Acc=WaistSimulator(patientID)
    pressure_sensor=PressureSimulator(patientID)
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
                wrist_cycle.append(deepcopy(wrist_Acc.NormalWristGenerator()))
                waist_cycle.append(deepcopy(waist_Acc.StopGenerator()))
                pressure_cycle.append(deepcopy(pressure_sensor.StandingGenerator(weight)))
            else:
                wrist_cycle.append(deepcopy(wrist_Acc.NormalWristGenerator()))
                waist_cycle.append(deepcopy(waist_Acc.NormalWalkGenerator()))
                pressure_cycle.append(deepcopy(pressure_sensor.StandingGenerator(weight)))
            print(waist_cycle[i])
    elif situation == "Falling":
        for i in range(30):
            if i == 15 or i == 25:
                wrist_cycle.append(deepcopy(wrist_Acc.NormalWristGenerator()))
                waist_cycle.append(deepcopy(waist_Acc.StopGenerator()))
                pressure_cycle.append(deepcopy(pressure_sensor.LyingGenerator()))
                
            elif i in range(16,25):
                wrist_cycle.append(deepcopy(wrist_Acc.NormalWristGenerator()))
                waist_cycle.append(deepcopy(waist_Acc.TwoGenerator()))
                pressure_cycle.append(deepcopy(pressure_sensor.LyingGenerator()))

            else:
                wrist_cycle.append(deepcopy(wrist_Acc.NormalWristGenerator()))
                waist_cycle.append(deepcopy(waist_Acc.NormalWalkGenerator()))
                pressure_cycle.append(deepcopy(pressure_sensor.StandingGenerator(weight)))
    elif situation == "Tremor":
        for i in range(30):
            if i in range(15,17):
                wrist_cycle.append(deepcopy(wrist_Acc.TremorGenerator()))
                waist_cycle.append(deepcopy(waist_Acc.NormalWalkGenerator()))
                pressure_cycle.append(deepcopy(pressure_sensor.StandingGenerator(weight)))
            else:
                wrist_cycle.append(deepcopy(wrist_Acc.NormalWristGenerator()))
                waist_cycle.append(deepcopy(waist_Acc.NormalWalkGenerator()))
                pressure_cycle.append(deepcopy(pressure_sensor.StandingGenerator(weight)))
    elif situation == "T+Fr":
        for i in range(30):
            if i in range(13,15):
                wrist_cycle.append(deepcopy(wrist_Acc.TremorGenerator()))
                waist_cycle.append(deepcopy(waist_Acc.NormalWalkGenerator()))
                pressure_cycle.append(deepcopy(pressure_sensor.StandingGenerator(weight)))
            elif i in range(15,17):
                wrist_cycle.append(deepcopy(wrist_Acc.TremorGenerator()))
                waist_cycle.append(deepcopy(waist_Acc.StopGenerator()))
                pressure_cycle.append(deepcopy(pressure_sensor.StandingGenerator(weight)))
            else:
                wrist_cycle.append(deepcopy(wrist_Acc.NormalWristGenerator()))
                waist_cycle.append(deepcopy(waist_Acc.NormalWalkGenerator()))
                pressure_cycle.append(deepcopy(pressure_sensor.StandingGenerator(weight)))
    elif situation == "Fr+Fa":
        for i in range(30):
            if i in range(13,15):
                wrist_cycle.append(deepcopy(wrist_Acc.NormalWristGenerator()))
                waist_cycle.append(deepcopy(waist_Acc.StopGenerator()))
                pressure_cycle.append(deepcopy(pressure_sensor.StandingGenerator(weight)))
            elif i == 15 or i == 25:
                wrist_cycle.append(deepcopy(wrist_Acc.NormalWristGenerator()))
                waist_cycle.append(deepcopy(waist_Acc.StopGenerator()))
                pressure_cycle.append(deepcopy(pressure_sensor.LyingGenerator()))
            elif i in range(16,25):
                wrist_cycle.append(deepcopy(wrist_Acc.NormalWristGenerator()))
                waist_cycle.append(deepcopy(waist_Acc.TwoGenerator()))
                pressure_cycle.append(deepcopy(pressure_sensor.LyingGenerator()))
            else:
                wrist_cycle.append(deepcopy(wrist_Acc.NormalWristGenerator()))
                waist_cycle.append(deepcopy(waist_Acc.NormalWalkGenerator()))
                pressure_cycle.append(deepcopy(pressure_sensor.StandingGenerator(weight)))
    elif situation == "T+Fa":
        for i in range(30):
            if i in range(13,15):
                wrist_cycle.append(deepcopy(wrist_Acc.TremorGenerator()))
                waist_cycle.append(deepcopy(waist_Acc.NormalWalkGenerator()))
                pressure_cycle.append(deepcopy(pressure_sensor.StandingGenerator(weight)))
            elif i == 15 :
                wrist_cycle.append(deepcopy(wrist_Acc.TremorGenerator()))
                waist_cycle.append(deepcopy(waist_Acc.StopGenerator()))
                pressure_cycle.append(deepcopy(pressure_sensor.LyingGenerator()))
            elif i in range(15,19):
                wrist_cycle.append(deepcopy(wrist_Acc.TremorGenerator()))
                waist_cycle.append(deepcopy(waist_Acc.TwoGenerator()))
                pressure_cycle.append(deepcopy(pressure_sensor.LyingGenerator()))
            elif i in range(19,25):
                wrist_cycle.append(deepcopy(wrist_Acc.NormalWristGenerator()))
                waist_cycle.append(deepcopy(waist_Acc.TwoGenerator()))
                pressure_cycle.append(deepcopy(pressure_sensor.LyingGenerator()))
            elif i == 25 :
                wrist_cycle.append(deepcopy(wrist_Acc.NormalWristGenerator()))
                waist_cycle.append(deepcopy(waist_Acc.StopGenerator()))
                pressure_cycle.append(deepcopy(pressure_sensor.LyingGenerator()))   
            else:
                wrist_cycle.append(deepcopy(wrist_Acc.NormalWristGenerator()))
                waist_cycle.append(deepcopy(waist_Acc.NormalWalkGenerator()))
                pressure_cycle.append(deepcopy(pressure_sensor.StandingGenerator(weight)))
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

    # Simulation rendering
    wrist_values = np.zeros(30)
    waist_values = np.zeros(30)
    pressure_values = np.zeros(30)

    print(waist_cycle)
    for j in range(30):
        wrist_values[j] = wrist_cycle[j]["e"][0]["v"]
        waist_values[j] = waist_cycle[j]["e"][0]["v"]
        pressure_values[j] = pressure_cycle[j]["e"][0]["v"]

    plt.figure()
    plt.subplot(311)
    plt.plot(np.arange(0,60,2),wrist_values,'r')
    plt.ylim(0,10)
    plt.ylabel("Mean wrist frequency (Hz)")
    plt.xlabel("time (s)")
    plt.title("Wrist Accelerometer")
    plt.subplot(312)
    plt.plot(np.arange(0,60,2),waist_values,'b')
    plt.ylim(0,2)
    plt.ylabel("Time from last peak (s)")
    plt.xlabel("time (s)")
    plt.title("Waist Accelerometer")
    plt.subplot(313)
    plt.plot(np.arange(0,60,2),pressure_values,'g')
    plt.ylim(0,weight+10)
    plt.ylabel("pressure (kg)")
    plt.xlabel("time (s)")
    plt.title("Pressure sensor")
    plt.tight_layout()
    plt.show()

    #MQTT parameters initialitation
    clientID1 = 'sensors1478523691'
    clientID2 = 'sensors1478523692'
    clientID3 = 'sensors1478523693'
    port = 1883
    broker = 'mqtt.eclipseprojects.io'
    waist_topic = '/sensors/waist_acc'
    wrist_topic = '/sensors/wrist_acc'
    pressure_topic = '/sensors/pressure'

    waist = sensors_MQTT(clientID1, port, broker, waist_topic, "waist")
    wrist = sensors_MQTT(clientID2, port, broker, wrist_topic, "wrist")
    pressure = sensors_MQTT(clientID3, port, broker, pressure_topic, "pressure")

    waist.start()
    wrist.start()
    pressure.start()

    for k in range(30):
        time.sleep(2)
        waist.publisher(json.dumps(waist_cycle[k]))
        wrist.publisher(json.dumps(wrist_cycle[k]))
        pressure.publisher(json.dumps(pressure_cycle[k]))

    waist.stop()
    wrist.stop()
    pressure.stop()


