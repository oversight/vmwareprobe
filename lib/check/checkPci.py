from pyVmomi import vim
from .base import EsxOnlyCheck


class CheckPci(EsxOnlyCheck):

    obj_type = vim.HostSystem

    def fmt_pci_device(self, prop, output):
        output['pci'] = pcis = []
        for item in prop.val:
            pcis.append(self.prop_val_to_dict(item, item_name=str(item.id)))

    properties = {
        'hardware.pciDevice': fmt_pci_device
    }
