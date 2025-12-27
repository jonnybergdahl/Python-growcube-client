import asyncio
import logging
import argparse
import ipaddress
import socket
from growcube_client import GrowcubeDiscovery

'''
A simple autodiscovery script for Growcube devices
If your devices are in another network than your networks default subnet you can add the subnet as 
a command-line argument in the format '192.168.1.0/24'.

I also found the default max open files limit to be too low for this script to work in macOS (100 files). 
You can increase the limit by running this command before running this script:
ulimit -n 1024
'''


def guess_subnet() -> ipaddress.IPv4Network:
    '''
    Guess the local subnet based on the local IP address
    We just assume a /24 network as that is true in 99,999% of the cases
    Returns:
        The local subnet
    '''
    # Get local IP address
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(("8.8.8.8", 80))  # Using Google's DNS server as an example
    local_ip = sock.getsockname()[0]
    sock.close()
    # Make network mask
    split = local_ip.split(".")
    subnet = f"{split[0]}.{split[1]}.{split[2]}.0/24"
    return ipaddress.IPv4Network(subnet, strict=False)


async def main() -> None:
    '''
    Main async function
    Returns:
        None
    '''
    # Get the command-line argument
    parser = argparse.ArgumentParser(description="Discover Growcube devices in a subnet.")
    parser.add_argument("subnet", nargs="?", type=str, help="Subnet in CIDR notation (e.g., 192.168.1.0/24)")
    args = parser.parse_args()
    if args.subnet:
        subnet = ipaddress.IPv4Network(args.subnet, strict=False)
    else:
        subnet = None # guess_subnet()

    discovery = GrowcubeDiscovery()
    print(f"Discovering Growcube clients on subnet {subnet}")
    devices = await discovery.discover_devices_in_local_subnet(subnet)
    print(f"Found {len(devices)} devices:")
    for device in devices:
        print(f"Found device: {device}")


if __name__ == "__main__":
    asyncio.run(main())