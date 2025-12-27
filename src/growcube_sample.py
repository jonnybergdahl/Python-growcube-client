import asyncio
import logging

from growcube_client import GrowcubeReport, GrowcubeClient, DeviceVersionGrowcubeReport, SetWorkModeCommand


# Define a callback function to print messages to the screen
def callback(report: GrowcubeReport) -> None:
    # Just dump the message to the console
    print(f"Received: {report.get_description()}")


def on_connected(self, host):
    print(f"Connected to {host}")


def on_disconnected(self, host):
    print(f"Disconnected from {host}")


async def main(host: str) -> None:
    logging.basicConfig(level=logging.DEBUG)

    # Create a client instance
    client = GrowcubeClient(host, callback)
    print(f"Connecting to Growcube at {HOST}")

    # Connect to the Growcube and start listening for messages
    await client.connect()

    while True:
        await asyncio.sleep(2)

if __name__ == "__main__":
    # Set host name or IP address
    HOST = "172.30.2.73"

    asyncio.run(main(HOST))
