import asyncio
import logging

_LOGGER = logging.getLogger(__name__)

from typing import (
    Callable,
)

from .growcubemessage import GrowcubeMessage

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
    :type _data: bytearray
    :ivar _on_connected: Callback function for connection established event.
    :type _on_connected: Callable[[str], None] or None
    :ivar _on_message: Callback function for message received event.
    :type _on_message: Callable[[str], None] or None
    :ivar _on_connection_lost: Callback function for connection lost event.
    :type _on_connection_lost: Callable[[], None] or None
    """

    def __init__(self, on_connected: Callable[[], None],
                 on_message: Callable[[GrowcubeMessage], None],
                 on_connection_lost: Callable[[], None]):
        """
        Initializes a new instance of the GrowcubeProtocol.

        :param on_connected: A callback function to be executed when the connection is established.
        :type on_connected: Callable[[str], None]
        :param on_message: A callback function to be executed when a message is received.
        :type on_message: Callable[[GrowcubeMessage], None]
        :param on_connection_lost: A callback function to be executed when the connection is lost.
        :type on_connection_lost: Callable[[], None]
        """
        self.transport = None
        self._data = bytearray()
        self._on_connected = on_connected
        self._on_message = on_message
        self._on_connection_lost = on_connection_lost
        # Resolved lazily in _reset_timeout(), which only ever runs inside the
        # loop. Grabbing it here would tie construction to a current loop
        # existing at that moment, which is not guaranteed and is on its way
        # out: asyncio.get_event_loop() raises outside a running loop from
        # Python 3.14 on.
        self._loop = None
        self._timeout_handle = None
        self._timeout = 30

    def connection_made(self, transport) -> None:
        """
        Called when a connection is made.

        :param transport: The transport instance associated with the connection.
        :type transport: asyncio.Transport
        """
        self.transport = transport
        _LOGGER.info("Connection established.")
        if self._on_connected:
            self._on_connected()
        self._reset_timeout()

    def data_received(self, data) -> None:
        """
        Called when data is received.

        :param data: The received data.
        :type data: bytes
        """
        self._reset_timeout()
        # Remove all b'\x00' characters, used for padding
        data = bytearray(filter(lambda c: c != 0, data))
        # add the data to the message buffer
        self._data += data

        while self._data:
            # Check for a complete message
            try:
                new_index, message = GrowcubeMessage.from_bytes(self._data)
            except ValueError as exception:
                # A malformed message would fail to parse again on every later
                # call, so the buffer has to be resynchronized here. Leaving it
                # in place wedges the connection for good: the read below keeps
                # feeding the same bytes back in, and the inactivity watchdog
                # never fires because it was just reset above.
                _LOGGER.warning("Discarding malformed message: %s", exception)
                self._resync()
                continue

            # Discard any junk before the next header (new_index can be > 0 even with no message)
            if new_index > 0 and message is None:
                self._data = self._data[new_index:]

            if message is None:
                break

            if new_index <= 0:
                # A message that consumes nothing would loop forever.
                _LOGGER.error("Parser made no progress, discarding buffer")
                self._data = bytearray()
                break

            # Consume this message
            self._data = self._data[new_index:]

            _LOGGER.debug(f"message: {message.command} - {message.payload}")
            if self._on_message:
                self._on_message(message)

    def _resync(self) -> None:
        """
        Drops data up to and including the current message header, so the next
        parse attempt starts at the following header instead of re-reading the
        bytes that just failed.
        """
        header = GrowcubeMessage.HEADER.encode("ascii")
        start_index = self._data.find(header)
        if start_index == -1:
            self._data = bytearray()
        else:
            self._data = self._data[start_index + len(header):]

    def send_message(self, message: bytes) -> None:
        """
        Sends a message to the connected device.

        :param message: The message to send.
        :type message: bytes
        """
        self.transport.write(message)
        self._reset_timeout()

    def connection_lost(self, exc: Exception) -> None:
        """
        Called when the connection is lost.

        :param exc: An exception indicating the reason for the connection loss.
        :type exc: Exception
        """
        _LOGGER.debug(f"Connection lost, reason: {exc}")
        if self._timeout_handle:
            self._timeout_handle.cancel()
        if self._on_connection_lost:
            self._on_connection_lost()

    def _reset_timeout(self) -> None:
        """
        Resets the timeout
        """
        if self._loop is None:
            self._loop = asyncio.get_event_loop()
        if self._timeout_handle:
            self._timeout_handle.cancel()
        self._timeout_handle = self._loop.call_later(self._timeout, self._check_timeout)

    def _check_timeout(self) -> None:
        _LOGGER.debug("Connection timed out.")
        if self.transport:
            self.transport.abort()
