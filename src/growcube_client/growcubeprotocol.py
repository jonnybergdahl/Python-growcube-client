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
    """
    Implements a custom asyncio Protocol for communication with a Growcube device.

    This protocol is designed to handle the communication between a client and a Growcube device.
    It includes methods for handling connection events, receiving and processing data,
    and sending messages to the device.

    :param on_connected: A callback function to be executed when the connection is established.
    :type on_connected: Callable[[str], None]
    :param on_message: A callback function to be executed when a message is received.
    :type on_message: Callable[[str], None]
    :param on_connection_lost: A callback function to be executed when the connection is lost.
    :type on_connection_lost: Callable[[], None]

    :ivar transport: The transport instance associated with the protocol.
    :type transport: asyncio.Transport or None
    :ivar _data: A buffer to accumulate received data.
    :type _data: bytes
    :ivar _on_connected: Callback function for connection established event.
    :type _on_connected: Callable[[str], None] or None
    :ivar _on_message: Callback function for message received event.
    :type _on_message: Callable[[str], None] or None
    :ivar _on_connection_lost: Callback function for connection lost event.
    :type _on_connection_lost: Callable[[], None] or None
    """
    def __init__(self, on_connected: Callable[[str], None],
                 on_message: Callable[[str], None],
                 on_connection_lost: Callable[[], None]):
        """
        Initializes a new instance of the GrowcubeProtocol.

        :param on_connected: A callback function to be executed when the connection is established.
        :type on_connected: Callable[[str], None]
        :param on_message: A callback function to be executed when a message is received.
        :type on_message: Callable[[str], None]
        :param on_connection_lost: A callback function to be executed when the connection is lost.
        :type on_connection_lost: Callable[[], None]
        """
        self.transport = None
        self._data = b""
        self._on_connected = on_connected
        self._on_message = on_message
        self._on_connection_lost = on_connection_lost

    def connection_made(self, transport):
        """
        Called when a connection is made.

        :param transport: The transport instance associated with the connection.
        :type transport: asyncio.Transport
        """
        self.transport = transport
        logging.info("Connection established.")
        if self._on_connected:
            self._on_connected()

    def data_received(self, data):
        """
        Called when data is received.

        :param data: The received data.
        :type data: bytes
        """
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
        """
        Sends a message to the connected device.

        :param message: The message to send.
        :type message: bytes
        """
        self.transport.write(message)

    def connection_lost(self, exc):
        """
        Called when the connection is lost.

        :param exc: An exception indicating the reason for the connection loss.
        :type exc: Exception
        """
        print("Connection lost.")
