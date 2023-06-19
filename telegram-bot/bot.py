import logging
import json
import requests
import time
import datetime
import paho.mqtt.client as PahoMQTT
import numpy as np
import threading
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from pathlib import Path

P = Path(__file__).parent.absolute()
CONF = P / 'conf.json'

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - '
                           '"%(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


class MyPublisher(object):
    """MQTT Publisher."""

    def __init__(self, clientID, serverIP, port):
        """Initialise MQTT client."""
        self.clientID = clientID + '_pub'
        self.devID = clientID
        self.port = int(port)
        self.messageBroker = serverIP
        self._paho_mqtt = PahoMQTT.Client(clientID, False)
        self._paho_mqtt.on_connect = self.my_on_connect
        self.loop_flag = 1

    def start(self):
        """Start publisher."""
        self._paho_mqtt.connect(self.messageBroker, self.port)
        self._paho_mqtt.loop_start()

    def stop(self):
        """Stop publisher."""
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()

    def my_on_connect(self, client, userdata, flags, rc):
        """Define custom on_connect function."""
        print("P - Connected to %s - Res code: %d" % (self.messageBroker, rc))
        self.loop_flag = 0

    def my_publish(self, message, topic):
        """Define custom publish function."""
        print(json.dumps(json.loads(message), indent=2))
        self._paho_mqtt.publish(topic, message, 2)
        print("Publishing on %s:" % topic)


