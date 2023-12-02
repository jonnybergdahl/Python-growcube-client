import asyncio
import ipaddress
import logging
from socket import socket

"""
Growcube client library
https://github.com/jonnybergdahl/Python-growcube-client

Author: Jonny Bergdahl
Date: 2023-09-05
"""


class GrowcubeDiscovery:
    """
    Class for discovering Growcube devices on the network.

    :cvar PORT: The default port for Growcube device discovery.
    :vartype PORT: int

    :ivar log_level: The logging level.
    :type log_level: int
    :ivar _devices: A list to store discovered devices.
    :type _devices: list[str]
    """

    PORT = 8800

    def __init__(self, log_level: int = logging.INFO) -> None:
        """
        GrowcubeDiscovery constructor

        :param log_level: The logging level. (Default: logging.INFO)
        :type log_level: int
        """
        self.log_level = log_level
        self._devices = []

    async def discover_device(self, ip_address: str) -> bool:
        """
        Attempt to discover a Growcube device at the specified IP address.

        :param ip_address: The IP address to check.
        :type ip_address: str
        :return: True if the device is discovered, False otherwise.
        :rtype: bool
        """
        try:
            # Attempt to connect to port self.PORT with a timeout of 5 seconds
            print(f"Trying to connect to {ip_address}")
            _, writer = await asyncio.wait_for(asyncio.open_connection(ip_address, self.PORT), timeout=5)
            logging.debug(f"Device discovered at {ip_address}:777")
            writer.close()
            await writer.wait_closed()
            self._devices.append(ip_address)
            return True
        except (asyncio.TimeoutError, ConnectionRefusedError):
            # Timeout or connection refused, device is not discovered
            return False

    async def discover_devices_in_local_subnet(self, subnet: ipaddress.IPv4Network = None) -> list[str]:
        """
        Discover Growcube devices in the local subnet.

        :param subnet: The local subnet to scan.
        :type subnet: ipaddress.IPv4Network
        :return: A list of discovered device IP addresses.
        :rtype: list[str]
        """
        # Get the local subnet automatically
        if not subnet:
            subnet = self.guess_subnet()
        local_subnet = subnet
        self._devices = []
        if local_subnet:
            logging.debug(f"Scanning devices in local subnet: {local_subnet}")
            tasks = [self.discover_device(str(ip)) for ip in local_subnet.hosts()]

            # Run the tasks concurrently
            # Set the maximum number of concurrent tasks
            max_concurrent_tasks = 5
            semaphore = asyncio.Semaphore(max_concurrent_tasks)
            async with semaphore:
                await asyncio.gather(*tasks)
            return self._devices
        else:
            logging.error("Failed to determine the local subnet. Make sure you are connected to a network.")

    def guess_subnet(self) -> ipaddress.IPv4Network:
        '''
        Guess the local subnet based on the local IP address
        We just assume a /24 network as that is true in 99,999% of the cases

        :return: The local subnet
        :rtype: ipaddress.IPv4Network
        '''
        # Get local IP address
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))  # Using Google's DNS server address
        local_ip = sock.getsockname()[0]
        sock.close()
        # Make network mask
        split = local_ip.split(".")
        subnet = f"{split[0]}.{split[1]}.{split[2]}.0/24"
        logging.debug(f"Guessed local subnet: {subnet}")
        return ipaddress.IPv4Network(subnet, strict=False)