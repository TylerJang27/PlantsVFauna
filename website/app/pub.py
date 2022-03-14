# python3.6

import json
import random
import time

from paho.mqtt import client as mqtt_client
from datetime import datetime as dt

broker = '172.20.0.2'
port = 1883
topic = "/plant"
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(50, 100)}'
# TODO: CHANGE CREDS
username = 'test'
password = 'test'

DEVICE_KEY = "device_id"
TYPE_KEY = "type"
BATTERY_KEY = "battery"
DESCRIPTION_KEY = "description"
TIMESTAMP_KEY = "time"


def connect_mqtt():
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


def publish(client, device_id, msg):
    # TODO: USE DEVICE_ID
    result = client.publish(topic, msg)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{topic}`")
    else:
        print(f"Failed to send message to topic {topic}")


def run():
    client = connect_mqtt()
    client.loop_start()
    publish(client)


def generate_on_off(device_id, turn_on):
    d = {DEVICE_KEY: device_id, TYPE_KEY: "power_on" if turn_on else "power_off",
         BATTERY_KEY: 50, DESCRIPTION_KEY: "turn on" if turn_on else "turn off",
         TIMESTAMP_KEY: str(dt.now())}
    return json.dumps(d)


# TODO: ADD ADDITIONAL METHODS DEPENDING ON BEHAVIOR
def send_announcement(device_id, turn_on):
    try:
        msg = generate_on_off(device_id, turn_on)
        print("SENDING MESSAGE to {}".format("TURN ON" if turn_on else "TURN OFF"))
        client = connect_mqtt()
        client.loop_start()  # TODO: TROUBLESHOOT THIS
        publish(client, device_id, msg)

        time.sleep(5)
        client.loop_stop()
    except Exception as e:
        print(e)
        print("UNKNOWN ERROR WITH SENDING MESSAGE")


if __name__ == '__main__':
    run()
