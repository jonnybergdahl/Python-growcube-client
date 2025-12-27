import asyncio
import datetime, time
import inspect
import logging

_LOGGER = logging.getLogger(__name__)

from typing import Callable, Tuple, Awaitable
from .growcubeenums import Channel
from .growcubemessage import GrowcubeMessage
from .growcubereport import GrowcubeReport
from .growcubecommand import GrowcubeCommand, WaterCommand, SetWorkModeCommand
from .growcubeprotocol import GrowcubeProtocol

"""
Growcube client library
https://github.com/jonnybergdahl/Python-growcube-client

Author: Jonny Bergdahl
Date: 2023-09-05
"""


class GrowcubeClient:
    """
    Growcube client class

    :ivar host: The name or IP address of the Growcube device.
    :type host: str
    :ivar port: The port number for the connection. (Default: 8800)
    :type port: int
    :ivar _on_message_callback: Callback function to receive data from the Growcube.
    :type _on_message_callback: Callable[[GrowcubeReport], None]
    :ivar _on_connected_callback: Callback function for when the connection is established.
    :type _on_connected_callback: Callable[[str], None] or None
    :ivar _disconnected_callback: Callback function for when the connection is lost.
    :type _on_disconnected_callback: Callable[[str], None] or None
    :ivar _exit: Internal flag indicating if the client is exiting.
    :type _exit: bool
    :ivar _data: Buffer to accumulate received data.
    :type _data: bytes
    :ivar transport: The transport instance associated with the protocol.
    :type transport: asyncio.Transport or None
    :ivar protocol: The protocol instance associated with the connection.
    :type protocol: GrowcubeProtocol or None
    :ivar connected: Indicates whether the client is connected to the Growcube.
    :type connected: bool
    :ivar connection_timeout: Timeout for connection attempts. (Default: 5 seconds)
    :type connection_timeout: int
    """
    host: str

    def __init__(self,
                 host: str,
                 on_message_callback: Callable[[GrowcubeReport], Awaitable[None]],
                 on_connected_callback: Callable[[str], Awaitable[None]] = None,
                 on_disconnected_callback: Callable[[str], Awaitable[None]] = None) -> None:
        """
        GrowcubeClient constructor

        :param host: Name or IP address of the Growcube device.
        :param on_message_callback: Callback function to receive data from the Growcube.
        :param on_connected_callback: Callback function for when the connection is established.
        :param on_disconnected_callback: Callback function for when the connection is lost.
        """
        self.host = host
        self.port = 8800
        self._on_message_callback = on_message_callback
        self._on_connected_callback = on_connected_callback
        self._on_disconnected_callback = on_disconnected_callback
        self._exit = False
        self._data = b''
        self.transport = None
        self.protocol = None
        self.connected = False
        self.connection_timeout = 5
        self.heartbeat = datetime.datetime.now().timestamp()

    def on_connected(self) -> None:
        """
        Callback function for when the connection is established
        """
        self.connected = True
        _LOGGER.debug(f"Connected to {self.host}")
        if self._on_connected_callback:
            if inspect.iscoroutinefunction(self._on_connected_callback):
                asyncio.create_task(self._on_connected_callback(self.host))
            else:
                self._on_connected_callback(self.host)

    def on_message(self, message: GrowcubeMessage) -> None:
        """
        Callback function for when a message is received from the Growcube

        :param message: The received GrowcubeMessage.
        :type message: GrowcubeMessage
        """
        report = GrowcubeReport.get_report(message)
        _LOGGER.debug(f"< {report.get_description()}")
        self.heartbeat = datetime.datetime.now().timestamp()
        if self._on_message_callback:
            if inspect.iscoroutinefunction(self._on_message_callback):
                asyncio.create_task(self._on_message_callback(report))
            else:
                self._on_message_callback(report)

    def on_connection_lost(self) -> None:
        """
        Callback function for when the connection is lost

        :return: None
        :rtype: None
        """
        _LOGGER.debug(f"Connection to {self.host} lost")
        self.connected = False
        if self._on_disconnected_callback:
            if inspect.iscoroutinefunction(self._on_disconnected_callback):
                asyncio.create_task(self._on_disconnected_callback(self.host))
            else:
                self._on_disconnected_callback(self.host)

    async def connect(self) -> Tuple[bool, str]:
        """
        Connect to the Growcube and start listening for data.

        :return: A tuple. True and an empty string if the connection was successful,
                otherwise False and the error message.
        :rtype: Tuple[bool, str]
        """
        error_message = ""
        try:
            _LOGGER.debug("Connecting to %s:%i", self.host, self.port)
            loop = asyncio.get_event_loop()
            connection_coroutine = loop.create_connection(lambda: GrowcubeProtocol(self.on_connected,
                                                                                   self.on_message,
                                                                                   self.on_connection_lost),
                                                          self.host,
                                                          self.port)
            self.transport, self.protocol = await asyncio.wait_for(connection_coroutine,
                                                                   timeout=self.connection_timeout)
            _LOGGER.debug("Connected to %s:%i", self.host, self.port)
            # await asyncio.create_task(self.send_keep_alive(interval=10))
            return True, ""
        except ConnectionRefusedError:
            error_message = f"Connection to {self.host}:{self.port} refused"
            _LOGGER.error(error_message)
        except asyncio.CancelledError:
            error_message = "Client was cancelled"
            _LOGGER.error(error_message)
        except asyncio.IncompleteReadError:
            error_message = "Connection closed by server"
            _LOGGER.error(error_message)
        except asyncio.TimeoutError:
            error_message = f"Connection to {self.host} timed out"
            _LOGGER.error(error_message)
        except Exception as e:
            error_message = f"Error {str(e)}"
            _LOGGER.error(error_message)
        return False, error_message

    def disconnect(self) -> None:
        """
        Disconnect from the Growcube

        :return: None
        """
        _LOGGER.info("Disconnecting")
        if self.transport:
            self.transport.close()
        self.connected = False

    def send_command(self, command: GrowcubeCommand) -> bool:
        """
        Send a command to the Growcube.

        :param command: A GrowcubeCommand object.
        :type command: GrowcubeCommand
        :return: True if the command was sent successfully, otherwise False.
        :rtype: bool
        """
        try:
            _LOGGER.info("> %s", command.get_description())
            message_bytes = command.get_message().encode('ascii')
            self.protocol.send_message(message_bytes)
        except OSError as e:
            _LOGGER.error(f"send_command OSError {str(e)}")
            return False
        except Exception as e:
            _LOGGER.error(f"send_command Exception {str(e)}")
            return False
        return True

    async def send_keep_alive(self, interval: int) -> None:
        """
        Send a keep alive, we are using the SetWorkModeCommand for this

        :param interval: How often to send keep alive message
        :type interval: int
        :return: None
        """
        while self.connected:
            self.send_command(SetWorkModeCommand(1))
            await asyncio.sleep(interval)

    async def water_plant(self, channel: Channel, duration: int) -> bool:
        """
        Water a plant for a given duration. This function will block until the watering is complete.

        :param channel: Channel number 0-3.
        :type channel: Channel
        :param duration: Duration in seconds.
        :type duration: int
        :return: True if the watering was successful, otherwise False.
        :rtype: bool
        """
        success = self.send_command(WaterCommand(channel, True))
        if success:
            await asyncio.sleep(duration)
            success = self.send_command(WaterCommand(channel, False))
            if not success:
                # Try again just to be sure
                success = self.send_command(WaterCommand(channel, False))
        return success
