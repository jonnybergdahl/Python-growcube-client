import unittest
from growcube_client import *


class GrowCubeReportTestCase(unittest.TestCase):
    def test_water_state_report_false(self):
        report = WaterStateReport('1')
        self.assertEqual(report.water_warning, False)

    def test_water_state_report_true(self):
        report = WaterStateReport('0')
        self.assertEqual(report.water_warning, True)

    def test_moisture_humidity_state_report(self):
        report = MoistureHumidityStateReport("1@63@62@26")
        self.assertEqual(1, report.pump)
        self.assertEqual(63, report.moisture)
        self.assertEqual(62, report.humidity)
        self.assertEqual(26, report.temperature)

    def test_auto_water_report(self):
        report = AutoWaterReport("2@2023@7@13@14@23")
        self.assertEqual(2, report.pump)
        self.assertEqual(2023, report.year)
        self.assertEqual(7, report.month)
        self.assertEqual(13, report.date)
        self.assertEqual(14, report.hour)
        self.assertEqual(23, report.minute)

    def test_version_and_water_report(self):
        report = VersionAndWaterReport("3.6@12663500")
        self.assertEqual("3.6", report.version)
        self.assertEqual(False, report.water_warning)

    def test_unknown_report(self):
        report = UnknownReport("99", "1@2@3")

        self.assertEqual("Unknown: 99", report.command)
        self.assertEqual("1, 2, 3", report.data)


if __name__ == '__main__':
    unittest.main()
