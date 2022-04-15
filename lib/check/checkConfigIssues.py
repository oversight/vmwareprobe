from pyVmomi import vim
from .base import VmwareCheck
from .utils import datetime_to_timestamp


class CheckConfigIssues(VmwareCheck):

    obj_type = vim.HostSystem

    def fmt_issue(self, issue):
        dct = self.prop_val_to_dict(issue)
        dct['fullFormattedMessage'] = getattr(
            issue, 'fullFormattedMessage', None)
        dct['name'] = str(datetime_to_timestamp(issue.createdTime)
                          ) + str(hash(dct['fullFormattedMessage']))
        return dct

    def fmt_config_issues(self, prop, output):
        output['configIssues'] = [self.fmt_issue(issue) for issue in prop.val]

    properties = {
        'configIssue': fmt_config_issues
    }
