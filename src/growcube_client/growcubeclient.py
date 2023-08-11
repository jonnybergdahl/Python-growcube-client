import logging as logger
import time
from growcube_client.crowcubesocketclient import GrowcubeSocketClient
from growcube_client.growcubereport import *
from growcube_client.growcubecommand import *

class GrowcubeClient:
    """
    A class that encapsulates a GrowCube device

    :param host: Address of the GrowCube device
    :param port: Port of the GrowCube device, default is 8800
    """
    def __init__(self, host: str, port: str = GrowcubeSocketClient.DEFAULT_PORT):
        self.socket_client = GrowcubeSocketClient(host, port)
        self.firmware_version = None
        self.device_id = None
        self.water_warning = None
        self.humidity = None
        self.temperature = None
        self.moisture0 = None
        self.moisture1 = None
        self.moisture2 = None
        self.moisture3 = None
        self.water_warning = False
        self.device_locked = False
        self.pump0_state = False
        self.pump1_state = False
        self.pump2_state = False
        self.pump3_state = False

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

    def send_command(self, command: GrowcubeCommand):
        print(command.get_message())
        self.socket_client.send_message(command.get_message())

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
                report = WaterStateReport(message.payload)
                report.water_warning = report.water_warning
                return report
            elif message.command == 21:
                report = MoistureHumidityStateReport(message.payload)
                self.temperature = report.temperature
                self.humidity = report.humidity
                if report.pump == 0:
                    self.moisture0 = report.moisture
                elif report.pump == 1:
                    self.moisture1 = report.moisture
                elif report.pump == 2:
                    self.moisture2 = report.moisture
                else:
                    self.moisture3 = report.moisture
                return report
            elif message.command == 23:
                return AutoWaterReport(message.payload)
            elif message.command == 24:
                report = DeviceVersionReport(message.payload)
                self.firmware_version = report.version
                self.device_id = report.device_id
                return report
            elif message.command == 25:
                return EraseDataReport(message.payload)
            elif message.command == 26:
                report = PumpOpenReport(message.payload)
                if report.pump == 0:
                    self.pump0_state = True
                elif report.pump == 1:
                    self.pump1_state = True
                elif report.pump == 2:
                    self.pump2_state = True
                else:
                    self.pump3_state = True
                return report
            elif message.command == 27:
                report = PumpCloseReport(message.payload)
                if report.pump == 0:
                    self.pump0_state = False
                elif report.pump == 1:
                    self.pump1_state = False
                elif report.pump == 2:
                    self.pump2_state = False
                else:
                    self.pump3_state = False
            elif message.command == 28:
                return CheckSensorReport(message.payload)
            elif message.command == 29:
                return CheckDuZhuanReport(message.payload)
            elif message.command == 30:
                return CheckSensorNotConnectedReport(message.payload)
            elif message.command == 31:
                return CheckWifiStateReport(message.payload)
            elif message.command == 32:
                return GrowCubeIPReport(message.payload)
            elif message.command == 33:
                report = LockStateReport(message.payload)
                self.device_locked = report.lock_state
                return report
            elif message.command == 34:
                return CheckSensorLockReport(message.payload)
            elif message.command == 35:
                return RepCurveEndFlagReport(message.payload)
            else:
                return UnknownReport(message.command, message.payload)
        return None

    def dump(self):
        '''
        Dump the current state
        '''
        print(f"Host             : {self.socket_client.host}:{self.socket_client.port}")
        print(f'Firmware version : {self.firmware_version}')
        print(f'Device id        : {self.device_id}')
        print(f'Humidity         : {self.humidity}')
        print(f'Temperature      : {self.temperature}')
        print(f'Moisture sensor 0: {self.moisture0}')
        print(f'Moisture sensor 1: {self.moisture1}')
        print(f'Moisture sensor 2: {self.moisture2}')
        print(f'Moisture sensor 3: {self.moisture3}')
        print(f'Pump state 0     : {self.pump0_state}')
        print(f'Pump state 1     : {self.pump1_state}')
        print(f'Pump state 2     : {self.pump2_state}')
        print(f'Pump state 3     : {self.pump3_state}')
        print(f'Water warning    : {self.water_warning}')
        print(f'Device locked    : {self.device_locked}')

