import json
import cherrypy
import time
import requests
import threading
from pathlib import Path


P = Path(__file__).parent.absolute()
SERVICE_CATALOG = P / 'service_catalog.json'
RESUORCE_CATALOG = P / 'resource_catalog.json'
MAXDELAY = 300

class Catalog(object):
    def __init__(self):
        self.filename_service = SERVICE_CATALOG
        self.filename_resource = RESUORCE_CATALOG
    
    def load_file(self):
        """Load static and dynamic parts of catalog.
        Load data (static, dynamic) from json files and get MQTT broker IP
        and MQTT broker port saved on static file.
        """
        loaded = 0
        while not loaded:
            try:
                with open(self.filename_service, "r") as fs:
                    self.service = json.loads(fs.read())
                with open(self.filename_resource, "r") as fd:
                    self.resource = json.loads(fd.read())
                loaded = 1
            except Exception:
                print("Problem in loading catalogs, retrying...")
                time.sleep(.5)

        self.broker_ip = self.service["broker"]["IP"]
        self.mqtt_port = self.service["broker"]["mqtt_port"]

    def write_service(self):
        """Write data on service json file."""
        with open(self.filename_service, "w") as fs:
            json.dump(self.service, fs, ensure_ascii=False, indent=2)
            fs.write("\n")

    def write_resource(self):
        """Write data on resource json file."""
        with open(self.filename_resource, "w") as fd:
            json.dump(self.resource, fd, ensure_ascii=False, indent=2)
            fd.write("\n")

    def add_patient(self, patient_json):
        # patient_json will be the body in the POST method
        # Look at the existing patient IDs.
        self.load_file()
        list_id = []

        for p in self.service["patients_list"]:
            list_id.append(p["patientID"])

        # Generate a new gardenID starting from 1000 and taking the first free
        # number which is available.
        numID = 1
        new_id = numID

        while new_id in list_id:
            numID += 1
            new_id = numID

        patient_json["patientName"] = ""
        patient_json["device_list"] = []
        patient_json["patientID"] = new_id
        print(patient_json)

        self.service["patients_list"].append(patient_json)
        garden_res_json = {
            "patientID": patient_json["patientID"],
            "device_list": []
        }
        self.resource["patients_list"].append(garden_res_json)
        self.write_service()
        self.write_resource()


def main():
    cc = Catalog()
    d = {
                "patientName": "",
                "device_list": [],
        }
    cc.add_patient(d)

if __name__ == '__main__':
    main()