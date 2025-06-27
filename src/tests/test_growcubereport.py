import unittest
from growcube_client import *


class GrowCubeReportTestCase(unittest.TestCase):
    def test_water_state_report_false(self):
        report = WaterStateGrowcubeReport('1')
        self.assertEqual(report.water_warning, False)

    def test_water_state_report_true(self):
        report = WaterStateGrowcubeReport('0')
        self.assertEqual(report.water_warning, True)

    def test_moisture_humidity_state_report(self):
        report = MoistureHumidityStateGrowcubeReport("1@63@62@26")
        self.assertEqual(Channel.Channel_B, report.channel)
        self.assertEqual(63, report.moisture)
        self.assertEqual(62, report.humidity)
        self.assertEqual(26, report.temperature)

    def test_auto_water_report(self):
        report = AutoWaterGrowcubeReport("2@2023@7@13@14@23")
        self.assertEqual(Channel.Channel_C, report.channel)
        self.assertEqual(2023, report.year)
        self.assertEqual(7, report.month)
        self.assertEqual(13, report.day)
        self.assertEqual(14, report.hour)
        self.assertEqual(23, report.minute)

    def test_device_version_report(self):
        report = DeviceVersionGrowcubeReport("3.6@12663500")
        self.assertEqual("3.6", report._version)
        self.assertEqual("12663500", report._device_id)

    def test_erasure_date(self):
        report = EraseDataGrowcubeReport("xyz")
        self.assertFalse(report.success)

    def test_pump_open_report(self):
        report = PumpOpenGrowcubeReport("0")
        self.assertEqual(Channel.Channel_A, report.channel)

    def test_pump_closed_report(self):
        report = PumpCloseGrowcubeReport("1")
        self.assertEqual(Channel.Channel_B, report.channel)

    def test_check_sensor_report(self):
        report = CheckSensorGrowcubeReport("2")
        self.assertEqual(Channel.Channel_C, report.channel)

    def test_check_outlet_blocked_report(self):
        report = CheckOutletBlockedGrowcubeReport("1")
        self.assertEqual(Channel.Channel_B, report.channel)

    def test_check_sensor_not_connect_report_b(self):
        report = CheckSensorNotConnectedGrowcubeReport("1")
        self.assertEqual(Channel.Channel_B, report.channel)

    def test_check_sensor_not_connect_report_a(self):
        report = CheckSensorNotConnectedGrowcubeReport("0")
        self.assertEqual(Channel.Channel_A, report.channel)

    def test_wifi_state_report(self):
        report = CheckWifiStateGrowcubeReport("1")
        self.assertFalse(report._state)

    def test_growcube_ip_report(self):
        report = GrowCubeIPGrowcubeReport("xyz")
        self.assertEqual("xyz", report._ip)

    def test_lockstate_report_false(self):
        report = LockStateGrowcubeReport("0@0")
        self.assertFalse(report._lock_state)

    def test_lockstate_report_true(self):
        report = LockStateGrowcubeReport("1@1")
        self.assertTrue(report._lock_state)

    def test_outlet_lock_report(self):
        report = CheckOutletLockedGrowcubeReport("2")
        self.assertEqual(Channel.Channel_C, report.channel)

    def test_unknown_report(self):
        report = UnknownGrowcubeReport("99", "1@2@3")

        self.assertEqual("Unknown response: 99", report._command)
        self.assertEqual("1, 2, 3", report.data)


if __name__ == '__main__':
    unittest.main()
