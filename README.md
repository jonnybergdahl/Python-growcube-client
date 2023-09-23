# Python-growcube-client

This is an asyncio Python library to communicate with 
[Elecrow Growcube](https://www.elecrow.com/growcube-gardening-plants-smart-watering-kit-device.html) devices.
By using this library you can communicate directly with the device, without the need to use the phone app.

Once connected to a device, the library will listen for messages from the device and use a callback function
to return parsed messages to the application. The application can also send commands to the device.

## Installation

```
pip install growcube-client
```

## Getting started

The `src/rowcube.sample.py` file shows how to use the library. It defines a callback function where the GrowcubeClient
sends messages as they arrive from the Growcube device. To use the sample, change the `HOST` variable to the host
name or IP address of the Growcube device. Then run the sample with:

```bash
python3 growcube_sample.py
```

Source code:

```python
import asyncio
from growcube_client import GrowcubeClient, GrowcubeReport


# Define a callback function to print messages to the screen
def callback(report: GrowcubeReport) -> None:
    # Just dump the message to the console
    print(f"Received: {report.get_description()}")


async def main(host: str) -> None:
    # Create a client instance
    client = GrowcubeClient(host, callback)
    print(f"Connecting to Growcube at {HOST}")

    # Connect to the Growcube and start listening for messages
    await client.connect_and_listen()
    # The above call never finishes, so we will not reach here
    # In a real application this could be run in a background thread


if __name__ == "__main__":
    # Set host name or IP address
    HOST = "172.30.2.70"

    asyncio.run(main(HOST))
```

Sample script output.

```log
Connecting to Growcube at 172.30.2.70
Received: RepDeviceVersionCmd: version 3.6, device_id 12663500
Received: RepLockstateCmd: lock_state False
Received: RepWaterStateCmd: water_warning: True
Received: RepSTHSateCmd: pump: 0, moisture: 26, humidity: 41, temperature: 24
Received: RepSTHSateCmd: pump: 1, moisture: 26, humidity: 41, temperature: 24
Received: RepSTHSateCmd: pump: 2, moisture: 30, humidity: 41, temperature: 24
Received: RepSTHSateCmd: pump: 3, moisture: 33, humidity: 41, temperature: 24
```

## More advanced use

The `src/growcube_app.py` file shows how to use the library in a more advanced application. 

To use the app, you need to install `wxPython` first, please follow [the directions here](https://wiki.wxpython.org/How%20to%20install%20wxPython).

Start the app with:
```bash
python3 growcube_app.py
```

You are greeted with a screen asking for the host name or IP address of the Growcube device. 
Enter that and click the _Submit_ button. The app will connect to your Growcube and starts
displaying received data.

You can water plants by setting a watering duration and clicking the _Pump X_ button.

![Growcube app page 1](assets/app1.png)

# Auto discovery

You can use the sample script `src/growcube_discover.py` to search for devices on your network. By default, it will
search for devices on the local network, but if the devices are located in a separate subnet you can also specify 
that network to search in. 

```bash
python3 growcube_discover.py 192.168.4.0/24
```