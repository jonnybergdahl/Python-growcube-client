from enum import IntEnum
"""
Growcube client library
https://github.com/jonnybergdahl/Python-growcube-client

Author: Jonny Bergdahl
Date: 2023-09-05
"""


class Channel(IntEnum):
    """
    Enum representing watering channels

    :cvar Channel_A: Channel A
    :vartype Channel_A: int
    :cvar Channel_B: Channel B
    :vartype Channel_B: int
    :cvar Channel_C: Channel C
    :vartype Channel_C: int
    :cvar Channel_D: Channel D
    :vartype Channel_D: int
    """
    Channel_A = 0
    Channel_B = 1
    Channel_C = 2
    Channel_D = 3


class WateringMode(IntEnum):
    """
    Enum representing the configured watering mode

    :cvar Smart: Smart watering
    :vartype Smart: int
    :cvar SmartOutside: Smart watering "outside" (haven't seen this in use in the app)
    :vartype SmartOutside: int
    :cvar Scheduled: Scheduled watering
    :vartype Scheduled: int
    """
    Scheduled = 1
    SmartOutside = 2
    Smart = 3

class WorkMode(IntEnum):
    """
    Enum representing the configured work mode

    :cvar Direct: Direct connection, device as AP
    :vartype Direct: int
    :cvar Network: Network connection, connected as WiFi client
    :vartype Network: int
    """
    Direct = 1
    Network = 2