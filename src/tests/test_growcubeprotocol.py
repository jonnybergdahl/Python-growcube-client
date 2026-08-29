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
        # Mock a complete message, then an empty buffer
        mock_message = MagicMock()
        mock_from_bytes.side_effect = [(10, mock_message), (0, None)]
        
        # Reset the timeout handle mock
        with patch.object(self.protocol, '_reset_timeout') as mock_reset_timeout:
            self.protocol.data_received(b'elea28#1#0#')
            
            mock_reset_timeout.assert_called_once()
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
        # Mock a message with null bytes, then an empty buffer
        mock_message = MagicMock()
        mock_from_bytes.side_effect = [(10, mock_message), (0, None)]
        
        # Reset the timeout handle mock
        with patch.object(self.protocol, '_reset_timeout') as mock_reset_timeout:
            self.protocol.data_received(b'elea28\x00#1#0#')
            
            mock_reset_timeout.assert_called_once()
            # Check that null bytes were filtered out
            self.assertEqual(b'elea28#1#0#', mock_from_bytes.call_args_list[0][0][0])
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

    def test_check_timeout_without_transport(self):
        # The watchdog can fire after the transport is gone
        self.protocol.transport = None
        
        self.protocol._check_timeout()

    def test_data_received_recovers_from_malformed_message(self):
        """Garbage on the wire must not wedge the connection.

        The bad bytes have to be dropped from the buffer, otherwise every
        later read re-parses them, raises again, and no message ever gets
        through - while the inactivity watchdog keeps being reset, so the
        connection is never torn down either.
        """
        with patch.object(self.protocol, '_reset_timeout'):
            # 'abc' is not a valid payload length
            self.protocol.data_received(b'elea24#abc#hello#')
            
            self.on_message.assert_not_called()
            
            # A well formed message after the garbage still gets delivered
            self.protocol.data_received(GrowcubeMessage.to_bytes(24, '3.6@12345678'))
            
            self.on_message.assert_called_once()
            self.assertEqual(24, self.on_message.call_args[0][0].command)

    @patch('growcube_client.GrowcubeMessage.from_bytes')
    def test_data_received_stops_when_parser_makes_no_progress(self, mock_from_bytes):
        """A message that consumes no bytes must not loop forever."""
        mock_from_bytes.return_value = (0, MagicMock())
        
        with patch.object(self.protocol, '_reset_timeout'):
            self.protocol.data_received(b'elea28#1#0#')
            
            self.on_message.assert_not_called()


if __name__ == '__main__':
    unittest.main()