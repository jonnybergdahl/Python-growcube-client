import asyncio
import logging
from typing import (
    Callable,
)
from .growcubemessage import GrowcubeMessage
from .growcubereport import GrowcubeReport

"""
Growcube client library
https://github.com/jonnybergdahl/Python-growcube-client

Author: Jonny Bergdahl
Date: 2023-09-05
"""


class GrowcubeProtocol(asyncio.Protocol):

    def __init__(self, on_connected: Callable[[str], None], on_message: Callable[[str], None],
                 on_connection_lost: Callable[[], None]):
        self.transport = None
        self._data = b""
        self._on_connected = on_connected
        self._on_message = on_message
        self._on_connection_lost = on_connection_lost

    def connection_made(self, transport):
        self.transport = transport
        logging.info("Connection established.")
        if self._on_connected:
            self._on_connected()

    def data_received(self, data):
        # Remove all b'\x00' characters, used for padding
        data = bytearray(filter(lambda c: c != 0, data))
        # add the data to the message buffer
        self._data += data
        # check for complete message
        new_index, message = GrowcubeMessage.from_bytes(self._data)
        self._data = self._data[new_index:]

        if message is not None:
            logging.debug(f"message: {message._command} - {message.payload}")
            if self._on_message:
                self._on_message(message)

    def send_message(self, message: bytes) -> None:
        self.transport.write(message)

    def connection_lost(self, exc):
        print("Connection lost.")
