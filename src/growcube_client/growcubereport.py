from typing_extensions import Self
from datetime import datetime

from growcube_client import Channel

"""
Growcube client library
https://github.com/jonnybergdahl/Python-growcube-client

Author: Jonny Bergdahl
Date: 2023-09-05
"""


class GrowcubeReport:
    """
    Growcube report base class

    :cvar Response: A dictionary mapping command values to corresponding report names.
    :vartype Response: dict[int, str]
    :cvar CMD_INNER: The inner command delimiter.
    :vartype CMD_INNER: str

    :ivar _command: The report command.
    :type _command: str
    """
    Response = {
        20: "RepWaterStateCmd",
        21: "RepSTHSateCmd",
        22: "RepCurveCmd",
        23: "RepAutoWaterCmd",
        24: "RepDeviceVersionCmd",
        25: "RepErasureDataCmd",
        26: "RepPumpOpenCmd",
        27: "RepPumpCloseCmd",
        28: "RepCheckSenSorNotConnectedCmd",
        29: "RepCheckDuZhuanCmd",
        30: "RepCheckSenSorNotConnectCmd",
        31: "RepWifistateCmd",
        32: "RepGrowCubeIPCmd",
        33: "RepLockstateCmd",
        34: "ReqCheckSenSorLockCmd",
        35: "RepCurveEndFlagCmd"
    }
    CMD_INNER = "@"

    def __init__(self, command):
        """
        GrowcubeReport constructor

        :param command: Command value.
        :type command: int
        """
        if command in self.Response:
            self._command = self.Response[command]
        else:
            self._command = f"Unknown: {command}"

    @property
    def command(self) -> str:
        """
        Command value

        :return: Command value.
        :rtype: str
        """
        return self._command

    def get_description(self) -> str:
        """
        Get a human-readable description of the report

        :return: A human-readable description of the report.
        :rtype: str
        """
        print(self._command)

    @staticmethod
    def get_report(message) -> Self:
        """
        Create a report from a message

        :param message: The message to create a report from.
        :type message: GrowcubeMessage
        :return: A GrowcubeReport child class instance.
        :rtype: GrowcubeReport or None
        """
        if message is None:
            return None
        if message.command == 20:
            return WaterStateGrowcubeReport(message.payload)
        elif message.command == 21:
            return MoistureHumidityStateGrowcubeReport(message.payload)
        elif message.command == 23:
            return AutoWaterGrowcubeReport(message.payload)
        elif message.command == 24:
            return DeviceVersionGrowcubeReport(message.payload)
        elif message.command == 25:
            return EraseDataGrowcubeReport(message.payload)
        elif message.command == 26:
            return PumpOpenGrowcubeReport(message.payload)
        elif message.command == 27:
            return PumpCloseGrowcubeReport(message.payload)
        elif message.command == 28:
            return CheckSensorGrowcubeReport(message.payload)
        elif message.command == 29:
            return CheckPumpBlockedGrowcubeReport(message.payload)
        elif message.command == 30:
            return CheckSensorNotConnectedGrowcubeReport(message.payload)
        elif message.command == 31:
            return CheckWifiStateGrowcubeReport(message.payload)
        elif message.command == 32:
            return GrowCubeIPGrowcubeReport(message.payload)
        elif message.command == 33:
            return LockStateGrowcubeReport(message.payload)
        elif message.command == 34:
            return CheckSensorLockGrowcubeReport(message.payload)
        elif message.command == 35:
            return RepCurveEndFlagGrowcubeReport(message.payload)
        else:
            return UnknownGrowcubeReport(message.command, message.payload)


class WaterStateGrowcubeReport(GrowcubeReport):
    """
    Response 20 - RepWaterState

    Reports water low state.

    :ivar _water_warning: Flag indicating water warning.
    :type _water_warning: bool
    """

    def __init__(self, data):
        """
        WaterStateGrowcubeReport constructor

        :param data: Response data.
        :type data: str
        """
        GrowcubeReport.__init__(self, 20)
        self._water_warning = int(data) != 0

    @property
    def water_warning(self) -> bool:
        """
        Water warning

        :return: True if water warning, otherwise False.
        :rtype: bool
        """
        return self._water_warning

    def get_description(self):
        """
        Get a human-readable description of the report

        :return: A human-readable description of the report.
        :rtype: str
        """
        return f"{self._command}: water_warning: {self._water_warning}"


