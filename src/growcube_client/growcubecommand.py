import datetime

from growcube_client import Channel, WateringMode

"""
Growcube client library
https://github.com/jonnybergdahl/Python-growcube-client

Author: Jonny Bergdahl
Date: 2023-09-05
"""


class GrowcubeCommand:
    """
    Growcube command base class
    """
    Command = {
        "43": "SetWorkModeCmd",
        "44": "SyncTimeCmd",
        "45": "PlantEndCmd",
        "46": "ClosePumpCmd",
        "47": "ReqWaterCmd",
        "48": "ReqCurveDataCmd",
        "49": "WaterModeCmd",
        "50": "WifiSettingsCmd",
        "ele502": "SyncWaterLevelCmd",
        "ele503": "SyncWaterTimeCmd",
        "ele504": "DeviceUpgradeCmd",
        "ele505": "FactoryResetCmd"
    }

    CHD_HEAD = "elea"
    CMD_SET_WORK_MODE = "43"
    CMD_SYNC_TIME = "44"
    CMD_PLANT_END = "45"
    CMD_CLOSE_PUMP = "46"
    CMD_REQ_WATER = "47"
    CMD_REQ_CURVE_DATA = "48"
    CMD_WATER_MODE = "49"
    CMD_WIFI_SETTINGS = "50"
    MSG_SYNC_WATER_LEVEL = "ele502"
    MSG_SYNC_WATER_TIME = "ele503"
    MSG_DEVICE_UPGRADE = "ele504"
    MSG_FACTORY_RESET = "ele505"

    def __init__(self, command: str, message: str):
        """
        GrowcubeCommand constructor
        Args:
            command: A string from the Command dictionary keys
            message: The message to send
        """
        self.command = command;
        self.message = message

    def get_message(self) -> str:
        """
        Get the complete message for sending to the Growcube device
        Returns:
            The complete message
        """
        if self.message is not None:
            return f"elea{self.command}#{len(self.message)}#{self.message}#"
        else:
            return self.command

    def get_description(self) -> str:
        """
        Get a human readable description of the command
        Returns:
            A human readable description of the command
        """
        if self.command in self.Command:
            return self.Command[self.command]
        else:
            return f"Unknown: {self.command}"


class SetWorkModeCommand(GrowcubeCommand):
    """
    Command 43 - Set work mode command
    No idea what this does, always sent as the first package from the phone app.
    """

    def __init__(self, mode: int):
        """
        SetWorkModeCommand constructor
        Args:
            mode: Mode.
        """
        super().__init__(self.CMD_SET_WORK_MODE, str(mode))
        self.mode = mode

    def get_description(self) -> str:
        """
        Get a human readable description of the command
        Returns:
            A human readable description of the command
        """
        if self.mode == 0:
            return "Auto"
        elif self.mode == 1:
            return "Manual"
        else:
            return f"Unknown: {self.mode}"


class SyncTimeCommand(GrowcubeCommand):
    """
    Command 44 - Sync time command
    """

    def __init__(self, timestamp: datetime):
        """
        SyncTimeCommand constructor
        Args:
            timestamp: The timestamp to use for the command
        """
        super().__init__(self.CMD_SYNC_TIME, timestamp.strftime("%Y@%m@%d@%H@%M@%S"))  # Java: yyyy@MM@dd@HH@mm@ss


class PlantEndCommand(GrowcubeCommand):
    """
    Command 45 - Plant end command
    This deletes any existing curve data for the given channel
    """

    def __init__(self, channel: Channel):
        """
        PlantEndCommand constructor
        Args:
            channel: Channel
        """
        super().__init__(self.CMD_PLANT_END, str(channel))


# Command 46 - Close pump
class ClosePumpCommand(GrowcubeCommand):
    """
    Command 46 - Close pump command
    This deletes any pump releated settings for the given channel
    """

    def __init__(self, channel: Channel):
        """
        ClosePumpCommand constructor
        Args:
            channel: Channel
        """
        super().__init__(GrowcubeCommand.CMD_CLOSE_PUMP, str(channel))


class WaterCommand(GrowcubeCommand):
    """
    Command 47 - Water command
    This starts or stops watering on the given channel
    """

    def __init__(self, channel: Channel, state: bool):
        """
        WaterCommand constructor
        Args:
            channel: Channel
            state: True for start watering or False for stop
        """
        super().__init__(GrowcubeCommand.CMD_REQ_WATER, f"{channel}@{1 if state else 0}")
        self.channel = channel
        self.state = state

    def get_description(self) -> str:
        """
        Get a human readable description of the command
        Returns:
            A human readable description of the command
        """
        return f"{self.Command[self.command]}: channel {self.channel}, state {self.state}"


class RequestCurveDataCommand(GrowcubeCommand):
    """
    Command 48 - Request curve data command
    This requests the moisture data for the given channel, used in the app to construct a graph
    """

    def __init__(self, channel: Channel):
        """
        RequestCurveDataCommand constructor
        Args:
            channel: Channel
        """
        super().__init__(GrowcubeCommand.CMD_REQ_CURVE_DATA, str(channel))


class WateringModeCommand(GrowcubeCommand):
    """
    Command 49 - Water mode command
    This sets the watering mode for the given channel
    """

    def __init__(self, channel: Channel, watering_mode: WateringMode, min_value: int, max_value: int):
        """
        WaterModeCommand constructor
        Args:
            channel: Channel
            watering_mode: Mode
            min_value: Min value
            max_value: Max value
        """
        super().__init__(self.CMD_WATER_MODE, f"{channel}@{watering_mode.value}@{min_value}@{max_value}")


class WiFiSettingsCommand(GrowcubeCommand):
    """
    Command 50 - WiFi settings command
    This setups the WiFi settings for the Growcube
    """

    def __init__(self, ssid: str, password: str):
        """
        WiFiSettingsCommand constructor
        Args:
            ssid: WiFi SSID
            password: WiFi password
        """
        super().__init__(self.CMD_WIFI_SETTINGS, f"{ssid}@{password}")


class SyncWaterLevelCommand(GrowcubeCommand):
    """
    Command 502 - Sync water level
    No idea what this does
    """

    def __init__(self):
        """
        SyncWaterLevelCommand constructor
        """
        super().__init__(GrowcubeCommand.MSG_SYNC_WATER_LEVEL, None)


class SyncWaterTimeCommand(GrowcubeCommand):
    """
    Command 503 - Sync water time
    No idea what this does
    """

    def __init__(self):
        """
        SyncWaterTimeCommand constructor
        """
        super().__init__(GrowcubeCommand.MSG_SYNC_WATER_TIME, None)


class SyncDeviceUpgradeCommand(GrowcubeCommand):
    """
    Command 504 - Device upgrade
    Issues a device upgrade request
    """

    def __init__(self):
        """
        SyncDeviceUpgradeCommand constructor
        """
        super().__init__(GrowcubeCommand.MSG_DEVICE_UPGRADE, None)


class SyncWFactoryResetCommand(GrowcubeCommand):
    """
    Command 505 - Factory reset
    Issues a factory reset request
    """

    def __init__(self):
        """
        SyncWFactoryResetCommand constructor
        """
        super().__init__(GrowcubeCommand.MSG_FACTORY_RESET, None)
