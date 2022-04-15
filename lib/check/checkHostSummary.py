from pyVmomi import vim
from .base import EsxOnlyCheck


class CheckHostSummary(EsxOnlyCheck):

    obj_type = vim.HostSystem

    def fmt_summary(self, prop, output):
        output['quickStats'] = [
            self.prop_val_to_dict(
                prop.val.quickStats,
                item_name='quickStats')]
        output['hardwareOther'] = [
            self.dyn_property_list_to_dict(
                prop.val.hardware.otherIdentifyingInfo,
                item_name='hardwareOther')]
        output['hardware'] = [
            self.prop_val_to_dict(
                prop.val.hardware,
                item_name='hardware')]
        output['feature'] = self.dyn_property_list_to_kv_list(
            prop.val.config.featureVersion)
        output['product'] = [
            self.prop_val_to_dict(
                prop.val.config.product,
                item_name='product')]
        output['config'] = [self.prop_val_to_dict(prop.val.config)]
        output['netstack'] = []
        output['nic'] = []
        net_runtime_info = prop.val.runtime.networkRuntimeInfo
        if net_runtime_info:
            for stackInfo in net_runtime_info.netStackInstanceRuntimeInfo:
                output['netstack'].append(
                    self.prop_val_to_dict(
                        stackInfo, item_name='netstack'))
                for nic in stackInfo.vmknicKeys:
                    output['nic'].append({
                        'netstack': stackInfo.netStackInstanceKey,
                        'name': stackInfo.netStackInstanceKey + ':' + nic,
                        'nic': nic
                    })
        output['runtime'] = [
            self.prop_val_to_dict(
                prop.val.runtime,
                item_name='runtime')]

    properties = {'summary': fmt_summary}
