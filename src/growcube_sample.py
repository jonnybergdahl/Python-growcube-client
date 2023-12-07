import asyncio
from growcube_client import GrowcubeReport, GrowcubeClient


# Define a callback function to print messages to the screen
def callback(report: GrowcubeReport) -> None:
    # Just dump the message to the console
    print(f"Received: {report.get_description()}")


async def main(host: str) -> None:
    # Create a client instance
    client = GrowcubeClient(host, callback)
    print(f"Connecting to Growcube at {HOST}")

    # Connect to the Growcube and start listening for messages
    await client.connect()

    while True:
        await asyncio.sleep(2)

if __name__ == "__main__":
    # Set host name or IP address
    HOST = "172.30.2.71"

    asyncio.run(main(HOST))
