import time
from pyVmomi import vim
from .base import VmwareCheck
from .utils import datetime_to_timestamp


class CheckDatastoreSummary(VmwareCheck):

    @classmethod
    def _get_data(cls, content):
        dstores = cls.get_properties(
            content, vim.Datastore, ['name', 'summary', 'info'])

        datastores_out = {}
        vmfs_out = {}
        nas_out = {}
        for dstore in dstores:
            dstore_dct = cls.prop_val_to_dict(dstore['summary'])
            dstore_dct.update(cls.prop_val_to_dict(dstore['info']))
            if hasattr(dstore['info'], 'timestamp'):
                dt = dstore['info'].timestamp
                if dt:
                    dstore_dct['timestamp'] = ts = datetime_to_timestamp(dt)
                    dstore_dct['age'] = time.time() - ts
            if hasattr(dstore['info'], 'vmfs'):
                vmfs = dstore['info'].vmfs
                if vmfs:
                    dstore_dct['vmfs'] = vmfs.name
                    vmfs_dct = cls.prop_val_to_dict(vmfs, item_name=vmfs.name)
                    vmfs_dct['datastore'] = dstore_dct['name']
                    vmfs_out[vmfs.name] = vmfs_dct
            elif hasattr(dstore['info'], 'nas'):
                nas = dstore['info'].nas
                if nas:
                    nas_dct = cls.prop_val_to_dict(nas)
                    nas_dct['datastore'] = dstore_dct['name']
                    nas_out[nas.name] = nas_dct

            datastores_out[dstore_dct['name']] = dstore_dct

        return {
            'datastore': datastores_out,
            'vmfs': vmfs_out,
            'nas': nas_out
        }
