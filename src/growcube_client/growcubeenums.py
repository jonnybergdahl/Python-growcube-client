from enum import Enum
"""
Growcube client library
https://github.com/jonnybergdahl/Python-growcube-client

Author: Jonny Bergdahl
Date: 2023-09-05
"""


class Channel(Enum):
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
    Channel_A: int = 0
    Channel_B: int = 1
    Channel_C: int = 2
    Channel_D: int = 3


class WateringMode(Enum):
    """
    Enum representing the configured watering mode

    :cvar Smart: Smart watering
    :vartype Smart: int
    :cvar SmartOutside: Smart watering "outside" (haven't seen this in use in the app)
    :vartype SmartOutside: int
    :cvar Scheduled: Scheduled watering
    :vartype Scheduled: int
    """
    Smart: int = 1
    SmartOutside: int = 2
    Scheduled: int = 3
