import unittest
import re
from datetime import datetime, date, time
from growcube_client import GrowcubeCommand, WateringMode, Channel
from growcube_client import SetWorkModeCommand
from growcube_client import SyncTimeCommand
from growcube_client import PlantEndCommand
from growcube_client import ClosePumpCommand
from growcube_client import WaterCommand
from growcube_client import RequestCurveDataCommand
from growcube_client import WateringModeCommand
from growcube_client import WiFiSettingsCommand
from growcube_client import SyncWaterLevelCommand
from growcube_client import SyncWaterTimeCommand
from growcube_client import SyncDeviceUpgradeCommand
from growcube_client import SyncWFactoryResetCommand
from growcube_client.growcubeenums import WorkMode


class GrowCubeCommandTestCase(unittest.TestCase):
    def test_command_base(self):
        command = GrowcubeCommand(GrowcubeCommand.CMD_SYNC_TIME, "payload")
        self.assertEqual(GrowcubeCommand.CMD_SYNC_TIME, command.command)
        self.assertEqual("payload", command.message)
        self.assertEqual("elea44#7#payload#", command.get_message())

    def test_set_work_mode(self):
        command = SetWorkModeCommand(WorkMode.Network)
        self.assertEqual(GrowcubeCommand.CMD_SET_WORK_MODE, command.command)
        self.assertEqual("2", command.message)
        self.assertEqual("elea43#1#2#", command.get_message())

    def test_sync_time_command(self):
        d = date(2023, 7, 13)
        t = time(12, 30, 40)
        now = datetime.combine(d, t)
        command = SyncTimeCommand(now)
        self.assertEqual(GrowcubeCommand.CMD_SYNC_TIME, command.command)
        self.assertEqual(now.strftime("%Y@%m@%d@%H@%M@%S"), command.message)
        self.assertEqual("elea44#19#2023@07@13@12@30@40#", command.get_message())

    def test_plant_end_command(self):
        command = PlantEndCommand(Channel.Channel_B)
        self.assertEqual(GrowcubeCommand.CMD_PLANT_END, command.command)
        self.assertEqual("1", command.message)
        self.assertEqual("elea45#1#1#", command.get_message())

    def test_close_pump_command(self):
        command = ClosePumpCommand(Channel.Channel_D)
        self.assertEqual(GrowcubeCommand.CMD_CLOSE_PUMP, command.command)
        self.assertEqual("3", command.message)
        self.assertEqual("elea46#1#3#", command.get_message())

    def test_water_command(self):
        command = WaterCommand(Channel.Channel_B, 0)
        self.assertEqual(GrowcubeCommand.CMD_REQ_WATER, command.command)
        self.assertEqual("1@0", command.message)
        self.assertEqual("elea47#3#1@0#", command.get_message())

    def test_request_curve_data_command(self):
        command = RequestCurveDataCommand(Channel.Channel_D)
        self.assertEqual(GrowcubeCommand.CMD_REQ_CURVE_DATA, command.command)
        self.assertEqual("3", command.message)
        self.assertEqual("elea48#1#3#", command.get_message())

    def test_watering_mode_command_smart(self):
        command = WateringModeCommand(Channel.Channel_B, WateringMode.Smart, 2, 3)
        self.assertEqual(GrowcubeCommand.CMD_WATER_MODE, command.command)
        self.assertEqual("1@3@2@3", command.message)
        self.assertEqual("elea49#7#1@3@2@3#", command.get_message())

    def test_watering_mode_command_smart_outside(self):
        command = WateringModeCommand(Channel.Channel_B, WateringMode.SmartOutside, 2, 3)
        self.assertEqual(GrowcubeCommand.CMD_WATER_MODE, command.command)
        self.assertEqual("1@2@2@3", command.message)
        self.assertEqual("elea49#7#1@2@2@3#", command.get_message())

    def test_watering_mode_command_scheduled(self):
        command = WateringModeCommand(Channel.Channel_A, WateringMode.Scheduled, 2, 3)
        self.assertEqual(GrowcubeCommand.CMD_WATER_MODE, command.command)
        self.assertEqual("0@1@2s@3", command.message)
        self.assertEqual("elea49#8#0@1@2s@3#", command.get_message())

    def test_wifi_settings_command(self):
        command = WiFiSettingsCommand("SSID", "Password")
        self.assertEqual(GrowcubeCommand.CMD_WIFI_SETTINGS, command.command)
        self.assertEqual(None, command.message)
        msg = command.get_message()
        self.assertTrue(msg.startswith("elea50]*26]*SSID}'Password}'"),f"prefix wrong: {msg!r}")
        self.assertTrue(msg.endswith("]*"), f"suffix wrong: {msg!r}")
        ts = re.search(r"SSID\}'Password\}'(\d+)\]\*$", msg).group(1)
        self.assertTrue(ts.isdigit(), f"timestamp not numeric: {ts!r}")

    def test_sync_water_level_command(self):
        command = SyncWaterLevelCommand()
        self.assertEqual("ele502", command.get_message())

    def test_sync_water_time_command(self):
        command = SyncWaterTimeCommand()
        self.assertEqual("ele503", command.get_message())

    def test_sync_device_upgrade_command(self):
        command = SyncDeviceUpgradeCommand()
        self.assertEqual("ele504", command.get_message())

    def test_sync_w_factory_reset(self):
        command = SyncWFactoryResetCommand()
        self.assertEqual("ele505", command.get_message())


if __name__ == '__main__':
    unittest.main()
