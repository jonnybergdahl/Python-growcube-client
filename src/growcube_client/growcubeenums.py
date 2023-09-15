from enum import Enum
"""
Growcube client library
https://github.com/jonnybergdahl/Python-growcube-client

Author: Jonny Bergdahl
Date: 2023-09-05
"""


class Channel(Enum):
    """
    Channel

    Attributes:
        Channel_A = Channel A
        Channel_B = Channel B
        Channel_C = Channel C
        Channel_D = Channel D
    """
    Channel_A: int = 1
    Channel_B: int = 2
    Channel_C: int = 3
    Channel_D: int = 4


class WateringMode(Enum):
    """
    Watering mode

    Attributes:
        Smart = Smart watering based on moisture level
        SmartOutside = Smart watering, outside of sunlight hours
        Scheduled = Scheduled watering
    """
    Smart: int = 1
    SmartOutside: int = 2
    Scheduled: int = 3
