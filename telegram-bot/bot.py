#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Telegram bot for smart gardening."""
#from telegram.ext import Updater, CommandHandler
#from telegram import ParseMode
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
        with open(CONF, "r") as f:
            config = json.loads(f.read())

        self.url = config["cat_ip"]
        self.port = config["cat_port"]
        self.uri = "http://" + self.url + ":" + self.port + "/" + "api/telegramtoken"
        self.chatID = 0
        self.clientID = ""
        self.msg = {}
        #token = json.loads(requests.get(string).text)
        #token = token["token"]

        # Local token
        self.token = "6033951332:AAG2vwBOhgkv14NJbXM0csj7-0up6-ief9E"
        self.bot = telepot.Bot(self.token)
        MessageLoop(self.bot,{'chat': self.on_chat_message}).run_as_thread()

    def on_chat_message(self,msg):
        content_type, chat_type ,self.chat_ID = telepot.glance(msg)
        self.msg = msg
        message=msg['text']
        if (message == "/start"):
            self.start()
        elif (message == "/help"):
            self.help()
        elif(message.find("/login") != -1):
            self.patientID()
        elif(message == "/stats"):
            self.stats()

    """Send a message when the command /start is issued."""
    def start(self):
        
        msg = ("Welcome to the Parkinson Helper bot\n" +
            "Please write /login <patient_id> to log in\n" +
            "or write /help to get the full list of commands")
        self.bot.sendMessage(self.chat_ID, text=msg)
        

    """Send a message when the command /login is issued."""
    def patientID(self):
        self.bot.sendMessage(self.chat_ID, text="Login")
        message = self.msg["text"]
        self.clientID = message.split()[1]
        msg = ("Patient " + str(self.clientID) + 
               " has been logged correctly")
        self.bot.sendMessage(self.chat_ID, text=msg)

    """Send a message when the command /help is issued."""
    def help(self):
        
        help_message = ("*This is your Parkinson Helper Bot Help menu!*\n\n"
                        "You can perform the following actions:\n"
                        "- '/stats': Get your health statistics\n"
                        "- '/login': Log in with your patient ID\n"
                        )

        self.bot.sendMessage(self.chat_ID, text=help_message)

    """Get the statistics"""
    def stats(self):

        msg = "Retrieving the last sensor stats...\n"
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

class Notification(threading.Thread):
    def __init__(self, ThreadID, name):
        """Initialise thread with MQTT data."""
        threading.Thread.__init__(self)
        self.ThreadID = ThreadID
        self.name = name
        with open(CONF, "r") as f:
            config = json.loads(f.read())
        self.cat_url = config["cat_ip"]
        self.cat_port = config["cat_port"]
        self.topic = config["topic"]
        (self.broker_ip, mqtt_port) = broker_info(self.cat_url, self.cat_port)
        self.mqtt_port = int(mqtt_port)

    def run(self):
        """Run thread."""
        sub = MQTTsubscriber("telegrambot", self.broker_ip, self.mqtt_port,
                             self.topic, self.cat_url, self.cat_port)
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

        patientNumber = int(self.clientID.replace("patient", ''))
        waistSensorName = "waist_acc" + str(patientNumber)
        wristSensorName = "wrist_acc" + str(patientNumber)
        pressureSensorName = "pressure" + str(patientNumber)
        print(waistSensorName)
        if(receivedActuator == waistSensorName):
            self.waist_acc_received = 1
            msg_to_send = "Printing the Waist Accelerometer values for the last 60s\n" +\
            "Received at: "
        if(receivedActuator == wristSensorName):
            self.wrist_acc_received = 1
            msg_to_send = "Printing the Waist Accelerometer values for the last 60s\n" +\
            "Received at: "
        if(receivedActuator == pressureSensorName):
            self.pressure_received = 1
            msg_to_send = "Printing the Pressure values for the last 60s\n" +\
            "Received at: "

        msg_to_send = msg_to_send + str(sensor_info["e"][0]["timeStamp"]) + '\n' + \
        str(sensor_info["e"][0]["value"])
        print(msg_to_send)
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
    """Setup and start the bot.

    Run the bot until you press Ctrl-C or the process receives SIGINT,
    SIGTERM or SIGABRT. This should be used most of the time, since
    start_polling() is non-blocking and will stop the bot gracefully.
    """
    
    # Activate different commands.
    #dp.add_handler(CommandHandler("start", start))
    #dp.add_handler(CommandHandler("help", help))
    #dp.add_handler(CommandHandler("status", status, pass_args=True))
    #dp.add_handler(CommandHandler("values", values, pass_args=True))
    #dp.add_handler(CommandHandler("irrigate", irrigation))

    # Log all errors.
    #dp.add_error_handler(error)

    # Start the Bot.
    #updater.start_polling()

    telebot = MyBot()
    
    #notification = Notification("not1", "notification")
    #notification.start()

    #updater.idle()
    while True:
        pass


if __name__ == '__main__':
    main()
