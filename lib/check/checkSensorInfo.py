from pyVmomi import vim
from .base import EsxOnlyCheck


class CheckSensorInfo(EsxOnlyCheck):
    obj_type = vim.HostSystem

    def fmt_sensors(self, prop, output):
        output['sensor'] = sensors = []
        for sensor in prop.val:
            sensors.append({
                'name': sensor.name,
                'healthState': sensor.healthState.key,
                'currentReading': sensor.currentReading,
                'unitModifier': sensor.unitModifier,
                'baseUnits': sensor.baseUnits,
                'readingValue': sensor.currentReading * (
                    10 ** sensor.unitModifier),
                'rateUnits': sensor.rateUnits,
                'sensorType': sensor.sensorType
            })

    properties = {
        'runtime.healthSystemRuntime.systemHealthInfo.numericSensorInfo':
        fmt_sensors
    }
