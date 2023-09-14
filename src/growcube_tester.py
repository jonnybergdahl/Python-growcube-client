import asyncio
import logging
import sys
import threading
import time
import curses
from growcube_client import GrowcubeClient


class SampleClient:

    def __init__(self, host):
        self.host = host
        self.client = None
        self.screen = curses.initscr()
        self.height, self.width = self.screen.getmaxyx()  # get the window size
        curses.start_color()
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLUE)

    # Write a header and footer, first write colored strip, then write text
        self.screen.bkgd(curses.color_pair(3))
        self.screen.addstr(0, 0, " " * self.width, curses.color_pair(1))
        self.screen.addstr(self.height - 1, 0, " " * (self.width - 1), curses.color_pair(1))
        self.screen.addstr(0, 0, " Curses Dynamic Text Example", curses.color_pair(1))
        self.screen.addstr(self.height - 1, 0, " Key Commands : q - to quit ", curses.color_pair(1))
        self.screen.addstr(3, 5, "RASPBERRY PI SIMULATED SENSOR VALUES", curses.A_BOLD)
        self.screen.screenscr.refresh()

    def callback(self, report):
        report.dump()

    def disconnect(self):
        self.client.disconnect()

    async def water(self, pump, duration):
        await self.client.water_plant(pump, duration)

    async def run_client(self):
        print(f"Connecting to Growcube at {self.host}")
        self.client = GrowcubeClient(self.host, self.callback)
        await self.client.connect_and_listen()

    def async_runner(self):
        start_time = time.time()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.run_client())
        loop.close()
        print(f"Exiting async_runner after {time.time() - start_time} seconds")


async def main(host):
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    client = SampleClient(host)
    worker_thread = threading.Thread(target=client.async_runner)
    worker_thread.start()
    print("Press Ctrl+C to exit")
    while True:
        try:
            user_input = input()
            if user_input == "x":
                print("Exiting...")
                client.disconnect()
                break
            elif user_input == "w":
                print("Watering...")
                await client.water(0, 2)
        except KeyboardInterrupt:
            print("Exiting...")
            break
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    HOST = "172.30.2.72"
    asyncio.run(main(HOST))
    print("All done!")


