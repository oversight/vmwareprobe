import asyncio
import datetime
import logging
import ssl
from agentcoreclient import IgnoreResultException
from http.client import BadStatusLine
from pyVmomi import vmodl
from pyVmomi import vim
from pyVim import connect
from pyVmomi.VmomiSupport import short as vmoni_short
from pyVmomi.VmomiSupport import long as vmoni_long
from requests.exceptions import ConnectionError

# TODO is this needed?
# try:
#     import requests
#     requests.packages.urllib3.disable_warnings()
# except Exception:
#     pass


from .asset_cache import AssetCache
from .utils import datetime_to_timestamp

MAX_CONN_AGE = 900

BASE_TYPES = (
    str,
    int,
    vmoni_long,
    vmoni_short,
    float,
    bool)


class VmwareCheck:

    interval = 300

    @classmethod
    async def run(cls, data, asset_config=None):
        try:
            asset_id = data['hostUuid']
            config = data['hostConfig']['probeConfig']['vmwareProbe']
            ip4 = config['ip4']
        except Exception as e:
            logging.error(
                f'invalid check configuration: {e.__class__.__name__}: {e}')
            return

        if asset_config is None or 'credentials' not in asset_config:
            logging.warning(f'missing asset config for {asset_id} {ip4}')
            return

        try:
            state_data = await asyncio.get_event_loop().run_in_executor(
                None,
                cls.get_data,
                ip4,
                asset_config['credentials']['username'],
                asset_config['credentials']['password']
            )
        except IgnoreResultException:
            raise
        except BadStatusLine:
            msg = 'Vmware is shutting down'
            # cls.tryDropVmwareConnection()
            raise Exception(f'Check error: {e.__class__.__name__}: {msg}')
        except (vim.fault.InvalidLogin,
                vim.fault.NotAuthenticated,
                IOError,
                ConnectionError) as e:
            msg = str(e)
            if (
                'Cannot complete login due to an incorrect user name or'
                ' password'
            ) in msg:
                msg = (
                    'Cannot complete login due to an incorrect user name'
                    ' or password')
            elif 'The session is not authenticated.' in msg:
                # drop the rest of the ugly message
                msg = 'The session is not authenticated.'
            # cls.tryDropVmwareConnection()
            raise Exception(f'Check error: {e.__class__.__name__}: {msg}')
        except (vim.fault.HostConnectFault, Exception) as e:
            msg = str(e)
            if '503 Service Unavailable' in msg:
                msg = (
                    '503 Service Unavailable'
                    '\nSee: '
                    'https://kb.vmware.com/clsservice/microsites/search.do?'
                    'language=en_US&cmd=displayKC&externalId=2033822'
                )
            else:
                logging.warning('Unhandled check error {}'.format(msg))
            # cls.tryDropVmwareConnection()
            raise Exception(f'Check error: {e.__class__.__name__}: {msg}')
        else:
            return state_data

    @classmethod
    def get_data(cls, ip4, username, password):
        content = cls.get_content(ip4, username, password)
        return cls._get_data(content)

    @classmethod
    def _get_data(cls, content):
        if isinstance(cls.properties, list):
            properties = cls.properties
        elif isinstance(cls.properties, dict):
            properties = list(cls.properties.keys())

        data = cls.query_view(
            content=content,
            obj_type=cls.obj_type,
            properties=properties)

        return cls.on_result(data)

    @classmethod
    def has_cluster_nodes(cls, content, host):
        cluster_nodes, _ = AssetCache.get_value((host, 'cluster_nodes'))
        if cluster_nodes is None:
            cluster_nodes = cls.get_has_cluster_nodes(content)
            AssetCache.set_value((host, 'cluster_nodes'), cluster_nodes)
        return cluster_nodes

    @classmethod
    def get_has_cluster_nodes(cls, content):
        try:
            # only vcentre hosts answer to this type
            res = cls.get_properties(
                content, vim.ClusterComputeResource, 'name')
        except AttributeError:
            return False
        else:
            return bool(res)

    @classmethod
    def dyn_property_list_to_kv_list(cls, lst):
        lst_out = []
        for feature in lst:
            lst_out.append({
                'name': feature.key,
                'value': feature.value
            })
        return lst_out

    @classmethod
    def dyn_property_list_to_dict(cls, lst, item_name=None):
        dct = {}
        for item in lst:
            dct[item.identifierType.key] = item.identifierValue
        if item_name:
            dct['name'] = item_name
        return dct

    @classmethod
    def prop_val_to_value_list(cls, prop_val, value_name='value'):
        lst = []
        for name, info in prop_val._propInfo.items():
            if info.type in BASE_TYPES:
                lst.append({'name': name, value_name: getattr(prop_val, name)})
            elif info.type == datetime.datetime:
                lst.append({'name': name, value_name:
                            datetime_to_timestamp(getattr(prop_val, name))})
            elif hasattr(info.type, 'values'):
                # values (lookup) is always empty
                lst.append({'name': name, value_name: getattr(prop_val, name)})
        return lst

    @classmethod
    def prop_val_to_dict(cls, prop_val, item_name=None):
        dct = {}
        for name, info in prop_val._propInfo.items():
            if info.type in BASE_TYPES:
                dct[name] = getattr(prop_val, name)
            elif info.type == datetime.datetime:
                dct[name] = datetime_to_timestamp(getattr(prop_val, name))
            elif hasattr(info.type, 'values'):
                # values (lookup) is always empty
                dct[name] = getattr(prop_val, name)
        if item_name:
            dct['name'] = item_name
        return dct

    @classmethod
    def get_content(cls, host, username, password):
        conn, expired = AssetCache.get_value((host, 'connection'))
        if expired:
            conn._stub.DropConnections()
        elif conn:
            return conn.RetrieveContent()

        conn = cls.get_connection(host, username, password)
        if not conn:
            raise ConnectionError('Unable to connect')
        AssetCache.set_value((host, 'connection'), conn, MAX_CONN_AGE)
        return conn.RetrieveContent()

    @staticmethod
    def get_connection(host, username, password):
        logging.info('CONNECTING to {}'.format(host))
        context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        context.verify_mode = ssl.CERT_NONE
        return connect.SmartConnect(
            host=host,
            user=username,
            pwd=password,
            sslContext=context,
            connectionPoolTimeout=10)

    @classmethod
    def _build_view(cls, content, obj_type, container=None, recursive=True):
        if container is None:
            container = content.rootFolder
        return content.viewManager.CreateContainerView(
            container=container, type=[obj_type], recursive=recursive)

    @classmethod
    def query_view(
            cls,
            content,
            obj_type,
            container=None,
            properties=None,
            list_all_properties=False,
            recursive=True):
        if properties is None:
            properties = []

        view_ref = cls._build_view(content, obj_type, container, recursive)

        collector = content.propertyCollector

        obj_spec = vmodl.query.PropertyCollector.ObjectSpec()
        obj_spec.obj = view_ref
        obj_spec.skip = True

        # Create a traversal specification to identify the
        # path for collection
        traversal_spec = vmodl.query.PropertyCollector.TraversalSpec()
        traversal_spec.name = 'traverseEntities'
        traversal_spec.path = 'view'
        traversal_spec.skip = False
        traversal_spec.type = view_ref.__class__
        obj_spec.selectSet = [traversal_spec]

        # Identify the properties to the retrieved
        property_spec = vmodl.query.PropertyCollector.PropertySpec()
        property_spec.type = obj_type

        property_spec.all = list_all_properties

        property_spec.pathSet = properties

        # Add the object and property specification to the
        # property filter specification
        filter_spec = vmodl.query.PropertyCollector.FilterSpec()
        filter_spec.objectSet = [obj_spec]
        filter_spec.propSet = [property_spec]

        # Retrieve properties
        return collector.RetrieveContents([filter_spec])

    @classmethod
    def get_properties(cls, content, spec_type, props):
        # Build a view and get basic properties for all Virtual Machines
        obj_view = content.viewManager.CreateContainerView(
            content.rootFolder, [spec_type], True)
        t_spec = vim.PropertyCollector.TraversalSpec(
            name='tSpecName', path='view', skip=False,
            type=vim.view.ContainerView)
        p_spec = vim.PropertyCollector.PropertySpec(
            all=False, pathSet=props, type=spec_type)
        o_spec = vim.PropertyCollector.ObjectSpec(
            obj=obj_view, selectSet=[t_spec], skip=False)
        pf_spec = vim.PropertyCollector.FilterSpec(
            objectSet=[o_spec], propSet=[p_spec],
            reportMissingObjectsInResults=False)
        ret_options = vim.PropertyCollector.RetrieveOptions()
        total_props = []
        ret_props = content.propertyCollector.RetrievePropertiesEx(
            specSet=[pf_spec], options=ret_options)
        if ret_props is None:
            return []
        total_props += ret_props.objects
        while ret_props.token:
            ret_props = content.propertyCollector.ContinueRetrievePropertiesEx(
                token=ret_props.token)
            total_props += ret_props.objects
        obj_view.Destroy()
        # Turn the output in ret_props into a usable dictionary of values
        gpOutput = []
        for each_prop in total_props:
            propDic = {}
            for prop in each_prop.propSet:
                propDic[prop.name] = prop.val
            propDic['moref'] = each_prop.obj
            gpOutput.append(propDic)
        return gpOutput

    @classmethod
    def on_result(cls, result):
        output = {}
        for item in result:
            for prop in item.propSet:
                if prop.name in cls.properties:
                    cls.properties[prop.name](cls, prop, output)
                else:
                    logging.warning(
                        'Encounted property without formatting fun {}'.format(
                            prop.name))
        return output


class VmwareCheckCluster(VmwareCheck):

    @classmethod
    def get_data(cls, ip4, username, password):
        content = cls.get_content(ip4, username, password)

        has_cluster_nodes = cls.has_cluster_nodes(content, ip4)
        if not has_cluster_nodes:
            return

        return cls._get_data(content)


class EsxOnlyCheck(VmwareCheck):

    @classmethod
    def get_data(cls, ip4, username, password):
        content = cls.get_content(ip4, username, password)

        has_cluster_nodes = cls.has_cluster_nodes(content, ip4)
        if has_cluster_nodes:
            return

        return cls._get_data(content)
