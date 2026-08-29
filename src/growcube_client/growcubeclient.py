import asyncio
import datetime, time
import inspect
import logging

_LOGGER = logging.getLogger(__name__)

from typing import Callable, Optional, Set, Tuple, Awaitable
from .growcubeenums import Channel
from .growcubemessage import GrowcubeMessage
from .growcubereport import GrowcubeReport, DeviceVersionGrowcubeReport
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
    :ivar device_id_timeout: Timeout for the device ID handshake. (Default: 5 seconds)
    :type device_id_timeout: int
    :ivar device_id: Device ID reported by the device, None until it identifies itself.
    :type device_id: str or None
    :ivar version: Firmware version reported by the device, None until it identifies itself.
    :type version: str or None
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
        self.device_id_timeout = 5
        # Populated from the DeviceVersionGrowcubeReport of the most recent
        # handshake. Both keep their last known value across a reconnect.
        self.device_id: Optional[str] = None
        self.version: Optional[str] = None
        # Created per connection attempt in connect(), so the handshake can
        # only be satisfied by a report from that attempt. Not created here:
        # on Python 3.9 an Event binds to the loop that is current when it is
        # constructed, which need not be the loop the client runs on.
        self._device_id_event: Optional[asyncio.Event] = None
        # asyncio only keeps a weak reference to a running task, so callback
        # tasks need a strong one here or they can be collected mid-flight.
        self._background_tasks: Set[asyncio.Task] = set()
        self.heartbeat = datetime.datetime.now().timestamp()

    def _create_task(self, coro) -> None:
        """
        Schedules a callback coroutine, keeping a reference until it finishes.
        """
        task = asyncio.ensure_future(coro)
        self._background_tasks.add(task)
        task.add_done_callback(self._background_tasks.discard)

    def on_connected(self) -> None:
        """
        Callback function for when the connection is established
        """
        self.connected = True
        # Take the transport from the protocol rather than from connect()'s
        # return value. connection_made() runs before create_connection()
        # returns, so an attempt that times out or is cancelled in that window
        # would otherwise leave a live socket that self.transport never saw and
        # disconnect() therefore cannot close.
        if self.protocol is not None:
            self.transport = self.protocol.transport
        _LOGGER.debug(f"Connected to {self.host}")
        if self._on_connected_callback:
            if inspect.iscoroutinefunction(self._on_connected_callback):
                self._create_task(self._on_connected_callback(self.host))
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
        if isinstance(report, DeviceVersionGrowcubeReport):
            # First report a Growcube sends, and the only proof that the peer
            # really is one. connect() waits for this.
            self.device_id = report.device_id
            self.version = report.version
            if self._device_id_event is not None:
                self._device_id_event.set()
        if self._on_message_callback:
            if inspect.iscoroutinefunction(self._on_message_callback):
                self._create_task(self._on_message_callback(report))
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
                self._create_task(self._on_disconnected_callback(self.host))
            else:
                self._on_disconnected_callback(self.host)

    async def connect(self, wait_for_device_id: bool = True) -> Tuple[bool, str]:
        """
        Connect to the Growcube and start listening for data.

        By default this waits for the device to identify itself with a
        DeviceVersionGrowcubeReport before reporting success, so a peer that
        accepts the connection but never speaks the protocol is reported as a
        failure rather than as a working connection. On success device_id and
        version hold the values from that report.

        The connection is always closed before returning False, so a failed
        attempt never leaves a socket behind. That matters because a Growcube
        serves a single client at a time: a leaked connection blocks every
        later attempt until the process is restarted.

        :param wait_for_device_id: Wait for the device to identify itself.
                Set to False for a bare TCP connect.
        :type wait_for_device_id: bool
        :return: A tuple. True and an empty string if the connection was successful,
                otherwise False and the error message.
        :rtype: Tuple[bool, str]
        """
        error_message = ""
        try:
            _LOGGER.debug("Connecting to %s:%i", self.host, self.port)
            loop = asyncio.get_event_loop()
            # Recreated per attempt so the wait below cannot be satisfied by a
            # report that arrived on an earlier connection.
            self._device_id_event = asyncio.Event()
            # Held before awaiting: connection_made() runs before
            # create_connection() returns, so this is the only reference to the
            # transport that is guaranteed to exist if the attempt does not
            # complete. See on_connected().
            self.protocol = GrowcubeProtocol(self.on_connected,
                                             self.on_message,
                                             self.on_connection_lost)
            connection_coroutine = loop.create_connection(lambda: self.protocol,
                                                          self.host,
                                                          self.port)
            self.transport, _ = await asyncio.wait_for(connection_coroutine,
                                                       timeout=self.connection_timeout)
            _LOGGER.debug("Connected to %s:%i", self.host, self.port)

            if wait_for_device_id:
                try:
                    await asyncio.wait_for(self._device_id_event.wait(),
                                           timeout=self.device_id_timeout)
                except asyncio.TimeoutError:
                    error_message = f"Timed out waiting for device ID from {self.host}"
                    _LOGGER.error(error_message)
                    self.disconnect()
                    return False, error_message

            return True, ""
        except asyncio.CancelledError:
            # Close the socket, then let the cancellation continue. Swallowing
            # it here would leave the caller's task running after cancel().
            _LOGGER.debug("Connection to %s cancelled", self.host)
            self.disconnect()
            raise
        except ConnectionRefusedError:
            error_message = f"Connection to {self.host}:{self.port} refused"
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

        self.disconnect()
        return False, error_message

    @staticmethod
    async def get_device_id(host: str, port: int = 8800, timeout: float = 5) -> Tuple[bool, str]:
        """
        Connect just long enough to read the device ID, then disconnect.

        Intended for discovery and configuration flows that need to check that
        a host really is a Growcube before setting it up.

        :param host: Name or IP address of the Growcube device.
        :type host: str
        :param port: Port number for the connection.
        :type port: int
        :param timeout: Seconds to wait for each of the connect and the handshake.
        :type timeout: float
        :return: A tuple. True and the device ID if the device answered,
                otherwise False and the error message.
        :rtype: Tuple[bool, str]
        """
        async def _ignore_report(report: GrowcubeReport) -> None:
            return

        client = GrowcubeClient(host, _ignore_report)
        client.port = port
        client.connection_timeout = timeout
        client.device_id_timeout = timeout
        result, error = await client.connect()
        client.disconnect()
        if not result:
            return False, error
        return True, client.device_id

    def disconnect(self) -> None:
        """
        Disconnect from the Growcube

        :return: None
        """
        _LOGGER.debug("Disconnecting")
        # Fall back to the protocol's transport: connect() assigns
        # self.transport only once create_connection() returns, while the
        # protocol has it from connection_made() onwards.
        transport = self.transport
        if transport is None and self.protocol is not None:
            transport = self.protocol.transport
        if transport:
            transport.close()
        self.transport = None
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
