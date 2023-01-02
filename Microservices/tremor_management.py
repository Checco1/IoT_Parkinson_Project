# 1st. Read information from device connectors (wrist accelerometer) via MQTT
# 2nd. Check if the frequency of the accelerometer is between 4 - 9 Hz
# 3rd. If the frequency is in that range for a period of time, a tremor is occuring
# 4th . Send the data to the statistics manager
# 5th. Send a message to the ThingSpeak adaptor if a tremor is detected

import time

class tremor_management():

    def __init__ (self, patientID):

        self.bn = "marta/ParkinsonHelper/"
        self.patientID=patientID

        self.structure = {"bn": self.bn+str(patientID)+"/tremor_manager",
                "e":
                    [
                        {
                            "microservice":"tremor_manager",
                            "unit":"Hz",
                            "timeStamp":"",
                            "last_tremor_timeStamp"
                            "wristAcc_value":"",
                            "tremor_flag": "",
                        }
                    ]

        }

if __name__ == "__main__":

    tremor = 0 #will be 1 if tremor

    #start of MQTT connection
    sensor_info = # this will be the read structure from the sensor
    patientID = sensor_info["bn"]

    # Detect when the value of the frequency changes 

    # Check the value of the wrist accelerometer frequency
    wrist_freq = sensor_info["e"][0]["value"]

    if (wrist_freq >= 4) and (wrist_freq <= 9):
        tremor = 1
        tremor_ts = sensor_info["e"][0]["timeStamp"]
        print ("Tremor situation at " + str(tremor_ts) + "s")
    else:
        tremor = 0

    # Creation of the MQTT message to send to the actuators
    tremor_msg = tremor_management(patientID)
    tremor_msg.structure["e"][0]["timeStamp"] = sensor_info["e"][0]["timeStamp"]
    tremor_msg.structure["e"][0]["last_tremor_timeStamp"] = tremor_ts
    tremor_msg.structure["e"][0]["wristAcc_value"] = wrist_freq
    tremor_msg.structure["e"][0]["tremor_flag"] = str(tremor)

    
