# python3.6

import random

from paho.mqtt import client as mqtt_client


broker = '172.20.0.2'
port = 1883
topic = "/plant"
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(50, 100)}'
# TODO: CHANGE CREDS
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


def send_announcement(device_id, turn_on):
    try:
        msg = "turn {} device {}".format("ON" if turn_on else "OFF", device_id)
        print("SENDING MESSAGE")
        client = connect_mqtt()
        client.loop_start()  # TODO: TROUBLESHOOT THIS
        publish(client, device_id, msg)
    except Exception as e:
        print(e)
        print("UNKNOWN ERROR WITH SENDING MESSAGE")


if __name__ == '__main__':
    run()
