# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pylint: disable=too-many-public-methods

# stdlib
import logging
import inspect
import os
import sys
from errno import ENOENT
from inspect import isclass
from shutil import rmtree
from tempfile import gettempdir
from threading import RLock
from traceback import format_exc
from uuid import uuid4

# Bunch
from bunch import bunchify

# orjson
from orjson import dumps

# Zato
from zato.bunch import Bunch
from zato.common import broker_message
from zato.common.api import API_Key, CHANNEL, CONNECTION, DATA_FORMAT, GENERIC as COMMON_GENERIC, \
     HTTP_SOAP_SERIALIZATION_TYPE, SEC_DEF_TYPE, simple_types, \
     URL_TYPE, Wrapper_Name_Prefix_List, ZATO_ODB_POOL_NAME
from zato.common.broker_message import code_to_name, GENERIC as BROKER_MSG_GENERIC, SERVICE
from zato.common.const import SECRETS
from zato.common.dispatch import dispatcher
from zato.common.json_internal import loads
from zato.common.odb.api import PoolStore, SessionWrapper
from zato.common.typing_ import cast_
from zato.common.util.api import fs_safe_name, import_module_from_path, new_cid, update_apikey_username_to_channel, utcnow, \
    visit_py_source, wait_for_dict_key, wait_for_dict_key_by_get_func
from zato.server.base.worker.common import WorkerImpl
from zato.server.connection.amqp_ import ConnectorAMQP
from zato.server.connection.cache import CacheAPI
from zato.server.connection.connector import ConnectorStore, Connector_Type
from zato.server.connection.email import IMAPAPI, IMAPConnStore, SMTPAPI, SMTPConnStore
from zato.server.connection.ftp import FTPStore
from zato.server.connection.http_soap.channel import RequestDispatcher, RequestHandler
from zato.server.connection.http_soap.outgoing import HTTPSOAPWrapper
from zato.server.connection.http_soap.url_data import URLData
from zato.server.connection.odoo import OdooWrapper
from zato.server.connection.sap import SAPWrapper
from zato.server.connection.search.es import ElasticSearchAPI, ElasticSearchConnStore
from zato.server.ext.zunicorn.workers.ggevent import GeventWorker as GunicornGeventWorker
from zato.server.generic.api.cloud_confluence import CloudConfluenceWrapper
from zato.server.generic.api.cloud_jira import CloudJiraWrapper
from zato.server.generic.api.cloud_microsoft_365 import CloudMicrosoft365Wrapper
from zato.server.generic.api.cloud_salesforce import CloudSalesforceWrapper
from zato.server.generic.api.outconn_ldap import OutconnLDAPWrapper
from zato.server.generic.api.outconn_mongodb import OutconnMongoDBWrapper

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from bunch import Bunch as bunch_
    from zato.broker.client import BrokerClient
    from zato.common.typing_ import any_, anylist, anytuple, callable_, dictnone, stranydict, tupnone
    from zato.server.base.parallel import ParallelServer
    from zato.server.config import ConfigDict
    from zato.server.config import ConfigStore
    from zato.server.connection.http_soap.outgoing import BaseHTTPSOAPWrapper
    from zato.server.service import Service
    from zato.server.store import BaseAPI
    ConfigStore    = ConfigStore
    ParallelServer = ParallelServer
    Service        = Service

# ################################################################################################################################
# ################################################################################################################################

_data_format_dict = DATA_FORMAT.DICT

# ################################################################################################################################
# ################################################################################################################################

pickup_conf_item_prefix = 'zato.pickup'

# ################################################################################################################################
# ################################################################################################################################

class _generic_msg:
    create          = BROKER_MSG_GENERIC.CONNECTION_CREATE.value
    edit            = BROKER_MSG_GENERIC.CONNECTION_EDIT.value
    delete          = BROKER_MSG_GENERIC.CONNECTION_DELETE.value
    change_password = BROKER_MSG_GENERIC.CONNECTION_CHANGE_PASSWORD.value

# ################################################################################################################################
# ################################################################################################################################

class GeventWorker(GunicornGeventWorker):

    def __init__(self, *args:'any_', **kwargs:'any_') -> 'None':
        self.deployment_key = '{}.{}'.format(utcnow().isoformat(), uuid4().hex)
        super(GunicornGeventWorker, self).__init__(*args, **kwargs)

# ################################################################################################################################

def _get_base_classes() -> 'anytuple':
    ignore = ('__init__.py', 'common.py')
    out = []

    for py_path in visit_py_source(os.path.dirname(os.path.abspath(__file__))):
        import_path = True
        for item in ignore:
            if py_path.endswith(item):
                import_path = False
                continue

        if import_path:
            mod_info = import_module_from_path(py_path)
            for name in dir(mod_info.module):
                item = getattr(mod_info.module, name)
                if isclass(item) and issubclass(item, WorkerImpl) and item is not WorkerImpl:
                    out.append(item)

    return tuple(out) # type: ignore

# ################################################################################################################################
# ################################################################################################################################

_base_type = '_WorkerStoreBase'

# Dynamically adds as base classes everything found in current directory that subclasses WorkerImpl
_WorkerStoreBase = type(_base_type, _get_base_classes(), {})

class WorkerStore(_WorkerStoreBase):
    """ Dispatches work between different pieces of configuration of an individual gunicorn worker.
    """
    broker_client: 'BrokerClient | None' = None

    def __init__(self, worker_config:'ConfigStore', server:'ParallelServer') -> 'None':
        self.logger = logging.getLogger(self.__class__.__name__)
        self.is_ready = False
        self.worker_config = worker_config
        self.server = server
        self.update_lock = RLock()
        self.worker_idx = int(os.environ['ZATO_SERVER_WORKER_IDX'])

        # To expedite look-ups
        self._simple_types = simple_types

        # Generic connections - Cloud - Confluence
        self.cloud_confluence = {}

        # Generic connections - Cloud - Dropbox
        self.cloud_dropbox = {}

        # Generic connections - Cloud - Jira
        self.cloud_jira = {}

        # Generic connections - Cloud - Microsoft 365
        self.cloud_microsoft_365 = {}

        # Generic connections - Cloud - Salesforce
        self.cloud_salesforce = {}

        # Generic connections - LDAP outconns
        self.outconn_ldap = {}

        # Generic connections - MongoDB outconns
        self.outconn_mongodb = {}

