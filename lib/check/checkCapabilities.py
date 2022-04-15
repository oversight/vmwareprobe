from pyVmomi import vim
from .base import EsxOnlyCheck


class CheckCapabilities(EsxOnlyCheck):

    obj_type = vim.HostSystem

    def fmt_capabilities(self, prop, output):
        output['capability'] = self.prop_val_to_value_list(
            prop.val, value_name='capability')

    properties = {
        'capability': fmt_capabilities
    }
