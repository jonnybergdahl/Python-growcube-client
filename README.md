# Python-growcube-client

Python library for communication with Growcube devices.

## Installation

```
pip install growcube-client
```

## Get started

Simple use, connect to device, get all data and exit.
```python
from growcube_client import GrowcubeClient

HOST = "172.30.2.70"

print(f"Connecting to Growcube at {HOST}")
client = GrowcubeClient(HOST)
client.connect()
print(f"Getting data...")
data = client.get_all_data()
if data:
    client.dump()

```

continuous use, connect to device and dump all received data.

```python
from growcube_client import GrowcubeClient

HOST = "172.30.2.71"
PORT = 8800

print(f"Connecting to Growcube at {HOST}")
client = GrowcubeClient(HOST, PORT)
client.connect()

while True:
    message = client.get_next_report()
    if message is not None:
        message.dump()

```

Sample output
```
Connecting to Growcube at 172.30.2.71
RepVersionAndWater: version 3.6
Unknown report: 33: data 0, @, 0
RepWaterState: water_warning: False
RepSTHSate: pump: 0, moisture: 18, humidity: 39, temperature: 22
RepSTHSate: pump: 1, moisture: 22, humidity: 39, temperature: 22
RepSTHSate: pump: 2, moisture: 31, humidity: 39, temperature: 22
RepSTHSate: pump: 3, moisture: 24, humidity: 39, temperature: 22
```