# ################################################################################################################################

    def init(self) -> 'None':

        # Search
        self.search_es_api = ElasticSearchAPI(ElasticSearchConnStore())

        # E-mail
        self.email_smtp_api = SMTPAPI(SMTPConnStore())
        self.email_imap_api = IMAPAPI(IMAPConnStore())

        # AMQP
        self.amqp_api = ConnectorStore(Connector_Type.duplex.amqp, ConnectorAMQP)
        self.amqp_out_name_to_def = {} # Maps outgoing connection names to definition names, i.e. to connector names

        # Caches
        self.cache_api = CacheAPI(self.server)

        # Maps generic connection types to their API handler objects
        self.generic_conn_api = {
            COMMON_GENERIC.CONNECTION.TYPE.CLOUD_CONFLUENCE: self.cloud_confluence,
            COMMON_GENERIC.CONNECTION.TYPE.CLOUD_JIRA: self.cloud_jira,
            COMMON_GENERIC.CONNECTION.TYPE.CLOUD_MICROSOFT_365: self.cloud_microsoft_365,
            COMMON_GENERIC.CONNECTION.TYPE.CLOUD_SALESFORCE: self.cloud_salesforce,
            COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_LDAP: self.outconn_ldap,
            COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_MONGODB: self.outconn_mongodb,
        }

        self._generic_conn_handler = {
            COMMON_GENERIC.CONNECTION.TYPE.CLOUD_CONFLUENCE: CloudConfluenceWrapper,
            COMMON_GENERIC.CONNECTION.TYPE.CLOUD_JIRA: CloudJiraWrapper,
            COMMON_GENERIC.CONNECTION.TYPE.CLOUD_MICROSOFT_365: CloudMicrosoft365Wrapper,
            COMMON_GENERIC.CONNECTION.TYPE.CLOUD_SALESFORCE: CloudSalesforceWrapper,
            COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_LDAP: OutconnLDAPWrapper,
            COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_MONGODB: OutconnMongoDBWrapper,
        }

        # Maps message actions against generic connection types and their message handlers
        self.generic_impl_func_map = {}

        # Search
        self.init_search_es()

        # E-mail
        self.init_email_smtp()
        self.init_email_imap()

        # Odoo
        self.init_odoo()

        # SAP RFC
        self.init_sap()

        # Caches
        self.init_caches()

        # API keys
        self.update_apikeys()

        request_handler = RequestHandler(self.server)
        url_data = URLData(
            self,
            self.worker_config.http_soap,
            self._get_channel_url_sec(),
            self.worker_config.basic_auth,
            self.worker_config.ntlm,
            self.worker_config.oauth,
            self.worker_config.apikey,
            self.broker_client,
            self.server.odb,
        )

        # Request dispatcher - matches URLs, checks security and dispatches HTTP requests to services.
        self.request_dispatcher = RequestDispatcher(
            server = self.server,
            url_data = url_data,
            request_handler = request_handler,
            simple_io_config = self.worker_config.simple_io,
            return_tracebacks = self.server.return_tracebacks,
            default_error_message = self.server.default_error_message,
            http_methods_allowed = self.server.http_methods_allowed
        )

        # Security groups - add details of each one to REST channels
        self._populate_channel_security_groups_info(self.worker_config.http_soap)

        # Create all the expected connections and objects
        self.init_sql()
        self.init_http_soap()

        # AMQP
        self.init_amqp()

        # Generic connections
        self.init_generic_connections_config()
        self.init_generic_connections()

        # All set, whoever is waiting for us, if anyone at all, can now proceed
        self.is_ready = True

# ################################################################################################################################

    def _populate_channel_security_groups_info(self, channel_data:'anylist') -> 'None':

        # First, make sure the server has all the groups ..
        self.server.security_groups_ctx_builder.populate_members()

        # .. now, we can attach a groups context object to each channel that has any groups.
        for channel_item in channel_data:
            if security_groups := channel_item.get('security_groups'):
                security_groups_ctx = self.server.security_groups_ctx_builder.build_ctx(channel_item['id'], security_groups)
                channel_item['security_groups_ctx'] = security_groups_ctx

# ################################################################################################################################

    def _get_channel_url_sec(self) -> 'any_':
        out:'any_' = self.server.odb.get_url_security(self.server.cluster_id, 'channel')[0]
        return out

# ################################################################################################################################

    def early_init(self) -> 'None':
        """ Initialises these parts of our configuration that are needed earlier than others.
        """
        self.init_ftp()

# ################################################################################################################################

    def _config_to_dict(self, config_list:'anylist', key:'str'='name') -> 'stranydict':
        """ Converts a list of dictionaries produced by ConfigDict instances to a dictionary keyed with 'key' elements.
        """
        out = {}
        for elem in config_list:
            out[elem[key]] = elem
        return out

# ################################################################################################################################

    def set_broker_client(self, broker_client:'BrokerClient') -> 'None':
        self.broker_client = broker_client

# ################################################################################################################################

    def filter(self, msg:'bunch_') -> 'bool':
        return True

# ################################################################################################################################

    def _update_queue_build_cap(self, item:'any_') -> 'None':
        item.queue_build_cap = float(self.server.fs_server_config.misc.queue_build_cap)

# ################################################################################################################################

    def _http_soap_wrapper_from_config(self, config:'bunch_', *, has_sec_config:'bool'=True) -> 'BaseHTTPSOAPWrapper':
        """ Creates a new HTTP/SOAP connection wrapper out of a configuration dictionary.
        """

        # Populate it upfront
        conn_name = config['name']

        # This can also be populated upfront but we need to ensure
        # we do not include any potential name prefix in the FS-safe name.
        for prefix in Wrapper_Name_Prefix_List:
            if conn_name.startswith(prefix):
                name_without_prefix = conn_name.replace(prefix, '', 1)
                is_wrapper = True
                break
        else:
            is_wrapper = False
            prefix = ''
            name_without_prefix = conn_name

        config['name_fs_safe'] = prefix + fs_safe_name(name_without_prefix)

        security_name = config.get('security_name')
        sec_config = {
            'security_name': security_name,
            'security_id': None,
            'sec_type': None,
            'username': None,
            'password': None,
            'password_type': None,
            'orig_username': None
        }
        _sec_config = None

        # This will be set to True only if the method's invoked on a server's starting up
        if has_sec_config:

            # It's possible that there is no security config attached at all
            if security_name:
                _sec_config = config
        else:
            if security_name:
                sec_type = config.sec_type
                func = getattr(self.request_dispatcher.url_data, sec_type + '_get')
                _sec_config = func(security_name).config

        # Update the security configuration if it is a separate one ..
        if _sec_config:
            _sec_config_id = _sec_config.get('security_id') or _sec_config.get('id')
            sec_config['security_id'] = _sec_config_id
            sec_config['sec_type'] = _sec_config['sec_type']
            sec_config['username'] = _sec_config.get('username')
            sec_config['orig_username'] = _sec_config.get('orig_username')
            sec_config['password'] = _sec_config.get('password')
            sec_config['password_type'] = _sec_config.get('password_type')
            sec_config['salt'] = _sec_config.get('salt')

        # .. otherwise, try to find it elsewhere ..
        else:

            # .. if it is a REST wrapper, it will have its own security configuration that we can use ..
            if is_wrapper:
                sec_config['sec_type'] = SEC_DEF_TYPE.BASIC_AUTH
                sec_config['username'] = config['username']
                sec_config['password'] = self.server.decrypt(config['password'])

        wrapper_config = {
            'id':config.id,
            'is_active':config.is_active,
            'method':config.method,
            'data_format':config.get('data_format'),
            'name':config.name,
            'transport':config.transport,
            'address_host':config.host,
            'address_url_path':config.url_path,
            'soap_action':config.soap_action,
            'soap_version':config.soap_version,
            'ping_method':config.ping_method,
            'pool_size':config.pool_size,
            'serialization_type':config.serialization_type,
            'timeout':config.timeout,
            'content_type':config.content_type,
        }
        wrapper_config.update(sec_config)

        raise Exception('TODO: Implement tls_verify True / False')

        """
        # 3.2+
        if config.sec_tls_ca_cert_verify_strategy:
            if sec_tls_ca_cert_verify_strategy is True:
                tls_verify = True

            elif sec_tls_ca_cert_verify_strategy is False:
                tls_verify = False

            else:
                tls_verify = self._get_tls_verify_from_config(config)

        wrapper_config['tls_verify'] = tls_verify

        return HTTPSOAPWrapper(self.server, wrapper_config)
        """

