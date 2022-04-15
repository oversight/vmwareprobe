from pyVmomi import vim
from .base import EsxOnlyCheck


class CheckCpuPkg(EsxOnlyCheck):

    obj_type = vim.HostSystem

    def format_cpu_pkg(self, prop, output):
        output['cpu'] = cpus = []
        for item in prop.val:
            cpus.append(self.prop_val_to_dict(item, item_name=str(item.index)))

    properties = {
        'hardware.cpuPkg': format_cpu_pkg
    }
