import unittest
import asyncio
import ipaddress
from unittest.mock import MagicMock, patch
from growcube_client import GrowcubeDiscovery


class GrowcubeDiscoveryTestCase(unittest.TestCase):
    def setUp(self):
        self.discovery = GrowcubeDiscovery()

    @patch('asyncio.open_connection')
    @patch('asyncio.wait_for')
    async def test_discover_device_success(self, mock_wait_for, mock_open_connection):
        # Mock a successful connection
        mock_reader = MagicMock()
        mock_writer = MagicMock()
        mock_wait_for.return_value = (mock_reader, mock_writer)
        
        result = await self.discovery.discover_device("192.168.1.100")
        
        self.assertTrue(result)
        self.assertIn("192.168.1.100", self.discovery._devices)
        mock_wait_for.assert_called_once()
        mock_writer.close.assert_called_once()
        mock_writer.wait_closed.assert_called_once()

    @patch('asyncio.open_connection')
    @patch('asyncio.wait_for')
    async def test_discover_device_timeout(self, mock_wait_for, mock_open_connection):
        # Mock a connection timeout
        mock_wait_for.side_effect = asyncio.TimeoutError()
        
        result = await self.discovery.discover_device("192.168.1.100")
        
        self.assertFalse(result)
        self.assertNotIn("192.168.1.100", self.discovery._devices)

    @patch('asyncio.open_connection')
    @patch('asyncio.wait_for')
    async def test_discover_device_connection_refused(self, mock_wait_for, mock_open_connection):
        # Mock a connection refused error
        mock_wait_for.side_effect = ConnectionRefusedError()
        
        result = await self.discovery.discover_device("192.168.1.100")
        
        self.assertFalse(result)
        self.assertNotIn("192.168.1.100", self.discovery._devices)

    @patch('asyncio.open_connection')
    @patch('asyncio.wait_for')
    async def test_discover_device_other_exception(self, mock_wait_for, mock_open_connection):
        # Mock another exception
        mock_wait_for.side_effect = Exception("Test exception")
        
        result = await self.discovery.discover_device("192.168.1.100")
        
        self.assertFalse(result)
        self.assertNotIn("192.168.1.100", self.discovery._devices)

    @patch.object(GrowcubeDiscovery, 'discover_device')
    async def test_discover_devices_in_local_subnet(self, mock_discover_device):
        # Mock the discover_device method to return True for some IPs
        async def mock_discover(ip):
            if ip == "192.168.1.100" or ip == "192.168.1.200":
                self.discovery._devices.append(ip)
                return True
            return False
        
        mock_discover_device.side_effect = mock_discover
        
        # Create a small subnet for testing
        subnet = ipaddress.IPv4Network("192.168.1.0/29")  # 192.168.1.1 - 192.168.1.6
        
        devices = await self.discovery.discover_devices_in_local_subnet(subnet)
        
        # Check that discover_device was called for each host in the subnet
        self.assertEqual(6, mock_discover_device.call_count)  # 6 usable IPs in a /29
        # Check that the discovered devices were returned
        self.assertEqual(["192.168.1.100", "192.168.1.200"], devices)

    @patch('socket.socket')
    def test_guess_subnet(self, mock_socket):
        # Mock the socket to return a specific IP
        mock_sock_instance = MagicMock()
        mock_sock_instance.getsockname.return_value = ("192.168.1.123", 12345)
        mock_socket.return_value = mock_sock_instance
        
        subnet = GrowcubeDiscovery.guess_subnet()
        
        self.assertEqual(ipaddress.IPv4Network("192.168.1.0/24"), subnet)
        mock_sock_instance.connect.assert_called_once_with(("8.8.8.8", 80))
        mock_sock_instance.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()