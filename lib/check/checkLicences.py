from pyVmomi import vim
from .base import VmwareCheck


class CheckLicences(VmwareCheck):

    obj_type = vim.HostSystem

    def fmt_licences(self, prop, output):
        output['licensableResource'] = resources = []
        for item in prop.val.resource:
            resources.append({'name': item.key, 'value': item.value})

    properties = {
        'licensableResource': fmt_licences
    }