# ################################################################################################################################

    def get_outconn_http_config_dicts(self) -> 'any_':

        out:'any_' = []

        for transport in('soap', 'plain_http'):
            config_dict = getattr(self.worker_config, 'out_' + transport)
            for name in list(config_dict): # Must use list explicitly so config_dict can be changed during iteration
                config_data = config_dict[name]
                if not isinstance(config_data, str):
                    out.append([config_dict, config_data])

        return out

# ################################################################################################################################

    def init_sql(self) -> 'None':
        """ Initializes SQL connections, first to ODB and then any user-defined ones.
        """
        # We need a store first
        self.sql_pool_store = PoolStore()

        # Connect to ODB
        self.sql_pool_store[ZATO_ODB_POOL_NAME] = self.worker_config.odb_data
        self.odb = SessionWrapper()
        self.odb.init_session(ZATO_ODB_POOL_NAME, self.worker_config.odb_data, self.sql_pool_store[ZATO_ODB_POOL_NAME].pool)

        # Any user-defined SQL connections left?
        for pool_name in self.worker_config.out_sql:
            config = self.worker_config.out_sql[pool_name]['config']
            config['fs_sql_config'] = self.server.fs_sql_config
            self.sql_pool_store[pool_name] = config

    def init_ftp(self) -> 'None':
        """ Initializes FTP connections. The method replaces whatever value self.out_ftp
        previously had (initially this would be a ConfigDict of connection definitions).
        """
        config_list = self.worker_config.out_ftp.get_config_list()
        self.worker_config.out_ftp = FTPStore() # type: ignore
        self.worker_config.out_ftp.add_params(config_list)

    def init_http_soap(self, *, has_sec_config:'bool'=True) -> 'None':
        """ Initializes plain HTTP/SOAP connections.
        """
        config_dicts = self.get_outconn_http_config_dicts()

        for config_dict, config_data in config_dicts:

            wrapper = self._http_soap_wrapper_from_config(config_data.config, has_sec_config=has_sec_config)
            config_data.conn = wrapper

            # To make the API consistent with that of SQL connection pools
            config_data.ping = wrapper.ping

            # Store ID -> name mapping
            config_dict.set_key_id_data(config_data.config)

# ################################################################################################################################

    def init_simple(self, config:'bunch_', api:'BaseAPI', name:'str') -> 'None':
        for k, v in config.items():
            self._update_queue_build_cap(v.config)
            try:
                api.create(k, v.config)
            except Exception:
                logger.warning('Could not create {} connection `%s`, e:`%s`'.format(name), k, format_exc())

# ################################################################################################################################

    def init_search_es(self) -> 'None':
        self.init_simple(self.worker_config.search_es, self.search_es_api, 'an ElasticSearch')

# ################################################################################################################################

    def init_email_smtp(self) -> 'None':
        self.init_simple(self.worker_config.email_smtp, self.email_smtp_api, 'an SMTP')

# ################################################################################################################################

    def init_email_imap(self) -> 'None':
        self.init_simple(self.worker_config.email_imap, self.email_imap_api, 'an IMAP')

# ################################################################################################################################

    def init_amqp(self) -> 'None':
        """ Initializes all AMQP connections.
        """
        self.amqp_api.start()

# ################################################################################################################################

    def init_odoo(self) -> 'None':
        names = self.worker_config.out_odoo.keys()
        for name in names:
            item = config = self.worker_config.out_odoo[name]
            config = item['config']
            config.queue_build_cap = float(self.server.fs_server_config.misc.queue_build_cap)
            item.conn = OdooWrapper(config, self.server)
            item.conn.build_queue()

# ################################################################################################################################

    def init_sap(self) -> 'None':
        names = self.worker_config.out_sap.keys()
        for name in names:
            item = config = self.worker_config.out_sap[name]
            config = item['config']
            config.queue_build_cap = float(self.server.fs_server_config.misc.queue_build_cap)
            item.conn = SAPWrapper(config, self.server)
            item.conn.build_queue()

# ################################################################################################################################

    def init_caches(self) -> 'None':

        for name in ['builtin']:
            cache = getattr(self.worker_config, 'cache_{}'.format(name))
            for value in cache.values():
                self.cache_api.create(bunchify(value['config']))

# ################################################################################################################################

    def sync_security(self):
        """ Rebuilds all the in-RAM security structures and objects.
        """

        # First, load up all the definitions from the database ..
        self.server.set_up_security(self.server.cluster_id)

        # .. update in-RAM config values ..
        url_sec = self._get_channel_url_sec()
        self.request_dispatcher.url_data.set_security_objects(
            url_sec=url_sec,
            basic_auth_config=self.worker_config.basic_auth,
            ntlm_config=self.worker_config.ntlm,
            oauth_config=self.worker_config.oauth,
            apikey_config=self.worker_config.apikey,
        )

        # .. now, initialize connections that may depend on what we have just loaded ..
        self.init_http_soap(has_sec_config=False)

# ################################################################################################################################

    def update_apikeys(self) -> 'None':
        """ API keys need to be upper-cased and in the format that WSGI environment will have them in.
        """
        for config_dict in self.worker_config.apikey.values():
            config_dict.config.orig_header = config_dict.config.get('header') or API_Key.Default_Header
            update_apikey_username_to_channel(config_dict.config)

