from pyVmomi import vim
from .base import VmwareCheckCluster


class CheckClusterSummary(VmwareCheckCluster):

    @classmethod
    def _get_data(cls, content):
        summary = {}
        output = {'clusterSummary': summary}
        clusters = cls.get_properties(
            content, vim.ClusterComputeResource, ['summary'])

        for cluster in clusters:
            cluster_name = '{}-{}'.format(
                cluster['moref'].parent.parent.name,
                cluster['moref'].name)

            dct = cls.prop_val_to_dict(
                cluster['summary'],
                item_name=cluster_name)
            summary[cluster_name] = dct

        return output
