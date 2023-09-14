import unittest
from growcube_client import *


class GrowCubeReportTestCase(unittest.TestCase):
    def test_water_state_report_false(self):
        report = WaterStateGrowcubeReport('0')
        self.assertEqual(report.water_warning, False)

    def test_water_state_report_true(self):
        report = WaterStateGrowcubeReport('1')
        self.assertEqual(report.water_warning, True)

    def test_moisture_humidity_state_report(self):
        report = MoistureHumidityStateGrowcubeReport("1@63@62@26")
        self.assertEqual(1, report._pump)
        self.assertEqual(63, report._moisture)
        self.assertEqual(62, report._humidity)
        self.assertEqual(26, report._temperature)

    def test_auto_water_report(self):
        report = AutoWaterGrowcubeReport("2@2023@7@13@14@23")
        self.assertEqual(2, report.pump)
        self.assertEqual(2023, report._year)
        self.assertEqual(7, report._month)
        self.assertEqual(13, report._day)
        self.assertEqual(14, report._hour)
        self.assertEqual(23, report._minute)

    def test_device_version_report(self):
        report = DeviceVersionGrowcubeReport("3.6@12663500")
        self.assertEqual("3.6", report._version)
        self.assertEqual("12663500", report._device_id)

    def test_erasure_date(self):
        report = EraseDataGrowcubeReport("xyz")
        self.assertFalse(report.success)

    def test_pump_open_report(self):
        report = PumpOpenGrowcubeReport("0")
        self.assertEqual(0, report._pump)

    def test_pump_closed_report(self):
        report = PumpCloseGrowcubeReport("1")
        self.assertEqual(1, report._pump)

    def test_check_sensor_report(self):
        report = CheckSensorGrowcubeReport("1")
        self.assertTrue(report._fault_state)

    def test_check_du_zhuan_report(self):
        report = CheckDuZhuanGrowcubeReport("1")
        self.assertTrue(report._state)

    def test_check_sensor_not_connect_report_false(self):
        report = CheckSensorNotConnectedGrowcubeReport("1")
        self.assertFalse(report._state)

    def test_check_sensor_not_connect_report_true(self):
        report = CheckSensorNotConnectedGrowcubeReport("0")
        self.assertTrue(report._state)

    def test_wifi_state_report(self):
        report = CheckWifiStateGrowcubeReport("1")
        self.assertTrue(report._state)

    def test_growcube_ip_report(self):
        report = GrowCubeIPGrowcubeReport("xyz")
        self.assertEqual("xyz", report._ip)

    def test_lockstate_report_false(self):
        report = LockStateGrowcubeReport("0@0")
        self.assertFalse(report._lock_state)

    def test_lockstate_report_true(self):
        report = LockStateGrowcubeReport("1@1")
        self.assertTrue(report._lock_state)

    def test_unknown_report(self):
        report = UnknownGrowcubeReport("99", "1@2@3")

        self.assertEqual("Unknown: 99", report._command)
        self.assertEqual("1, 2, 3", report.data)


if __name__ == '__main__':
    unittest.main()