import asyncio
import logging

"""
Growcube client library
https://github.com/jonnybergdahl/Python-growcube-client

Author: Jonny Bergdahl
Date: 2023-09-05
"""


class GrowcubeDiscovery:
    PORT = 8800

    def __init__(self, log_level: int = logging.INFO) -> None:
        self.log_level = log_level
        self._devices = []

    def log_debug(self, message: str, *args) -> None:
        """
        Log a debug message

        Args:
            message: Message to log
            *args: Arguments for the message

        Returns:
            None

        """
        if self.log_level <= logging.DEBUG:
            logging.debug(message, *args)

    def log_error(self, message: str, *args) -> None:
        """
        Log a error message

        Args:
            message: Message to log
            *args: Arguments for the message

        Returns:
            None

        """
        if self.log_level <= logging.ERROR:
            logging.error(message, *args)

    async def discover_device(self, ip_address: str) -> bool:
        try:
            # Attempt to connect to port 777 with a timeout of 5 seconds
            print(f"Trying to connect to {ip_address}")
            _, writer = await asyncio.wait_for(asyncio.open_connection(ip_address, self.PORT), timeout=5)
            self.log_debug(f"Device discovered at {ip_address}:777")
            writer.close()
            await writer.wait_closed()
            self._devices.append(ip_address)
            return True
        except (asyncio.TimeoutError, ConnectionRefusedError):
            # Timeout or connection refused, device is not discovered
            return False

    async def discover_devices_in_local_subnet(self, subnet) -> list[str]:
        # Get the local subnet automatically
        local_subnet = subnet
        self._devices = []
        if local_subnet:
            self.log_debug(f"Scanning devices in local subnet: {local_subnet}")
            tasks = [self.discover_device(str(ip)) for ip in local_subnet.hosts()]

            # Run the tasks concurrently
            # Set the maximum number of concurrent tasks
            max_concurrent_tasks = 5
            semaphore = asyncio.Semaphore(max_concurrent_tasks)
            async with semaphore:
                await asyncio.gather(*tasks)
            return self._devices
        else:
            self.log_error("Failed to determine the local subnet. Make sure you are connected to a network.")