# ################################################################################################################################

    def _update_auth(
        self,
        msg,           # type: Bunch
        action_name,   # type: str
        sec_type,      # type: str
        visit_wrapper, # type: callable_
        keys=None      # type: tupnone
    ) -> 'None':
        """ A common method for updating auth-related configuration.
        """
        with self.update_lock:

            handler = getattr(self.request_dispatcher.url_data, 'on_broker_msg_' + action_name)
            handler(msg)

            for transport in ['plain_http', 'soap']:
                config_dict = getattr(self.worker_config, 'out_' + transport)

                for conn_name in config_dict.copy_keys():

                    config = config_dict[conn_name]['config']
                    wrapper = config_dict[conn_name]['conn']

                    if config['sec_type'] == sec_type:
                        if keys:
                            visit_wrapper(wrapper, msg, keys)
                        else:
                            visit_wrapper(wrapper, msg)

    def _visit_wrapper_edit(self, wrapper:'HTTPSOAPWrapper', msg:'bunch_', keys:'anytuple') -> 'None':
        """ Updates a given wrapper's security configuration.
        """
        if wrapper.config['security_name'] == msg['old_name']:
            for key in keys:
                # All's good except for 'name', the msg's 'name' is known
                # as 'security_name' in wrapper's config.
                if key == 'name':
                    key1 = 'security_name'
                    key2 = key
                else:
                    key1, key2 = key, key
                wrapper.config[key1] = msg[key2]
            wrapper.set_auth()

    def _visit_wrapper_delete(self, wrapper:'HTTPSOAPWrapper', msg:'bunch_') -> 'None':
        """ Deletes a wrapper.
        """
        config_dict = getattr(self.worker_config, 'out_' + wrapper.config['transport'])
        if wrapper.config['security_name'] == msg['name']:
            del config_dict[wrapper.config['name']]

    def _visit_wrapper_change_password(self, wrapper:'HTTPSOAPWrapper', msg:'bunch_', *, check_name:'bool'=True) -> 'None':
        """ Changes a wrapper's password.
        """
        # This check is performed by non-wrapper connection types
        if check_name:
            if not (wrapper.config['security_name'] == msg['name']):
                return

        # If we are here, it means that either the name matches or that the connection is a wrapper object
        wrapper.config['password'] = msg['password']
        wrapper.set_auth()

# ################################################################################################################################

    def init_generic_connections(self) -> 'None':

        # Some connection types are built elsewhere
        to_skip = {}

        for config_dict in self.worker_config.generic_connection.values():

            if config_dict:
                config = config_dict.get('config')
                if config:
                    config_type = config['type_']

                    # Not all generic connections are created here
                    if config_type in to_skip:
                        continue

                    self._create_generic_connection(bunchify(config), raise_exc=False, is_starting=True)

# ################################################################################################################################

    def init_generic_connections_config(self) -> 'None':

        # Local aliases
        cloud_confluence_map = self.generic_impl_func_map.setdefault(COMMON_GENERIC.CONNECTION.TYPE.CLOUD_CONFLUENCE, {})
        cloud_jira_map = self.generic_impl_func_map.setdefault(COMMON_GENERIC.CONNECTION.TYPE.CLOUD_JIRA, {})
        cloud_microsoft_365_map = self.generic_impl_func_map.setdefault(COMMON_GENERIC.CONNECTION.TYPE.CLOUD_MICROSOFT_365, {})
        cloud_salesforce_map = self.generic_impl_func_map.setdefault(COMMON_GENERIC.CONNECTION.TYPE.CLOUD_SALESFORCE, {})
        outconn_ldap_map = self.generic_impl_func_map.setdefault(COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_LDAP, {})
        outconn_mongodb_map = self.generic_impl_func_map.setdefault(COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_MONGODB, {})

        # These generic connections are regular - they use common API methods for such connections
        regular_maps = [
            cloud_confluence_map,
            cloud_jira_map,
            cloud_microsoft_365_map,
            cloud_salesforce_map,
            outconn_ldap_map,
            outconn_mongodb_map,
        ]

        password_maps = [
            outconn_ldap_map,
            outconn_mongodb_map,
        ]

        for regular_item in regular_maps:
            regular_item[_generic_msg.create] = self._create_generic_connection
            regular_item[_generic_msg.edit]   = self._edit_generic_connection
            regular_item[_generic_msg.delete] = self._delete_generic_connection

        for password_item in password_maps:
            password_item[_generic_msg.change_password] = self._change_password_generic_connection

# ################################################################################################################################

    def _get_generic_impl_func(self, msg:'bunch_', *args:'any_', **kwargs:'any_') -> 'any_':
        """ Returns a function/method to invoke depending on which generic connection type is given on input.
        Required because some connection types are not managed via GenericConnection objects.
        """
        conn_type = msg['type_']
        msg_action = msg['action']
        func_map = self.generic_impl_func_map[conn_type]
        impl_func = func_map.get(msg_action)
        if impl_func:
            return impl_func
        else:
            # Ignore missing CHANGE_PASSWORD handlers because they will rarely exist across generic connection types.
            if msg_action == BROKER_MSG_GENERIC.CONNECTION_CHANGE_PASSWORD.value:
                pass
            else:
                raise Exception('No impl_func found for action `%s` -> %s', msg_action, conn_type)

# ################################################################################################################################
# ################################################################################################################################

    def wait_for_basic_auth(self, name:'str', timeout:'int'=999999) -> 'bool':
        return wait_for_dict_key_by_get_func(self._basic_auth_get, name, timeout, interval=0.5)

# ################################################################################################################################

    def _basic_auth_get(self, name:'str') -> 'bunch_':
        """ Implements self.basic_auth_get.
        """
        return self.request_dispatcher.url_data.basic_auth_get(name)

# ################################################################################################################################

    def basic_auth_get(self, name:'str') -> 'bunch_':
        """ Returns the configuration of the HTTP Basic Auth security definition of the given name.
        """
        return self._basic_auth_get(name)

# ################################################################################################################################

    def basic_auth_get_by_id(self, def_id:'int') -> 'bunch_':
        """ Same as basic_auth_get but by definition ID.
        """
        return self.request_dispatcher.url_data.basic_auth_get_by_id(def_id)

# ################################################################################################################################

    def on_broker_msg_SECURITY_BASIC_AUTH_CREATE(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Creates a new HTTP Basic Auth security definition
        """
        dispatcher.notify(broker_message.SECURITY.BASIC_AUTH_CREATE.value, msg)

# ################################################################################################################################

    def on_broker_msg_SECURITY_BASIC_AUTH_EDIT(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Updates an existing HTTP Basic Auth security definition.
        """
        # Update channels and outgoing connections ..
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.BASIC_AUTH,
            self._visit_wrapper_edit, keys=('username', 'name'))

        # .. extract the newest information  ..
        sec_def = self.basic_auth_get_by_id(msg.id)

        # .. update security groups.
        for security_groups_ctx in self._yield_security_groups_ctx_items(): # type: ignore
            security_groups_ctx.set_current_basic_auth(msg.id, sec_def['username'], sec_def['password'])

