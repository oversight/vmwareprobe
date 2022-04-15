from itertools import chain
from pyVmomi import vim
from .base import EsxOnlyCheck

# http://kb.vmware.com/selfservice/microsites/search.do?language=en_US&cmd=displayKC&externalId=1037330


class CheckHardwareStatus(EsxOnlyCheck):

    obj_type = vim.HostSystem

    def fmt_hardware_status(self, prop, output):
        output['hardwareStatus'] = hardware_status = []
        for item in chain(
                prop.val.memoryStatusInfo,
                prop.val.cpuStatusInfo,
                prop.val.storageStatusInfo):
            hardware_status.append(
                {'name': item.name, 'status': item.status.key})

    properties = {
        'runtime.healthSystemRuntime.hardwareStatusInfo': fmt_hardware_status
    }
