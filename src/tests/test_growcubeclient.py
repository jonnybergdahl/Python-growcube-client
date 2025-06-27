import unittest
import asyncio
from unittest.mock import MagicMock, patch
from growcube_client import GrowcubeClient, GrowcubeReport, Channel, WateringMode


class GrowcubeClientTestCase(unittest.TestCase):
    def setUp(self):
        self.callback = MagicMock()
        self.on_connected_callback = MagicMock()
        self.on_disconnected_callback = MagicMock()
        self.client = GrowcubeClient(
            "127.0.0.1",
            self.callback,
            self.on_connected_callback,
            self.on_disconnected_callback
        )
        # Mock the transport and protocol
        self.client.transport = MagicMock()
        self.client.protocol = MagicMock()

    @patch('asyncio.get_event_loop')
    @patch('asyncio.wait_for')
    async def test_connect_success(self, mock_wait_for, mock_get_event_loop):
        # Mock successful connection
        mock_transport = MagicMock()
        mock_protocol = MagicMock()
        mock_wait_for.return_value = (mock_transport, mock_protocol)
        mock_loop = MagicMock()
        mock_get_event_loop.return_value = mock_loop
        mock_loop.create_connection.return_value = asyncio.Future()
        mock_loop.create_connection.return_value.set_result((mock_transport, mock_protocol))

        success, error = await self.client.connect()
        
        self.assertTrue(success)
        self.assertEqual("", error)
        mock_get_event_loop.assert_called_once()
        mock_wait_for.assert_called_once()

    @patch('asyncio.get_event_loop')
    @patch('asyncio.wait_for')
    async def test_connect_timeout(self, mock_wait_for, mock_get_event_loop):
        # Mock connection timeout
        mock_wait_for.side_effect = asyncio.TimeoutError()
        mock_loop = MagicMock()
        mock_get_event_loop.return_value = mock_loop

        success, error = await self.client.connect()
        
        self.assertFalse(success)
        self.assertIn("timed out", error)

    def test_disconnect(self):
        self.client.disconnect()
        
        self.client.transport.close.assert_called_once()
        self.assertFalse(self.client.connected)

    def test_send_command(self):
        # Create a mock command
        mock_command = MagicMock()
        mock_command.get_message.return_value = "test_command"
        mock_command.get_description.return_value = "Test Command"
        
        result = self.client.send_command(mock_command)
        
        self.assertTrue(result)
        self.client.protocol.send_message.assert_called_once_with(b"test_command")

    def test_send_command_exception(self):
        # Create a mock command
        mock_command = MagicMock()
        mock_command.get_message.return_value = "test_command"
        mock_command.get_description.return_value = "Test Command"
        
        # Make protocol.send_message raise an exception
        self.client.protocol.send_message.side_effect = Exception("Test exception")
        
        result = self.client.send_command(mock_command)
        
        self.assertFalse(result)

    @patch('asyncio.sleep')
    async def test_water_plant(self, mock_sleep):
        # Mock the send_command method
        self.client.send_command = MagicMock(return_value=True)
        
        result = await self.client.water_plant(Channel.Channel_A, 5)
        
        self.assertTrue(result)
        self.assertEqual(2, self.client.send_command.call_count)  # Called twice (start and stop)
        mock_sleep.assert_called_once_with(5)

    def test_on_connected(self):
        self.client.on_connected()
        
        self.assertTrue(self.client.connected)
        self.on_connected_callback.assert_called_once_with(self.client.host)

    def test_on_connection_lost(self):
        self.client.connected = True
        
        self.client.on_connection_lost()
        
        self.assertFalse(self.client.connected)
        self.on_disconnected_callback.assert_called_once_with(self.client.host)

    def test_on_message(self):
        # Create a mock message and report
        mock_message = MagicMock()
        mock_report = MagicMock()
        
        # Mock the GrowcubeReport.get_report method
        with patch('growcube_client.GrowcubeReport.get_report', return_value=mock_report):
            self.client.on_message(mock_message)
            
            self.callback.assert_called_once_with(mock_report)


if __name__ == '__main__':
    unittest.main()