# ################################################################################################################################

    def on_broker_msg_SECURITY_BASIC_AUTH_DELETE(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Deletes an HTTP Basic Auth security definition.
        """
        # Update channels and outgoing connections ..
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.BASIC_AUTH, self._visit_wrapper_delete)

        # .. update security groups.
        for security_groups_ctx in self._yield_security_groups_ctx_items(): # type: ignore
            security_groups_ctx.on_basic_auth_deleted(msg.id)

# ################################################################################################################################

    def on_broker_msg_SECURITY_BASIC_AUTH_CHANGE_PASSWORD(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Changes password of an HTTP Basic Auth security definition.
        """
        # Update channels and outgoing connections ..
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.BASIC_AUTH, self._visit_wrapper_change_password)

        # .. extract the newest information  ..
        if msg.id:
            sec_def = self.basic_auth_get_by_id(msg.id)

            # .. and update security groups.
            for security_groups_ctx in self._yield_security_groups_ctx_items(): # type: ignore
                security_groups_ctx.set_current_basic_auth(msg.id, sec_def['username'], sec_def['password'])

# ################################################################################################################################
# ################################################################################################################################

    def wait_for_apikey(self, name:'str', timeout:'int'=999999) -> 'bool':
        return wait_for_dict_key_by_get_func(self.apikey_get, name, timeout, interval=0.5)

# ################################################################################################################################

    def apikey_get(self, name:'str') -> 'bunch_':
        """ Returns the configuration of the API key of the given name.
        """
        return self.request_dispatcher.url_data.apikey_get(name)

# ################################################################################################################################

    def apikey_get_by_id(self, def_id:'int') -> 'bunch_':
        """ Same as apikey_get but by definition ID.
        """
        return self.request_dispatcher.url_data.apikey_get_by_id(def_id)

# ################################################################################################################################

    def on_broker_msg_SECURITY_APIKEY_CREATE(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Creates a new API key security definition.
        """
        dispatcher.notify(broker_message.SECURITY.APIKEY_CREATE.value, msg)

# ################################################################################################################################

    def on_broker_msg_SECURITY_APIKEY_EDIT(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Updates an existing API key security definition.
        """
        # Update channels and outgoing connections.
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.APIKEY, self._visit_wrapper_edit, keys=('username', 'name'))

# ################################################################################################################################

    def on_broker_msg_SECURITY_APIKEY_DELETE(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Deletes an API key security definition.
        """
        # Update channels and outgoing connections ..
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.APIKEY, self._visit_wrapper_delete)

        # .. update security groups.
        for security_groups_ctx in self._yield_security_groups_ctx_items(): # type: ignore
            security_groups_ctx.on_apikey_deleted(msg.id)

# ################################################################################################################################

    def on_broker_msg_SECURITY_APIKEY_CHANGE_PASSWORD(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Changes password of an API key security definition.
        """
        # Update channels and outgoing connections ..
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.APIKEY, self._visit_wrapper_change_password)

        # .. and update security groups.
        for security_groups_ctx in self._yield_security_groups_ctx_items(): # type: ignore
            security_groups_ctx.set_current_apikey(msg.id, msg.password)

