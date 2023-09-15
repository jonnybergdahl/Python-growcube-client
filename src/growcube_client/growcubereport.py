from typing_extensions import Self
from datetime import datetime
"""
Growcube client library
https://github.com/jonnybergdahl/Python-growcube-client

Author: Jonny Bergdahl
Date: 2023-09-05
"""


class GrowcubeReport:
    """
    Growcube report base class
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
        Args:
            command: Command value
        """
        if command in self.Response:
            self._command = self.Response[command]
        else:
            self._command = f"Unknown: {command}"

    @property
    def command(self) -> str:
        """
        Command value
        Returns:
            Command value
        """
        return self._command

    def get_description(self) -> str:
        """
        Get a human readable description of the report
        Returns:
            A human readable description of the report
        """
        print(self._command)

    @staticmethod
    def get_report(message) -> Self:
        """
        Create a report from a message
        Args:
            message: The message to create a report from

        Returns:
            A GrowcubeReport child class instance
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
            return CheckDuZhuanGrowcubeReport(message.payload)
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
    Reports water low state
    """
    def __init__(self, data):
        """
        WaterStateGrowcubeReport constructor
        Args:
            data: Response data
        """
        GrowcubeReport.__init__(self, 20)
        self._water_warning = int(data) != 0

    @property
    def water_warning(self) -> bool:
        """
        Water warning
        Returns:
            True if water warning, otherwise False
        """
        return self._water_warning

    def get_description(self):
        """
        Get a human readable description of the report
        Returns:
            A human readable description of the report
        """
        return f"{self._command}: water_warning: {self._water_warning}"


class MoistureHumidityStateGrowcubeReport(GrowcubeReport):
    """
    Response 21 - RepSTHSate
    Report moisture, humidity and temperature for a channel
    """
    def __init__(self, data):
        """
        MoistureHumidityStateGrowcubeReport constructor
        Args:
            data: Response data
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
        Returns:
            Channel number 0-3
        """
        return self._channel

    @property
    def moisture(self):
        """
        Moisture value
        Returns:
            Moisture value, %
        """
        return self._moisture

    @property
    def humidity(self):
        """
        Humidity value
        Returns:
            Humidity value, %
        """
        return self._humidity

    @property
    def temperature(self):
        """
        Temperature value
        Returns:
            Temperature value, °C
        """
        return self._temperature

    def get_description(self):
        """
        Get a human readable description of the report
        Returns:
            A human readable description of the report
        """
        return f"{self._command}: channel: {self._channel}, moisture: {self._moisture}, humidity: {self._humidity}, temperature: {self._temperature}"


class AutoWaterGrowcubeReport(GrowcubeReport):
    """
    Response 23 - AutoWater
    Reports a historic watering event
    """
    def __init__(self, data):
        """
        AutoWaterGrowcubeReport constructor
        Args:
            data: Response data
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
        Returns:
            Channel number 0-3
        """
        return self._channel

    @property
    def year(self) -> int:
        """
        Year
        Returns:
            Year
        """
        return self._year

    @property
    def month(self) -> int:
        """
        Month
        Returns:
            Month
        """
        return self._month

    @property
    def day(self) -> int:
        """
        Day of month
        Returns:
            Day of month
        """
        return self._day

    @property
    def hour(self) -> int:
        """
        Hour
        Returns:
            Hour
        """
        return self._hour

    @property
    def minute(self) -> int:
        """
        Minute
        Returns:
            Minute
        """
        return self._minute

    @property
    def timestamp(self) -> datetime:
        """
        Timestamp
        Returns:
            Timestamp
        """
        return datetime(self._year, self._month, self._day, self._hour, self._minute)

    def get_description(self):
        """
        Get a human readable description of the report
        Returns:
            A human readable description of the report
        """
        return f"{self._command}: {self._channel} - {self._year}-{self._month}-{self._day} {self._hour}:{self._minute}"


