import concurrent
import datetime
import queue
import time

import wx
import threading
import asyncio
import logging

_LOGGER = logging.getLogger(__name__)

from growcube_client import GrowcubeClient, Channel, GrowcubeCommand, PumpOpenGrowcubeReport, PumpCloseGrowcubeReport, \
    SyncWaterLevelCommand, SyncWaterTimeCommand, SetWorkModeCommand
from growcube_client import (DeviceVersionGrowcubeReport, LockStateGrowcubeReport, CheckSensorGrowcubeReport, \
                             MoistureHumidityStateGrowcubeReport, WaterStateGrowcubeReport, \
                             CheckSensorNotConnectedGrowcubeReport,  CheckOutletLockedGrowcubeReport, \
                             CheckOutletBlockedGrowcubeReport)

DEBUG_LEVEL = logging.DEBUG


class LogHandler(logging.Handler):
    def __init__(self, gui):
        super(LogHandler, self).__init__()
        self.gui = gui

    def emit(self, record):
        log_entry = self.format(record)  # Format the log message
        self.gui.add_log_entry(log_entry)


class WaterCommand:
    def __init__(self, channel: Channel, duration: int):
        self.channel = channel
        self.duration = duration


class SimpleGUI(wx.Frame):
    def __init__(self):
        super().__init__(None, wx.ID_ANY, "Growcube Python App")

        # Create a custom log handler and add it to the root logger
        custom_handler = LogHandler(self)
        logging.root.addHandler(custom_handler)
        self.log_lines = []

        self.host_name = "-"
        self.version = "-"
        self.device_id = "-"
        self.humidity = 0
        self.temperature = 0
        self.moisture_a = 0
        self.moisture_b = 0
        self.moisture_c = 0
        self.moisture_d = 0
        self.lock_state = False
        self.sensor_state_a = False
        self.sensor_state_b = False
        self.sensor_state_c = False
        self.sensor_state_d = False
        self.water_state = False
        self.sensor_connected_a = False
        self.sensor_connected_b = False
        self.sensor_connected_c = False
        self.sensor_connected_d = False
        self.pump_state_a = False
        self.pump_state_b = False
        self.pump_state_c = False
        self.pump_state_d = False
        self.outlet_locked_a = False
        self.outlet_locked_b = False
        self.outlet_locked_c = False
        self.outlet_locked_d = False
        self.outlet_blocked_a = False
        self.outlet_blocked_b = False
        self.outlet_blocked_c = False
        self.outlet_blocked_d = False
        self.client = None
        self.client_thread = None
        self.loop = None
        self.background_thread_loop = None
        self.background_thread_executor = None
        self.exit_background_thread = False

        self.command_queue = queue.Queue()

        if self.loop is None:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

        # Set the window size
        self.SetSize((1024, 1024))

        panel = wx.Panel(self)

        # Create a sizer for the main layout
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # First group box
        group_box1 = wx.StaticBox(panel, label="Growcube address")
        group_box_sizer1 = wx.StaticBoxSizer(group_box1, wx.VERTICAL)
        row_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.host_name_input = wx.TextCtrl(panel, value="172.30.2.72")
        button = wx.Button(panel, label="Submit")
        button.Bind(wx.EVT_BUTTON, self.connect)
        row_sizer.Add(self.host_name_input, 1, wx.EXPAND | wx.ALL, 5)
        row_sizer.Add(button, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        group_box_sizer1.Add(row_sizer, 0, wx.EXPAND | wx.ALL, 0)

        # Second group box
        group_box2 = wx.StaticBox(panel, label="Growcube data")
        group_box_sizer2 = wx.StaticBoxSizer(group_box2, wx.VERTICAL)

        # Data row 1
        row1_sizer = wx.BoxSizer(wx.HORIZONTAL)
        label1 = wx.StaticText(panel, label=f"Host name:")
        self.host_name_text = wx.StaticText(panel, label="-")
        label2 = wx.StaticText(panel, label="Humidity:")
        self.humidity_text = wx.StaticText(panel, label="- %")
        row1_sizer.Add(label1, 1, wx.EXPAND | wx.ALL, 5)
        row1_sizer.Add(self.host_name_text, 1, wx.EXPAND | wx.ALL, 5)
        row1_sizer.Add(label2, 1, wx.EXPAND | wx.ALL, 5)
        row1_sizer.Add(self.humidity_text, 1, wx.EXPAND | wx.ALL, 5)
        group_box_sizer2.Add(row1_sizer, 0, wx.EXPAND | wx.ALL, 0)

        # Data row 2
        row2_sizer = wx.BoxSizer(wx.HORIZONTAL)
        label1 = wx.StaticText(panel, label=f"Device ID")
        self.device_id_text = wx.StaticText(panel, label="-")
        label2 = wx.StaticText(panel, label="Temperature")
        self.temperature_text = wx.StaticText(panel, label="-° C")  # You can set initial values here
        row2_sizer.Add(label1, 1, wx.EXPAND | wx.ALL, 5)
        row2_sizer.Add(self.device_id_text, 1, wx.EXPAND | wx.ALL, 5)
        row2_sizer.Add(label2, 1, wx.EXPAND | wx.ALL, 5)
        row2_sizer.Add(self.temperature_text, 1, wx.EXPAND | wx.ALL, 5)
        group_box_sizer2.Add(row2_sizer, 0, wx.EXPAND | wx.ALL, 0)

        # Data row 3
        row3_sizer = wx.BoxSizer(wx.HORIZONTAL)
        label1 = wx.StaticText(panel, label=f"Version")
        self.version_text = wx.StaticText(panel, label="-")
        label2 = wx.StaticText(panel, label=f"Lock state:")
        self.lock_state_text = wx.StaticText(panel, label="OK")
        row3_sizer.Add(label1, 1, wx.EXPAND | wx.ALL, 5)
        row3_sizer.Add(self.version_text, 1, wx.EXPAND | wx.ALL, 5)
        row3_sizer.Add(label2, 1, wx.EXPAND | wx.ALL, 5)
        row3_sizer.Add(self.lock_state_text, 1, wx.EXPAND | wx.ALL, 5)
        group_box_sizer2.Add(row3_sizer, 0, wx.EXPAND | wx.ALL, 0)

        # Data row 4
        row4_sizer = wx.BoxSizer(wx.HORIZONTAL)
        label1 = wx.StaticText(panel, label=f"Water state:")
        self.water_state_text = wx.StaticText(panel, label="OK")
        label2 = wx.StaticText(panel, label=f"")
        label3 = wx.StaticText(panel, label=f"")
        row4_sizer.Add(label1, 1, wx.EXPAND | wx.ALL, 5)
        row4_sizer.Add(self.water_state_text, 1, wx.EXPAND | wx.ALL, 5)
        row4_sizer.Add(label2, 1, wx.EXPAND | wx.ALL, 5)
        row4_sizer.Add(label3, 1, wx.EXPAND | wx.ALL, 5)
        group_box_sizer2.Add(row4_sizer, 0, wx.EXPAND | wx.ALL, 0)

        # Data row 5
        row5_sizer = wx.BoxSizer(wx.HORIZONTAL)
        label1 = wx.StaticText(panel, label="Moisture A")
        self.moisture_a_text = wx.StaticText(panel, label="- %")  # You can set initial values here
        label2 = wx.StaticText(panel, label="Moisture B:")
        self.moisture_b_text = wx.StaticText(panel, label="- %")  # You can set initial values here
        row5_sizer.Add(label1, 1, wx.EXPAND | wx.ALL, 5)
        row5_sizer.Add(self.moisture_a_text, 1, wx.EXPAND | wx.ALL, 5)
        row5_sizer.Add(label2, 1, wx.EXPAND | wx.ALL, 5)
        row5_sizer.Add(self.moisture_b_text, 1, wx.EXPAND | wx.ALL, 5)
        group_box_sizer2.Add(row5_sizer, 0, wx.EXPAND | wx.ALL, 0)

        # Data row 6
        row6_sizer = wx.BoxSizer(wx.HORIZONTAL)
        label1 = wx.StaticText(panel, label="Moisture C:")
        self.moisture_c_text = wx.StaticText(panel, label="- %")  # You can set initial values here
        label2 = wx.StaticText(panel, label="Moisture D:")
        self.moisture_d_text = wx.StaticText(panel, label="- %")  # You can set initial values here
        row6_sizer.Add(label1, 1, wx.EXPAND | wx.ALL, 5)
        row6_sizer.Add(self.moisture_c_text, 1, wx.EXPAND | wx.ALL, 5)
        row6_sizer.Add(label2, 1, wx.EXPAND | wx.ALL, 5)
        row6_sizer.Add(self.moisture_d_text, 1, wx.EXPAND | wx.ALL, 5)
        group_box_sizer2.Add(row6_sizer, 0, wx.EXPAND | wx.ALL, 0)

        # Data row 7
        row7_sizer = wx.BoxSizer(wx.HORIZONTAL)
        label1 = wx.StaticText(panel, label="Pump state A:")
        self.pump_state_a_text = wx.StaticText(panel, label="OK")
        label2 = wx.StaticText(panel, label="Pump state B:")
        self.pump_state_b_text = wx.StaticText(panel, label="OK")
        row7_sizer.Add(label1, 1, wx.EXPAND | wx.ALL, 5)
        row7_sizer.Add(self.pump_state_a_text, 1, wx.EXPAND | wx.ALL, 5)
        row7_sizer.Add(label2, 1, wx.EXPAND | wx.ALL, 5)
        row7_sizer.Add(self.pump_state_b_text, 1, wx.EXPAND | wx.ALL, 5)
        group_box_sizer2.Add(row7_sizer, 0, wx.EXPAND | wx.ALL, 0)

        # Data row 8
        row8_sizer = wx.BoxSizer(wx.HORIZONTAL)
        label1 = wx.StaticText(panel, label="Pump state C:")
        self.pump_state_c_text = wx.StaticText(panel, label="OK")
        label2 = wx.StaticText(panel, label="Pump state D:")
        self.pump_state_d_text = wx.StaticText(panel, label="OK")
        row8_sizer.Add(label1, 1, wx.EXPAND | wx.ALL, 5)
        row8_sizer.Add(self.pump_state_c_text, 1, wx.EXPAND | wx.ALL, 5)
        row8_sizer.Add(label2, 1, wx.EXPAND | wx.ALL, 5)
        row8_sizer.Add(self.pump_state_d_text, 1, wx.EXPAND | wx.ALL, 5)
        group_box_sizer2.Add(row8_sizer, 0, wx.EXPAND | wx.ALL, 0)

        # Data row 9
        row9_sizer = wx.BoxSizer(wx.HORIZONTAL)
        label1 = wx.StaticText(panel, label=f"Sensor A connected:")
        self.sensor_connected_a_text = wx.StaticText(panel, label="OK")
        label2 = wx.StaticText(panel, label=f"Sensor B connected:")
        self.sensor_connected_b_text = wx.StaticText(panel, label="OK")
        row9_sizer.Add(label1, 1, wx.EXPAND | wx.ALL, 5)
        row9_sizer.Add(self.sensor_connected_a_text, 1, wx.EXPAND | wx.ALL, 5)
        row9_sizer.Add(label2, 1, wx.EXPAND | wx.ALL, 5)
        row9_sizer.Add(self.sensor_connected_b_text, 1, wx.EXPAND | wx.ALL, 5)
        group_box_sizer2.Add(row9_sizer, 0, wx.EXPAND | wx.ALL, 0)

        # Data row 10
        row10_sizer = wx.BoxSizer(wx.HORIZONTAL)
        label1 = wx.StaticText(panel, label=f"Sensor C connected:")
        self.sensor_connected_c_text = wx.StaticText(panel, label="OK")
        label2 = wx.StaticText(panel, label=f"Sensor D connected:")
        self.sensor_connected_d_text = wx.StaticText(panel, label="OK")
        row10_sizer.Add(label1, 1, wx.EXPAND | wx.ALL, 5)
        row10_sizer.Add(self.sensor_connected_c_text, 1, wx.EXPAND | wx.ALL, 5)
        row10_sizer.Add(label2, 1, wx.EXPAND | wx.ALL, 5)
        row10_sizer.Add(self.sensor_connected_d_text, 1, wx.EXPAND | wx.ALL, 5)
        group_box_sizer2.Add(row10_sizer, 0, wx.EXPAND | wx.ALL, 0)

        # Data row 11
        row11_sizer = wx.BoxSizer(wx.HORIZONTAL)
        label1 = wx.StaticText(panel, label=f"Sensor A fault:")
        self.sensor_state_a_text = wx.StaticText(panel, label="OK")
        label2 = wx.StaticText(panel, label="Sensor B fault:")
        self.sensor_state_b_text = wx.StaticText(panel, label="OK")  # You can set initial values here
        row11_sizer.Add(label1, 1, wx.EXPAND | wx.ALL, 5)
        row11_sizer.Add(self.sensor_state_a_text, 1, wx.EXPAND | wx.ALL, 5)
        row11_sizer.Add(label2, 1, wx.EXPAND | wx.ALL, 5)
        row11_sizer.Add(self.sensor_state_b_text, 1, wx.EXPAND | wx.ALL, 5)
        group_box_sizer2.Add(row11_sizer, 0, wx.EXPAND | wx.ALL, 0)

        # Data row 12
        row12_sizer = wx.BoxSizer(wx.HORIZONTAL)
        label1 = wx.StaticText(panel, label=f"Sensor C fault:")
        self.sensor_state_c_text = wx.StaticText(panel, label="OK")
        label2 = wx.StaticText(panel, label="Sensor D fault:")
        self.sensor_state_d_text = wx.StaticText(panel, label="OK")  # You can set initial values here
        row12_sizer.Add(label1, 1, wx.EXPAND | wx.ALL, 5)
        row12_sizer.Add(self.sensor_state_c_text, 1, wx.EXPAND | wx.ALL, 5)
        row12_sizer.Add(label2, 1, wx.EXPAND | wx.ALL, 5)
        row12_sizer.Add(self.sensor_state_d_text, 1, wx.EXPAND | wx.ALL, 5)
        group_box_sizer2.Add(row12_sizer, 0, wx.EXPAND | wx.ALL, 0)

        # Data row 13
        row13_sizer = wx.BoxSizer(wx.HORIZONTAL)
        label1 = wx.StaticText(panel, label=f"Outlet A locked:")
        self.outlet_locked_a_text = wx.StaticText(panel, label="OK")
        label2 = wx.StaticText(panel, label="Outlet B locked:")
        self.outlet_locked_b_text = wx.StaticText(panel, label="OK")  # You can set initial values here
        row13_sizer.Add(label1, 1, wx.EXPAND | wx.ALL, 5)
        row13_sizer.Add(self.outlet_locked_a_text, 1, wx.EXPAND | wx.ALL, 5)
        row13_sizer.Add(label2, 1, wx.EXPAND | wx.ALL, 5)
        row13_sizer.Add(self.outlet_locked_b_text, 1, wx.EXPAND | wx.ALL, 5)
        group_box_sizer2.Add(row13_sizer, 0, wx.EXPAND | wx.ALL, 0)

        # Data row 14
        row14_sizer = wx.BoxSizer(wx.HORIZONTAL)
        label1 = wx.StaticText(panel, label=f"Outlet C locked:")
        self.outlet_locked_c_text = wx.StaticText(panel, label="OK")
        label2 = wx.StaticText(panel, label="Outlet D locked:")
        self.outlet_locked_d_text = wx.StaticText(panel, label="OK")  # You can set initial values here
        row14_sizer.Add(label1, 1, wx.EXPAND | wx.ALL, 5)
        row14_sizer.Add(self.outlet_locked_c_text, 1, wx.EXPAND | wx.ALL, 5)
        row14_sizer.Add(label2, 1, wx.EXPAND | wx.ALL, 5)
        row14_sizer.Add(self.outlet_locked_d_text, 1, wx.EXPAND | wx.ALL, 5)
        group_box_sizer2.Add(row14_sizer, 0, wx.EXPAND | wx.ALL, 0)

        # Data row 15
        row15_sizer = wx.BoxSizer(wx.HORIZONTAL)
        label1 = wx.StaticText(panel, label=f"Outlet A blocked:")
        self.outlet_blocked_a_text = wx.StaticText(panel, label="OK")
        label2 = wx.StaticText(panel, label="Outlet B blocked:")
        self.outlet_blocked_b_text = wx.StaticText(panel, label="OK")  # You can set initial values here
        row15_sizer.Add(label1, 1, wx.EXPAND | wx.ALL, 5)
        row15_sizer.Add(self.outlet_blocked_a_text, 1, wx.EXPAND | wx.ALL, 5)
        row15_sizer.Add(label2, 1, wx.EXPAND | wx.ALL, 5)
        row15_sizer.Add(self.outlet_blocked_b_text, 1, wx.EXPAND | wx.ALL, 5)
        group_box_sizer2.Add(row15_sizer, 0, wx.EXPAND | wx.ALL, 0)

        # Data row 16
        row16_sizer = wx.BoxSizer(wx.HORIZONTAL)
        label1 = wx.StaticText(panel, label=f"Outlet C blocked:")
        self.outlet_blocked_c_text = wx.StaticText(panel, label="OK")
        label2 = wx.StaticText(panel, label="Outlet D blocked:")
        self.outlet_blocked_d_text = wx.StaticText(panel, label="OK")
        row16_sizer.Add(label1, 1, wx.EXPAND | wx.ALL, 5)
        row16_sizer.Add(self.outlet_blocked_c_text, 1, wx.EXPAND | wx.ALL, 5)
        row16_sizer.Add(label2, 1, wx.EXPAND | wx.ALL, 5)
        row16_sizer.Add(self.outlet_blocked_d_text, 1, wx.EXPAND | wx.ALL, 5)
        group_box_sizer2.Add(row16_sizer, 0, wx.EXPAND | wx.ALL, 0)

        group_box3 = wx.StaticBox(panel, label="Watering")
        group_box_sizer3 = wx.StaticBoxSizer(group_box3, wx.VERTICAL)
        row13_sizer = wx.BoxSizer(wx.HORIZONTAL)
        label1 = wx.StaticText(panel, label=f"Duration (s):")
        self.watering_duration_text = wx.TextCtrl(panel, value="5")
        button_a = wx.Button(panel, label="Pump A")
        button_a.Bind(wx.EVT_BUTTON, self.water_channel_a)
        button_b = wx.Button(panel, label="Pump B")
        button_b.Bind(wx.EVT_BUTTON, self.water_channel_b)
        button_c = wx.Button(panel, label="Pump C")
        button_c.Bind(wx.EVT_BUTTON, self.water_channel_c)
        button_d = wx.Button(panel, label="Pump D")
        button_d.Bind(wx.EVT_BUTTON, self.water_channel_d)
        row13_sizer.Add(label1, 1, wx.EXPAND | wx.ALL, 5)
        row13_sizer.Add(self.watering_duration_text, 1, wx.EXPAND | wx.ALL, 5)
        row13_sizer.Add(button_a, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        row13_sizer.Add(button_b, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        row13_sizer.Add(button_c, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        row13_sizer.Add(button_d, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        group_box_sizer3.Add(row13_sizer, 0, wx.EXPAND | wx.ALL, 0)

        # Third group box
        group_box4 = wx.StaticBox(panel, label="Log")
        group_box_sizer4 = wx.StaticBoxSizer(group_box4, wx.VERTICAL)
        self.log_text = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY, size=(wx.DefaultSize[0], 12 * 22))
        group_box_sizer4.Add(self.log_text, 1, wx.EXPAND | wx.ALL, 8)

        # Add group boxes to main sizer
        main_sizer.Add(group_box_sizer1, 0, wx.EXPAND | wx.ALL, 10)
        main_sizer.Add(group_box_sizer2, 0, wx.EXPAND | wx.ALL, 10)
        main_sizer.Add(group_box_sizer3, 0, wx.EXPAND | wx.ALL, 10)
        main_sizer.Add(group_box_sizer4, 0, wx.EXPAND | wx.ALL, 10)

        # Set the main sizer for the panel
        panel.SetSizer(main_sizer)

        self.status_bar = self.CreateStatusBar()
        self.status_bar.SetStatusText("Not connected");

        # Center and show the frame
        # self.Centre()
        # self.Show()

    def add_log_entry(self, log_entry):
        print(log_entry)
        self.log_lines.append(log_entry)
        self.log_lines = self.log_lines[-10:]
        wx.CallAfter(self.update_log)

    def update_log(self):
        log_text = "\n".join(self.log_lines)
        self.log_text.SetValue(log_text)

    async def run_client_until_terminated(self):
        await self.client.connect()
        while not self.exit_background_thread:
            if not self.command_queue.empty():
                command = self.command_queue.get()
                if isinstance(command, GrowcubeCommand):
                    self.client.send_command(command)
                elif isinstance(command, WaterCommand):
                    await self.client.water_plant(command.channel, command.duration)
            if self.client.connected and time.time() - self.client.heartbeat > 10:
                _LOGGER.debug("Heartbeat timeout")
                self.client.disconnect()
            await asyncio.sleep(1)

    def start_async_client_thread(self, host_name):
        self.client = GrowcubeClient(host_name, self.on_message,
                                     on_connected_callback=self.on_connected,
                                     on_disconnected_callback=self.on_disconnected)
        self.exit_background_thread = False
        if self.background_thread_loop is None:
            self.background_thread_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.background_thread_loop)
            self.background_thread_executor = concurrent.futures.ThreadPoolExecutor()
        self.background_thread_loop.run_until_complete(self.run_client_until_terminated())

    def stop_async_client_thread(self):
        if self.client is not None:
            self.client.disconnect()
            self.exit_background_thread = True;
        if self.client_thread is not None:
            self.client_thread.join()

    def connect(self, event):
        if self.client is not None:
            self.stop_async_client_thread()

        self.host_name = self.host_name_input.GetValue()
        self.client_thread = threading.Thread(target=self.start_async_client_thread, args=(self.host_name,))
        self.client_thread.start()

    def update_status_bar(self, status):
        self.status_bar.SetStatusText(status)

    def on_connected(self, host):
        wx.CallAfter(self.update_status_bar, f"Connected to {host}")

    def on_disconnected(self, host):
        wx.CallAfter(self.update_status_bar, f"Disconnected from {host}")

    def on_message(self, data):
        self.add_log_entry(f"< {data.get_description()}")
        if isinstance(data, DeviceVersionGrowcubeReport):
            self.version = data.version
            self.device_id = data.device_id
        elif isinstance(data, MoistureHumidityStateGrowcubeReport):
            if data.channel == Channel.Channel_A:
                self.humidity = data.humidity
                self.temperature = data.temperature
                self.moisture_a = data.moisture
            elif data.channel == Channel.Channel_B:
                self.moisture_b = data.moisture
            elif data.channel == Channel.Channel_C:
                self.moisture_c = data.moisture
            elif data.channel == Channel.Channel_D:
                self.moisture_d = data.moisture
        elif isinstance(data, LockStateGrowcubeReport):
            self.lock_state = data.lock_state
        elif isinstance(data, CheckSensorGrowcubeReport):
            if data.channel == Channel.Channel_A:
                self.sensor_state_a = True
            elif data.channel == Channel.Channel_B:
                self.sensor_state_b = True
            elif data.channel == Channel.Channel_C:
                self.sensor_state_c = True
            elif data.channel == Channel.Channel_D:
                self.sensor_state_d = True
        elif isinstance(data, CheckSensorNotConnectedGrowcubeReport):
            if data.channel == Channel.Channel_A:
                self.sensor_connected_a = True
            elif data.channel == Channel.Channel_B:
                self.sensor_connected_b = True
            elif data.channel == Channel.Channel_C:
                self.sensor_connected_c = True
            elif data.channel == Channel.Channel_D:
                self.sensor_connected_d = True
        elif isinstance(data, CheckOutletLockedGrowcubeReport):
            if data.channel == Channel.Channel_A:
                self.outlet_locked_a = True
            elif data.channel == Channel.Channel_B:
                self.outlet_locked_b = True
            elif data.channel == Channel.Channel_C:
                self.outlet_locked_c = True
            elif data.channel == Channel.Channel_D:
                self.outlet_locked_d = True
        elif isinstance(data, CheckOutletBlockedGrowcubeReport):
            if data.channel == Channel.Channel_A:
                self.outlet_blocked_a = True
            elif data.channel == Channel.Channel_B:
                self.outlet_blocked_b = True
            elif data.channel == Channel.Channel_C:
                self.outlet_blocked_c = True
            elif data.channel == Channel.Channel_D:
                self.outlet_blocked_d = True
        elif isinstance(data, WaterStateGrowcubeReport):
            self.water_state = data.water_warning
        elif isinstance(data, PumpOpenGrowcubeReport):
            if data.channel == Channel.Channel_A:
                self.pump_state_a = True
            elif data.channel == Channel.Channel_B:
                self.pump_state_b = True
            elif data.channel == Channel.Channel_C:
                self.pump_state_c = True
            elif data.channel == Channel.Channel_D:
                self.pump_state_d = True
        elif isinstance(data, PumpCloseGrowcubeReport):
            if data.channel == Channel.Channel_A:
                self.pump_state_a = False
            elif data.channel == Channel.Channel_B:
                self.pump_state_b = False
            elif data.channel == Channel.Channel_C:
                self.pump_state_c = False
            elif data.channel == Channel.Channel_D:
                self.pump_state_d = False
        wx.CallAfter(self.update_gui, None)

    def _water_channel(self, channel: Channel) -> None:
        duration = 0
        value = self.watering_duration_text.GetValue()
        if value.isnumeric():
            duration = int(value)
        if duration > 0:
            self.command_queue.put(WaterCommand(channel, duration))

    def water_channel_a(self, event):
        self._water_channel(Channel.Channel_A)

    def water_channel_b(self, event):
        self._water_channel(Channel.Channel_B)

    def water_channel_c(self, event):
        self._water_channel(Channel.Channel_C)

    def water_channel_d(self, event):
        self._water_channel(Channel.Channel_D)

    def update_gui(self, _):
        self.host_name_text.SetLabel(self.host_name)
        self.version_text.SetLabel(self.version)
        self.device_id_text.SetLabel(self.device_id)
        self.humidity_text.SetLabel(f"{self.humidity} %")
        self.temperature_text.SetLabel(f"{self.temperature} °C")
        self.moisture_a_text.SetLabel(f"{self.moisture_a} %")
        self.moisture_b_text.SetLabel(f"{self.moisture_b} %")
        self.moisture_c_text.SetLabel(f"{self.moisture_c} %")
        self.moisture_d_text.SetLabel(f"{self.moisture_d} %")
        self.lock_state_text.SetLabel('OK' if not self.lock_state else 'Locked')
        self.water_state_text.SetLabel('OK' if not self.water_state else 'Water warning')
        self.sensor_connected_a_text.SetLabel('OK' if not self.sensor_connected_a else 'Failed')
        self.sensor_connected_b_text.SetLabel('OK' if not self.sensor_connected_b else 'Failed')
        self.sensor_connected_c_text.SetLabel('OK' if not self.sensor_connected_c else 'Failed')
        self.sensor_connected_d_text.SetLabel('OK' if not self.sensor_connected_d else 'Failed')
        self.sensor_state_a_text.SetLabel('OK' if not self.sensor_state_a else 'Check')
        self.sensor_state_b_text.SetLabel('OK' if not self.sensor_state_b else 'Check')
        self.sensor_state_c_text.SetLabel('OK' if not self.sensor_state_c else 'Check')
        self.sensor_state_d_text.SetLabel('OK' if not self.sensor_state_d else 'Check')
        self.outlet_locked_a_text.SetLabel('OK' if not self.outlet_locked_a else 'Locked')
        self.outlet_locked_b_text.SetLabel('OK' if not self.outlet_locked_b else 'Locked')
        self.outlet_locked_c_text.SetLabel('OK' if not self.outlet_locked_c else 'Locked')
        self.outlet_locked_b_text.SetLabel('OK' if not self.outlet_locked_d else 'Locked')
        self.pump_state_a_text.SetLabel('On' if self.pump_state_a else 'Off')
        self.pump_state_b_text.SetLabel('On' if self.pump_state_b else 'Off')
        self.pump_state_c_text.SetLabel('On' if self.pump_state_c else 'Off')
        self.pump_state_d_text.SetLabel('On' if self.pump_state_d else 'Off')


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = wx.App(False)
    frame = SimpleGUI()
    frame.Show()
    app.MainLoop()
    # Shut down any background tasks
    frame.stop_async_client_thread()
    print("Done")
