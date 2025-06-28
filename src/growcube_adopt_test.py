import asyncio
import logging

from growcube_client import GrowcubeReport, GrowcubeClient, SetWorkModeCommand, WiFiSettingsCommand
from growcube_client.growcubeenums import WorkMode


# Define a on_message_callback function to print messages to the screen
def on_message(report: GrowcubeReport) -> None:
    # Just dump the message to the console
    print(f"Received: {report.get_description()}")


def on_connected(self, host):
    print(f"Connected to {host}")


def on_disconnected(self, host):
    print(f"Disconnected from {host}")


async def main(host: str) -> None:
    logging.basicConfig(level=logging.DEBUG)

    # Create a client instance
    client = GrowcubeClient(host, on_message, on_connected, on_disconnected)
    print(f"Connecting to Growcube at {HOST}")

    # Connect to the Growcube and start listening for messages
    await client.connect()

    result = client.send_command(WiFiSettingsCommand(SSID, PASSWORD))
    result = client.send_command(SetWorkModeCommand(WorkMode.Network))
    while True:
        await asyncio.sleep(2)

if __name__ == "__main__":
    # Set host name or IP address
    HOST = "192.168.1.125"
    SSID = "SSID"
    PASSWORD = "password"

    asyncio.run(main(HOST))
