from MyMQTT import *

class MyMicroservice():
    def __init__(self, clientID, broker, port, topic):
        self.topic = topic
        self.client = MyMQTT(clientID,broker,port,self)

    def start(self):
        self.client.start()
        self.client.mySubscribe(self.topic)

    def stop(self):
        self.client.stop()

    def notify(self, topic, msg):
        d = json.loads(msg)
        #print(d)
        value = d["e"][0]["value"]
        client = d["bn"]
        print(f"The sensor {client} have sent the value {value} with the topic {topic}")

if __name__ == "__main__":
    conf=json.load(open("settings.json"))
    broker = conf["broker"]
    port = conf["port"]
    baseTopic = conf["baseTopic"]
    topic = baseTopic+"/#"
    subscriber = MyMicroservice("MySubscriber", broker, port, topic)
    subscriber.start()

    while True:
        pass