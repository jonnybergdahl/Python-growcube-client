import time
import logging
import npyscreen
import threading
import asyncio
from growcube_client import GrowcubeClient
from growcube_client import (DeviceVersionGrowcubeReport, LockStateGrowcubeReport, CheckSensorGrowcubeReport,
                             MoistureHumidityStateGrowcubeReport, WaterStateGrowcubeReport)

MAIN_FORM = "MAIN"
DATA_FORM = "DATA"


async def async_client_with_callback(client, callback):
    await client.connect_and_listen()


class HostNameForm(npyscreen.ActionForm):

    def create(self):
        self.host_name_widget = self.add(npyscreen.TitleText, name='Host name', value="172.30.2.72")

    def on_ok(self):
        host_name = self.host_name_widget.value
        if host_name:
            self.parentApp.start_async_client(host_name)
            self.parentApp.setNextForm(DATA_FORM)
            self.parentApp.getForm(DATA_FORM).set_host_name(host_name)

    def on_cancel(self):
        self.parentApp.setNextForm(None)

class DetailForm(npyscreen.ActionFormMinimal):

    def create(self):
        column_width = min(self.max_x // 2 - 1, 44)
        self.footer_widget = self.add(npyscreen.TitleFixedText, name="Commands:", value="Exit: x, Water plants: a, b, c, d", editable=False)
        self.nextrely += 1
        # Add widgets for displaying Growcube data
        self.host_name_widget = self.add(npyscreen.TitleFixedText, name="Host Name:", title="Kuken", value="", max_width=column_width)
        self.device_id_widget = self.add(npyscreen.TitleFixedText, name="Device ID:", max_width=column_width)
        self.version_widget = self.add(npyscreen.TitleFixedText, name="Version:", max_width=column_width)
        self.lock_state_widget = self.add(npyscreen.TitleFixedText, name="Lock state:", value="OK", max_width=column_width)
        self.sensor_state_widget = self.add(npyscreen.TitleFixedText, name="Sensor state:", value="OK", max_width=column_width)
        self.water_state_widget = self.add(npyscreen.TitleFixedText, name="Water state:", value="OK", max_width=column_width)
        self.nextrely = 4
        self.nextrelx = column_width - 1
        self.humidity_widget = self.add(npyscreen.TitleFixedText, name="Humidity:", max_width=column_width)
        self.temperature_widget = self.add(npyscreen.TitleFixedText, name="Temperature:", max_width=column_width)
        self.moistureA_widget = self.add(npyscreen.TitleFixedText, name="Moisture A:", max_width=column_width)
        self.moistureB_widget = self.add(npyscreen.TitleFixedText, name="Moisture B:", max_width=column_width)
        self.moistureC_widget = self.add(npyscreen.TitleFixedText, name="Moisture C:", max_width=column_width)
        self.moistureD_widget = self.add(npyscreen.TitleFixedText, name="Moisture D:", max_width=column_width)
        self.nextrely += 1
        self.nextrelx = 2
        self.log_widget = self.add(npyscreen.Pager, name="Log:")
        self.add_handlers({
            "x": self.on_cancel,
            "a": self.on_water_a,
            "b": self.on_water_b,
            "c": self.on_water_c,
            "d": self.on_water_d,
        })

        # Create a custom log handler and add it to the root logger
        custom_handler = LogHandler(self)
        logging.root.addHandler(custom_handler)
        logging.getLogger().setLevel(logging.DEBUG)

    def on_ok(self):
        # Exit application
        self.parentApp.setNextForm(None)

    def set_host_name(self, host_name):
        self.host_name_widget.value = host_name
        self.display()

    def update_data(self, data):
        logging.info(f"Got message {data.get_description()}")
        if isinstance(data, MoistureHumidityStateGrowcubeReport):
            if data.pump == 0:
                self.humidity_widget.value = f"{data.humidity}%"
                self.temperature_widget.value = f"{data.temperature}°C"
                self.moistureA_widget.value = f"{data.moisture}%"
            elif data.pump == 1:
                self.moistureB_widget.value = f"{data.moisture}%"
            elif data.pump == 2:
                self.moistureC_widget.value = f"{data.moisture}%"
            elif data.pump == 3:
                self.moistureD_widget.value = f"{data.moisture}%"
        elif isinstance(data, DeviceVersionGrowcubeReport):
            self.version_widget.value = data.version
            self.device_id_widget.value = data.device_id
        elif isinstance(data, LockStateGrowcubeReport):
            self.lock_state_widget.value = 'OK' if not data.lock_state else 'Locked'
        elif isinstance(data, CheckSensorGrowcubeReport):
            self.sensor_state_widget.value = 'OK' if not data.fault_state else 'Check sensors'
        elif isinstance(data, WaterStateGrowcubeReport):
            self.water_state_widget.value = 'OK' if not data.water_warning else 'Water warning'
        self.display()

    def add_log_entry(self, log_entry):
        self.log_widget.values.append(log_entry)
        self.log_widget.values = self.log_widget.values[-self.log_widget.height:]
        self.display()

    def on_cancel(self):
        self.parentApp.setNextForm(None)

    def on_water_a(self, key):
        asyncio.run(self.parentApp.client.water_plant(0, 5))

    def on_water_b(self, key):
        asyncio.run(self.parentApp.client.water_plant(1, 5))

    def on_water_c(self, key):
        asyncio.run(self.parentApp.client.water_plant(2, 5))

    def on_water_d(self, key):
        asyncio.run(self.parentApp.client.water_plant(3, 5))


class LogHandler(logging.Handler):
    def __init__(self, log_form):
        super(LogHandler, self).__init__()
        self.log_form = log_form

    def emit(self, record):
        log_entry = self.format(record)  # Format the log message
        self.log_form.add_log_entry(log_entry)


class GrowcubeApp(npyscreen.NPSAppManaged):
    def onStart(self):
        # Add the forms to the app
        self.addForm(MAIN_FORM, HostNameForm, name="Growcube host name")
        self.addForm(DATA_FORM, DetailForm, name="Growcube data")

    def start_async_client(self, host_name):
        def callback(data):
            # This callback receives data from the Growcube client thread
            self.getForm(DATA_FORM).update_data(data)

        # Start the async background thread
        self.async_thread = threading.Thread(target=self.async_runner, args=(host_name, callback))
        self.async_thread.daemon = True
        self.async_thread.start()

    def async_runner(self, host_name, callback):
        time.sleep(2)   # Give the GUI time to initialize
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self.client = GrowcubeClient(host_name, callback)
        client_task = loop.create_task(async_client_with_callback(self.client, callback))
        loop.run_forever()


if __name__ == "__main__":
    app = GrowcubeApp()
    app.run()