class MoistureHumidityStateGrowcubeReport(GrowcubeReport):
    """
    Response 21 - RepSTHSate

    Report moisture, humidity, and temperature for a channel.

    :ivar _channel: Channel number 0-3.
    :type _channel: int
    :ivar _moisture: Moisture value.
    :type _moisture: int
    :ivar _humidity: Humidity value.
    :type _humidity: int
    :ivar _temperature: Temperature value.
    :type _temperature: int
    """

    def __init__(self, data):
        """
        MoistureHumidityStateGrowcubeReport constructor

        :param data: Response data.
        :type data: str
        """
        GrowcubeReport.__init__(self, 21)
        values = data.split(self.CMD_INNER)
        self._channel = int(values[0])
        self._moisture = int(values[1])
        self._humidity = int(values[2])
        self._temperature = int(values[3])

    @property
    def channel(self):
        """
        Channel number 0-3

        :return: Channel number 0-3.
        :rtype: int
        """
        return self._channel

    @property
    def moisture(self):
        """
        Moisture value

        :return: Moisture value, %
        :rtype: int
        """
        return self._moisture

    @property
    def humidity(self):
        """
        Humidity value

        :return: Humidity value, %
        :rtype: int
        """
        return self._humidity

    @property
    def temperature(self):
        """
        Temperature value

        :return: Temperature value, °C
        :rtype: int
        """
        return self._temperature

    def get_description(self):
        """
        Get a human-readable description of the report

        :return: A human-readable description of the report.
        :rtype: str
        """
        return f"{self._command}: channel: {self._channel}, moisture: {self._moisture}, humidity: {self._humidity}, temperature: {self._temperature}"


class AutoWaterGrowcubeReport(GrowcubeReport):
    """
    Response 23 - AutoWater

    Reports a historic watering event.

    :ivar _channel: Channel number 0-3.
    :type _channel: int
    :ivar _year: Year.
    :type _year: int
    :ivar _month: Month.
    :type _month: int
    :ivar _day: Day of month.
    :type _day: int
    :ivar _hour: Hour.
    :type _hour: int
    :ivar _minute: Minute.
    :type _minute: int

    :param data: Response data.
    :type data: str
    """

    def __init__(self, data):
        """
        AutoWaterGrowcubeReport constructor

        :param data: Response data.
        :type data: str
        """

        GrowcubeReport.__init__(self, 23)
        parts = data.split(self.CMD_INNER)
        self._channel = int(parts[0])
        self._year = int(parts[1])
        self._month = int(parts[2])
        self._day = int(parts[3])
        self._hour = int(parts[4])
        self._minute = int(parts[5])

    @property
    def channel(self) -> int:
        """
        Channel number 0-3

        :return: Channel number 0-3.
        :rtype: int
        """
        return self._channel

    @property
    def year(self) -> int:
        """
        Year

        :return: Year.
        :rtype: int
        """
        return self._year

    @property
    def month(self) -> int:
        """
        Month

        :return: Month.
        :rtype: int
        """
        return self._month

    @property
    def day(self) -> int:
        """
        Day of month

        :return: Day of month.
        :rtype: int
        """
        return self._day

    @property
    def hour(self) -> int:
        """
        Hour

        :return: Hour.
        :rtype: int
        """
        return self._hour

    @property
    def minute(self) -> int:
        """
        Minute

        :return: Minute.
        :rtype: int
        """
        return self._minute

    @property
    def timestamp(self) -> datetime:
        """
        Timestamp

        :return: Timestamp.
        :rtype: datetime
        """
        return datetime(self._year, self._month, self._day, self._hour, self._minute)

    def get_description(self):
        """
        Get a human-readable description of the report

        :return: A human-readable description of the report.
        :rtype: str
        """
        return f"{self._command}: {self._channel} - {self._year}-{self._month}-{self._day} {self._hour}:{self._minute}"


class DeviceVersionGrowcubeReport(GrowcubeReport):
    """
    Response 24 - RepDeviceVersion
    Reports firmware version and device ID.

    :ivar _version: Firmware version.
    :type _version: str
    :ivar _device_id: Device ID.
    :type _device_id: str
    """
    def __init__(self, data):
        """
        DeviceVersionGrowcubeReport constructor

        :param data: Response data.
        :type data: str
        """
        GrowcubeReport.__init__(self, 24)
        temp = data.split(self.CMD_INNER)
        self._version = temp[0]
        self._device_id = temp[1]

    @property
    def version(self) -> str:
        """
        Firmware version

        :return: Firmware version.
        :rtype: str
        """
        return self._version

    @property
    def device_id(self) -> str:
        """
        Device ID

        :return: Device ID.
        :rtype: str
        """
        return self._device_id

    def get_description(self) -> str:
        """
        Get a human-readable description of the report

        :return: A human-readable description of the report.
        :rtype: str
        """
        return f"{self._command}: version {self._version}, device_id {self._device_id}"