class DeviceVersionGrowcubeReport(GrowcubeReport):
    """
    Response 24 - RepDeviceVersion
    Reports firmware version and device ID
    """
    def __init__(self, data):
        """
        DeviceVersionGrowcubeReport constructor
        Args:
            data: Response data
        """
        GrowcubeReport.__init__(self, 24)
        temp = data.split(self.CMD_INNER)
        self._version = temp[0]
        self._device_id = temp[1]

    @property
    def version(self) -> str:
        """
        Firmware version
        Returns:
            Firmware version
        """
        return self._version

    @property
    def device_id(self) -> str:
        """
        Device ID
        Returns:
            Device ID
        """
        return self._device_id

    def get_description(self) -> str:
        """
        Get a human readable description of the report
        Returns:
            A human readable description of the report
        """
        return f"{self._command}: version {self._version}, device_id {self._device_id}"


class EraseDataGrowcubeReport(GrowcubeReport):
    """
    Response 25 - RepErasureData
    """
    def __init__(self, data):
        """
        EraseDataGrowcubeReport constructor
        Args:
            data: Response data
        """
        GrowcubeReport.__init__(self, 25)
        self._success = data == "52d"

    @property
    def success(self) -> bool:
        """
        Success
        Returns:
            True if success, otherwise False
        """
        return self._success

    def get_description(self):
        """
        Get a human readable description of the report
        Returns:
            A human readable description of the report
        """
        return f"{self._command}: version {self.version}, device_id {self.device_id}"


class PumpOpenGrowcubeReport(GrowcubeReport):
    """
    Response 26 - RepPumpOpen
    Reports that a pump has been started
    """
    def __init__(self, data):
        """
        PumpOpenGrowcubeReport constructor
        Args:
            data: Response data
        """
        GrowcubeReport.__init__(self, 26)
        self._channel = int(data)

    @property
    def channel(self) -> int:
        """
        Channel number 0-3
        Returns:
            Channel number 0-3
        """
        return self._channel

    def get_description(self):
        """
        Get a human readable description of the report
        Returns:
            A human readable description of the report
        """
        return f"{self._command}: channel {self._channel}"


class PumpCloseGrowcubeReport(GrowcubeReport):
    """
    Response 27 - RepPumpClose
    Reports that a pump has been stopped
    """
    def __init__(self, data):
        """
        PumpCloseGrowcubeReport constructor
        Args:
            data: Response data
        """
        GrowcubeReport.__init__(self, 27)
        self._channel = int(data)

    @property
    def channel(self) -> int:
        """
        channel number 0-3
        Returns:
            channel number 0-3
        """
        return self._channel

    def get_description(self):
        """
        Get a human readable description of the report
        Returns:
            A human readable description of the report
        """
        return f"{self._command}: channel {self._channel}"


class CheckSensorGrowcubeReport(GrowcubeReport):
    """
    Response 28 - RepCheckSenSorNotConnected
    Reports that a sensor is malfunctioning
    """
    def __init__(self, data):
        """
        CheckSensorGrowcubeReport constructor
        Args:
            data: Response data
        """
        GrowcubeReport.__init__(self, 28)
        self._fault_state = data == "1"

    @property
    def fault_state(self) -> bool:
        """
        Fault state
        Returns:
            True if fault, otherwise False
        """
        return self._fault_state

    def get_description(self):
        """
        Get a human readable description of the report
        Returns:
            A human readable description of the report
        """
        return f"{self._command}: fault_state {self._fault_state}"


class CheckDuZhuanGrowcubeReport(GrowcubeReport):
    """
    Response 29 - RepCheckDuZhuan
    I have no idea what this is, the chinese phrase "du zhuan" translates to something like "read transmission"
    """
    def __init__(self, data):
        """
        CheckDuZhuanGrowcubeReport constructor
        Args:
            data: Response data
        """
        GrowcubeReport.__init__(self, 29)
        self._state = data == "1"

    @property
    def state(self) -> bool:
        """
        State
        Returns:
            True if state is 1, otherwise False
        """
        return self._state

    def get_description(self):
        """
        Get a human readable description of the report
        Returns:
            A human readable description of the report
        """
        return f"{self._command}: fault_state {self._state}"


class CheckSensorNotConnectedGrowcubeReport(GrowcubeReport):
    """
    Response 30 - RepCheckSenSorNotConnect
    Reports that a sensor is not connected
    """
    def __init__(self, data):
        """
        CheckSensorNotConnectedGrowcubeReport constructor
        Args:
            data: Response data
        """
        GrowcubeReport.__init__(self, 30)
        self._channel = int(data)

    @property
    def channel(self) -> int:
        """
        State
        Returns:
            Channel number 0-3
        """
        return self._channel

    def get_description(self):
        """
        Get a human readable description of the report
        Returns:
            A human readable description of the report
        """
        return f"{self._command}: channel {self._channel}"


