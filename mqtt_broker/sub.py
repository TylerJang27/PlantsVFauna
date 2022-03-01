#!/usr/bin/env python3
# python3.6

import random
import matplotlib.pyplot as plt
from matplotlib import colors
import numpy as np


from paho.mqtt import client as mqtt_client
from mqtt.models.device import Device
from mqtt.models.report import Report
from mqtt.models.base import Base
from mqtt.config import Config
from mqtt.db import DB
from mqtt.message_enum import MessageType as mt
import time


# broker = '10.194.90.55'
broker = '127.0.0.1'
port = 1883
topic = "/plant"
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 100)}'
username = 'test'
password = 'test'
config = Config()
db = DB()


def triage_message(userdata, msg):
    try:
        obj_in = json.loads(msg)
        type_enum = mt[obj_in['type']]
        device_id = obj_in['device_id']
        description = obj_in['description']
        battery = obj_in['battery']
    
    except Exception as e:
        print("Error occurred on message triage:")
        print(e)
        return

    with db.make_session() as session:
        device = session.query(Device).filter(Device.device_id == device_id)
        if type_enum == mt.message or type_enum == mt.report:
            # Pest detected or Daily report
            status = "Pest detected" if type_enum == mt.message else "Daily report"
            report = Report(device_id, status, description, battery)
            session.add(report)
        elif type_enum == mt.battery:
            # Battery update
            pass

        elif type_enum == mt.startup.name:
            # Manual On
            device.manual_on = True

        elif type_enum == mt.shutdown.name:
            # Manual Off
            device.manual_on = False
        
        else:
            # Undefined behavior
            print("UNDEFINED BEHAVIOR. TRIAGE FAILED")
            return
        device.battery = battery
        session.add(device)
        session.commit()


heatmap_count = 0
image = np.zeros((24,32))
height = 0
width = 0
start_frame = 0
frame = []

def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        print("AHA!")
        print(f"Received {msg.payload.decode()} from {msg.topic} topic with {userdata}")
        triage_message(userdata, msg)

    client.subscribe(topic)
    client.on_message = on_message


def subscribe_thermal(client: mqtt_client):
    def on_message(client, userdata, msg):
        f = open("output.txt", "a")
        f.write(msg.payload.decode() + "\n")
        f.close()
        print(msg.payload.decode())

    client.subscribe(topic)
    client.on_message = on_message
        

def subscribe_image(client: mqtt_client):
    def on_message(client, userdata, msg):
        f = open("output.jpg", "wb")
        f.write(msg.payload)
        print("Image Received")
        f.close()
    client.subscribe(topic)
    client.on_message = on_message

def run():
    client = connect_mqtt()
    subscribe_thermal(client)
    client.loop_forever()


if __name__ == '__main__':
    time.sleep(2)
    print("HEYO")
    run()