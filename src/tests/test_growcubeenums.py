import unittest
from growcube_client import Channel, WateringMode


class GrowcubeEnumsTestCase(unittest.TestCase):
    def test_channel_values(self):
        # Test that the Channel enum has the correct values
        self.assertEqual(0, Channel.Channel_A.value)
        self.assertEqual(1, Channel.Channel_B.value)
        self.assertEqual(2, Channel.Channel_C.value)
        self.assertEqual(3, Channel.Channel_D.value)
        
        # Test that there are exactly 4 channels
        self.assertEqual(4, len(Channel))

    def test_watering_mode_values(self):
        # Test that the WateringMode enum has the correct values
        self.assertEqual(1, WateringMode.Scheduled.value)
        self.assertEqual(2, WateringMode.SmartOutside.value)
        self.assertEqual(3, WateringMode.Smart.value)
        
        # Test that there are exactly 3 watering modes
        self.assertEqual(3, len(WateringMode))


if __name__ == '__main__':
    unittest.main()