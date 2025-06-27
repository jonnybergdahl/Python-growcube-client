import time

import wx
import asyncio
import threading
from datetime import datetime
import logging

from getmac import get_mac_address
from growcube_client.growcubeclient import GrowcubeClient
from growcube_client.growcubecommand import WiFiSettingsCommand, SetWorkModeCommand, WorkMode
from growcube_client.growcubereport import GrowCubeIPGrowcubeReport, CheckWifiStateGrowcubeReport

# Default device IP
DEFAULT_DEVICE_IP = "192.168.1.125"

class AdoptFrame(wx.Frame):
    def __init__(self, parent=None, device_ip=DEFAULT_DEVICE_IP):
        super().__init__(parent, wx.ID_ANY, "Growcube WiFi Setup", size=(500, 400))
        self.device_ip = device_ip
        self.client = None
        self._build_ui()
        self.Centre()
        logging.basicConfig(level=logging.DEBUG)

    def _build_ui(self):
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Connect button
        self.connect_btn = wx.Button(panel, label="Connect")
        self.connect_btn.Bind(wx.EVT_BUTTON, self.on_connect)
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
        self._append_log("UI initialized.")

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
            self._append_log(f"Inputs {'enabled' if enabled else 'disabled'}.")
        wx.CallAfter(_enable)

    def on_connect(self, event):
        self.connect_btn.Enable(False)
        threading.Thread(target=self._connect_to_device, daemon=True).start()

    def _connect_to_device(self):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            client = GrowcubeClient(
                self.device_ip,
                callback=self._on_report,
                on_connected_callback=None,
                on_disconnected_callback=None
            )
            success, err = loop.run_until_complete(client.connect())
            if success:
                self.client = client
                wx.CallAfter(self._on_connected_success)
            else:
                wx.CallAfter(self._on_connected_failure, err)
        except Exception as e:
            wx.CallAfter(self._on_connected_failure, str(e))

    def _on_connected_success(self):
        try:
            mac = get_mac_address(ip=self.device_ip) or ""
            self._append_log(f"Device MAC: {mac}")
        except Exception:
            self._append_log("Failed to lookup MAC address.")
        self._set_controls_enabled(True)

    def _on_connected_failure(self, error_msg):
        self._append_log(f"Failed to connect: {error_msg}")
        self.connect_btn.Enable(True)

    def on_save(self, event):
        ssid = self.ssid_text.GetValue()
        password = self.pass_text.GetValue()
        if not ssid:
            wx.MessageBox("SSID cannot be empty.", "Validation Error", wx.ICON_WARNING)
            return
        if self.client.send_command(WiFiSettingsCommand(ssid, password)):
            time.sleep(1)
            self.client.send_command(SetWorkModeCommand(WorkMode.Network))
            self._append_log("WiFi settings command sent. Waiting for IP report...")
            self._set_controls_enabled(False)
        else:
            self._append_log("Failed to send WiFi settings.")

    async def _on_report(self, report):
        if isinstance(report, GrowCubeIPGrowcubeReport):
            self._append_log(f"New IP: {report.ip}")
        elif isinstance(report, CheckWifiStateGrowcubeReport):
            self._append_log(f"New WIFI state: {report.state}")

if __name__ == '__main__':
    app = wx.App(False)
    frame = AdoptFrame()
    frame.Show()
    app.MainLoop()
