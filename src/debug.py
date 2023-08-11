from growcube_client import *
import time

execute_water_command = False
client = GrowcubeClient("172.30.2.72")
client.connect()
client.set_work_mode(1)
while True:
    report = client.get_next_report()
    if report is not None:
        report.dump()
    if execute_water_command:
        # Turn on the #0 pump for 2 seconds
        command = WaterCommand(0, 1)
        client.send_command(command)
        time.sleep(2)
        command = WaterCommand(0, 0)
        client.send_command(command)
        execute_water_command = False
    #client.dump()