# Response 31
class CheckWifiStateGrowcubeReport(GrowcubeReport):
    """
    Response 31 - RepWifistate
    Reports wifi state, probably ony valid when in AP mode, to check if the new WiFi SSID is available
    """
    def __init__(self, data):
        """
        CheckWifiStateGrowcubeReport constructor
        Args:
            data: Response data
        """
        GrowcubeReport.__init__(self, 31)
        self._state = data == "1"

    @property
    def state(self) -> bool:
        """
        State
        Returns:
            True if state is 1, otherwise False
        """
        return self._state

    def get_description(self):
        """
        Get a human readable description of the report
        Returns:
            A human readable description of the report
        """
        return f"{self._command}: state {self._state}"


class GrowCubeIPGrowcubeReport(GrowcubeReport):
    """
    Response 32 - RepGrowCubeIP
    Reports the IP address of the Growcube, I have no idea how to trigger this
    """
    def __init__(self, data):
        """
        GrowCubeIPGrowcubeReport constructor
        Args:
            data: Response data
        """
        GrowcubeReport.__init__(self, 32)
        self._ip = data

    @property
    def ip(self) -> str:
        """
        IP address
        Returns:
            IP address
        """
        return self._ip

    def get_description(self):
        """
        Get a human readable description of the report
        Returns:
            A human readable description of the report
        """
        return f"{self._command}: ip {self._ip}"


class LockStateGrowcubeReport(GrowcubeReport):
    """
    Response 33 - RepLockstate
    Reports if the device is in locked state, as indicated by the red LED on the device
    """
    def __init__(self, data):
        """
        LockStateGrowcubeReport constructor
        Args:
            data: Response data
        """
        GrowcubeReport.__init__(self, 33)
        temp = data.split(self.CMD_INNER)
        self._lock_state = temp[1] == "1"

    @property
    def lock_state(self) -> bool:
        """
        Lock state
        Returns:
            True if locked, otherwise False
        """
        return self._lock_state

    def get_description(self):
        """
        Get a human readable description of the report
        Returns:
            A human readable description of the report
        """
        return f"{self._command}: lock_state {self._lock_state}"


class CheckSensorLockGrowcubeReport(GrowcubeReport):
    """
    Response 34 - ReqCheckSenSorLock
    I have no idea what this is.
    """
    def __init__(self, data):
        """
        CheckSensorLockGrowcubeReport constructor
        Args:
            data: Response data
        """
        GrowcubeReport.__init__(self, 34)
        temp = data.split(self.CMD_INNER)
        self._channel = int(temp[0])
        self._lock_state = temp[1]

    @property
    def channel(self) -> int:
        """
        Channel number 0-3
        Returns:
            Channel number 0-3
        """
        return self._channel

    @property
    def lock_state(self) -> bool:
        """
        Lock state
        Returns:
            True if locked, otherwise False
        """
        return self._lock_state

    def get_description(self):
        """
        Get a human readable description of the report
        Returns:
            A human readable description of the report
        """
        return f"{self._command}: channel {self._channel} lock_state {self._lock_state}"


class RepCurveEndFlagGrowcubeReport(GrowcubeReport):
    """
    Response 35 - RepCurveEndFlag
    Reports the end of the water event reports stream
    """
    def __init__(self, data):
        """
        RepCurveEndFlagGrowcubeReport constructor
        Args:
            data: Response data
        """
        GrowcubeReport.__init__(self, 35)
        temp = data.split(self.CMD_INNER)
        self._channel = int(data[0])
        self.data = data

    @property
    def channel(self) -> int:
        """
        Channel number 0-3
        Returns:
            Channel number 0-3
        """
        return self._channel

    def get_description(self):
        """
        Get a human readable description of the report
        Returns:
            A human readable description of the report
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
        Args:
            command: Command value
            data: Response data
        """
        super().__init__(command)
        temp = data.split(self.CMD_INNER)
        self.data = ", ".join(temp)

    def get_description(self):
        """
        Get a human readable description of the report
        Returns:
            A human readable description of the report
        """
        return f"{self._command}: data {self.data}"
