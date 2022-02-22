#!/usr/bin/env python3
# python3.6

import random

from paho.mqtt import client as mqtt_client
from mqtt.models.device import Device
from mqtt.models.report import Report

from mqtt.models.base import Base
from mqtt.config import Config
from mqtt.db import DB
import time


# broker = '10.197.54.17'
broker = '127.0.0.1'
port = 1883
topic = "/plant"
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 100)}'
username = 'test'
password = 'test'
config = Config()
db = DB()

def handle_message(userdata, msg):
    with db.make_session() as session:
        # TODO: TRIAGE BASED ON MESSAGE TYPE
        pass
        # obj = obj
        # session.add(obj)
        # session.commit()

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
        handle_message(userdata, msg)

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
    subscribe(client)
    client.loop_forever()


if __name__ == '__main__':
    time.sleep(2)
    print("HEYO")
    run()