import unittest
import asyncio
from unittest.mock import MagicMock, patch
from growcube_client import GrowcubeClient, GrowcubeMessage, Channel


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

    def test_disconnect(self):
        transport = self.client.transport

        self.client.disconnect()

        transport.close.assert_called_once()
        self.assertFalse(self.client.connected)
        self.assertIsNone(self.client.transport)

    def test_disconnect_closes_transport_held_only_by_the_protocol(self):
        """connect() assigns self.transport only once create_connection returns.

        If the attempt times out or is cancelled before that, the protocol is
        the only thing holding the open socket, and it still has to be closed:
        a Growcube serves one client at a time, so a leaked connection blocks
        every later attempt.
        """
        self.client.transport = None

        self.client.disconnect()

        self.client.protocol.transport.close.assert_called_once()

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

    def test_on_connected(self):
        self.client.on_connected()

        self.assertTrue(self.client.connected)
        self.on_connected_callback.assert_called_once_with(self.client.host)

    def test_on_connected_takes_the_transport_from_the_protocol(self):
        self.client.transport = None

        self.client.on_connected()

        self.assertIs(self.client.protocol.transport, self.client.transport)

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

    def test_on_message_records_the_device_id(self):
        data = GrowcubeMessage.to_bytes(24, "3.6@12345678")
        message = GrowcubeMessage(24, "3.6@12345678", data)

        self.client.on_message(message)

        self.assertEqual("12345678", self.client.device_id)
        self.assertEqual("3.6", self.client.version)


class GrowcubeClientConnectTestCase(unittest.IsolatedAsyncioTestCase):
    """Connection tests against a local server standing in for a Growcube."""

    DEVICE_ID = "12345678"
    VERSION = "3.6"

    async def asyncSetUp(self):
        self.reports = []
        self.server_saw_connection = asyncio.Event()
        self.server_saw_close = asyncio.Event()

    async def _collect_report(self, report):
        self.reports.append(report)

    async def _silent_handler(self, reader, writer):
        """Accepts the connection and then says nothing, like a wedged device."""
        self.server_saw_connection.set()
        # Returns as soon as the client closes its end
        await reader.read()
        self.server_saw_close.set()
        writer.close()

    async def _growcube_handler(self, reader, writer):
        self.server_saw_connection.set()
        writer.write(GrowcubeMessage.to_bytes(
            24, "{}@{}".format(self.VERSION, self.DEVICE_ID)))
        await writer.drain()
        await reader.read()
        self.server_saw_close.set()
        writer.close()

    async def _start_server(self, handler):
        """Starts a server on a free port and returns (server, port)."""
        server = await asyncio.start_server(handler, "127.0.0.1", 0)
        self.addAsyncCleanup(self._close_server, server)
        return server, server.sockets[0].getsockname()[1]

    async def _close_server(self, server):
        server.close()
        await server.wait_closed()

    def _make_client(self, port):
        client = GrowcubeClient("127.0.0.1", self._collect_report)
        client.port = port
        client.connection_timeout = 5
        client.device_id_timeout = 0.5
        self.addCleanup(client.disconnect)
        return client

    async def test_connect_returns_after_the_device_identifies_itself(self):
        _, port = await self._start_server(self._growcube_handler)
        client = self._make_client(port)

        result, error = await client.connect()

        self.assertTrue(result, error)
        self.assertEqual("", error)
        self.assertEqual(self.DEVICE_ID, client.device_id)
        self.assertEqual(self.VERSION, client.version)
        self.assertTrue(client.connected)

    async def test_connect_fails_and_closes_socket_when_device_stays_silent(self):
        """The core of the leak: a peer that accepts but never speaks.

        connect() used to report success as soon as the socket opened, and a
        later failure left that socket open. A Growcube serves a single client,
        so the leaked connection blocked every later attempt.
        """
        _, port = await self._start_server(self._silent_handler)
        client = self._make_client(port)

        result, error = await client.connect()

        self.assertFalse(result)
        self.assertIn("device ID", error)
        self.assertFalse(client.connected)
        self.assertIsNone(client.transport)
        # The server has to see the connection go away
        await asyncio.wait_for(self.server_saw_close.wait(), timeout=5)

    async def test_connect_without_handshake_returns_on_tcp_connect(self):
        _, port = await self._start_server(self._silent_handler)
        client = self._make_client(port)

        result, error = await client.connect(wait_for_device_id=False)

        self.assertTrue(result, error)
        self.assertIsNone(client.device_id)

    async def test_cancelled_connect_closes_the_socket(self):
        """Cancellation has to propagate, and must not leave the socket open."""
        _, port = await self._start_server(self._silent_handler)
        client = self._make_client(port)
        client.device_id_timeout = 30

        task = asyncio.ensure_future(client.connect())
        await asyncio.wait_for(self.server_saw_connection.wait(), timeout=5)
        task.cancel()

        with self.assertRaises(asyncio.CancelledError):
            await task
        await asyncio.wait_for(self.server_saw_close.wait(), timeout=5)

    async def test_connect_reports_an_unreachable_host(self):
        # Start a server to get a free port, then close it before connecting
        server, port = await self._start_server(self._silent_handler)
        await self._close_server(server)
        client = self._make_client(port)

        result, error = await client.connect()

        self.assertFalse(result)
        self.assertNotEqual("", error)

    async def test_get_device_id_returns_the_device_id(self):
        _, port = await self._start_server(self._growcube_handler)

        result, device_id = await GrowcubeClient.get_device_id(
            "127.0.0.1", port=port, timeout=5)

        self.assertTrue(result, device_id)
        self.assertEqual(self.DEVICE_ID, device_id)
        await asyncio.wait_for(self.server_saw_close.wait(), timeout=5)

    async def test_get_device_id_reports_a_device_that_stays_silent(self):
        _, port = await self._start_server(self._silent_handler)

        result, error = await GrowcubeClient.get_device_id(
            "127.0.0.1", port=port, timeout=0.5)

        self.assertFalse(result)
        self.assertIn("device ID", error)
        await asyncio.wait_for(self.server_saw_close.wait(), timeout=5)

    async def test_water_plant(self):
        _, port = await self._start_server(self._growcube_handler)
        client = self._make_client(port)
        client.send_command = MagicMock(return_value=True)

        result = await client.water_plant(Channel.Channel_A, 0)

        self.assertTrue(result)
        # Called twice, start and stop
        self.assertEqual(2, client.send_command.call_count)


if __name__ == '__main__':
    unittest.main()
