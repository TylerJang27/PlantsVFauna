import json
from datetime import datetime as dt
from .message_enum import MessageType as mt

DEVICE_KEY = "device_id"
TYPE_KEY = "type"
BATTERY_KEY = "battery"
DESCRIPTION_KEY = "description"
TIMESTAMP_KEY = "time"


def serialize_json(message_type, description):
    out = {DEVICE_KEY: get_id(), TYPE_KEY: message_type,
           BATTERY_KEY: get_battery(), DESCRIPTION_KEY: description,
           TIMESTAMP_KEY: str(dt.now())}
    return json.dumps(out)


def get_id():
    # TODO, probs configuration
    return 1


def get_battery():
    # TODO, probs circuitry
    return 50


def generate_message(description):
    return serialize_json(mt.pest.name, description)


def generate_report(description):
    return serialize_json(mt.report.name, description)


def generate_battery(description):
    return serialize_json(mt.battery.name, description)


def generate_manual_on(description):
    return serialize_json(mt.startup.name, description)


def generate_manual_off(description):
    return serialize_json(mt.shutdown.name, description)
