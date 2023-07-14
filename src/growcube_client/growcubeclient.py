import logging as logger
import time
from growcube_client.crowcubesocketclient import GrowcubeSocketClient
from growcube_client.growcubereport import *
from growcube_client.growcubecommand import *

class GrowcubeClient:
    '''
    A class that encapsulates a GrowCube device

    :param host: Address of the GrowCube device
    :param port: Port of the GrowCube device, default is 8800
    '''
    def __init__(self, host: str, port: str = GrowcubeSocketClient.DEFAULT_PORT):
        self.socket_client = GrowcubeSocketClient(host, port)
        self.firmware_version = None
        self.water_warning = None
        self.humidity = None
        self.temperature = None
        self.moisture0 = None
        self.moisture1 = None
        self.moisture2 = None
        self.moisture3 = None

    def connect(self):
        return self.socket_client.connect()

    def set_work_mode(self, mode: int):
        logger.debug("Set work mode %i", mode)
        message = SetWorkModeCommand(mode)
        return self.socket_client.send_message(message.get_message())

    def disconnect(self):
        logger.debug("Disconnect")
        self.socket_client.disconnect()

    def data_complete(self):
        return self.firmware_version is not None and \
            self.water_warning is not None and \
            self.humidity is not None and \
            self.temperature is not None and \
            self.moisture0 is not None and \
            self.moisture1 is not None and \
            self.moisture2 is not None and \
            self.moisture3 is not None

    def get_all_data(self, timeout: int = 30):
        '''
        Waits until the device has reported all data, and exits.

        :param timeout: Timeout in seconds
        '''
        start_time = time.time()
        while not self.data_complete():
            self.get_next_report()
            if time.time() - start_time > 30:
                logger.info("Timeout getting all data")
                return False
        return True

    def get_next_report(self):
        '''
        Get the next report to returned from the GrowCube
        '''
        message = self.socket_client.receive_message()
        if message is not None:
            logger.debug("Got message %s", message.message)
            if message.command == 20:
                return WaterStateReport(message.payload)
            elif message.command == 21:
                data = MoistureHumidityStateReport(message.payload)
                self.temperature = data.temperature
                self.humidity = data.humidity
                if data.pump == 0:
                    self.moisture0 = data.moisture
                elif data.pump == 1:
                    self.moisture1 = data.moisture
                elif data.pump == 2:
                    self.moisture2 = data.moisture
                else:
                    self.moisture3 = data.moisture
                return data
            elif message.command == 23:
                return AutoWaterReport(message.payload)
            elif message.command == 24:
                data = VersionAndWaterReport(message.payload)
                self.firmware_version = data.version
                self.water_warning = data.water_warning
                return data
            else:
                return UnknownReport(message.command, message.payload)
        return None

    def dump(self):
        '''
        Dump the current state
        '''
        print(f"Host             : {self.socket_client.host}:{self.socket_client.port}")
        print(f'Firmware version : {self.firmware_version}')
        print(f'Water warning    : {self.water_warning}')
        print(f'Humidity         : {self.humidity}')
        print(f'Temperature      : {self.temperature}')
        print(f'Moisture sensor 0: {self.moisture0}')
        print(f'Moisture sensor 1: {self.moisture1}')
        print(f'Moisture sensor 2: {self.moisture2}')
        print(f'Moisture sensor 3: {self.moisture3}')