class MyBot:
    def __init__(self):
        
        self.flag = 0
        self.position = "home_page"
        self.chatID = 0
        self.lastmsg = 0
        self.clientID = ""
        self.msg = {}

        # Local token
        self.token = "6033951332:AAG2vwBOhgkv14NJbXM0csj7-0up6-ief9E"
        self.bot = telepot.Bot(self.token)
        MessageLoop(self.bot,{'chat': self.on_chat_message, 'callback_query': self.on_callback_query}).run_as_thread()

    def on_chat_message(self,msg):
        content_type, chat_type ,self.chat_ID = telepot.glance(msg)
        self.msg = msg
        print (msg)
        message=msg['text']
        if (message == "/start"):
            self.start()
        elif (message == "/help"):
            self.help()
        elif(message == "/stats"):
            self.stats()
        else:
            if self.flag == 1:
                self.patientID()


    def on_callback_query(self, msg):
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
        print('Callback Query:', query_id, from_id, query_data)
        if (query_data == "doctor"):
            self.doctor()
        elif (query_data == "patient"):
            self.patient_login()
        elif (query_data == "back"):
            self.undo()
           
        
        #Example of Notification
        #self.bot.answerCallbackQuery(query_id, text='Got it')

    """Send a message when the command /start is issued."""
    def start(self):
        if (self.position != "home_page"):
            self.lastmsg = self.lastmsg["message_id"]
            self.bot.deleteMessage((self.chat_ID, self.lastmsg))

        self.position = "home_page"

        msg = ("Welcome to the Parkinson Helper bot 🏥\n" +
               "Touch your credentials or write /help to get the full list of commands")
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
                   [InlineKeyboardButton(text='Doctor', callback_data='doctor'),InlineKeyboardButton(text='Patient', callback_data='patient')],
               ])

        self.lastmsg = self.bot.sendMessage(self.chat_ID, text=msg, reply_markup=keyboard)
        
    def doctor(self):
        
        self.position = "doctor_page"

        msg = ("This is the doctor section 👨🏼‍⚕️\n" + 
               "Please select the funcionality:\n")
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
                   [InlineKeyboardButton(text='MQTT', callback_data='mqtt'),InlineKeyboardButton(text='ThingSpeak', callback_data='ts')],
                   [InlineKeyboardButton(text='Back', callback_data='back')]
               ])
        """Procedure to delete the last message"""
        self.lastmsg = self.lastmsg["message_id"]
        self.bot.deleteMessage((self.chat_ID, self.lastmsg))      
        self.lastmsg = self.bot.sendMessage(self.chat_ID, text=msg, reply_markup=keyboard)
    
    def patient_login(self):

        self.position = "patient_page"

        msg = ("This is the patient section 🙎🏻‍♂️\n" +
               "Please write your Patient ID. \n" +
               "It must be \"patient_N\" where N is your number\n")
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[
                   InlineKeyboardButton(text='Back', callback_data='back')]])
        
        self.flag = 1
        
        """Procedure to delete the last message"""
        self.lastmsg = self.lastmsg["message_id"]
        self.bot.deleteMessage((self.chat_ID, self.lastmsg))      
        self.lastmsg = self.bot.sendMessage(self.chat_ID, text=msg, reply_markup=keyboard)

    """Send a message when the patient insert its information"""
    def patientID(self):
        self.position = "login_page"
        
        self.flag = 0
        
        self.lastmsg = self.lastmsg["message_id"]
        self.bot.deleteMessage((self.chat_ID, self.lastmsg))   
        self.lastmsg = self.bot.sendMessage(self.chat_ID, text="Login...")
        
        self.clientID = self.msg["text"]
        # Subscribe to fall microservice
        notification = Notification("not1", "notification", self)
        notification.run()

        msg = ("Patient " + str(self.clientID) + 
               " has been logged correctly ✅")
        
        """Procedure to delete the last message"""
        self.lastmsg = self.lastmsg["message_id"]
        self.bot.deleteMessage((self.chat_ID, self.lastmsg))  
        self.lastmsg =  self.bot.sendMessage(self.chat_ID, text=msg)

        self.patient_menu()
    
    """Menu with all possible actions for the patient"""
    def patient_menu(self):
        




        pass

    """Send a message when the command /help is issued."""
    def help(self):
        self.position = "help_page"
        
        help_message = ("*This is your Parkinson Helper Bot Help menu!\n"
                        "You can perform the following actions:\n"
                        "- '/stats': Get your health statistics 📈\n"
                        "- '/login': Log in with your patient ID 🪪\n"
                        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text='Back', callback_data='back')]])

        self.lastmsg = self.lastmsg["message_id"]
        self.bot.deleteMessage((self.chat_ID, self.lastmsg))  
        self.lastmsg = self.bot.sendMessage(self.chat_ID, text=help_message, reply_markup=keyboard)

    """Get the statistics"""
    def stats(self):

        msg = "📊 Retrieving the last sensor stats...\n"
        self.bot.sendMessage(self.chat_ID, text=msg)

        uri_broker = 'http://localhost:8080/broker'
        settings = requests.get(uri_broker).json()
        port = int(settings["mqtt_port"])
        broker = settings["IP"]
        mqtt_id = self.clientID
        topic = "ParkinsonHelper/" + self.clientID +"/actuator/statistics"
        stats_subscriber = MQTTsubscriber(mqtt_id, broker, port, topic, self)
        stats_subscriber.start()
        print("Subscribed to patient: " + topic)
    
    def undo(self):
        if (self.position == "help_page"):
            self.start()
        elif(self.position == "doctor_page"):
            self.start()
        elif(self.position == "patient_page"):
            self.start()

class Notification(threading.Thread):
    def __init__(self, ThreadID, name, telebot_instance):
        """Initialise thread with MQTT data."""
        threading.Thread.__init__(self)
        self.ThreadID = ThreadID
        self.name = name
        uri_broker = 'http://localhost:8080/broker'
        settings = requests.get(uri_broker).json()
        self.port = int(settings["mqtt_port"])
        self.broker = settings["IP"]
        self.clientID = telebot_instance.clientID
        self.topic = "ParkinsonHelper/" + self.clientID +"/actuator/fall"
        self.telebot_instance = telebot_instance
        
    def run(self):
        """Run thread."""
        sub = MQTTsubscriber(self.clientID, self.broker, self.port,
                             self.topic, self.telebot_instance)
        sub.start()

        while sub.loop_flag:
            print("Waiting for connection...")
            time.sleep(1)


