import cherrypy
import json

class InfoProvider():
    exposed = True
    def __init__(self):
        self.catalog=json.load(open("patient.json"))
        self.patient=self.catalog["patientList"]

    def GET(self,*uri):
        self.uri = uri
        if len(uri)==0:
            raise cherrypy.HTTPError(400,"URL is empty: please insert valid url")
        else:
            if uri[0]=="get_topics" and "patient" in uri[1]:
                patient=uri[1]
                patientID=patient.replace("patient","")
                for p in self.patient:
                    if int(p["patientID"])==int(patientID):
                        result = {
                            "waist_topic": p["deviceList"][0]["Services"][0]["topic"],
                            "wrist_topic": p["deviceList"][1]["Services"][0]["topic"],
                            "pressure_topic": p["deviceList"][2]["Services"][0]["topic"]
                        }
                        print(json.dumps(result))
                        return json.dumps(result)
            elif uri[0]=="get_settings":
                result={
                    "broker":self.catalog["broker"],
                    "port": self.catalog["port"]
                }
                print((json.dumps(result)))
                return json.dumps(result)
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