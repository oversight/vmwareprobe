from pyVmomi import vim
from .base import EsxOnlyCheck


class CheckNetworkSummary(EsxOnlyCheck):

    obj_type = vim.Network

    @classmethod
    def on_result(cls, data):
        networks = []
        output = {'network': networks}

        dct = {}
        for network in data:
            network_dct = {}
            for prop in network.propSet:
                network_dct[prop.name] = prop.val

            dct = cls.prop_val_to_dict(
                network_dct['summary'],
                item_name=network_dct['name'])
            networks.append(dct)

        return output

    properties = ['name', 'summary']
