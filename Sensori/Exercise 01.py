import json

class Catalog:
    def __init__(self, jsonFile):
        self.catalog = json.load(open('catalog.json'))
        self.broker = self.catalog["broker"]
        self.devices = self.catalog["devicesList"]
    
    def searchByName(self, name):
        for device in self.catalog["devicesList"]:
            if (device["deviceName"] == name):
                print(device)
    
    def searchByID(self, id):
        for device in self.catalog["devicesList"]:
            if (device["deviceID"] == int(id)):
                print(device)
    
    def searchByService(self, service):
        for device in self.catalog["devicesList"]:
            for serv in device["servicesDetails"]:
                if (serv["serviceType"] == service):
                    print(device)
                    break
    
       #ciaooooo         
        
if __name__ == "__main__":
    C = Catalog('catalog.json') 
    #C.searchByName("DHT11")
    #C.searchByID("2")
    C.searchByService("REST")