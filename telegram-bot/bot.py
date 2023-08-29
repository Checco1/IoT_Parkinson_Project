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
        self.url = "http://localhost:8080"

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
        else:
            if self.flag == 1:
                self.patientID()
            elif self.flag == 2:
                self.doctor_menu()

    def on_callback_query(self, msg):
        #content_type, chat_type ,self.chat_ID = telepot.glance(msg)
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
        print('Callback Query:', query_id, from_id, query_data)
        if (query_data == "doctor"):
            self.doctor()
        elif (query_data == "patient_list"):
            self.patient_list()
        elif (query_data == "patient_info"):
            self.patient_info()
        elif (query_data == "patient"):
            self.patient_login()
        elif (query_data == "actual_measure"):
            self.actual_measure()
        elif (query_data == "daily_episode"):
            self.daily_episode()
        elif (query_data == "back"):
            self.undo()


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
        self.flag = 2

        msg = ("This is the doctor section 👨🏼‍⚕️\n" + 
               "Insert the patient ID (patientN) on the textbox\n" +
               "Or retrive the list of Patients with the corresponding button\n")
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
                   [InlineKeyboardButton(text='Patient List', callback_data='patient_list')],
                   [InlineKeyboardButton(text='Back', callback_data='back')]
               ])

        """Procedure to delete the last message"""
        self.lastmsg = self.lastmsg["message_id"]
        self.bot.deleteMessage((self.chat_ID, self.lastmsg))      
        self.lastmsg = self.bot.sendMessage(self.chat_ID, text=msg, reply_markup=keyboard)
    
    def patient_list(self):
        
        self.position = "patient_list"

        request = self.url+"/patient"
        response = requests.get(request)
        response = response.json()
    
        list_msg = ("📋 Patient List\n" +
                    "|Patient Name|Patient ID|\n")

        if(response != -1):
            for patient in response["patients_list"]:
                list_msg = list_msg + (f"{patient['patientName']} | {patient['patientID']}\n")

        keyboard = InlineKeyboardMarkup(inline_keyboard=[[
                   InlineKeyboardButton(text='Back', callback_data='back')]])
        
        self.lastmsg = self.lastmsg["message_id"]
        self.bot.deleteMessage((self.chat_ID, self.lastmsg))      
        self.lastmsg = self.bot.sendMessage(self.chat_ID, text=list_msg, reply_markup=keyboard)
    
    def doctor_menu(self):

        self.position = "doctor_menu"
        self.flag = 3
        self.clientID = self.msg["text"]
        request = self.url+"/info/"+self.clientID
        response = requests.get(request)
        response = response.json()

        doctor_msg = (f"Selected Patient: {response['patientName']}\n" +
                      f"Choose One of the following action:\n" +
                      f"\n" +
                      f"👤 Patient Info: Retrive patient information\n" +
                      f"\n" +
                      f"📊 Actual measures: it is useful to check the mean value of each sensor.\n" +
                      f"\n" +
                      f"📅 Daily episodes: it will tell you how many episodes occurred today.\n" +
                      "\n"+
                      "Please wait, it will take few seconds ⌚")
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Patient Info', callback_data='patient_info')],
            [InlineKeyboardButton(text='Actual measures', callback_data='actual_measure')],
            [InlineKeyboardButton(text='Daily Episodes', callback_data='daily_episode')],
            [InlineKeyboardButton(text='Back', callback_data='back')]
            ])
        
        """Procedure to delete the last message"""
        self.lastmsg = self.lastmsg["message_id"]
        self.bot.deleteMessage((self.chat_ID, self.lastmsg))      
        self.lastmsg = self.bot.sendMessage(self.chat_ID, text=doctor_msg, reply_markup=keyboard)

    def patient_info(self):
        
        self.position = "patient_info"
        request = self.url+"/info/"+self.clientID
        response = requests.get(request)
        response = response.json()
        for services in response["Statistic_services"]:
            if services["ServiceName"] == "ThingSpeak":
                read_api = services["ReadApi"]
                TS_channel_ID = services["Channel_ID"]

        info_msg = ("📋 Here the personal information of the patient:\n" +
                    f"-Name and surname: {response['patientName']}\n" +
                    f"-Document ID: {response['patientDocument']}\n" +
                    f"-Personal channel ID: {TS_channel_ID}\n" +
                    f"-Personal Read API: {read_api}\n")
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[
           InlineKeyboardButton(text='Back', callback_data='back')]])
    
        """Procedure to delete the last message"""
        self.lastmsg = self.lastmsg["message_id"]
        self.bot.deleteMessage((self.chat_ID, self.lastmsg))      
        self.lastmsg = self.bot.sendMessage(self.chat_ID, text=info_msg, reply_markup=keyboard)

    def patient_login(self):

        self.position = "patient_page"

        msg = ("This is the patient section 🙎🏻‍♂️\n" +
               "Please write your Patient ID. \n" +
               "It must be \"patientN\" where N is your number\n")
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
        
        self.flag = 4

        """Procedure to delete the last message"""
        self.lastmsg = self.lastmsg["message_id"]
        self.bot.deleteMessage((self.chat_ID, self.lastmsg))   
        self.lastmsg = self.bot.sendMessage(self.chat_ID, text="Login...")
        
        self.clientID = self.msg["text"]
        # Subscribe to fall microservice
        self.notification = Notification("not1", "notification", self)
        self.notification.run()

        msg = ("Patient " + str(self.clientID) + 
               " has been logged correctly ✅")
        
        """Procedure to delete the last message"""
        self.lastmsg = self.lastmsg["message_id"]
        self.bot.deleteMessage((self.chat_ID, self.lastmsg))  
        self.lastmsg =  self.bot.sendMessage(self.chat_ID, text=msg)
        time.sleep(1)
        self.patient_menu()
    
    """Menu with all possible actions for the patient"""
    def patient_menu(self):

        self.position = "patient_menu"
        
        msg = ("This is the patient Menu 🙎🏻‍♂️\n" +
               "Please select one of these options. \n" +
               "\n"+
               "📊 Actual measures: it is useful to check the mean value of each sensor.\n"+
               "\n"+
               "📅 Daily episodes: it will tell you how many episodes occurred today.\n"+
               "\n"+
               "Please wait, it will take few seconds ⌚")
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Actual Measurements', callback_data='actual_measure'), InlineKeyboardButton(text='Daily Episodes', callback_data='daily_episode')],
                [InlineKeyboardButton(text='Back', callback_data='back')]
                ])
        
        """Procedure to delete the last message"""
        self.lastmsg = self.lastmsg["message_id"]
        self.bot.deleteMessage((self.chat_ID, self.lastmsg))  
        self.lastmsg =  self.bot.sendMessage(self.chat_ID, text=msg, reply_markup=keyboard)

    def actual_measure(self):
        self.position = "actual_measure"

        request = self.url+"/patient"
        response = requests.get(request)
        response = response.json()

        for patient in response["patients_list"]:
            if patient["patientID"] == self.clientID:
                for services in patient["Statistic_services"]:
                    if services["ServiceName"] == "ThingSpeak":
                        self.read_api = services["ReadApi"]
                        self.TS_url = services["URL"]
                        self.TS_channel_ID = services["Channel_ID"]

        request_url = "https://api.thingspeak.com/channels/"+str(self.TS_channel_ID)+"/feeds.json?api_key="+str(self.read_api)+"&average=10"
        response = requests.get(request_url)
        response = response.json()

        waist_m = response["feeds"][0]["field1"]
        if waist_m == None:
            waist_m = 0
        wrist_m = response["feeds"][0]["field2"]
        if wrist_m == None:
            wrist_m = 0
        pressure_m = response["feeds"][0]["field3"]
        if pressure_m == None:
            pressure_m = 0

        measure_msg = ("📋 Here the last measurements\n"+
                        f"👖 Waist: {waist_m} \n"+
                        f"⌚️ Wrist: {wrist_m} \n"+
                        f"👟 Pressure: {pressure_m} \n")

        keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text='Back', callback_data='back')]])
        
        self.lastmsg = self.lastmsg["message_id"]
        self.bot.deleteMessage((self.chat_ID, self.lastmsg))  
        self.lastmsg = self.bot.sendMessage(self.chat_ID, text=measure_msg, reply_markup=keyboard)

    def daily_episode(self):
        self.position = "daily_episode"

        counter_f4 = 0
        counter_f5 = 0
        counter_f6 = 0

        now = time.time()
        start_time = datetime.datetime.utcfromtimestamp(now).isoformat()
        current_day = start_time[:11]+"00:00:00.000000"
    
        request = self.url+"/patient"
        response = requests.get(request)
        response = response.json()

        for patient in response["patients_list"]:
            if patient["patientID"] == self.clientID:
                for services in patient["Statistic_services"]:
                    if services["ServiceName"] == "ThingSpeak":
                        #self.write_api = services["WriteApi"]
                        self.read_api = services["ReadApi"]
                        self.TS_url = services["URL"]
                        self.TS_channel_ID = services["Channel_ID"]

        request_url = "https://api.thingspeak.com/channels/"+str(self.TS_channel_ID)+"/fields/4.json?api_key="+str(self.read_api)+"&days=24"
        response = requests.get(request_url)
        response = response.json()

        for entries in response["feeds"]:
            if entries["field4"] != None:
                if entries["created_at"] >= current_day:
                    counter_f4 += 1

        request_url = "https://api.thingspeak.com/channels/"+str(self.TS_channel_ID)+"/fields/5.json?api_key="+str(self.read_api)+"&days=24"
        response = requests.get(request_url)
        response = response.json()

        for entries in response["feeds"]:
            if entries["field5"] != None:
                if entries["created_at"] >= current_day:
                    counter_f5 += 1

        request_url = "https://api.thingspeak.com/channels/"+str(self.TS_channel_ID)+"/fields/6.json?api_key="+str(self.read_api)+"&days=24"
        response = requests.get(request_url)
        response = response.json()

        for entries in response["feeds"]:
            if entries["field6"] != None:
                if entries["created_at"] >= current_day:
                    counter_f6 += 1

        episode_message = ("📋 Here are your results!\n"+
                           "\n"+
                           f"📌 Numer of falls: {counter_f4} \n"+
                           f"📌 Number of tremors: {counter_f5} \n"+
                           f"📌 Numer of freezings: {counter_f6} \n")
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text='Back', callback_data='back')]])
        
        self.lastmsg = self.lastmsg["message_id"]
        self.bot.deleteMessage((self.chat_ID, self.lastmsg))  
        self.lastmsg = self.bot.sendMessage(self.chat_ID, text=episode_message, reply_markup=keyboard)
        

    """Send a message when the command /help is issued."""
    def help(self):
        self.position = "help_page"
        
        help_message = ("👨🏽‍⚕️ This is your ParkinsonHelper Help menu!👩🏼‍🔧\n"
                        "After going back to the previous menu, you have to choose if you're a Doctor or a Patient.\n"
                        "\n"
                        "If you press 'Doctor' button, you will be able to:"
                        "📋 See the list of your patients, with name, surname and ID"
                        "📬 Require info about a specific patient"
                        "📅 See the daily episodes of one patient"
                        "📊 See the average value of the measurements acquired in the last minute of one patient"
                        "\n"
                        "If you press 'Patient', after inserting your ID you will be able to:"
                        "📅 See your daily episodes"
                        "📊 See the average value of the measurements acquired in the last minute"
                        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text='Back', callback_data='back')]])

        self.lastmsg = self.lastmsg["message_id"]
        self.bot.deleteMessage((self.chat_ID, self.lastmsg))  
        self.lastmsg = self.bot.sendMessage(self.chat_ID, text=help_message, reply_markup=keyboard)
        
    def undo(self):
        if (self.position == "help_page"):
            self.start()
        elif(self.position == "doctor_page"):
            self.start()
        elif(self.position == "patient_list"):
            self.doctor()
        elif(self.position == "doctor_menu"):
            self.doctor()
        elif(self.position == "patient_info"):
            self.doctor_menu()
        elif(self.position == "patient_page"):
            self.start()
        elif(self.position == "patient_menu"):
            self.notification.stop()
            self.patient_login()
        elif(self.position == "actual_measure"):
            if self.flag == 4:
                self.patient_menu()
            elif self.flag == 3:
                self.doctor_menu()
        elif(self.position == "daily_episode"):
            if self.flag == 4:
                self.patient_menu()
            elif self.flag == 3:
                self.doctor_menu()

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
        self.topic = [("ParkinsonHelper/" + self.clientID +"/microservices/#",2),("ParkinsonHelper/" + self.clientID +"/actuators/#",2)]
        self.telebot_instance = telebot_instance
        
    def run(self):
        """Run thread."""
        self.sub = MQTTsubscriber(self.clientID, self.broker, self.port,
                             self.topic, self.telebot_instance)
        self.sub.start()

        while self.sub.loop_flag:
            print("Waiting for connection...")
            time.sleep(1)
    
    def stop(self):
        self.sub.stop()

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
        topics = ["ParkinsonHelper/" + self.clientID +"/microservices/#", "ParkinsonHelper/" + self.clientID +"/actuators/#"]
        self._paho_mqtt.unsubscribe(topics)
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()

    def my_on_connect(self, client, userdata, flags, rc):
        """Define custom on_connect function."""
        print("S - Connected to %s - Res code: %d" % (self.messageBroker, rc))
        self.loop_flag = 0

    def my_on_message_received(self, client, userdata, msg):
        """Define custom on_message function."""
        message = json.loads(msg.payload.decode("utf-8"))
        #print(message)
        devID = message['bn']
        devID = devID.split('/')
        topic = devID[1]

        if topic == "tremor_manager":
            t = message["e"][0]["timeStamp"]
            episode = datetime.datetime.utcfromtimestamp(t).isoformat()
            tremor_message = ("⚠️ ATTENTION ⚠️\n"
                              "The Patient has suffered a tremor episode ⚡️\n"
                              "Date: " + f"{episode}")
            self.telebot.bot.sendMessage(self.telebot.chat_ID, text=tremor_message)
        elif topic == "freezing_manager":
            t = message["e"][0]["timeStamp"]
            episode = datetime.datetime.utcfromtimestamp(t).isoformat()
            freezing_message = ("⚠️ ATTENTION ⚠️\n"
                              "The Patient has suffered of a freezing episode ❄️\n"
                              "Date: " + f"{episode}")
            self.telebot.bot.sendMessage(self.telebot.chat_ID, text=freezing_message)
        elif topic == "fall_manager":
            t = message["e"][0]["timeStamp"]
            episode = datetime.datetime.utcfromtimestamp(t).isoformat()
            fall_message = ("⚠️ ATTENTION ⚠️\n"
                              "The Patient has suffered of a fall episode 💢\n"
                              "Date: " + f"{episode}")
            self.telebot.bot.sendMessage(self.telebot.chat_ID, text=fall_message)

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
