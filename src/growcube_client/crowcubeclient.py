import asyncio
import logging
from typing import Callable

from growcube_client.growcubeenums import Channel
from growcube_client.growcubemessage import GrowcubeMessage
from growcube_client.growcubereport import GrowcubeReport
from growcube_client.growcubecommand import GrowcubeCommand, WaterCommand
"""
Growcube client library
https://github.com/jonnybergdahl/Python-growcube-client

Author: Jonny Bergdahl
Date: 2023-09-05
"""

class GrowcubeClient:
    """
    Growcube client class
    """
    def __init__(self, host: str, callback: Callable[[GrowcubeReport], None],
                 log_level: int = logging.INFO) -> None:
        """
        GrowcubeClient constructor
        Args:
            host: name or IP address of the Growcube device
            callback: callback function to receive data from the Growcube
            log_level: logging level
        """
        self.host = host
        self.port = 8800
        self.callback = callback
        self.log_level = log_level
        self._exit = False
        self._data = b''
        self.reader = None
        self.writer = None
        self.connected = False
        self.connection_timeout = 10

    def log_debug(self, message: str, *args) -> None:
        """
        Log a debug message

        Args:
            message: Message to log
            *args: Arguments for the message

        Returns:
            None

        """
        if self.log_level <= logging.DEBUG:
            logging.debug(message, *args)

    def log_info(self, message: str, *args) -> None:
        """
        Log an info message

        Args:
            message: Message to log
            *args: Arguments for the message

        Returns:
            None
        """
        if self.log_level <= logging.INFO:
            logging.info(message, *args)

    def log_error(self, message:str, *args) -> None:
        """
        Log an error message
        Args:
            message: Message to log
            *args: Arguments for the message

        Returns:
            None
        """
        if self.log_level <= logging.ERROR:
            logging.error(message, *args)

    async def connect_and_listen(self) -> None:
        """
        Connect to the Growcube and start listening for data. This function will not return until the connection is
        closed.
        Returns:
            None
        """
        while not self._exit:
            try:
                if not self.connected:
                    self.log_info("Connecting to %s:%i", self.host, self.port)
                    self.reader, self.writer = await asyncio.wait_for(asyncio.open_connection(self.host, self.port),
                                                                      timeout=self.connection_timeout)
                    self.log_info("Connected to %s:%i", self.host, self.port)
                    self.connected = True

                # Read data
                data = await self.reader.read(24)
                if not data:
                    break

                # Remove all b'\x00' characters, used for padding
                data = bytearray(filter(lambda c: c != 0, data))
                # add the data to the message buffer
                self._data += data
                # check for complete message
                new_index, message = GrowcubeMessage.from_bytes(self._data)
                self._data = self._data[new_index:]

                if message is not None:
                    self.log_debug(f"message: {message._command} - {message.payload}")
                    if self.callback is not None:
                        report = GrowcubeReport.get_report(message)
                        self.log_info(f"< {report.get_description()}")
                        self.callback(report)

            except ConnectionRefusedError:
                self.log_error(f"Connection to {self.host} refused")
                self.connected = False
                self._exit = True
            except asyncio.CancelledError:
                self.log_info("Client was cancelled. Exiting...")
                self.connected = False
                self._exit = True
            except asyncio.IncompleteReadError:
                self.log_info("Connection closed by server")
            except asyncio.TimeoutError:
                self.log_error(f"Connection to {self.host} timed out")
                self.connected = False
                self._exit = True
            except Exception as e:
                self.log_error(f"Error {str(e)}")
                self.connected = False
                self._exit = True
        self.log_debug("Exiting connect_and_listen loop")

    def disconnect(self) -> None:
        """
        Disconnect from the Growcube
        Returns:
            None
        """
        self.log_info("Disconnecting")
        self._exit = True

    async def send_command(self, command: GrowcubeCommand) -> bool:
        """
        Send a command to the Growcube. C

        Args:
            command: A GrowcubeCommand object

        Returns:
            A boolean indicating if the command was sent successfully
        """
        try:
            self.log_info("> %s", command.get_description())
            message_bytes = command.get_message().encode('ascii')
            self.writer.write(message_bytes)
            await self.writer.drain()
        except OSError as e:
            self.log_error(f"send_command OSError {str(e)}")
            return False
        except Exception as e:
            self.log_error(f"send_command Exception {str(e)}")
            return False
        return True

    async def water_plant(self, channel: Channel, duration: int) -> bool:
        """
        Water a plant for a given duration. This function will block until the watering is complete.

        Args:
            channel: Channel number 0-3
            duration: Duration in seconds

        Returns:
            A boolean indicating if the watering was successful
        """
        success = await self.send_command(WaterCommand(channel, True))
        if success:
            await asyncio.sleep(duration)
            success = await self.send_command(WaterCommand(channel, False))
        return success
