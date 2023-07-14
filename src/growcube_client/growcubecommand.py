import datetime


class GrowcubeCommand:
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
        self.command = command;
        self.message = message

    def get_message(self):
        if self.message is not None:
            return f"elea{self.command}#{len(self.message)}#{self.message}#"
        else:
            return f"{self.command}#"


# Command 43 - SetWorkMode
class SetWorkModeCommand(GrowcubeCommand):
    def __init__(self, mode: int):
        super().__init__(self.CMD_SET_WORK_MODE, str(mode))


# Command 44 - Sync time
class SyncTimeCommand(GrowcubeCommand):
    def __init__(self, timestamp: datetime):
        super().__init__(self.CMD_SYNC_TIME, timestamp.strftime("%Y@%m@%d@%H@%M@%S"))  # Java: yyyy@MM@dd@HH@mm@ss


# Command 45 - Plant end ??
class PlantEndCommand(GrowcubeCommand):
    def __init__(self, pump: int):
        super().__init__(self.CMD_PLANT_END, str(pump))


# Command 46 - Close pump
class ClosePumpCommand(GrowcubeCommand):
    def __init__(self, pump: int):
        super().__init__(GrowcubeCommand.CMD_CLOSE_PUMP, str(pump))


# Command 47 - Water
class WaterCommand(GrowcubeCommand):
    def __init__(self, pump: int, state: int):
        super().__init__(GrowcubeCommand.CMD_REQ_WATER, f"{pump}#{state}")


# Command 48 - Request curve data
class RequestCurveDataCommand(GrowcubeCommand):
    def __init__(self, pump: int):
        super().__init__(GrowcubeCommand.CMD_REQ_CURVE_DATA, str(pump))


# Command 49 - Water mode
class WaterModeCommand(GrowcubeCommand):
    def __init__(self, pump: int, mode: int, min_value: int, max_value: int):
        super().__init__(self.CMD_WATER_MODE, f"{pump}@{mode}@{min_value}@{max_value}")


# Command 50 - WiFi settings
class WiFiSettingsCommand(GrowcubeCommand):
    def __init__(self, ssid: str, password: str):
        super().__init__(self.CMD_WIFI_SETTINGS, f"{ssid}@{password}")


# Command 502 - Sync water level
class SyncWaterLevelCommand(GrowcubeCommand):
    def __init__(self):
        super().__init__(GrowcubeCommand.MSG_SYNC_WATER_LEVEL, None)


# Command 503 - Sync water time
class SyncWaterTimeCommand(GrowcubeCommand):
    def __init__(self):
        super().__init__(GrowcubeCommand.MSG_SYNC_WATER_TIME, None)


# Command 504 - Device upgrade
class SyncDeviceUpgradeCommand(GrowcubeCommand):
    def __init__(self):
        super().__init__(GrowcubeCommand.MSG_DEVICE_UPGRADE, None)


# Command 505 - Factory reset
class SyncWFactoryResetCommand(GrowcubeCommand):
    def __init__(self):
        super().__init__(GrowcubeCommand.MSG_FACTORY_RESET, None)