# ################################################################################################################################

    def wait_for_ntlm(self, name:'str', timeout:'int'=999999) -> 'bool':
        return wait_for_dict_key_by_get_func(self.ntlm_get, name, timeout, interval=0.5)

    def ntlm_get(self, name:'str') -> 'bunch_':
        """ Returns the configuration of the NTLM security definition
        of the given name.
        """
        return self.request_dispatcher.url_data.ntlm_get(name)

    def on_broker_msg_SECURITY_NTLM_CREATE(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Creates a new NTLM security definition
        """
        dispatcher.notify(broker_message.SECURITY.NTLM_CREATE.value, msg)

    def on_broker_msg_SECURITY_NTLM_EDIT(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Updates an existing NTLM security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.NTLM,
                self._visit_wrapper_edit, keys=('username', 'name'))

    def on_broker_msg_SECURITY_NTLM_DELETE(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Deletes an NTLM security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.NTLM,
                self._visit_wrapper_delete)

    def on_broker_msg_SECURITY_NTLM_CHANGE_PASSWORD(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Changes password of an NTLM security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.NTLM,
                self._visit_wrapper_change_password)

# ################################################################################################################################

    def wait_for_oauth(self, name:'str', timeout:'int'=999999) -> 'bool':
        return wait_for_dict_key_by_get_func(self.oauth_get, name, timeout, interval=0.5)

    def oauth_get(self, name:'str') -> 'bunch_':
        """ Returns the configuration of the OAuth security definition
        of the given name.
        """
        return self.request_dispatcher.url_data.oauth_get(name)

    def oauth_get_by_id(self, def_id:'int') -> 'bunch_':
        """ Same as oauth_get but by definition ID.
        """
        return self.request_dispatcher.url_data.oauth_get_by_id(def_id)

    def oauth_get_all_id_list(self) -> 'any_':
        """ Returns IDs of all OAuth definitions.
        """
        for item in self.request_dispatcher.url_data.oauth_config.values():
            config = item.config
            yield config['id']

    def on_broker_msg_SECURITY_OAUTH_CREATE(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Creates a new OAuth security definition
        """
        dispatcher.notify(broker_message.SECURITY.OAUTH_CREATE.value, msg)

    def on_broker_msg_SECURITY_OAUTH_EDIT(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Updates an existing OAuth security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.OAUTH,
                self._visit_wrapper_edit, keys=('username', 'name'))

    def on_broker_msg_SECURITY_OAUTH_DELETE(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Deletes an OAuth security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.OAUTH,
                self._visit_wrapper_delete)

    def on_broker_msg_SECURITY_OAUTH_CHANGE_PASSWORD(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Changes password of an OAuth security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.OAUTH,
                self._visit_wrapper_change_password)

# ################################################################################################################################

    def invoke(self, service:'str', payload:'any_', **kwargs:'any_') -> 'any_':
        """ Invokes a service by its name with request on input.
        """
        channel = kwargs.get('channel', CHANNEL.WORKER)

        if 'serialize' in kwargs:
            serialize = kwargs.get('serialize')
        else:
            serialize = True

        return self.on_message_invoke_service({
            'channel': channel,
            'payload': payload,
            'data_format': kwargs.get('data_format'),
            'service': service,
            'cid': new_cid(),
            'is_async': kwargs.get('is_async'),
            'callback': kwargs.get('callback'),
            'zato_ctx': kwargs.get('zato_ctx'),
            'wsgi_environ': kwargs.get('wsgi_environ'),
            'channel_item': kwargs.get('channel_item'),
        }, channel, '', needs_response=True, serialize=serialize, skip_response_elem=kwargs.get('skip_response_elem'))

# ################################################################################################################################

    def on_message_invoke_service(self, msg:'any_', channel:'str', action:'str', args:'any_'=None, **kwargs:'any_') -> 'any_':
        """ Triggered by external events, such as messages sent through connectors. Creates a new service instance and invokes it.
        """
        zato_ctx = msg.get('zato_ctx') or {}
        cid = msg['cid']

        # The default WSGI environment that always exists ..
        wsgi_environ = {
            'zato.request_ctx.async_msg':msg,
            'zato.request_ctx.in_reply_to':msg.get('in_reply_to'),
            'zato.request_ctx.fanout_cid':zato_ctx.get('fanout_cid'),
            'zato.request_ctx.parallel_exec_cid':zato_ctx.get('parallel_exec_cid'),
        }

        if zato_ctx:
            wsgi_environ['zato.channel_item'] = zato_ctx.get('zato.channel_item')

        data_format = msg.get('data_format') or _data_format_dict
        transport = msg.get('transport')

        if msg.get('channel') in (CHANNEL.FANOUT_ON_TARGET, CHANNEL.FANOUT_ON_FINAL, CHANNEL.PARALLEL_EXEC_ON_TARGET):
            payload = loads(msg['payload'])
        else:
            payload = msg['payload']

        service, is_active = self.server.service_store.new_instance_by_name(msg['service'])
        if not is_active:
            msg = 'Could not invoke an inactive service:`{}`, cid:`{}`'.format(service.get_name(), cid)
            logger.warning(msg)
            raise Exception(msg)

        skip_response_elem=kwargs.get('skip_response_elem')

        response = service.update_handle(service.set_response_data, service, payload,
            channel, data_format, transport, self.server, self.broker_client, self, cid,
            self.worker_config.simple_io, job_type=msg.get('job_type'), wsgi_environ=wsgi_environ,
            environ=msg.get('environ'))

        if skip_response_elem:
            response = dumps(response)
            response = response.decode('utf8')

        # Invoke the callback, if any.
        if msg.get('is_async') and msg.get('callback'):

            cb_msg = {}
            cb_msg['action'] = SERVICE.PUBLISH.value
            cb_msg['service'] = msg['callback']
            cb_msg['payload'] = response if skip_response_elem else service.response.payload
            cb_msg['cid'] = new_cid()
            cb_msg['channel'] = CHANNEL.INVOKE_ASYNC_CALLBACK
            cb_msg['data_format'] = data_format
            cb_msg['transport'] = transport
            cb_msg['is_async'] = True
            cb_msg['in_reply_to'] = cid

            self.broker_client.invoke_async(cb_msg) # type: ignore

        if kwargs.get('needs_response'):

            if skip_response_elem:
                return response
            else:
                response = service.response.payload
                if hasattr(response, 'getvalue'):
                    response = response.getvalue(serialize=kwargs.get('serialize'))
                return response

# ################################################################################################################################

    def on_broker_msg_SCHEDULER_JOB_EXECUTED(self, msg:'bunch_', args:'any_'=None) -> 'any_':
        return self.on_message_invoke_service(msg, CHANNEL.SCHEDULER, 'SCHEDULER_JOB_EXECUTED', args)

# ################################################################################################################################

    def on_broker_msg_SCHEDULER_SET_SCHEDULER_ADDRESS(self, msg:'bunch_', args:'any_'=None) -> 'any_':
        self.invoke('zato.scheduler.set-scheduler-address-impl', msg)

# ################################################################################################################################

    def on_broker_msg_OUTGOING_SQL_CREATE_EDIT(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Creates or updates an SQL connection, including changing its
        password.
        """
        if msg.password.startswith(SECRETS.PREFIX):
            msg.password = self.server.decrypt(msg.password)

        # Is it a rename? If so, delete the connection first
        if msg.get('old_name') and msg.get('old_name') != msg['name']:
            del self.sql_pool_store[msg['old_name']]

        msg['fs_sql_config'] = self.server.fs_sql_config
        self.sql_pool_store[msg['name']] = msg

    def on_broker_msg_OUTGOING_SQL_CHANGE_PASSWORD(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Deletes an outgoing SQL connection pool and recreates it using the
        new password.
        """
        # First, make sure that we already have such an SQL connection
        if wait_for_dict_key(self.sql_pool_store.wrappers, msg['name']):

            # Ensure we use a clear-text form of the password
            password = msg['password']
            password = self.server.decrypt(password)

            logger.info('Setting SQL password for `%s`', msg['name'])

            # If we are here, it means that the connection must be available,
            self.sql_pool_store.change_password(msg['name'], password)

        else:
            self.logger.warning('SQL connection not found -> `%s` (change-password)', msg['name'])

    def on_broker_msg_OUTGOING_SQL_DELETE(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Deletes an outgoing SQL connection pool.
        """
        del self.sql_pool_store[msg['name']]

# ################################################################################################################################

    def _get_channel_rest(self, connection_type:'str', value:'str', by_name:'bool'=True) -> 'dictnone':

        item_key = 'name' if by_name else 'id'

        with self.update_lock:
            for item in self.request_dispatcher.url_data.channel_data:
                if item['connection'] == connection_type:
                    if item[item_key] == value:
                        return item

# ################################################################################################################################

    def _get_outconn_rest(self, value:'str', by_name:'bool'=True) -> 'dictnone':

        item_key = 'name' if by_name else 'id'

        with self.update_lock:
            for outconn_value in self.worker_config.out_plain_http.values():
                if isinstance(outconn_value, dict):
                    config = outconn_value['config'] # type: dict
                    if config[item_key] == value:
                        return outconn_value

# ################################################################################################################################

    def wait_for_outconn_rest(self, name:'str', timeout:'int'=999999) -> 'bool':
        return wait_for_dict_key(self.worker_config.out_plain_http, name, timeout, interval=0.5)

# ################################################################################################################################

    def get_channel_rest(self, name:'str') -> 'bunch_':
        return self._get_channel_rest(CONNECTION.CHANNEL, name)# type: ignore

# ################################################################################################################################

    def get_outconn_rest(self, name:'str') -> 'dictnone':
        _ = self.wait_for_outconn_rest(name)
        return self._get_outconn_rest(name)

# ################################################################################################################################

    def get_outconn_rest_by_id(self, id:'str') -> 'dictnone':
        return self._get_outconn_rest(id, False)

# ################################################################################################################################

    def on_broker_msg_CHANNEL_HTTP_SOAP_CREATE_EDIT(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Creates or updates an HTTP/SOAP channel.
        """
        self.request_dispatcher.url_data.on_broker_msg_CHANNEL_HTTP_SOAP_CREATE_EDIT(msg, *args)

    def on_broker_msg_CHANNEL_HTTP_SOAP_DELETE(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Deletes an HTTP/SOAP channel.
        """
        # First, check if there was a cache for this channel. If so, make sure of all entries pointing
        # to the channel are deleted too.
        item = self.get_channel_rest(msg.name) or {}
        if item['cache_type']:
            cache = self.server.get_cache(item['cache_type'], item['cache_name'])
            cache.delete_by_prefix('http-channel-{}'.format(item['id']))

        # Delete the channel object now
        self.request_dispatcher.url_data.on_broker_msg_CHANNEL_HTTP_SOAP_DELETE(msg, *args)

# ################################################################################################################################

    def _delete_config_close_wrapper(
        self,
        name,        # type: str
        config_dict, # type: ConfigDict
        conn_type,   # type: str
        log_func     # type: callable_
    ) -> 'None':
        """ Deletes a wrapper-based connection's config and closes its underlying wrapper.
        """
        # Delete the connection first, if it exists at all ..
        try:
            try:
                wrapper = config_dict[name].conn
            except(KeyError, AttributeError):
                log_func('Could not access wrapper, e:`{}`'.format(format_exc()))
            else:
                try:
                    wrapper.session.close()
                finally:
                    del config_dict[name]
        except Exception:
            log_func('Could not delete `{}`, e:`{}`'.format(conn_type, format_exc()))

# ################################################################################################################################

    def _delete_config_close_wrapper_http_soap(self, name:'str', transport:'str', log_func:'callable_') -> 'None':
        """ Deletes/closes an HTTP/SOAP outconn.
        """
        # Are we dealing with plain HTTP or SOAP?
        config_dict = getattr(self.worker_config, 'out_' + transport)

        self._delete_config_close_wrapper(name, config_dict, 'an outgoing HTTP/SOAP connection', log_func)

    def on_broker_msg_OUTGOING_HTTP_SOAP_CREATE_EDIT(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Creates or updates an outgoing HTTP/SOAP connection.
        """
        # With outgoing SOAP messages using suds, we need to delete /tmp/suds
        # before the connection can be created. This is because our method can
        # also be invoked by ReloadWSDL action and suds will not always reload
        # the WSDL if /tmp/suds is around.
        if msg.transport == URL_TYPE.SOAP and msg.serialization_type == HTTP_SOAP_SERIALIZATION_TYPE.SUDS.id:

            # This is how suds obtains the location of its tmp directory in suds/cache.py
            suds_tmp_dir = os.path.join(gettempdir(), 'suds')
            if os.path.exists(suds_tmp_dir):
                try:
                    rmtree(suds_tmp_dir, True)
                except Exception:
                    logger.warning('Could not remove suds directory `%s`, e:`%s`', suds_tmp_dir, format_exc())

        # It might be a rename
        old_name = msg.get('old_name')
        del_name = old_name if old_name else msg['name']

        # .. delete the connection if it exists ..
        self._delete_config_close_wrapper_http_soap(del_name, msg['transport'], logger.debug)

        # .. and create a new one
        wrapper = self._http_soap_wrapper_from_config(msg, has_sec_config=False)
        config_dict = getattr(self.worker_config, 'out_' + msg['transport'])
        config_dict[msg['name']] = Bunch()
        config_dict[msg['name']].config = msg
        config_dict[msg['name']].conn = wrapper
        config_dict[msg['name']].ping = wrapper.ping # (just like in self.init_http)

        # Store mapping of ID -> name
        config_dict.set_key_id_data(msg)

    def on_broker_msg_OUTGOING_HTTP_SOAP_DELETE(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Deletes an outgoing HTTP/SOAP connection (actually delegates the
        task to self._delete_config_close_wrapper_http_soap.
        """
        self._delete_config_close_wrapper_http_soap(msg['name'], msg['transport'], logger.error)

# ################################################################################################################################

    def on_broker_msg_OUTGOING_REST_WRAPPER_CHANGE_PASSWORD(self, msg:'bunch_', *args:'any_') -> 'None':

        # Reusable
        password = msg.password
        password_decrypted = self.server.decrypt(password)

        # All outgoing REST connections
        out_plain_http = self.worker_config.out_plain_http

        # .. get the one that we need ..
        item = out_plain_http.get_by_id(msg.id)

        # .. update its dict configuration ..
        item['config']['password'] = password

        # .. and its wrapper's configuration too.
        self._visit_wrapper_change_password(item['conn'], {'password': password_decrypted}, check_name=False) # type: ignore

# ################################################################################################################################

    def on_broker_msg_SERVICE_DELETE(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Deletes the service from the service store and removes it from the filesystem
        if it's not an internal one.
        """
        # Where to delete it from in the second step
        deployment_info = self.server.service_store.get_deployment_info(msg.impl_name)

        # If the service is not deployed, there is nothing for us to do here
        if not deployment_info:
            return

        fs_location = deployment_info['fs_location']

        # Delete it from the service store
        self.server.service_store.delete_service_data(msg.name)

        # Delete it from the filesystem, including any bytecode left over. Note that
        # other parallel servers may wish to do exactly the same so we just ignore
        # the error if any files are missing. Also note that internal services won't
        # be ever deleted from the FS.
        if not msg.is_internal:
            all_ext = ('py', 'pyc', 'pyo')
            no_ext = '.'.join(fs_location.split('.')[:-1])
            for ext in all_ext:
                path = '{}.{}'.format(no_ext, ext)
                try:
                    os.remove(path)
                except OSError as e:
                    if e.errno != ENOENT:
                        raise

        # It is possible that this module was already deleted from sys.modules
        # in case there was more than one service in it and we first deleted
        # one and then the other.
        try:
            service_info = self.server.service_store.services[msg.impl_name]
        except KeyError:
            return
        else:
            mod = inspect.getmodule(service_info['service_class'])
            if mod:
                del sys.modules[mod.__name__]

    def on_broker_msg_SERVICE_EDIT(self, msg:'bunch_', *args:'any_') -> 'None':
        del msg['action']
        self.server.service_store.edit_service_data(msg)

# ################################################################################################################################

    def on_broker_msg_OUTGOING_FTP_CREATE_EDIT(self, msg:'bunch_', *args:'any_') -> 'None':
        out_ftp = cast_('FTPStore', self.worker_config.out_ftp)
        out_ftp.create_edit(msg, msg.get('old_name'))

    def on_broker_msg_OUTGOING_FTP_DELETE(self, msg:'bunch_', *args:'any_') -> 'None':
        out_ftp = cast_('FTPStore', self.worker_config.out_ftp)
        out_ftp.delete(msg.name)

    def on_broker_msg_OUTGOING_FTP_CHANGE_PASSWORD(self, msg:'bunch_', *args:'any_') -> 'None':
        out_ftp = cast_('FTPStore', self.worker_config.out_ftp)
        out_ftp.change_password(msg.name, msg.password)

# ################################################################################################################################

    def on_broker_msg_hot_deploy(
        self,
        msg,     # type: Bunch
        service, # type: str
        payload, # type: any_
        action,  # type: str
        *args,   # type: any_
        **kwargs # type: any_
    ) -> 'any_':
        msg.cid = new_cid()
        msg.service = service
        msg.payload = payload
        return self.on_message_invoke_service(msg, 'hot-deploy', 'HOT_DEPLOY_{}'.format(action), args, **kwargs)

# ################################################################################################################################

    def on_broker_msg_HOT_DEPLOY_CREATE_SERVICE(self, msg:'bunch_', *args:'any_') -> 'None':

        # Uploads the service
        _ = self.on_broker_msg_hot_deploy(
            msg, 'zato.hot-deploy.create', {'package_id': msg.package_id}, 'CREATE_SERVICE', *args,
            serialize=False, needs_response=True)

# ################################################################################################################################

    def on_broker_msg_HOT_DEPLOY_CREATE_STATIC(self, msg:'bunch_', *args:'any_') -> 'None':
        return self.on_broker_msg_hot_deploy(msg, 'zato.pickup.on-update-static', {
            'data': msg.data,
            'file_name': msg.file_name,
            'full_path': msg.full_path,
            'relative_dir': msg.relative_dir
        }, 'CREATE_STATIC', *args)

# ################################################################################################################################

    def on_broker_msg_HOT_DEPLOY_CREATE_USER_CONF(self, msg:'bunch_', *args:'any_') -> 'None':
        return self.on_broker_msg_hot_deploy(msg, 'zato.pickup.on-update-user-conf', {
            'data': msg.data,
            'file_name': msg.file_name,
            'full_path': msg.full_path,
            'relative_dir': msg.relative_dir
        }, 'CREATE_USER_CONF', *args)

# ################################################################################################################################

    def on_broker_msg_HOT_DEPLOY_AFTER_DEPLOY(self, msg:'bunch_', *args:'any_') -> 'None':

        # Redeploy services that depended on the service just deployed.
        if self.server.fs_server_config.hot_deploy.redeploy_on_parent_change:
            self.server.service_store.redeploy_on_parent_changed(msg.service_name, msg.service_impl_name)

# ################################################################################################################################

    def on_broker_msg_SERVICE_PUBLISH(self, msg:'bunch_', args:'any_'=None) -> 'None':
        return self.on_message_invoke_service(msg, msg.get('channel') or CHANNEL.INVOKE_ASYNC, 'SERVICE_PUBLISH', args)

# ################################################################################################################################

    def _on_broker_msg_cloud_create_edit(
        self,
        msg,          # type: Bunch
        conn_type,    # type: str
        config_dict,  # type: ConfigDict
        wrapper_class # type: any_
    ) -> 'bunch_':

        # It might be a rename
        old_name = msg.get('old_name')
        del_name = old_name if old_name else msg['name']

        # .. delete the connection if it exists ..
        self._delete_config_close_wrapper(del_name, config_dict, conn_type, logger.debug)

        # .. and create a new one
        msg['queue_build_cap'] = float(self.server.fs_server_config.misc.queue_build_cap)
        wrapper = wrapper_class(msg, self.server)
        wrapper.build_queue()

        item = Bunch()

        config_dict[msg['name']] = item
        config_dict[msg['name']].config = msg
        config_dict[msg['name']].conn = wrapper

        return item

# ################################################################################################################################

    def on_broker_msg_OUTGOING_ODOO_CREATE(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Creates or updates an Odoo connection.
        """
        _ = self._on_broker_msg_cloud_create_edit(msg, 'Odoo', self.worker_config.out_odoo, OdooWrapper)

    on_broker_msg_OUTGOING_ODOO_CHANGE_PASSWORD = on_broker_msg_OUTGOING_ODOO_EDIT = on_broker_msg_OUTGOING_ODOO_CREATE

    def on_broker_msg_OUTGOING_ODOO_DELETE(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Closes and deletes an Odoo connection.
        """
        self._delete_config_close_wrapper(msg['name'], self.worker_config.out_odoo, 'Odoo', logger.debug)

# ################################################################################################################################

    def on_broker_msg_OUTGOING_SAP_CREATE(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Creates or updates an SAP RFC connection.
        """
        _ = self._on_broker_msg_cloud_create_edit(msg, 'SAP', self.worker_config.out_sap, SAPWrapper)

    on_broker_msg_OUTGOING_SAP_CHANGE_PASSWORD = on_broker_msg_OUTGOING_SAP_EDIT = on_broker_msg_OUTGOING_SAP_CREATE

    def on_broker_msg_OUTGOING_SAP_DELETE(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Closes and deletes an SAP RFC connection.
        """
        self._delete_config_close_wrapper(msg['name'], self.worker_config.out_sap, 'SAP', logger.debug)

# ################################################################################################################################

    def on_broker_msg_SEARCH_ES_CREATE(self, msg:'bunch_') -> 'None':
        self.search_es_api.create(msg.name, msg)

    def on_broker_msg_SEARCH_ES_EDIT(self, msg:'bunch_') -> 'None':
        # It might be a rename
        old_name = msg.get('old_name')
        del_name = old_name if old_name else msg['name']
        self.search_es_api.edit(del_name, msg)

    def on_broker_msg_SEARCH_ES_DELETE(self, msg:'bunch_') -> 'None':
        self.search_es_api.delete(msg.name)

# ################################################################################################################################

    def on_broker_msg_EMAIL_SMTP_CREATE(self, msg:'bunch_') -> 'None':
        self.email_smtp_api.create(msg.name, msg)

    def on_broker_msg_EMAIL_SMTP_EDIT(self, msg:'bunch_') -> 'None':
        # It might be a rename
        old_name = msg.get('old_name')
        del_name = old_name if old_name else msg['name']
        msg.password = self.email_smtp_api.get(del_name, True).config.password
        self.email_smtp_api.edit(del_name, msg)

    def on_broker_msg_EMAIL_SMTP_DELETE(self, msg:'bunch_') -> 'None':
        self.email_smtp_api.delete(msg.name)

    def on_broker_msg_EMAIL_SMTP_CHANGE_PASSWORD(self, msg:'bunch_') -> 'None':
        self.email_smtp_api.change_password(msg)

# ################################################################################################################################

    def on_broker_msg_EMAIL_IMAP_CREATE(self, msg:'bunch_') -> 'None':
        self.email_imap_api.create(msg.name, msg)

    def on_broker_msg_EMAIL_IMAP_EDIT(self, msg:'bunch_') -> 'None':
        # It might be a rename
        old_name = msg.get('old_name')
        del_name = old_name if old_name else msg['name']
        msg.password = self.email_imap_api.get(del_name, True).config.password
        self.email_imap_api.edit(del_name, msg)

    def on_broker_msg_EMAIL_IMAP_DELETE(self, msg:'bunch_') -> 'None':
        self.email_imap_api.delete(msg.name)

    def on_broker_msg_EMAIL_IMAP_CHANGE_PASSWORD(self, msg:'bunch_') -> 'None':
        self.email_imap_api.change_password(msg)

# ################################################################################################################################
