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

        #Empty uri --> Error
        if len(uri)==0:
            raise cherrypy.HTTPError(400,"URL is empty: please insert valid url")
        else:
            #Get Topics from patient.json
            #uri type for sensor's topics --> localhost:8080/get_topics/sensor/patient1
            if uri[0]=="get_topics" and uri[1]=="sensor" and "patient" in uri[2]:
                patient=uri[2]
                deviceType = uri[1]
                patientID=patient.replace("patient","")
                for p in self.patient:
                    if int(p["patientID"])==int(patientID):
                        for device in p["deviceList"]:
                            if device["deviceType"] == deviceType:
                                for service in device["Services"]:
                                    if service["serviceType"] == "MQTT":
                                        self.topics.update({str(device["deviceID"]):str(service["topic"])})
                        print(json.dumps(self.topics))
                        return json.dumps(self.topics)
                    
            #uri type for actuators's topics --> localhost:8080/get_topics/actuator/patient1
            elif uri[0]=="get_topics" and uri[1]=="actuator" and "patient" in uri[2]:
                patient=uri[2]
                deviceType = uri[1]
                patientID=patient.replace("patient","")
                for p in self.patient:
                    if int(p["patientID"])==int(patientID):
                        for device in p["deviceList"]:
                            if device["deviceType"] == deviceType:
                                for service in device["Services"]:
                                    if service["serviceType"] == "MQTT":
                                        self.topics.update({str(device["deviceID"]):str(service["topic"])})
                        print(json.dumps(self.topics))
                        return json.dumps(self.topics)
                    
            #uri type for telebot and ThingSpeak adaptor topics --> localhost:8080/get_topics/Statistic_services/patient1
            elif uri[0]=="get_topics" and uri[1]=="Statistic_services" and "patient" in uri[2]:
                patient=uri[2]
                patientID=patient.replace("patient","")
                for p in self.patient:
                    if int(p["patientID"])==int(patientID):
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