import datetime
from .growcubeenums import Channel, WateringMode

"""
Growcube client library
https://github.com/jonnybergdahl/Python-growcube-client

Author: Jonny Bergdahl
Date: 2023-09-05
"""


class GrowcubeCommand:
    """
    Growcube command base class

    :cvar Command: Dictionary mapping command codes to command names.
    :vartype Command: dict
    :cvar CHD_HEAD: Command header for CHD messages.
    :vartype CHD_HEAD: str
    :cvar CMD_SET_WORK_MODE: Command code for SetWorkModeCmd.
    :vartype CMD_SET_WORK_MODE: str
    :cvar CMD_SYNC_TIME: Command code for SyncTimeCmd.
    :vartype CMD_SYNC_TIME: str
    :cvar CMD_PLANT_END: Command code for PlantEndCmd.
    :vartype CMD_PLANT_END: str
    :cvar CMD_CLOSE_PUMP: Command code for ClosePumpCmd.
    :vartype CMD_CLOSE_PUMP: str
    :cvar CMD_REQ_WATER: Command code for ReqWaterCmd.
    :vartype CMD_REQ_WATER: str
    :cvar CMD_REQ_CURVE_DATA: Command code for ReqCurveDataCmd.
    :vartype CMD_REQ_CURVE_DATA: str
    :cvar CMD_WATER_MODE: Command code for WaterModeCmd.
    :vartype CMD_WATER_MODE: str
    :cvar CMD_WIFI_SETTINGS: Command code for WifiSettingsCmd.
    :vartype CMD_WIFI_SETTINGS: str
    :cvar MSG_SYNC_WATER_LEVEL: Command code for SyncWaterLevelCmd.
    :vartype MSG_SYNC_WATER_LEVEL: str
    :cvar MSG_SYNC_WATER_TIME: Command code for SyncWaterTimeCmd.
    :vartype MSG_SYNC_WATER_TIME: str
    :cvar MSG_DEVICE_UPGRADE: Command code for DeviceUpgradeCmd.
    :vartype MSG_DEVICE_UPGRADE: str
    :cvar MSG_FACTORY_RESET: Command code for FactoryResetCmd.
    :vartype MSG_FACTORY_RESET: str

    :ivar command: The command code.
    :type command: str
    :ivar message: The message to send.
    :type message: str

    :param command: A string from the Command dictionary keys.
    :param message: The message to send.
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

        :param command: A string from the Command dictionary keys.
        :type command: str
        :param message: The message to send.
        :type message: str
        """
        self.command = command;
        self.message = message

    def get_message(self) -> str:
        """
        Get the complete message for sending to the Growcube device.

        :return: The complete message.
        :rtype: str
        """
        if self.message is not None:
            return f"elea{self.command}#{len(self.message)}#{self.message}#"
        else:
            return self.command

    def get_description(self) -> str:
        """
        Get a human-readable description of the command.

        :return: A human-readable description of the command.
        :rtype: str
        """
        if self.command in self.Command:
            return self.Command[self.command]
        else:
            return f"Unknown: {self.command}"


class SetWorkModeCommand(GrowcubeCommand):
    """
    Command 43 - Set work mode command

    This command is used to set the work mode, and it is often sent as the first package from the phone app.
    """

    def __init__(self, mode: int):
        """
        SetWorkModeCommand constructor

        :param mode: The work mode.
        :type mode: int
        """
        super().__init__(self.CMD_SET_WORK_MODE, str(mode))
        self.mode = mode

    def get_description(self) -> str:
        """
        Get a human readable description of the command

        :return: A human readable description of the command
        :rtype: str
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

    This command is used to set the device time.
    """

    def __init__(self, timestamp: datetime):
        """
        SyncTimeCommand constructor
        :param timestamp: The timestamp to use for the command
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

        :param channel: The channel to delete curve data for
        :type channel: Channel
        """
        super().__init__(self.CMD_PLANT_END, str(channel.value))


# Command 46 - Close pump
class ClosePumpCommand(GrowcubeCommand):
    """
    Command 46 - Close pump command
    This deletes any pump related settings for the given channel
    """

    def __init__(self, channel: Channel):
        """
        ClosePumpCommand constructor

        :param channel: The channel to delete pump settings for
        :type channel: Channel
        """
        super().__init__(GrowcubeCommand.CMD_CLOSE_PUMP, str(channel.value))


class WaterCommand(GrowcubeCommand):
    """
    Command 47 - Water command
    This starts or stops watering on the given channel
    """

    def __init__(self, channel: Channel, state: bool):
        """
        WaterCommand constructor

        :param channel: Channel
        :type channel: Channel
        :param state: True for start watering or False for stop
        :type state: bool
        """
        super().__init__(GrowcubeCommand.CMD_REQ_WATER, f"{channel.value}@{1 if state else 0}")
        self.channel = channel
        self.state = state

    def get_description(self) -> str:
        """
        Get a human readable description of the command

        :return: A human readable description of the command
        :rtype: str
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

        :param channel: Channel
        :type channel: Channel
        """
        super().__init__(GrowcubeCommand.CMD_REQ_CURVE_DATA, str(channel.value))


class WateringModeCommand(GrowcubeCommand):
    """
    Command 49 - Water mode command
    This sets the watering mode for the given channel
    """

    def __init__(self, channel: Channel, watering_mode: WateringMode, min_value: int, max_value: int):
        """
        WaterModeCommand constructor

        :param channel: Channel
        :type channel: Channel
        :param watering_mode: Mode
        :type watering_mode: WateringMode
        :param min_value: Min value
        :type min_value: int
        :param max_value: Max value
        :type max_value: int
        """
        super().__init__(self.CMD_WATER_MODE, f"{str(channel.value)}@{watering_mode.value}@{min_value}@{max_value}")


class WiFiSettingsCommand(GrowcubeCommand):
    """
    Command 50 - WiFi settings command
    This setups the WiFi settings for the Growcube
    """

    def __init__(self, ssid: str, password: str):
        """
        WiFiSettingsCommand constructor

        :param ssid: SSID
        :type ssid: str
        :param password: Password
        :type password: str
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
