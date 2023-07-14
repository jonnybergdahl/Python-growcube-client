import logging
import sys
import time
from growcube_client import GrowcubeClient

HOST = "172.30.2.72"
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

print(f"Connecting to Growcube at {HOST}")
start_time = time.time()
client = GrowcubeClient(HOST)
if not client.connect():
    exit()
print('Set work mode')
client.set_work_mode(2)
print("Getting data...")
data = client.get_all_data()
client.dump()
print(f'Total run time: {time.time() - start_time:2f} seconds')