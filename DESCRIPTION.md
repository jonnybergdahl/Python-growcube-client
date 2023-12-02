This is an asyncio Python library to communicate with 
[Elecrow Growcube](https://www.elecrow.com/growcube-gardening-plants-smart-watering-kit-device.html) devices.
By using this library you can communicate directly with the device, without the need to use the phone app.

Once connected to a device, the library will listen for messages from the device and use a callback function
to return parsed messages to the application. The application can also send commands to the device.

## Features

- Connect to the Growcube device
- Listen for messages from the device
- Send commands to the device
- Search for devices in a local network

## Install

```bash
pip3 install growcube-client
```

## Getting started

Check out the instructions on [github.com/jonnybergdahl/Python-growcube-client](https://github.com/jonnybergdahl/Python-growcube-client).
You will find sample scripts that show how it is used, as well a more advanced GUI app.

# More information

Documentation on how the protocol was reverse engineered can be found at 
[Growcube_Hacking](https://github.com/jonnybergdahl/GrowCube_Hacking).
