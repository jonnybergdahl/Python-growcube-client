"""
Growcube client

Author: Jonny Bergdahl
Date: 2023-09-05
"""
import logging as logger


class GrowcubeReportBase:
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

    @staticmethod
    def get_report(message):
        if message is None:
            return None
        if message.command == 20:
            return WaterStateGrowcubeReport(message.payload)
        elif message.command == 21:
            return MoistureHumidityStateGrowcubeReport(message.payload)
        elif message.command == 23:
            return AutoWaterGrowcubeReport(message.payload)
        elif message.command == 24:
            return DeviceVersionGrowcubeReport(message.payload)
        elif message.command == 25:
            return EraseDataGrowcubeReport(message.payload)
        elif message.command == 26:
            return PumpOpenGrowcubeReport(message.payload)
        elif message.command == 27:
            return PumpCloseGrowcubeReport(message.payload)
        elif message.command == 28:
            return CheckSensorGrowcubeReport(message.payload)
        elif message.command == 29:
            return CheckDuZhuanGrowcubeReport(message.payload)
        elif message.command == 30:
            return CheckSensorNotConnectedGrowcubeReport(message.payload)
        elif message.command == 31:
            return CheckWifiStateGrowcubeReport(message.payload)
        elif message.command == 32:
            return GrowCubeIPGrowcubeReport(message.payload)
        elif message.command == 33:
            return LockStateGrowcubeReport(message.payload)
        elif message.command == 34:
            return CheckSensorLockGrowcubeReport(message.payload)
        elif message.command == 35:
            return RepCurveEndFlagGrowcubeReport(message.payload)
        else:
            return UnknownGrowcubeReport(message.command, message.payload)

    def get_description(self):
        print(self.command)


# Response 20 - RepWaterState
class WaterStateGrowcubeReport(GrowcubeReportBase):
    def __init__(self, data):
        GrowcubeReportBase.__init__(self, 20)
        self.water_warning = int(data) != 0

    def get_description(self):
        return f"{self.command}: water_warning: {self.water_warning}"


# Response 21 - RepSTHState
class MoistureHumidityStateGrowcubeReport(GrowcubeReportBase):
    def __init__(self, data):
        GrowcubeReportBase.__init__(self, 21)
        values = data.split(self.CMD_INNER)
        self.pump = int(values[0])
        self.moisture = int(values[1])
        self.humidity = int(values[2])
        self.temperature = int(values[3])

    def get_description(self):
        return f"{self.command}: pump: {self.pump}, moisture: {self.moisture}, humidity: {self.humidity}, temperature: {self.temperature}"


# Response 23 - AutoWater
class AutoWaterGrowcubeReport(GrowcubeReportBase):
    def __init__(self, data):
        GrowcubeReportBase.__init__(self, 23)
        parts = data.split(self.CMD_INNER)
        self.pump = int(parts[0])
        self.year = int(parts[1])
        self.month = int(parts[2])
        self.date = int(parts[3])
        self.hour = int(parts[4])
        self.minute = int(parts[5])

    def get_description(self):
        return f"{self.command}: {self.pump} - {self.year}-{self.month}-{self.date} {self.hour}:{self.minute}"


# Response 24 -
# elea24#11#3.6@2487625#
class DeviceVersionGrowcubeReport(GrowcubeReportBase):
    def __init__(self, data):
        GrowcubeReportBase.__init__(self, 24)
        temp = data.split(self.CMD_INNER)
        self.version = temp[0]
        self.device_id = temp[1]

    def get_description(self):
        return f"{self.command}: version {self.version}, device_id {self.device_id}"


# Reponse 25
# elea25#3#52d# 
class EraseDataGrowcubeReport(GrowcubeReportBase):
    def __init__(self, data):
        GrowcubeReportBase.__init__(self, 25)
        self.success = data == "52d"

    def get_description(self):
        return f"{self.command}: version {self.version}, device_id {self.device_id}"


# Reponse 26
class PumpOpenGrowcubeReport(GrowcubeReportBase):
    def __init__(self, data):
        GrowcubeReportBase.__init__(self, 26)
        self.pump = int(data)

    def get_description(self):
        return f"{self.command}: pump {self.pump}"


# Reponse 27
class PumpCloseGrowcubeReport(GrowcubeReportBase):
    def __init__(self, data):
        GrowcubeReportBase.__init__(self, 27)
        self.pump = int(data)

    def get_description(self):
        return f"{self.command}: pump {self.pump}"


# Reponse 28
class CheckSensorGrowcubeReport(GrowcubeReportBase):
    def __init__(self, data):
        GrowcubeReportBase.__init__(self, 28)
        self.fault_state = data == 1

    def get_description(self):
        return f"{self.command}: fault_state {self.fault_state}"


# Response 29
class CheckDuZhuanGrowcubeReport(GrowcubeReportBase):
    def __init__(self, data):
        GrowcubeReportBase.__init__(self, 29)
        self.state = data == "1"

    def get_description(self):
        return f"{self.command}: fault_state {self.state}"


# Response 30
class CheckSensorNotConnectedGrowcubeReport(GrowcubeReportBase):
    def __init__(self, data):
        GrowcubeReportBase.__init__(self, 30)
        self.state = data == "0"

    def get_description(self):
        return f"{self.command}: state {self.state}"


# Response 31
class CheckWifiStateGrowcubeReport(GrowcubeReportBase):
    def __init__(self, data):
        GrowcubeReportBase.__init__(self, 31)
        self.state = data == "1"

    def get_description(self):
        return f"{self.command}: state {self.state}"


# Response 32
class GrowCubeIPGrowcubeReport(GrowcubeReportBase):
    def __init__(self, data):
        GrowcubeReportBase.__init__(self, 32)
        self.ip = data

    def get_description(self):
        return f"{self.command}: ip {self.ip}"


# Response 33
class LockStateGrowcubeReport(GrowcubeReportBase):
    lock_state: bool

    def __init__(self, data):
        GrowcubeReportBase.__init__(self, 33)
        temp = data.split(self.CMD_INNER)
        self.lock_state = temp[1] == "1"

    def get_description(self):
        return f"{self.command}: lock_state {self.lock_state}"


# Response 34
class CheckSensorLockGrowcubeReport(GrowcubeReportBase):
    def __init__(self, data):
        GrowcubeReportBase.__init__(self, 34)
        temp = data.split(self.CMD_INNER)
        self.lock_state = temp[1]

    def get_description(self):
        return f"{self.command}: lock_state {self.lock_state}"


# Response 35
class RepCurveEndFlagGrowcubeReport(GrowcubeReportBase):
    def __init__(self, data):
        GrowcubeReportBase.__init__(self, 35)
        self.data = data

    def get_description(self):
        return f"{self.command}: data {self.lock_state}"


class UnknownGrowcubeReport(GrowcubeReportBase):
    def __init__(self, command, data):
        super().__init__(command)
        temp = data.split(self.CMD_INNER)
        self.data = ", ".join(temp)

    def get_description(self):
        return f"{self.command}: data {self.data}"
