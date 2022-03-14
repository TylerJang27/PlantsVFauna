# python3.6

import random
import time

from paho.mqtt import client as mqtt_client
from .pub_helper import generate_message


broker = '127.0.0.1'
port = 1883
topic = "/plant"
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 100)}'
username = 'test'
password = 'test'

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


def publish_json(client, json_obj):
    # TODO: ADD ERROR HANDLING
    result = client.publish(topic, json_obj)
    status = result[0]
    if status == 0:
        print(f"Send `{json_obj}` to topic `{topic}`")
    else:
        print(f"Failed to send message to topic {topic}")


def test_publish(client):
    msg_count = 0
    while True:
        time.sleep(1)
        description = "My message number is {}".format(msg_count)
        out = generate_message(description)
        publish_json(client, out)
        msg_count += 1


def run():
    client = connect_mqtt()
    client.loop_start()
    test_publish(client)


if __name__ == '__main__':
    run()
