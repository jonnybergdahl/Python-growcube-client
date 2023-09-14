"""
Growcube client

Author: Jonny Bergdahl
Date: 2023-09-05
"""
import asyncio
import logging
from growcube_client.growcubemessage import GrowcubeMessage
from growcube_client.growcubereport import GrowcubeReportBase
from growcube_client.growcubecommand import GrowcubeCommand, WaterCommand


class GrowcubeClient:
    def __init__(self, host: str, callback, log_level=logging.INFO):
        """
        Growcube client
        @param host: IP or DNS address of the Growcube
        @param callback: A callback method accepting a GrowcubeReport instance
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

    def log_debug(self, message, *args):
        if self.log_level <= logging.DEBUG:
            logging.debug(message, *args)

    def log_info(self, message, *args):
        if self.log_level <= logging.INFO:
            logging.info(message, *args)

    def log_error(self, message, *args):
        if self.log_level <= logging.ERROR:
            logging.error(message, *args)

    async def connect_and_listen(self):
        """
        Connects to the Growcube and continually listens for messages.
        Reports any received messages using the callback
        """
        while not self._exit:
            try:
                if not self.connected:
                    self.log_info("Connecting to %s:%i", self.host, self.port)
                    self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
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
                    self.log_debug(f"message: {message.command} - {message.payload}")
                    if self.callback is not None:
                        report = GrowcubeReportBase.get_report(message)
                        self.callback(report)

            except ConnectionRefusedError:
                self.log_error(f"Connection to {self.host} refused")
                self.connected = False
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                self.log_info("Client was cancelled. Exiting...")
                self.connected = False
            except asyncio.IncompleteReadError:
                self.log_info("Connection closed by server")
            except Exception as e:
                self.log_error(f"Error {str(e)}")
                self.connected = False

        print("Exiting listen loop")

    def disconnect(self):
        self.log_info("Disconnecting")
        self._exit = True

    async def send_command(self, command: GrowcubeCommand):
        try:
            self.log_info("Sending message %s", command.get_description())
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

    async def water_plant(self, pump: int, duration: int):
        await self.send_command(WaterCommand(pump, True))
        await asyncio.sleep(duration)
        await self.send_command(WaterCommand(pump, False))

