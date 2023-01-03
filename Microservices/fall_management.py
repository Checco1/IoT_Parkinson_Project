# 1st. Read information from device connectors (waist accelerometer and pressure) via MQTT
# 2nd. Check if:
#   pressure is between 4.9-5.1 (pressure)
#   last stop peak 1.69-1.71 (waist)
# 3rd. If both conditions are detected, then a falling is happening
# 4th. Send the data to the statistics manager
# 5th. Send a message to the Telebot if a fall is detected

import time

class fall_management():

    def __init__ (self, patientID):

        self.bn = "marta/ParkinsonHelper/"
        self.patientID=patientID

        self.structure = {"bn": self.bn+str(patientID)+"/fall_manager",
                "e":
                    [
                        {
                            "microservice":"fall_manager",
                            "unit":"s",
                            "timeStamp":"",
                            "last_fall_timeStamp"
                            "stop_timeStamp":"",
                            "pressure_value":"",
                            "waist_acc_value":"",
                            "fall_flag": "",
                        }
                    ]

        }

if __name__ == "__main__":

    stop_flag = 0 #will be 1 if there's a stop
    pressure_flag = 0 #will be 1 if pressure lies
    fall_flag = 0 # will be 1 when a fall is detected 

    #start of MQTT connection
    waist_info = # this will be the read structure from the waist acc sensor
    pressure_info = # this will be the read structure from the waist acc sensor
    patientID = waist_info["bn"]

    # Detect when the value of the waist acc frequency and the pressure changes 

    # Check the value of the waist accelerometer frequency
    # When we create the MQTT part, this would be inside a notify method, so we will only 
    # execute this part when the value of the waist sensor changes
    waist_freq = waist_info["e"][0]["value"]

    if (waist_freq >= 1.69) and (waist_freq <= 1.71):
        stop_flag = 1
        stop_ts = waist_info["e"][0]["timeStamp"]
        print ("Stop at " + str(stop_ts) + "s")
    else:
        stop_flag = 0

    # Check the value of the pressure sensor
    # When we create the MQTT part, this would be inside a notify method, so we will only 
    # execute this part when the value of the pressure sensor changes
    pressure = pressure_info["e"][0]["value"]

    if (pressure >= 4.9) and (pressure <= 5.1):
        pressure_flag = 1
        pressure_ts = pressure_info["e"][0]["timeStamp"]
        print ("Pressure lying at " + str(stop_ts) + "s")
    else:
        pressure_flag = 0

    if (pressure_flag == 1) and (stop_flag == 1):
        fall_flag = 1
    else:
        fall_flag = 0


    # Creation of the MQTT message to send to the actuators
    fall_msg = fall_management(patientID)
    fall_msg.structure["e"][0]["timeStamp"] = time.time()
    fall_msg.structure["e"][0]["last_fall_timeStamp"] = pressure_ts
    fall_msg.structure["e"][0]["stop_timeStamp"] = stop_ts
    fall_msg.structure["e"][0]["pressure_value"] = pressure
    fall_msg.structure["e"][0]["waist_acc_value"] = waist_freq
    fall_msg.structure["e"][0]["tremor_flag"] = str(fall_flag)

    # MQTT to communicate with telebot and statistics manager

    
