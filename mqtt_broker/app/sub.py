#!/usr/bin/env python3
# python3.6

import random
import matplotlib.pyplot as plt
from matplotlib import colors
import numpy as np


from paho.mqtt import client as mqtt_client
from app.models.device import Device
from app.models.report import Report
from app.models.base import Base
from app.config import Config
from app.db import DB
from app.message_enum import MessageType as mt
from datetime import datetime as dt
import time
import json

from app.mqtt_to_thermal import copy_file, read_file, make_image, make_numpy_array
from app.mqtt_to_thermal import output_image

# broker = '10.194.90.55'
broker = '172.20.0.2'
port = 1883
topic = "/plant"  # TODO: CHANGE TO /plant/#
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-broker2-{random.randint(0, 100)}'
username = 'test2'
password = 'test2'
config = Config()
db = DB()

DEVICE_KEY = "device_id"
TYPE_KEY = "type"
BATTERY_KEY = "battery"
DESCRIPTION_KEY = "description"
TIMESTAMP_KEY = "time"

MINTEMP_KEY = "minTemp"
MAXTEMP_KEY = "maxTemp"
COUNT_KEY = "count"
COLORINDEX_KEY = "colorIndex"


def send_remote_status(client, device_id, count_thresh, min_thresh, max_thresh, color_thresh):
    with db.make_session() as session:
        device = session.query(Device).filter(Device.device_id == device_id).one_or_none()
        message_type = mt.power_on.name if device.remote_on else mt.power_off.name
        description = "refresh remote on" if device.remote_on else "refresh remote off"
        out = {DEVICE_KEY: device_id, TYPE_KEY: message_type,
               BATTERY_KEY: 0, DESCRIPTION_KEY: description,
                TIMESTAMP_KEY: str(dt.now()), MINTEMP_KEY: min_thresh,
                COUNT_KEY: count_thresh, MAXTEMP_KEY: max_thresh, COLORINDEX_KEY: color_thresh}
        json_obj = json.dumps(out)

        result = client.publish(topic, json_obj, qos=2)
        status = result[0]
        if status == 0:
            print(f"Send `{json_obj}` to topic `{topic}`")
        else:
            print(f"Failed to send message to topic {topic}")


def triage_message(userdata, msg, client):
    try:
        print("msg is ", msg.payload.decode())
        obj_in = json.loads(msg.payload.decode())
        type_enum = mt[obj_in['type']]
        device_id = obj_in['device_id']
        description = obj_in['description']
        battery = obj_in['battery']
        try:
            time = dt.fromisoformat(obj_in['time'])
        except Exception as e:
            time = dt.now()
            print("COULDN'T PARSE TIME", e, "USING", time)
    
    except Exception as e:
        print("Error occurred on message triage:")
        print(e)
        return

    with db.make_session() as session:
        device = session.query(Device).filter(Device.device_id == device_id).one_or_none()
        if type_enum == mt.pest or type_enum == mt.report:
            # Pest detected or Daily report
            status = "Pest detected" if type_enum == mt.pest else "Daily report"
            # TODO: FIX REPORT PRIMARY KEY
            print("TIME LISTED AS ", time)
            report = Report(device_id, status, description, battery, time)
            try:
                # writes image
                output_image(device_id, obj_in)

                # only for logging
                with open('/data/images/json_data.json', 'w') as outfile:
                    outfile.write(msg.payload.decode())
                

            except Exception as e:
                print("ERROR WRITING AND PARSING IMAGE", e)
            session.add(report)
        elif type_enum == mt.battery:
            # Battery update
            pass

        elif type_enum == mt.startup:
            # Manual On
            device.manual_on = True
            print("DEVICE ALIVE")
            if description != "pinging" or True:
                count_thresh = device.count_thresh
                min_thresh = device.min_thresh
                max_thresh = device.max_thresh
                color_thresh = device.color_thresh
                send_remote_status(client, device_id, count_thresh, min_thresh, max_thresh, color_thresh)

        elif type_enum == mt.shutdown:
            # Manual Off
            device.manual_on = False
            print("DEVICE DIED")
        
        else:
            # Undefined behavior
            print("UNDEFINED BEHAVIOR. TRIAGE FAILED")
            print(type_enum, msg.payload.decode())
            return
        device.battery = battery
        session.add(device)
        session.commit()
        print("COMMITTED. Remote is currently:", device.remote_on)


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
        print(f"Received msg {msg.payload.decode()} from {msg.topic} topic with {userdata}")
        triage_message(userdata, msg, client)

    client.on_message = on_message
    client.subscribe(topic, qos=2)


def subscribe_regular(client: mqtt_client):
    def on_message(client, userdata, msg):
        raw_message = msg.payload.decode()
        print(f"Received msg {msg.payload.decode()} from {msg.topic} topic with {userdata}")
        triage_message(userdata, msg, client)
        time.sleep(1)  # TODO: REMOVE TIME STOP
    client.subscribe(topic, qos=2)
    client.on_message = on_message


def subscribe_thermal(client: mqtt_client):
    def on_message(client, userdata, msg):
        f = open("output.txt", "a")
        f.write(msg.payload.decode() + "\n")
        f.close()
        # print(msg.payload.decode())
        if msg.payload.decode().find("t=767") != -1:
            copy_file()
            image_buffer = read_file()
            print(image_buffer)
            for index in range(len(image_buffer)):
                raw_values = make_numpy_array(image_buffer[index])
                make_image(raw_values, index)

    client.subscribe(topic, qos=2)
    client.on_message = on_message
        

def subscribe_image(client: mqtt_client):
    def on_message(client, userdata, msg):
        f = open("output.jpg", "wb")
        f.write(msg.payload)
        print("Image Received")
        f.close()
    client.subscribe(topic, qos=2)
    client.on_message = on_message

def main():
    client = connect_mqtt()

    # with open('json_data.json', 'w') as outfile:
        # outfile.write("test")

    # THERMAL
    # f = open("output.txt", "w")
    # f.close()
    # subscribe_thermal(client)  # ORIGINAL THERMAL CODE

    # DB PROCESSING
    # subscribe(client)  # DB PROCESSING

    # IMAGE WRITING
    subscribe_regular(client)  # FRANK'S WRITING CODE

    client.loop_forever()
