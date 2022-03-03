from enum import Enum

class MessageType(Enum):
    pest = 1
    report = 2
    power_on = 3
    power_off = 4
    battery = 5
    startup = 6
    shutdown = 7