class EraseDataGrowcubeReport(GrowcubeReport):
    """
    Response 25 - RepErasureData

    Reports the success of data erasure.

    :ivar _success: Indicates whether the data erasure was successful.
    :type _success: bool
    """
    def __init__(self, data):
        """
        EraseDataGrowcubeReport constructor

        :param data: Response data.
        :type data: str
        """
        GrowcubeReport.__init__(self, 25)
        self._success = data == "52d"

    @property
    def success(self) -> bool:
        """
        Success

        :return: True if success, otherwise False.
        :rtype: bool
        """
        return self._success

    def get_description(self):
        """
        Get a human-readable description of the report

        :return: A human-readable description of the report.
        :rtype: str
        """
        return f"{self._command}: version {self.version}, device_id {self.device_id}"


class PumpOpenGrowcubeReport(GrowcubeReport):
    """
    Response 26 - RepPumpOpen

    Reports that a pump has been started

    :ivar _channel: Channel number 0-3
    :type _channel: int
    """
    def __init__(self, data):
        """
        PumpOpenGrowcubeReport constructor

        :param data: Response data.
        :type data: str
        """
        GrowcubeReport.__init__(self, 26)
        self._channel = Channel(int(data))

    @property
    def channel(self) -> Channel:
        """
        Channel number 0-3

        :return: Channel number 0-3
        :rtype: Channel
        """
        return self._channel

    def get_description(self):
        """
        Get a human readable description of the report

        :return: A human readable description of the report
        :rtype: str
        """
        return f"{self._command}: channel {self._channel}"


class PumpCloseGrowcubeReport(GrowcubeReport):
    """
    Response 27 - RepPumpClose
    Reports that a pump has been stopped

    :ivar _channel: Channel number 0-3
    :type _channel: int
    """
    def __init__(self, data):
        """
        PumpCloseGrowcubeReport constructor

        :param data: Response data.
        :type data: str
        """
        GrowcubeReport.__init__(self, 27)
        self._channel = Channel(int(data))

    @property
    def channel(self) -> Channel:
        """
        channel number 0-3

        :return: Channel number 0-3
        :rtype: int
        """
        return self._channel

    def get_description(self):
        """
        Get a human readable description of the report

        :return: A human readable description of the report
        :rtype: str
        """
        return f"{self._command}: channel {self._channel}"


class CheckSensorGrowcubeReport(GrowcubeReport):
    """
    Response 28 - RepCheckSenSorNotConnected
    Reports that a sensor is malfunctioning

    :ivar _fault_state: Fault state
    :type _fault_state: bool
    """
    def __init__(self, data):
        """
        CheckSensorGrowcubeReport constructor

        :param data: Response data.
        :type data: str
        """
        GrowcubeReport.__init__(self, 28)
        self._fault_state = data == "1"

    @property
    def fault_state(self) -> bool:
        """
        Fault state

        :return: True if fault, otherwise False
        :rtype: bool
        """
        return self._fault_state

    def get_description(self):
        """
        Get a human readable description of the report

        :return: A human readable description of the report
        :rtype: str
        """
        return f"{self._command}: fault_state {self._fault_state}"


class CheckPumpBlockedGrowcubeReport(GrowcubeReport):
    """
    Response 29 - Pump channel blocked
    Reports that a pump channel is blocked

    :ivar _channel: Channel number 0-3
    :type _channel: int
    """
    def __init__(self, data):
        """
        CheckPumpBlockGrowcubeReport constructor

        :params data: Response data
        :type data: str
        """
        GrowcubeReport.__init__(self, 29)
        temp = data.split(self.CMD_INNER)
        self._channel = int(data[0])
        self.data = data

    @property
    def channel(self) -> int:
        """
        Channel

        :return: Channel number 0-3
        :rtype: int
        """
        return self._channel

    def get_description(self):
        """
        Get a human readable description of the report

        :return: A human readable description of the report
        :rtype: str
        """
        return f"{self._command}: channel {self._channel}, fault_state {self._fault_state}"


class CheckSensorNotConnectedGrowcubeReport(GrowcubeReport):
    """
    Response 30 - RepCheckSenSorNotConnect
    Reports that a sensor is not connected

    :ivar _channel: Channel number 0-3
    :type _channel: int
    """
    def __init__(self, data):
        """
        CheckSensorNotConnectedGrowcubeReport constructor

        :param data: Response data.
        :type data: str
        """
        GrowcubeReport.__init__(self, 30)
        self._channel = Channel(int(data))

    @property
    def channel(self) -> Channel:
        """
        State

        :return: Channel number 0-3
        :rtype: int
        """
        return self._channel

    def get_description(self):
        """
        Get a human readable description of the report

        :return: A human readable description of the report
        :rtype: str
        """
        return f"{self._command}: channel {self._channel}"


