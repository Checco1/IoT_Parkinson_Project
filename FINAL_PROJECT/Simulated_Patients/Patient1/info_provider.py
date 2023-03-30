import cherrypy
import json

class InfoProvider():
    exposed = True
    def __init__(self):
        self.catalog=json.load(open("patient.json"))
        self.patient=self.catalog["patientList"]
        self.topics={}

    def GET(self,*uri):
        self.uri = uri
        self.topics={}
        found=0

        #Empty uri --> Error
        if len(uri)==0:
            raise cherrypy.HTTPError(400,"URL is empty: please insert valid url")
        else:
            #Get Topics from patient.json
            #uri type for sensor's topics --> localhost:8080/get_topics/sensor/patient1
            if uri[0]=="get_topics" and uri[1]=="sensor" and "patient" in uri[2]:
                patient=uri[2]
                deviceType = uri[1]
                patient_number=patient.replace("patient","")
                patientID = "p_"+str(patient_number)
                print(patient_number, patientID)
                for p in self.patient:
                    if p["patientID"]==patientID:
                        for device in p["deviceList"]:
                            if device["deviceType"] == deviceType:
                                for service in device["Services"]:
                                    if service["serviceType"] == "MQTT":
                                        self.topics.update({str(device["deviceID"]):str(service["topic"])})
                        print(json.dumps(self.topics))
                        return json.dumps(self.topics)
                    
            #uri type for actuators's topics 
            # --> localhost:8080/get_topics/actuator/patient1/<name_actuator>
            elif uri[0]=="get_topics" and uri[1]=="actuator" and "patient" in uri[2]:
                if len(uri)==3:
                    raise cherrypy.HTTPError(404,"Missing actuator: please, retry entering the name of the actuator to get its topic")
                else:
                    patient=uri[2]
                    deviceType = uri[1]
                    patient_number=patient.replace("patient","")
                    patientID = "p_"+str(patient_number)
                    deviceName = uri[3]+str(patient_number)
                    
                    for p in self.patient:
                        if p["patientID"]==patientID:
                            if "dbs" in deviceName or "soundfeedback" in deviceName:
                                for device in p["deviceList"]:
                                    if device["deviceType"] == deviceType and device["deviceID"]==(deviceName):
                                        for service in device["Services"]:
                                            if service["serviceType"] == "MQTT":
                                                self.topics.update({str(device["deviceID"]):str(service["topic"])})
                                                found=1
                                if found == 0:
                                    raise cherrypy.HTTPError(
                                                                status=404,
                                                                message=f"Actuator {deviceName} not found. Please retry entering the following\
                                                                actuators' name: dbs, soundfeedback, TeleBot or ThingSpeak"
                                                            )
                            elif "TeleBot" in deviceName or "ThingSpeak" in deviceName:
                                for service in p["Statistic_services"]:
                                    if service["ServiceName"] in deviceName:
                                        self.topics.update({str(service["ServiceName"]):str(service["topic"])})
                                        found = 1
                                if found == 0:
                                    raise cherrypy.HTTPError(
                                                                status=404,
                                                                message=f"Actuator {deviceName} not found. Please retry entering the following\
                                                                actuators' name: dbs, soundfeedback, TeleBot or ThingSpeak"
                                                            )
                            print(json.dumps(self.topics))
                            return json.dumps(self.topics)
                    
            #uri type for telebot and ThingSpeak adaptor topics --> localhost:8080/get_topics/Statistic_services/patient1
            elif uri[0]=="get_topics" and uri[1]=="Statistic_services" and "patient" in uri[2]:
                patient=uri[2]
                patient_number=patient.replace("patient","")
                patientID = "p_"+str(patient_number)
                for p in self.patient:
                    if p["patientID"]==patientID:
                        for service in p["Statistic_services"]:
                            self.topics.update({str(service["ServiceName"]):str(service["topic"])})
                        print(json.dumps(self.topics))
                        return json.dumps(self.topics)
                    
            #Get settings information from patient.json
            #uri type for broker and port --> localhost:8080/get_settings
            elif uri[0]=="get_settings":
                result={
                    "broker":self.catalog["broker"],
                    "port": self.catalog["port"]
                }
                print((json.dumps(result)))
                return json.dumps(result)
            
            #Wrong requests --> Error 404
            else:
                raise cherrypy.HTTPError(404,"Wrong request: please, retry entering the correct request")
            
if __name__ == "__main__":
    # Standard configuration to serve the url "localhost:8080"
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tool.session.on': True
        }
    }
    webService = InfoProvider()
    cherrypy.tree.mount(webService, '/', conf)
    cherrypy.engine.start()
    cherrypy.engine.block()