class MQTTsubscriber(object):
    
    def __init__(self, clientID, serverIP, port, topic, telebot_instance):
        """Initialise MQTT client."""
        self.clientID = clientID
        self.messageBroker = serverIP
        self.port = port
        self.topic = topic
        self.telebot = telebot_instance
        self._paho_mqtt = PahoMQTT.Client(self.clientID, False)
        self._paho_mqtt.on_connect = self.my_on_connect
        self._paho_mqtt.on_message = self.my_on_message_received
        self.loop_flag = 1
        self.waist_acc_received = 0
        self.wrist_acc_received = 0
        self.pressure_received = 0

    def start(self):
        """Start subscriber."""
        self._paho_mqtt.connect(self.messageBroker, self.port)
        self._paho_mqtt.loop_start()
        self._paho_mqtt.subscribe(self.topic, 2)

    def stop(self):
        """Stop subscriber."""
        self._paho_mqtt.unsubscribe(self.topic)
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()

    def my_on_connect(self, client, userdata, flags, rc):
        """Define custom on_connect function."""
        print("S - Connected to %s - Res code: %d" % (self.messageBroker, rc))
        self.loop_flag = 0

    def my_on_message_received(self, client, userdata, msg):
        """Define custom on_message function."""
        print("msg received")
        msg_to_send = ""
        sensor_info = json.loads(msg.payload)
        print(sensor_info)
        # Retrieve sensor and ID from the "bn field"
        sensor_id = sensor_info["bn"]

        sensorParameters = sensor_id.split('/')
        receivedActuator = sensorParameters[1]
        if (msg.topic == "ParkinsonHelper/" + self.clientID +"/actuator/statistics" ):
            patientNumber = int(self.clientID.replace("patient", ''))
            waistSensorName = "waist_acc" + str(patientNumber)
            wristSensorName = "wrist_acc" + str(patientNumber)
            pressureSensorName = "pressure" + str(patientNumber)
            print(waistSensorName)
            if(receivedActuator == waistSensorName):
                self.waist_acc_received = 1
                msg_to_send = "Printing the Waist Accelerometer values for the last 30s\n" +\
                "Received at: "
            if(receivedActuator == wristSensorName):
                self.wrist_acc_received = 1
                msg_to_send = "Printing the Waist Accelerometer values for the last 30s\n" +\
                "Received at: "
            if(receivedActuator == pressureSensorName):
                self.pressure_received = 1
                msg_to_send = "Printing the Pressure values for the last 30s\n" +\
                "Received at: "

            msg_to_send = msg_to_send + str(sensor_info["e"][0]["timeStamp"]) + '\n' + \
            str(sensor_info["e"][0]["value"])
            print(msg_to_send)
            self.telebot.bot.sendMessage(self.telebot.chat_ID, text=msg_to_send)
            if(self.waist_acc_received == self.wrist_acc_received == self.pressure_received == 1):
                self.waist_acc_received = 0
                self.wrist_acc_received = 0
                self.pressure_received = 0
                self.stop()
        
        elif(msg.topic == "ParkinsonHelper/" + self.clientID +"/actuator/fall" ):
            print("fall notification")
            msg_to_send = "⚠️ATTENTION: " + self.clientID + "has suffered a fall!"
            self.telebot.bot.sendMessage(self.telebot.chat_ID, text=msg_to_send)


def broker_info(url, port):
    """Get broker information.

    Send GET request to catalog in order to obtain MQTT broker IP and
    port.
    """
    string = "http://" + url + ":" + port + "/broker"
    broker = requests.get(string)
    broker_ip = json.loads(broker.text)["IP"]
    mqtt_port = json.loads(broker.text)["mqtt_port"]
    return (broker_ip, mqtt_port)


def main():

    telebot = MyBot()
    
    while True:
        pass


if __name__ == '__main__':
    main()