# Response 31
class CheckWifiStateGrowcubeReport(GrowcubeReport):
    """
    Response 31 - RepWifistate
    Reports wifi state, probably ony valid when in AP mode, to check if the new WiFi SSID is available

    :ivar _state: State
    :type _state: bool
    """
    def __init__(self, data):
        """
        CheckWifiStateGrowcubeReport constructor

        :param data: Response data.
        :type data: str
        """
        GrowcubeReport.__init__(self, 31)
        self._state = data == "1"

    @property
    def state(self) -> bool:
        """
        State

        :return: True if state, otherwise False
        :rtype: bool
        """
        return self._state

    def get_description(self):
        """
        Get a human readable description of the report

        :return: A human readable description of the report
        :rtype: str
        """
        return f"{self._command}: state {self._state}"


class GrowCubeIPGrowcubeReport(GrowcubeReport):
    """
    Response 32 - RepGrowCubeIP
    Reports the IP address of the Growcube, I have no idea how to trigger this

    :ivar _ip: IP address
    :type _ip: str
    """
    def __init__(self, data):
        """
        GrowCubeIPGrowcubeReport constructor

        :param data: Response data.
        :type data: str
        """
        GrowcubeReport.__init__(self, 32)
        self._ip = data

    @property
    def ip(self) -> str:
        """
        IP address

        :return: IP address
        :rtype: str
        """
        return self._ip

    def get_description(self):
        """
        Get a human readable description of the report

        :return: A human readable description of the report
        :rtype: str
        """
        return f"{self._command}: ip {self._ip}"


class LockStateGrowcubeReport(GrowcubeReport):
    """
    Response 33 - RepLockstate
    Reports if the device is in locked state, as indicated by the red LED on the device

    :ivar _lock_state: Lock state
    :type _lock_state: bool
    """
    def __init__(self, data):
        """
        LockStateGrowcubeReport constructor

        :param data: Response data.
        :type data: str
        """
        GrowcubeReport.__init__(self, 33)
        temp = data.split(self.CMD_INNER)
        self._lock_state = temp[1] == "1"

    @property
    def lock_state(self) -> bool:
        """
        Lock state

        :return: True if locked, otherwise False
        :rtype: bool
        """
        return self._lock_state

    def get_description(self):
        """
        Get a human readable description of the report

        :return: A human readable description of the report
        :rtype: str
        """
        return f"{self._command}: lock_state {self._lock_state}"


class CheckSensorLockGrowcubeReport(GrowcubeReport):
    """
    Response 34 - ReqCheckSenSorLock
    Something related to the lock state of the sensor, I have no idea how to trigger this.

    :ivar _channel: Channel number 0-3
    :type _channel: int
    :ivar _lock_state: Lock state
    :type _lock_state: bool
    """
    def __init__(self, data):
        """
        CheckSensorLockGrowcubeReport constructor

        :param data: Response data.
        :type data: str
        """
        GrowcubeReport.__init__(self, 34)
        temp = data.split(self.CMD_INNER)
        self._channel = int(temp[0])
        self._lock_state = temp[1]

    @property
    def channel(self) -> int:
        """
        Channel number 0-3

        :return: Channel number 0-3
        :rtype: int
        """
        return self._channel

    @property
    def lock_state(self) -> bool:
        """
        Lock state

        :return: True if locked, otherwise False
        :rtype: bool
        """
        return self._lock_state

    def get_description(self):
        """
        Get a human readable description of the report

        :return: A human readable description of the report
        :rtype: str
        """
        return f"{self._command}: channel {self._channel} lock_state {self._lock_state}"


class RepCurveEndFlagGrowcubeReport(GrowcubeReport):
    """
    Response 35 - RepCurveEndFlag
    Reports the end of the water event reports stream

    :ivar _channel: Channel number 0-3
    :type _channel: int
    """
    def __init__(self, data):
        """
        RepCurveEndFlagGrowcubeReport constructor

        :param data: Response data.
        :type data: str
        """
        GrowcubeReport.__init__(self, 35)
        temp = data.split(self.CMD_INNER)
        self._channel = int(data[0])
        self.data = data

    @property
    def channel(self) -> int:
        """
        Channel number 0-3

        :return: Channel number 0-3
        :rtype: int
        """
        return self._channel

    def get_description(self):
        """
        Get a human readable description of the report

        :return: A human readable description of the report
        :rtype: str
        """
        return f"{self._command}: channel {self._channel}"


class UnknownGrowcubeReport(GrowcubeReport):
    """
    UnknownGrowcubeReport
    Reports an unknown response
    """
    def __init__(self, command, data):
        """
        UnknownGrowcubeReport constructor

        :param command: Command value.
        :type command: int
        """
        super().__init__(command)
        temp = data.split(self.CMD_INNER)
        self.data = ", ".join(temp)

    def get_description(self):
        """
        Get a human readable description of the report

        :return: A human readable description of the report
        :rtype: str
        """
        return f"{self._command}: data {self.data}"
