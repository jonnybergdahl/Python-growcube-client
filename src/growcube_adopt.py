import queue
import wx
import asyncio
import threading
from datetime import datetime
import logging

from getmac import get_mac_address

from growcube_app import DEBUG_LEVEL
from growcube_client.growcubeclient import GrowcubeClient
from growcube_client.growcubecommand import WiFiSettingsCommand, SetWorkModeCommand, WorkMode, GrowcubeCommand, WaterCommand
from growcube_client.growcubereport import GrowCubeIPGrowcubeReport, CheckWifiStateGrowcubeReport

# Default device IP
DEFAULT_DEVICE_IP = "192.168.1.125"

class AdoptFrame(wx.Frame):
    def __init__(self, parent=None, device_ip=DEFAULT_DEVICE_IP):
        super().__init__(parent, wx.ID_ANY, "Growcube WiFi Setup", size=(500, 400))
        self.device_ip = device_ip
        self.client = None
        self.background_thread_loop = None
        self.exit_background_thread = False
        self.command_queue = queue.Queue()
        self.client_thread = None
        self._build_ui()
        self.Centre()
        logging.basicConfig(level=logging.DEBUG)

    def _build_ui(self):
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Connect button
        self.connect_btn = wx.Button(panel, label="Connect")
        self.connect_btn.Bind(wx.EVT_BUTTON, self.on_connect_pressed)
        sizer.Add(self.connect_btn, flag=wx.ALL | wx.EXPAND, border=10)

        # SSID input
        self.ssid_label = wx.StaticText(panel, label="SSID:")
        self.ssid_text = wx.TextCtrl(panel)
        sizer.Add(self.ssid_label, flag=wx.LEFT | wx.TOP, border=10)
        sizer.Add(self.ssid_text, flag=wx.LEFT | wx.EXPAND, border=10)

        # Password input
        self.pass_label = wx.StaticText(panel, label="Password:")
        self.pass_text = wx.TextCtrl(panel, style=wx.TE_PASSWORD)
        sizer.Add(self.pass_label, flag=wx.LEFT | wx.TOP, border=10)
        sizer.Add(self.pass_text, flag=wx.LEFT | wx.EXPAND, border=10)

        # Save button
        self.save_btn = wx.Button(panel, label="Save")
        self.save_btn.Bind(wx.EVT_BUTTON, self.on_save)
        sizer.Add(self.save_btn, flag=wx.ALL | wx.EXPAND, border=10)

        # Progress log display
        self.log_ctrl = wx.TextCtrl(panel,
                                     style=wx.TE_MULTILINE | wx.TE_READONLY)
        sizer.Add(self.log_ctrl,
                  proportion=1,
                  flag=wx.ALL | wx.EXPAND,
                  border=10)

        panel.SetSizer(sizer)

        # Disable inputs initially
        self._set_controls_enabled(False)

    def _append_log(self, message: str):
        entry = message
        if not message.startswith('['):
            entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}"
        self.log_ctrl.AppendText(f"{entry}\n")

    def _set_controls_enabled(self, enabled: bool):
        def _enable():
            self.ssid_text.Enable(enabled)
            self.pass_text.Enable(enabled)
            self.save_btn.Enable(enabled)
        wx.CallAfter(_enable)

    async def run_client_until_terminated(self):
        wx.CallAfter(self._append_log, f"Attempting to connect to {self.device_ip}...")
        success, error_message = await self.client.connect()
        if not success:
            wx.CallAfter(self._append_log, f"Connection failed: {error_message}")
        while not self.exit_background_thread:
            if not self.command_queue.empty():
                command = self.command_queue.get()
                if isinstance(command, GrowcubeCommand):
                    self.client.send_command(command)
            await asyncio.sleep(1)

    def start_async_client_thread(self, host_name):
        self.client = GrowcubeClient(host_name, 
                                     on_message_callback=self._on_message,
                                     on_connected_callback=self._on_connected,
                                     on_disconnected_callback=self._on_disconnected)
        self.exit_background_thread = False

        # Create a new event loop for the background thread
        self.background_thread_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.background_thread_loop)

        # Run the client until terminated
        self.background_thread_loop.run_until_complete(self.run_client_until_terminated())

    def on_connect_pressed(self, event):
        self.connect_btn.Enable(False)
        threading.Thread(target=self._connect_to_device, daemon=True).start()

    def _connect_to_device(self):
        try:
            # Stop any existing client thread
            if self.client_thread is not None:
                self.exit_background_thread = True
                self.client_thread.join()
                self.client_thread = None

            # Start a new client thread
            self.client_thread = threading.Thread(
                target=self.start_async_client_thread, 
                args=(self.device_ip,),
                daemon=True
            )
            self.client_thread.start()

            # Enable the UI after connection attempt
            wx.CallAfter(self.connect_btn.Enable, True)
        except Exception as e:
            wx.CallAfter(self._append_log, f"Error connecting: {str(e)}")
            wx.CallAfter(self.connect_btn.Enable, True)

    def on_save(self, event):
        ssid = self.ssid_text.GetValue()
        password = self.pass_text.GetValue()
        if not ssid:
            wx.MessageBox("SSID cannot be empty.", "Validation Error", wx.ICON_WARNING)
            return
        if not password:
            wx.MessageBox("Password cannot be empty.", "Validation Error", wx.ICON_WARNING)
            return

        # Add commands to the queue
        self.command_queue.put(WiFiSettingsCommand(ssid, password))
        self.command_queue.put(SetWorkModeCommand(WorkMode.Network))
        self._append_log("WiFi settings command sent. Waiting for IP report...")
        self._set_controls_enabled(False)

    async def _on_connected(self, host):
        wx.CallAfter(self._append_log, f"Connected to {host}")
        mac = get_mac_address(ip=host) or ""
        wx.CallAfter(self._append_log, f"Device MAC: {mac}")
        wx.CallAfter(self._set_controls_enabled, True)

    async def _on_disconnected(self, host):
        wx.CallAfter(self._append_log, f"Disconnected from {host}")
        wx.CallAfter(self._set_controls_enabled, False)

    async def _on_message(self, report):
        if isinstance(report, GrowCubeIPGrowcubeReport):
            wx.CallAfter(self._append_log, f"Successfully connected to: {self.ssid_text.GetValue()}")
            wx.CallAfter(self._append_log, f"New IP: {report.ip}")
            self.exit_background_thread = True
        elif isinstance(report, CheckWifiStateGrowcubeReport):
            wx.CallAfter(self._append_log, f"New WIFI state: {report.state}")
            wx.CallAfter(self._append_log, "==================================================")
            wx.CallAfter(self._append_log, "Connection to WiFi FAILED, check WiFi credentials!")
            wx.CallAfter(self._append_log, "==================================================")
            self.exit_background_thread = True
            # Start a new connection attempt
            wx.CallAfter(self._reconnect)

    def _reconnect(self):
        """
        Reconnect to the device by stopping the existing client thread and starting a new one.
        """
        self._append_log("Reconnecting to device...")
        threading.Thread(target=self._connect_to_device, daemon=True).start()

    def stop_async_client_thread(self):
        if self.client is not None:
            self.client.disconnect()
            self.exit_background_thread = True
        if self.client_thread is not None and self.client_thread.is_alive():
            self.client_thread.join(timeout=2)  # Add timeout to avoid hanging
            self.client_thread = None

    def Destroy(self):
        """
        Override the Destroy method to ensure the background thread is stopped
        when the application is closed.
        """
        self.stop_async_client_thread()
        return super().Destroy()

if __name__ == '__main__':
    app = wx.App(False)
    frame = AdoptFrame()
    frame.Show()
    app.MainLoop()
