from pyVmomi import vim
from .base import VmwareCheck


class CheckAlarms(VmwareCheck):

    obj_type = vim.Datacenter
    required = True

    def fmt_alarms(self, prop, output):
        output['alarms'] = alarms = []

        for alarm in prop.val:
            dct = self.prop_val_to_dict(alarm, item_name=str(alarm.key))
            dct['entityName'] = alarm.entity.name
            dct['alarmInfo'] = alarm.alarm.info.name
            dct['alarmDesc'] = alarm.alarm.info.description
            alarms.append(dct)

    properties = {'triggeredAlarmState': fmt_alarms}
