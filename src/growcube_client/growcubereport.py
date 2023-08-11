from typing import Union, Any


class ReportBase:
    Response = {
        20: "RepWaterStateCmd",
        21: "RepSTHSateCmd",
        22: "RepCurveCmd",
        23: "RepAutoWaterCmd",
        24: "RepDeviceVersionCmd",
        25: "RepErasureDataCmd",
        26: "RepPumpOpenCmd",
        27: "RepPumpCloseCmd",
        28: "RepCheckSenSorNotConnectedCmd",
        29: "RepCheckDuZhuanCmd",
        30: "RepCheckSenSorNotConnectCmd",
        31: "RepWifistateCmd",
        32: "RepGrowCubeIPCmd",
        33: "RepLockstateCmd",
        34: "ReqCheckSenSorLockCmd",
        35: "RepCurveEndFlagCmd"
    }
    CMD_INNER = "@"

    def __init__(self, command):
        if command in self.Response:
            self.command = self.Response[command]
        else:
            self.command = f"Unknown: {command}"

    def dump(self):
        print(self.command)


# Response 20 - RepWaterState
class WaterStateReport(ReportBase):
    def __init__(self, data):
        ReportBase.__init__(self, 20)
        self.water_warning = data == "1"

    def dump(self):
        print(f"{self.command}: water_warning: {self.water_warning}")


# Response 21 - RepSTHState
class MoistureHumidityStateReport(ReportBase):
    def __init__(self, data):
        ReportBase.__init__(self, 21)
        values = data.split(self.CMD_INNER)
        self.pump = int(values[0])
        self.moisture = int(values[1])
        self.humidity = int(values[2])
        self.temperature = int(values[3])

    def dump(self):
        print(f"{self.command}: pump: {self.pump}, moisture: {self.moisture}, humidity: {self.humidity}, temperature: {self.temperature}")


# Response 23 - AutoWater
class AutoWaterReport(ReportBase):
    def __init__(self, data):
        ReportBase.__init__(self, 23)
        parts = data.split(self.CMD_INNER)
        self.pump = int(parts[0])
        self.year = int(parts[1])
        self.month = int(parts[2])
        self.date = int(parts[3])
        self.hour = int(parts[4])
        self.minute = int(parts[5])

    def dump(self):
        print(f"{self.command}: {self.pump} - {self.year}-{self.month}-{self.date} {self.hour}:{self.minute}")


# Response 24 -
# elea24#11#3.6@2487625#
class DeviceVersionReport(ReportBase):
    def __init__(self, data):
        ReportBase.__init__(self, 24)
        temp = data.split(self.CMD_INNER)
        self.version = temp[0]
        self.device_id = temp[1]

    def dump(self):
        print(f"{self.command}: version {self.version}, device_id {self.device_id}")

# Reponse 25
# elea25#3#52d# 
class EraseDataReport(ReportBase):
    def __init__(self, data):
        ReportBase.__init__(self, 25)
        self.success = data == "52d"

    def dump(self):
        print(f"{self.command}: version {self.version}, device_id {self.device_id}")

# Reponse 26
class PumpOpenReport(ReportBase):
    def __init__(self, data):
        ReportBase.__init__(self, 26)
        self.pump = int(data)

    def dump(self):
        print(f"{self.command}: pump {self.pump}")

# Reponse 27
class PumpCloseReport(ReportBase):
    def __init__(self, data):
        ReportBase.__init__(self, 27)
        self.pump = int(data)

    def dump(self):
        print(f"{self.command}: pump {self.pump}")

# Reponse 28
class CheckSensorReport(ReportBase):
    def __init__(self, data):
        ReportBase.__init__(self, 28)
        self.fault_state = data

    def dump(self):
#        print(f"FIX ME")
        print(f"{self.command}: fault_state {self.fault_state}")

# Response 29
class CheckDuZhuanReport(ReportBase):
    def __init__(self, data):
        ReportBase.__init__(self, 29)
        self.state = data == "1"

    def dump(self):
        print(f"{self.command}: fault_state {self.state}")

# Response 30
class CheckSensorNotConnectedReport(ReportBase):
    def __init__(self, data):
        ReportBase.__init__(self, 30)
        self.state = data == "0"

    def dump(self):
        print(f"{self.command}: state {self.state}")

# Response 31
class CheckWifiStateReport(ReportBase):
    def __init__(self, data):
        ReportBase.__init__(self, 31)
        self.state = data == "1"

    def dump(self):
        print(f"{self.command}: state {self.state}")

# Response 32
class GrowCubeIPReport(ReportBase):
    def __init__(self, data):
        ReportBase.__init__(self, 32)
        self.ip = data

    def dump(self):
        print(f"{self.command}: ip {self.ip}")

# Response 33
class LockStateReport(ReportBase):
    lock_state: bool

    def __init__(self, data):
        ReportBase.__init__(self, 33)
        temp = data.split(self.CMD_INNER)
        self.lock_state = temp[1] == "1"

    def dump(self):
        print(f"{self.command}: lock_state {self.lock_state}")

# Response 34
class CheckSensorLockReport(ReportBase):
    def __init__(self, data):
        ReportBase.__init__(self, 34)
        temp = data.split(self.CMD_INNER)
        self.lock_state = temp[1]

    def dump(self):
        print(f"{self.command}: lock_state {self.lock_state}")

# Response 35
class RepCurveEndFlagReport(ReportBase):
    def __init__(self, data):
        ReportBase.__init__(self, 35)
        self.data = data

    def dump(self):
        print(f"{self.command}: data {self.lock_state}")

class UnknownReport(ReportBase):
    def __init__(self, command, data):
        super().__init__(command)
        temp = data.split(self.CMD_INNER)
        self.data = ", ".join(temp)

    def dump(self):
        print(f"{self.command}: data {self.data}")