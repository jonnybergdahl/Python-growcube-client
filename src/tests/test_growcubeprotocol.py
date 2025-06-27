import unittest
import asyncio
from unittest.mock import MagicMock, patch
from growcube_client import GrowcubeProtocol, GrowcubeMessage


class GrowcubeProtocolTestCase(unittest.TestCase):
    def setUp(self):
        self.on_connected = MagicMock()
        self.on_message = MagicMock()
        self.on_connection_lost = MagicMock()
        self.protocol = GrowcubeProtocol(
            self.on_connected,
            self.on_message,
            self.on_connection_lost
        )
        self.transport = MagicMock()
        self.protocol.transport = self.transport

    def test_connection_made(self):
        # Create a new transport mock to test connection_made
        transport = MagicMock()
        
        # Reset the timeout handle mock
        with patch.object(self.protocol, '_reset_timeout') as mock_reset_timeout:
            self.protocol.connection_made(transport)
            
            self.assertEqual(transport, self.protocol.transport)
            self.on_connected.assert_called_once()
            mock_reset_timeout.assert_called_once()

    @patch('growcube_client.GrowcubeMessage.from_bytes')
    def test_data_received_complete_message(self, mock_from_bytes):
        # Mock a complete message
        mock_message = MagicMock()
        mock_from_bytes.return_value = (10, mock_message)  # 10 bytes consumed, message returned
        
        # Reset the timeout handle mock
        with patch.object(self.protocol, '_reset_timeout') as mock_reset_timeout:
            self.protocol.data_received(b'elea28#1#0#')
            
            mock_reset_timeout.assert_called_once()
            mock_from_bytes.assert_called_once()
            self.on_message.assert_called_once_with(mock_message)

    @patch('growcube_client.GrowcubeMessage.from_bytes')
    def test_data_received_incomplete_message(self, mock_from_bytes):
        # Mock an incomplete message
        mock_from_bytes.return_value = (0, None)  # 0 bytes consumed, no message
        
        # Reset the timeout handle mock
        with patch.object(self.protocol, '_reset_timeout') as mock_reset_timeout:
            self.protocol.data_received(b'elea')
            
            mock_reset_timeout.assert_called_once()
            mock_from_bytes.assert_called_once()
            self.on_message.assert_not_called()

    @patch('growcube_client.GrowcubeMessage.from_bytes')
    def test_data_received_with_null_bytes(self, mock_from_bytes):
        # Mock a message with null bytes
        mock_message = MagicMock()
        mock_from_bytes.return_value = (10, mock_message)  # 10 bytes consumed, message returned
        
        # Reset the timeout handle mock
        with patch.object(self.protocol, '_reset_timeout') as mock_reset_timeout:
            self.protocol.data_received(b'elea28\x00#1#0#')
            
            mock_reset_timeout.assert_called_once()
            # Check that null bytes were filtered out
            mock_from_bytes.assert_called_once()
            self.assertEqual(b'elea28#1#0#', mock_from_bytes.call_args[0][0])
            self.on_message.assert_called_once_with(mock_message)

    def test_send_message(self):
        # Reset the timeout handle mock
        with patch.object(self.protocol, '_reset_timeout') as mock_reset_timeout:
            self.protocol.send_message(b'test_message')
            
            self.transport.write.assert_called_once_with(b'test_message')
            mock_reset_timeout.assert_called_once()

    def test_connection_lost(self):
        # Mock an exception
        exc = Exception("Test exception")
        
        # Mock the timeout handle
        self.protocol._timeout_handle = MagicMock()
        
        self.protocol.connection_lost(exc)
        
        self.protocol._timeout_handle.cancel.assert_called_once()
        self.on_connection_lost.assert_called_once()

    @patch('asyncio.get_event_loop')
    def test_reset_timeout(self, mock_get_event_loop):
        # Mock the loop and timeout handle
        mock_loop = MagicMock()
        mock_get_event_loop.return_value = mock_loop
        mock_timeout_handle = MagicMock()
        self.protocol._timeout_handle = mock_timeout_handle
        self.protocol._loop = mock_loop
        
        self.protocol._reset_timeout()
        
        # Check that the old timeout handle was canceled
        mock_timeout_handle.cancel.assert_called_once()
        # Check that a new timeout handle was created
        mock_loop.call_later.assert_called_once()

    def test_check_timeout(self):
        self.protocol._check_timeout()
        
        # Check that the transport was aborted
        self.transport.abort.assert_called_once()


if __name__ == '__main__':
    unittest.main()