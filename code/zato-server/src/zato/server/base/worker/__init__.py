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
from copy import deepcopy
from datetime import datetime
from errno import ENOENT
from inspect import isclass
from shutil import rmtree
from tempfile import gettempdir
from threading import RLock
from traceback import format_exc
from urllib.parse import urlparse
from uuid import uuid4

# Bunch
from bunch import bunchify

# gevent
import gevent

# orjson
from orjson import dumps

# Zato
from zato.bunch import Bunch
from zato.common import broker_message
from zato.common.api import API_Key, CHANNEL, CONNECTION, DATA_FORMAT, FILE_TRANSFER, GENERIC as COMMON_GENERIC, \
     HotDeploy, HTTP_SOAP_SERIALIZATION_TYPE, IPC, NOTIF, PUBSUB, RATE_LIMIT, SEC_DEF_TYPE, simple_types, \
     URL_TYPE, WEB_SOCKET, Wrapper_Name_Prefix_List, ZATO_DEFAULT, ZATO_NONE, ZATO_ODB_POOL_NAME, ZMQ
from zato.common.broker_message import code_to_name, GENERIC as BROKER_MSG_GENERIC, SERVICE
from zato.common.const import SECRETS
from zato.common.dispatch import dispatcher
from zato.common.json_internal import loads
from zato.common.match import Matcher
from zato.common.model.amqp_ import AMQPConnectorConfig
from zato.common.model.wsx import WSXConnectorConfig
from zato.common.odb.api import PoolStore, SessionWrapper
from zato.common.typing_ import cast_
from zato.common.util.api import get_tls_ca_cert_full_path, get_tls_key_cert_full_path, get_tls_from_payload, \
     fs_safe_name, import_module_from_path, new_cid, parse_extra_into_dict, parse_tls_channel_security_definition, \
     start_connectors, store_tls, update_apikey_username_to_channel, update_bind_port, visit_py_source, wait_for_dict_key, \
     wait_for_dict_key_by_get_func
from zato.common.util.file_system import resolve_path
from zato.common.util.pubsub import is_service_subscription
from zato.cy.reqresp.payload import SimpleIOPayload
from zato.server.base.parallel.subprocess_.api import StartConfig as SubprocessStartConfig
from zato.server.base.worker.common import WorkerImpl
from zato.server.connection.amqp_ import ConnectorAMQP
from zato.server.connection.cache import CacheAPI
from zato.server.connection.connector import ConnectorStore, connector_type
# from zato.server.connection.cloud.aws.s3 import S3Wrapper
from zato.server.connection.email import IMAPAPI, IMAPConnStore, SMTPAPI, SMTPConnStore
from zato.server.connection.ftp import FTPStore
from zato.server.connection.http_soap.channel import RequestDispatcher, RequestHandler
from zato.server.connection.http_soap.outgoing import HTTPSOAPWrapper, SudsSOAPWrapper
from zato.server.connection.http_soap.url_data import URLData
from zato.server.connection.odoo import OdooWrapper
from zato.server.connection.sap import SAPWrapper
from zato.server.connection.search.es import ElasticSearchAPI, ElasticSearchConnStore
from zato.server.connection.search.solr import SolrAPI, SolrConnStore
from zato.server.connection.sftp import SFTPIPCFacade
from zato.server.connection.sms.twilio import TwilioAPI, TwilioConnStore
from zato.server.connection.web_socket import ChannelWebSocket
from zato.server.connection.vault import VaultConnAPI
from zato.server.ext.zunicorn.workers.ggevent import GeventWorker as GunicornGeventWorker
from zato.server.file_transfer.api import FileTransferAPI
from zato.server.generic.api.channel_file_transfer import ChannelFileTransferWrapper
from zato.server.generic.api.channel_hl7_mllp import ChannelHL7MLLPWrapper
from zato.server.generic.api.cloud_confluence import CloudConfluenceWrapper
from zato.server.generic.api.cloud_dropbox import CloudDropbox
from zato.server.generic.api.cloud_jira import CloudJiraWrapper
from zato.server.generic.api.cloud_microsoft_365 import CloudMicrosoft365Wrapper
from zato.server.generic.api.cloud_salesforce import CloudSalesforceWrapper
from zato.server.generic.api.def_kafka import DefKafkaWrapper
from zato.server.generic.api.outconn_hl7_fhir import OutconnHL7FHIRWrapper
from zato.server.generic.api.outconn_hl7_mllp import OutconnHL7MLLPWrapper
from zato.server.generic.api.outconn_im_slack import OutconnIMSlackWrapper
from zato.server.generic.api.outconn_im_telegram import OutconnIMTelegramWrapper
from zato.server.generic.api.outconn_ldap import OutconnLDAPWrapper
from zato.server.generic.api.outconn_mongodb import OutconnMongoDBWrapper
from zato.server.generic.api.outconn.wsx.base import OutconnWSXWrapper
from zato.server.pubsub import PubSub
from zato.server.pubsub.delivery.tool import PubSubTool
from zato.server.rbac_ import RBAC
from zato.zmq_.channel import MDPv01 as ChannelZMQMDPv01, Simple as ChannelZMQSimple
from zato.zmq_.outgoing import Simple as OutZMQSimple

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from bunch import Bunch as bunch_
    from zato.broker.client import BrokerClient
    from zato.common.typing_ import any_, anydict, anylist, anytuple, callable_, callnone, dictnone, stranydict, tupnone
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
        self.deployment_key = '{}.{}'.format(datetime.utcnow().isoformat(), uuid4().hex)
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
        self.kvdb = server.kvdb
        self.pubsub = PubSub(self.server.cluster_id, self.server)
        self.rbac = RBAC()
        self.worker_idx = int(os.environ['ZATO_SERVER_WORKER_IDX'])

        # Which services can be invoked
        self.invoke_matcher = Matcher()

        # Which targets this server supports
        self.target_matcher = Matcher()

        # To expedite look-ups
        self._simple_types = simple_types

        # Generic connections - File transfer channels
        self.channel_file_transfer = {}

        # Generic connections - HL7 MLLP channels
        self.channel_hl7_mllp = {}

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

        # Generic connections - Kafka definitions
        self.def_kafka = {}

        # Generic connections - HL7 FHIR outconns
        self.outconn_hl7_fhir = {}

        # Generic connections - HL7 MLLP outconns
        self.outconn_hl7_mllp = {}

        # Generic connections - IM Slack
        self.outconn_im_slack = {}

        # Generic connections - IM Telegram
        self.outconn_im_telegram = {}

        # Generic connections - LDAP outconns
        self.outconn_ldap = {}

        # Generic connections - MongoDB outconns
        self.outconn_mongodb = {}

        # Generic connections - WSX outconns
        self.outconn_wsx = {}

# ################################################################################################################################

    def init(self) -> 'None':

        # Search
        self.search_es_api = ElasticSearchAPI(ElasticSearchConnStore())
        self.search_solr_api = SolrAPI(SolrConnStore())

        # SMS
        self.sms_twilio_api = TwilioAPI(TwilioConnStore())

        # E-mail
        self.email_smtp_api = SMTPAPI(SMTPConnStore())
        self.email_imap_api = IMAPAPI(IMAPConnStore())

        # ZeroMQ
        self.zmq_mdp_v01_api = ConnectorStore(connector_type.duplex.zmq_v01, ChannelZMQMDPv01)
        self.zmq_channel_api = ConnectorStore(connector_type.channel.zmq, ChannelZMQSimple)
        self.zmq_out_api = ConnectorStore(connector_type.out.zmq, OutZMQSimple)

        # WebSocket
        self.web_socket_api = ConnectorStore(connector_type.duplex.web_socket, ChannelWebSocket, self.server)

        # AMQP
        self.amqp_api = ConnectorStore(connector_type.duplex.amqp, ConnectorAMQP)
        self.amqp_out_name_to_def = {} # Maps outgoing connection names to definition names, i.e. to connector names

        # Vault connections
        self.vault_conn_api = VaultConnAPI()

        # Caches
        self.cache_api = CacheAPI(self.server)

        # File transfer
        self.file_transfer_api = FileTransferAPI(self.server, self)

        # Maps generic connection types to their API handler objects
        self.generic_conn_api = {
            COMMON_GENERIC.CONNECTION.TYPE.CHANNEL_FILE_TRANSFER: self.channel_file_transfer,
            COMMON_GENERIC.CONNECTION.TYPE.CHANNEL_HL7_MLLP: self.channel_hl7_mllp,
            COMMON_GENERIC.CONNECTION.TYPE.CLOUD_CONFLUENCE: self.cloud_confluence,
            COMMON_GENERIC.CONNECTION.TYPE.CLOUD_DROPBOX: self.cloud_dropbox,
            COMMON_GENERIC.CONNECTION.TYPE.CLOUD_JIRA: self.cloud_jira,
            COMMON_GENERIC.CONNECTION.TYPE.CLOUD_MICROSOFT_365: self.cloud_microsoft_365,
            COMMON_GENERIC.CONNECTION.TYPE.CLOUD_SALESFORCE: self.cloud_salesforce,
            COMMON_GENERIC.CONNECTION.TYPE.DEF_KAFKA: self.def_kafka,
            COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_HL7_FHIR: self.outconn_hl7_fhir,
            COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_HL7_MLLP: self.outconn_hl7_mllp,
            COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_IM_SLACK: self.outconn_im_slack,
            COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_IM_TELEGRAM: self.outconn_im_telegram,
            COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_LDAP: self.outconn_ldap,
            COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_MONGODB: self.outconn_mongodb,
            COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_WSX: self.outconn_wsx,
        }

        self._generic_conn_handler = {
            COMMON_GENERIC.CONNECTION.TYPE.CHANNEL_FILE_TRANSFER: ChannelFileTransferWrapper,
            COMMON_GENERIC.CONNECTION.TYPE.CHANNEL_HL7_MLLP: ChannelHL7MLLPWrapper,
            COMMON_GENERIC.CONNECTION.TYPE.CLOUD_CONFLUENCE: CloudConfluenceWrapper,
            COMMON_GENERIC.CONNECTION.TYPE.CLOUD_DROPBOX: CloudDropbox,
            COMMON_GENERIC.CONNECTION.TYPE.CLOUD_JIRA: CloudJiraWrapper,
            COMMON_GENERIC.CONNECTION.TYPE.CLOUD_MICROSOFT_365: CloudMicrosoft365Wrapper,
            COMMON_GENERIC.CONNECTION.TYPE.CLOUD_SALESFORCE: CloudSalesforceWrapper,
            COMMON_GENERIC.CONNECTION.TYPE.DEF_KAFKA: DefKafkaWrapper,
            COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_HL7_FHIR: OutconnHL7FHIRWrapper,
            COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_HL7_MLLP: OutconnHL7MLLPWrapper,
            COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_IM_SLACK: OutconnIMSlackWrapper,
            COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_IM_TELEGRAM: OutconnIMTelegramWrapper,
            COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_LDAP: OutconnLDAPWrapper,
            COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_MONGODB: OutconnMongoDBWrapper,
            COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_WSX: OutconnWSXWrapper
        }

        # Maps message actions against generic connection types and their message handlers
        self.generic_impl_func_map = {}

        # After connection is establised, a flag is stored here to let queries consult it
        # before they attempt to prepare statements. In other words, queries wait for connections.
        # They do it in separate greenlets.
        self._cassandra_connections_ready = {}

        # Cassandra
        self.init_cassandra()
        self.init_cassandra_queries()

        # Search
        self.init_search_es()
        self.init_search_solr()

        # SMS
        self.init_sms_twilio()

        # E-mail
        self.init_email_smtp()
        self.init_email_imap()

        # ZeroMQ
        self.init_zmq()

        # Odoo
        self.init_odoo()

        # SAP RFC
        self.init_sap()

        # RBAC
        self.init_rbac()

        # Vault connections
        self.init_vault_conn()

        # Caches
        self.init_caches()

        # API keys
        self.update_apikeys()

        # SFTP - attach handles to connections to each ConfigDict now that all their configuration is ready
        self.init_sftp()

        request_handler = RequestHandler(self.server)
        url_data = URLData(
            self,
            self.worker_config.http_soap,
            self._get_channel_url_sec(),
            self.worker_config.basic_auth,
            self.worker_config.jwt,
            self.worker_config.ntlm,
            self.worker_config.oauth,
            self.worker_config.apikey,
            self.worker_config.aws,
            self.worker_config.tls_channel_sec,
            self.worker_config.tls_key_cert,
            self.worker_config.vault_conn_sec,
            self.kvdb,
            self.broker_client,
            self.server.odb,
            self.server.jwt_secret,
            self.vault_conn_api
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
        self.init_cloud()

        # AMQP
        self.init_amqp()

        # Initialise file transfer-based pickup here because it is required when generic connections are being created
        self.convert_pickup_to_file_transfer()

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

    def after_broker_client_set(self) -> 'None':
        self.pubsub.broker_client = self.broker_client

        # Pub/sub requires broker client
        self.init_pubsub()

        # WebSocket connections may depend on pub/sub so we create them only after pub/sub is initialized
        self.init_wsx()

# ################################################################################################################################

    def set_broker_client(self, broker_client:'BrokerClient') -> 'None':
        self.broker_client = broker_client
        self.after_broker_client_set()

# ################################################################################################################################

    def filter(self, msg:'bunch_') -> 'bool':
        return True

# ################################################################################################################################

    def _update_queue_build_cap(self, item:'any_') -> 'None':
        item.queue_build_cap = float(self.server.fs_server_config.misc.queue_build_cap)

# ################################################################################################################################

    def _update_aws_config(self, msg:'bunch_') -> 'None':
        """ Parses the address to AWS we store into discrete components S3Connection objects expect.
        Also turns metadata string into a dictionary
        """
        url_info = urlparse(msg.address)

        msg.is_secure = True if url_info.scheme == 'https' else False
        msg.port = url_info.port if url_info.port else (443 if msg.is_secure else 80)
        msg.host = url_info.netloc

        msg.metadata = parse_extra_into_dict(msg.metadata_)

# ################################################################################################################################

    def _get_tls_verify_from_config(self, config:'any_') -> 'bool':

        tls_config = self.worker_config.tls_ca_cert[config.sec_tls_ca_cert_name]
        tls_config = tls_config.config
        tls_config = tls_config.value
        tls_from_payload = get_tls_from_payload(tls_config)
        tls_verify = get_tls_ca_cert_full_path(self.server.tls_dir, tls_from_payload)

        return tls_verify

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

            if sec_config['sec_type'] == SEC_DEF_TYPE.TLS_KEY_CERT:
                tls = cast_('bunch_', self.request_dispatcher.url_data.tls_key_cert_get(security_name))
                auth_data = self.server.decrypt(tls.config.auth_data)
                sec_config['tls_key_cert_full_path'] = get_tls_key_cert_full_path(
                    self.server.tls_dir, get_tls_from_payload(auth_data, True))

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

        # Key 'sec_tls_ca_cert_verify_strategy' was added in 3.2
        # so we need to handle cases when it exists or it does not.
        sec_tls_ca_cert_verify_strategy = config.get('sec_tls_ca_cert_verify_strategy')

        # 3.2+
        if sec_tls_ca_cert_verify_strategy:
            if sec_tls_ca_cert_verify_strategy is True:
                tls_verify = True

            elif sec_tls_ca_cert_verify_strategy is False:
                tls_verify = False

            else:
                tls_verify = self._get_tls_verify_from_config(config)

        # < 3.2
        else:
            if not config.get('sec_tls_ca_cert_id') and config.sec_tls_ca_cert_id in {ZATO_DEFAULT, ZATO_NONE}:
                tls_verify = self._get_tls_verify_from_config(config)
            else:
                tls_verify = False

        wrapper_config['tls_verify'] = tls_verify

        conn_soap = wrapper_config['transport'] == URL_TYPE.SOAP
        conn_suds = wrapper_config['serialization_type'] == HTTP_SOAP_SERIALIZATION_TYPE.SUDS.id

        if conn_soap and conn_suds:
            wrapper_config['queue_build_cap'] = float(self.server.fs_server_config.misc.queue_build_cap)
            wrapper = SudsSOAPWrapper(wrapper_config)
            if wrapper_config['is_active']:
                wrapper.build_client_queue()
            return wrapper

        return HTTPSOAPWrapper(self.server, wrapper_config)

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

    def init_sftp(self) -> 'None':
        """ Each outgoing SFTP connection requires a connection handle to be attached here,
        later, in run-time, this is the 'conn' parameter available via self.out[name].conn.
        """
        for value in self.worker_config.out_sftp.values():
            value['conn'] = SFTPIPCFacade(self.server, value['config'])

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

    def init_cloud(self) -> 'None':
        """ Initializes all the cloud connections.
        """
        # data = (
        #     ('cloud_aws_s3', S3Wrapper),
        # )
        data = []
        S3Wrapper = None

        for config_key, wrapper in data:
            config_attr = getattr(self.worker_config, config_key)
            for name in config_attr:
                config = config_attr[name]['config']
                if isinstance(wrapper, S3Wrapper):
                    self._update_aws_config(config)
                config.queue_build_cap = float(self.server.fs_server_config.misc.queue_build_cap)
                config_attr[name].conn = wrapper(config, self.server)
                config_attr[name].conn.build_queue()

    def get_notif_config(self, notif_type:'str', name:'str') -> 'ConfigDict':
        config_dict = {
            NOTIF.TYPE.SQL: self.worker_config.notif_sql,
        }[notif_type]

        return config_dict.get(name)

    def create_edit_notifier(self, msg:'bunch_', action:'str', config_dict:'ConfigDict', update_func:'callnone'=None) -> 'None':

        # It might be a rename
        old_name = msg.get('old_name')
        del_name = old_name if old_name else msg.name

        config_dict.pop(del_name, None) # Delete and ignore if it doesn't exit (it's CREATE then)
        config_dict[msg.name] = Bunch()
        config_dict[msg.name].config = msg

        if update_func:
            update_func(msg)

        # Start a new background notifier either if it's a create action or on rename.
        if msg.source_service_type == 'create' or (old_name and old_name != msg.name):

            self.on_message_invoke_service({
                'service': 'zato.notif.invoke-run-notifier',
                'payload': {'config': msg},
                'cid': new_cid(),
            }, CHANNEL.NOTIFIER_RUN, action)

# ################################################################################################################################

    def _on_cassandra_connection_established(self, config:'bunch_') -> 'None':
        self._cassandra_connections_ready[config.id] = True

    def init_cassandra(self) -> 'None':
        for k, v in self.worker_config.cassandra_conn.items():
            try:
                self._cassandra_connections_ready[v.config.id] = False
                self.update_cassandra_conn(v.config)
                self.cassandra_api.create_def(k, v.config, self._on_cassandra_connection_established)
            except Exception:
                logger.warning('Could not create a Cassandra connection `%s`, e:`%s`', k, format_exc())

# ################################################################################################################################

    def _init_cassandra_query(self, create_func:'callable_', k:'str', config:'bunch_') -> 'None':
        idx = 0
        while not self._cassandra_connections_ready.get(config.def_id):
            gevent.sleep(1)

            idx += 1
            if not idx % 20:
                logger.warning('Still waiting for `%s` Cassandra connection', config.def_name)

        create_func(k, config, def_=self.cassandra_api[config.def_name])

    def init_cassandra_queries(self) -> 'None':
        for k, v in self.worker_config.cassandra_query.items():
            try:
                gevent.spawn(self._init_cassandra_query, self.cassandra_query_api.create, k, v.config)
            except Exception:
                logger.warning('Could not create a Cassandra query `%s`, e:`%s`', k, format_exc())

# ################################################################################################################################

    def init_simple(self, config:'bunch_', api:'BaseAPI', name:'str') -> 'None':
        for k, v in config.items():
            self._update_queue_build_cap(v.config)
            try:
                api.create(k, v.config)
            except Exception:
                logger.warning('Could not create {} connection `%s`, e:`%s`'.format(name), k, format_exc())

# ################################################################################################################################

    def init_sms_twilio(self) -> 'None':
        self.init_simple(self.worker_config.sms_twilio, self.sms_twilio_api, 'a Twilio')

# ################################################################################################################################

    def init_search_es(self) -> 'None':
        self.init_simple(self.worker_config.search_es, self.search_es_api, 'an ElasticSearch')

# ################################################################################################################################

    def init_search_solr(self) -> 'None':
        self.init_simple(self.worker_config.search_solr, self.search_solr_api, 'a Solr')

# ################################################################################################################################

    def init_email_smtp(self) -> 'None':
        self.init_simple(self.worker_config.email_smtp, self.email_smtp_api, 'an SMTP')

# ################################################################################################################################

    def init_email_imap(self) -> 'None':
        self.init_simple(self.worker_config.email_imap, self.email_imap_api, 'an IMAP')

# ################################################################################################################################

    def _set_up_zmq_channel(self, name:'str', config:'bunch_', action:'str', start:'bool'=False) -> 'None':
        """ Actually initializes a ZeroMQ channel, taking into account dissimilarities between MDP ones and PULL/SUB.
        """
        # We need to consult old_socket_type because it may very well be the case that someone
        # not only (say) renamed a channel but also changed its socket type as well.

        if config.get('old_socket_type') and config.socket_type != config.old_socket_type:
            raise ValueError('Cannot change a ZeroMQ channel\'s socket type')

        if config.socket_type.startswith(ZMQ.MDP):
            api = self.zmq_mdp_v01_api

            zeromq_mdp_config = self.server.fs_server_config.zeromq_mdp
            zeromq_mdp_config = {k:int(v) for k, v in zeromq_mdp_config.items()}
            config.update(zeromq_mdp_config)

        else:
            api = self.zmq_channel_api

        getattr(api, action)(name, config, self.on_message_invoke_service)

        if start:
            api.start(name)

# ################################################################################################################################

    def init_zmq_channels(self) -> 'None':
        """ Initializes ZeroMQ channels and MDP connections.
        """
        # Channels
        for name, data in self.worker_config.channel_zmq.items():

            # Each worker uses a unique bind port
            data = bunchify(data)
            update_bind_port(data.config, self.worker_idx)

            self._set_up_zmq_channel(name, bunchify(data.config), 'create')

        self.zmq_mdp_v01_api.start()
        self.zmq_channel_api.start()

    def init_zmq_outconns(self):
        """ Initializes ZeroMQ outgoing connections (but not MDP that are initialized along with channels).
        """
        for name, data in self.worker_config.out_zmq.items():

            # MDP ones were already handled in channels above
            if data.config['socket_type'].startswith(ZMQ.MDP):
                continue

            self.zmq_out_api.create(name, data.config)

        self.zmq_out_api.start()

# ################################################################################################################################

    def init_zmq(self) -> 'None':
        """ Initializes all ZeroMQ connections.
        """
        # Iterate over channels and outgoing connections and populate their respetive connectors.
        # Note that MDP are duplex and we create them in channels while in outgoing connections they are skipped.

        self.init_zmq_channels()
        self.init_zmq_outconns()

# ################################################################################################################################

    def init_wsx(self) -> 'None':
        """ Initializes all WebSocket connections.
        """
        # Channels
        for name, data in self.worker_config.channel_web_socket.items():

            # Convert configuration to expected datatypes
            data.config['max_len_messages_sent'] = int(data.config.get('max_len_messages_sent') or 0)
            data.config['max_len_messages_received'] = int(data.config.get('max_len_messages_received') or 0)

            data.config['pings_missed_threshold'] = int(
                data.config.get('pings_missed_threshold') or WEB_SOCKET.DEFAULT.PINGS_MISSED_THRESHOLD)

            data.config['ping_interval'] = int(
                data.config.get('ping_interval') or WEB_SOCKET.DEFAULT.PING_INTERVAL)

            # Create a new WebSocket connector definition ..
            config = WSXConnectorConfig.from_dict(data.config)

            # .. append common hook service to the configuration.
            config.hook_service = self.server.fs_server_config.get('wsx', {}).get('hook_service', '')

            self.web_socket_api.create(name, config, self.on_message_invoke_service,
                self.request_dispatcher.url_data.authenticate_web_socket)

        self.web_socket_api.start()

# ################################################################################################################################

    def init_amqp(self) -> 'None':
        """ Initializes all AMQP connections.
        """
        def _name_matches(def_name:'str') -> 'callable_':
            def _inner(config:'stranydict') -> 'bool':
                return config['def_name']==def_name
            return _inner

        for def_name, data in self.worker_config.definition_amqp.items():

            channels = self.worker_config.channel_amqp.get_config_list(_name_matches(def_name))
            outconns = self.worker_config.out_amqp.get_config_list(_name_matches(def_name))

            for outconn in outconns:
                self.amqp_out_name_to_def[outconn['name']] = def_name

            # Create a new AMQP connector definition ..
            config = AMQPConnectorConfig.from_dict(data.config)

            # .. AMQP definitions as such are always active. It is channels or outconns that can be inactive.
            config.is_active = True

            self.amqp_api.create(def_name, config, self.invoke,
                channels=self._config_to_dict(channels), outconns=self._config_to_dict(outconns))

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

    def init_rbac(self) -> 'None':

        for value in self.worker_config.service.values():
            self.rbac.create_resource(value.config.id)

        for value in self.worker_config.rbac_permission.values():
            self.rbac.create_permission(value.config.id, value.config.name)

        for value in self.worker_config.rbac_role.values():
            self.rbac.create_role(value.config.id, value.config.name, value.config.parent_id)

        for value in self.worker_config.rbac_client_role.values():
            self.rbac.create_client_role(value.config.client_def, value.config.role_id)

        # TODO - handle 'deny' as well
        for value in self.worker_config.rbac_role_permission.values():
            self.rbac.create_role_permission_allow(value.config.role_id, value.config.perm_id, value.config.service_id)

        self.rbac.set_http_permissions()

# ################################################################################################################################

    def init_vault_conn(self) -> 'None':
        for value in self.worker_config.vault_conn_sec.values():
            self.vault_conn_api.create(bunchify(value['config']))

# ################################################################################################################################

    def init_caches(self) -> 'None':

        for name in 'builtin', 'memcached':
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
            jwt_config=self.worker_config.jwt,
            ntlm_config=self.worker_config.ntlm,
            oauth_config=self.worker_config.oauth,
            apikey_config=self.worker_config.apikey,
            aws_config=self.worker_config.aws,
            tls_channel_sec_config=self.worker_config.tls_channel_sec,
            tls_key_cert_config=self.worker_config.tls_key_cert,
            vault_conn_sec_config=self.worker_config.vault_conn_sec,
        )

        # .. now, initialize connections that may depend on what we have just loaded ..
        self.init_http_soap(has_sec_config=False)

# ################################################################################################################################

    def sync_pubsub(self):
        """ Rebuilds all the in-RAM pub/sub structures and tasks.
        """
        # First, stop everything ..
        self.pubsub.stop()

        # .. now, load it into RAM from the database ..
        self.server.set_up_pubsub(self.server.cluster_id)

        # .. finally, initialize everything once more.
        self.init_pubsub()

# ################################################################################################################################

    def init_pubsub(self) -> 'None':
        """ Sets up all pub/sub endpoints, subscriptions and topics. Also, configures pubsub with getters for each endpoint type.
        """
        if not self.server.should_run_pubsub:
            logger.info('Not starting publish/subscribe')
            return

        # This is a pub/sub tool for delivery of Zato services within this server
        service_pubsub_tool = PubSubTool(self.pubsub, self.server, PUBSUB.ENDPOINT_TYPE.SERVICE.id, True)
        self.pubsub.service_pubsub_tool = service_pubsub_tool

        for value in self.worker_config.pubsub_topic.values(): # type: ignore
            self.pubsub.create_topic_object(bunchify(value['config']))

        for value in self.worker_config.pubsub_endpoint.values(): # type: ignore
            self.pubsub.create_endpoint(bunchify(value['config']))

        for value in self.worker_config.pubsub_subscription.values(): # type: ignore

            config:'bunch_' = bunchify(value['config'])
            config.add_subscription = True # We don't create WSX subscriptions here so it is always True

            self.pubsub.create_subscription_object(config)

            # Special-case delivery of messages to services
            if is_service_subscription(config):
                self.pubsub.set_config_for_service_subscription(config['sub_key'])

        self.pubsub.set_endpoint_impl_getter(PUBSUB.ENDPOINT_TYPE.REST.id, self.worker_config.out_plain_http.get_by_id)

        # Not used but needed for API completeness
        self.pubsub.set_endpoint_impl_getter(
            PUBSUB.ENDPOINT_TYPE.WEB_SOCKETS.id,
            cast_('callable_', None),
        )

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

    def _convert_pickup_config_to_file_transfer(self, name:'str', config:'anydict | bunch_') -> 'bunch_ | None':

        # Convert paths to full ones
        pickup_from_list = config.get('pickup_from') or []

        if not pickup_from_list:
            return

        pickup_from_list = pickup_from_list if isinstance(pickup_from_list, list) else [pickup_from_list]
        pickup_from_list = [resolve_path(elem, self.server.base_dir) for elem in pickup_from_list]

        move_processed_to = config.get('move_processed_to')
        if move_processed_to:
            move_processed_to = resolve_path(move_processed_to, self.server.base_dir)

        # Make sure we have lists on input
        service_list = config.get('services') or []
        service_list = service_list if isinstance(service_list, list) else [service_list]

        topic_list = config.get('topic_list') or []
        topic_list = topic_list if isinstance(topic_list, list) else [topic_list]

        data = {

          # Tell the manager to start this channel only
          # if we are very first process among potentially many ones for this server.
          '_start_channel': True if self.server.is_starting_first else False,

          'type_': COMMON_GENERIC.CONNECTION.TYPE.CHANNEL_FILE_TRANSFER,
          'name': name,
          'is_active': True,
          'is_internal': True,
          'data_encoding': config.get('data_encoding') or 'utf-8',
          'source_type': FILE_TRANSFER.SOURCE_TYPE.LOCAL.id,
          'pickup_from_list': pickup_from_list,
          'is_hot_deploy': config.get('is_hot_deploy'),
          'should_deploy_in_place': config.get('deploy_in_place', False),
          'service_list': service_list,
          'topic_list': topic_list,
          'move_processed_to': move_processed_to,
          'file_patterns': config.get('patterns') or '*',
          'parse_with': config.get('parse_with'),
          'should_read_on_pickup': config.get('read_on_pickup', True),
          'should_parse_on_pickup': config.get('parse_on_pickup', False),
          'should_delete_after_pickup': config.get('delete_after_pickup', True),
          'is_case_sensitive': config.get('is_case_sensitive', True),
          'is_line_by_line': config.get('is_line_by_line', False),
          'is_recursive': config.get('is_recursive', False),
          'binary_file_patterns': config.get('binary_file_patterns') or [],
          'outconn_rest_list': [],
        }

        return bunchify(data)

# ################################################################################################################################

    def convert_pickup_to_file_transfer(self) -> 'None':

        # Default pickup directory
        self._add_service_pickup_to_file_transfer(
            'hot-deploy', self.server.hot_deploy_config.pickup_dir,
            self.server.hot_deploy_config.delete_after_pickup, False)

        # User-defined pickup directories
        for name, config in self.server.pickup_config.items():
            if name.startswith(HotDeploy.UserPrefix):
                self._add_service_pickup_to_file_transfer(
                    name, config.pickup_from, False,
                    config.get('deploy_in_place', True))

        # Convert all the other pickup entries
        self._convert_pickup_to_file_transfer()

# ################################################################################################################################

    def _add_service_pickup_to_file_transfer(
        self,
        name,       # type: str
        pickup_dir, # type: str
        delete_after_pickup, # type: bool
        deploy_in_place      # type: bool
    ) -> 'None':

        # Explicitly create configuration for hot-deployment
        hot_deploy_name = '{}.{}'.format(pickup_conf_item_prefix, name)
        hot_deploy_config = self._convert_pickup_config_to_file_transfer(hot_deploy_name, {
            'is_hot_deploy': True,
            'patterns': '*.py',
            'services': 'zato.hot-deploy.create',
            'pickup_from': pickup_dir,
            'delete_after_pickup': delete_after_pickup,
            'deploy_in_place': deploy_in_place,
        })

        # Add hot-deployment to local file transfer
        self.worker_config.generic_connection[hot_deploy_name] = {'config': hot_deploy_config}

# ################################################################################################################################

    def _convert_pickup_to_file_transfer(self) -> 'None':

        # Create transfer channels based on pickup.conf
        for key, value in self.server.pickup_config.items(): # type: (str, dict)

            # Skip user-defined service pickup because it was already added in self.convert_pickup_to_file_transfer
            if key.startswith(HotDeploy.UserPrefix):
                continue

            # This is an internal name
            name = '{}.{}'.format(pickup_conf_item_prefix, key)

            # We need to convert between config formats
            config = self._convert_pickup_config_to_file_transfer(name, value)

            if not config:
                continue

            # Add pickup configuration to local file transfer
            self.worker_config.generic_connection[name] = {'config': config}

# ################################################################################################################################

    def init_generic_connections(self) -> 'None':

        # Some connection types are built elsewhere
        to_skip = {
            COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_SFTP,
        }

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
        channel_file_transfer_map = self.generic_impl_func_map.setdefault(
            COMMON_GENERIC.CONNECTION.TYPE.CHANNEL_FILE_TRANSFER, {})
        channel_hl7_mllp_map = self.generic_impl_func_map.setdefault(
            COMMON_GENERIC.CONNECTION.TYPE.CHANNEL_HL7_MLLP, {})
        cloud_confluence_map = self.generic_impl_func_map.setdefault(COMMON_GENERIC.CONNECTION.TYPE.CLOUD_CONFLUENCE, {})
        cloud_dropbox_map = self.generic_impl_func_map.setdefault(COMMON_GENERIC.CONNECTION.TYPE.CLOUD_DROPBOX, {})
        cloud_jira_map = self.generic_impl_func_map.setdefault(COMMON_GENERIC.CONNECTION.TYPE.CLOUD_JIRA, {})
        cloud_microsoft_365_map = self.generic_impl_func_map.setdefault(COMMON_GENERIC.CONNECTION.TYPE.CLOUD_MICROSOFT_365, {})
        cloud_salesforce_map = self.generic_impl_func_map.setdefault(COMMON_GENERIC.CONNECTION.TYPE.CLOUD_SALESFORCE, {})
        def_kafka_map = self.generic_impl_func_map.setdefault(COMMON_GENERIC.CONNECTION.TYPE.DEF_KAFKA, {})
        outconn_hl7_fhir_map = self.generic_impl_func_map.setdefault(COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_HL7_FHIR, {})
        outconn_hl7_mllp_map = self.generic_impl_func_map.setdefault(COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_HL7_MLLP, {})
        outconn_im_slack_map = self.generic_impl_func_map.setdefault(COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_IM_SLACK, {})
        outconn_im_telegram_map = self.generic_impl_func_map.setdefault(COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_IM_TELEGRAM, {})
        outconn_ldap_map = self.generic_impl_func_map.setdefault(COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_LDAP, {})
        outconn_mongodb_map = self.generic_impl_func_map.setdefault(COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_MONGODB, {})
        outconn_sftp_map = self.generic_impl_func_map.setdefault(COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_SFTP, {})
        outconn_wsx_map = self.generic_impl_func_map.setdefault(COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_WSX, {})

        # These generic connections are regular - they use common API methods for such connections
        regular_maps = [
            channel_file_transfer_map,
            channel_hl7_mllp_map,
            cloud_confluence_map,
            cloud_dropbox_map,
            cloud_jira_map,
            cloud_microsoft_365_map,
            cloud_salesforce_map,
            def_kafka_map,
            outconn_hl7_fhir_map,
            outconn_hl7_mllp_map,
            outconn_im_slack_map,
            outconn_im_telegram_map,
            outconn_im_telegram_map,
            outconn_ldap_map,
            outconn_mongodb_map,
            outconn_wsx_map,
        ]

        password_maps = [
            cloud_dropbox_map,
            outconn_im_slack_map,
            outconn_im_telegram_map,
            outconn_ldap_map,
            outconn_mongodb_map,
        ]

        for regular_item in regular_maps:
            regular_item[_generic_msg.create] = self._create_generic_connection
            regular_item[_generic_msg.edit]   = self._edit_generic_connection
            regular_item[_generic_msg.delete] = self._delete_generic_connection

        for password_item in password_maps:
            password_item[_generic_msg.change_password] = self._change_password_generic_connection

        # Some generic connections require different admin APIs
        outconn_sftp_map[_generic_msg.create] = self._on_outconn_sftp_create
        outconn_sftp_map[_generic_msg.edit]   = self._on_outconn_sftp_edit
        outconn_sftp_map[_generic_msg.delete] = self._on_outconn_sftp_delete

# ################################################################################################################################

    def _on_outconn_sftp_create(self, msg:'bunch_') -> 'any_':

        if not self.server.is_first_worker:
            self.server._populate_connector_config(SubprocessStartConfig(has_sftp=True))
            return

        if not self.server.subproc_current_state.is_sftp_running:
            config = SubprocessStartConfig()
            config.has_sftp = True
            self.server.init_subprocess_connectors(config)

        connector_msg = deepcopy(msg)
        self.worker_config.out_sftp[msg.name] = msg
        self.worker_config.out_sftp[msg.name].conn = SFTPIPCFacade(self.server, msg)
        return self.server.connector_sftp.invoke_connector(connector_msg)

# ################################################################################################################################

    def _on_outconn_sftp_edit(self, msg:'bunch_') -> 'any_':

        if not self.server.is_first_worker:
            self.server._populate_connector_config(SubprocessStartConfig(has_sftp=True))
            return

        connector_msg = deepcopy(msg)
        del self.worker_config.out_sftp[msg.old_name]
        return self._on_outconn_sftp_create(connector_msg)

# ################################################################################################################################

    def _on_outconn_sftp_delete(self, msg:'bunch_') -> 'any_':

        if not self.server.is_first_worker:
            self.server._populate_connector_config(SubprocessStartConfig(has_sftp=True))
            return

        connector_msg = deepcopy(msg)
        del self.worker_config.out_sftp[msg.name]
        return self.server.connector_sftp.invoke_connector(connector_msg)

# ################################################################################################################################

    def _on_outconn_sftp_change_password(self, msg:'bunch_') -> 'None':
        raise NotImplementedError('No password for SFTP connections can be set')

# ################################################################################################################################

    def _get_generic_impl_func(self, msg:'bunch_', *args:'any_', **kwargs:'any_') -> 'any_':
        """ Returns a function/method to invoke depending on which generic connection type is given on input.
        Required because some connection types (e.g. SFTP) are not managed via GenericConnection objects,
        for instance, in the case of SFTP, it uses subprocesses and a different management API.
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

        # .. update security groups ..
        for security_groups_ctx in self._yield_security_groups_ctx_items(): # type: ignore
            security_groups_ctx.set_current_basic_auth(msg.id, sec_def['username'], sec_def['password'])

        # .. and update rate limiters.
        self.server.set_up_object_rate_limiting(RATE_LIMIT.OBJECT_TYPE.SEC_DEF, msg.name, 'basic_auth')

# ################################################################################################################################

    def on_broker_msg_SECURITY_BASIC_AUTH_DELETE(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Deletes an HTTP Basic Auth security definition.
        """
        # Update channels and outgoing connections ..
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.BASIC_AUTH, self._visit_wrapper_delete)

        # .. update security groups ..
        for security_groups_ctx in self._yield_security_groups_ctx_items(): # type: ignore
            security_groups_ctx.on_basic_auth_deleted(msg.id)

        # .. and update rate limiters.
        self.server.delete_object_rate_limiting(RATE_LIMIT.OBJECT_TYPE.SEC_DEF, msg.name)

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
        # Update channels and outgoing connections ..
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.APIKEY, self._visit_wrapper_edit, keys=('username', 'name'))

        # .. and update rate limiters.
        self.server.set_up_object_rate_limiting(RATE_LIMIT.OBJECT_TYPE.SEC_DEF, msg.name, 'apikey')

# ################################################################################################################################

    def on_broker_msg_SECURITY_APIKEY_DELETE(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Deletes an API key security definition.
        """
        # Update channels and outgoing connections ..
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.APIKEY, self._visit_wrapper_delete)

        # .. update security groups ..
        for security_groups_ctx in self._yield_security_groups_ctx_items(): # type: ignore
            security_groups_ctx.on_apikey_deleted(msg.id)

        # .. and update rate limiters.
        self.server.delete_object_rate_limiting(RATE_LIMIT.OBJECT_TYPE.SEC_DEF, msg.name)

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
# ################################################################################################################################

    def wait_for_aws(self, name:'str', timeout:'int'=999999) -> 'bool':
        return wait_for_dict_key_by_get_func(self.aws_get, name, timeout, interval=0.5)

    def aws_get(self, name:'str') -> 'bunch_':
        """ Returns the configuration of the AWS security definition
        of the given name.
        """
        return self.request_dispatcher.url_data.aws_get(name)

    def on_broker_msg_SECURITY_AWS_CREATE(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Creates a new AWS security definition
        """
        dispatcher.notify(broker_message.SECURITY.AWS_CREATE.value, msg)

    def on_broker_msg_SECURITY_AWS_EDIT(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Updates an existing AWS security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.AWS,
                self._visit_wrapper_edit, keys=('username', 'name'))

    def on_broker_msg_SECURITY_AWS_DELETE(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Deletes an AWS security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.AWS,
                self._visit_wrapper_delete)

    def on_broker_msg_SECURITY_AWS_CHANGE_PASSWORD(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Changes password of an AWS security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.AWS,
                self._visit_wrapper_change_password)

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

    def on_broker_msg_VAULT_CONNECTION_CREATE(self, msg:'bunch_') -> 'None':
        msg.token = self.server.decrypt(msg.token)
        self.vault_conn_api.create(msg)
        dispatcher.notify(broker_message.VAULT.CONNECTION_CREATE.value, msg)

    def on_broker_msg_VAULT_CONNECTION_EDIT(self, msg:'bunch_') -> 'None':
        msg.token = self.server.decrypt(msg.token)
        self.vault_conn_api.edit(msg)
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.VAULT,
                self._visit_wrapper_edit, keys=('username', 'name'))

    def on_broker_msg_VAULT_CONNECTION_DELETE(self, msg:'bunch_') -> 'None':
        self.vault_conn_api.delete(msg.name)
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.VAULT,
                self._visit_wrapper_delete)

# ################################################################################################################################

    def wait_for_jwt(self, name:'str', timeout:'int'=999999) -> 'bool':
        return wait_for_dict_key_by_get_func(self.jwt_get, name, timeout, interval=0.5)

    def jwt_get(self, name:'str') -> 'bunch_':
        """ Returns the configuration of the JWT security definition of the given name.
        """
        return self.request_dispatcher.url_data.jwt_get(name)

    def jwt_get_by_id(self, def_id:'int') -> 'bunch_':
        """ Same as jwt_get but returns information by definition ID.
        """
        return self.request_dispatcher.url_data.jwt_get_by_id(def_id)

    def on_broker_msg_SECURITY_JWT_CREATE(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Creates a new JWT security definition
        """
        dispatcher.notify(broker_message.SECURITY.JWT_CREATE.value, msg)

    def on_broker_msg_SECURITY_JWT_EDIT(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Updates an existing JWT security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.JWT,
                self._visit_wrapper_edit, keys=('username', 'name'))
        self.server.set_up_object_rate_limiting(RATE_LIMIT.OBJECT_TYPE.SEC_DEF, msg.name, 'jwt')

    def on_broker_msg_SECURITY_JWT_DELETE(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Deletes a JWT security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.JWT,
                self._visit_wrapper_delete)
        self.server.delete_object_rate_limiting(RATE_LIMIT.OBJECT_TYPE.SEC_DEF, msg.name)

    def on_broker_msg_SECURITY_JWT_CHANGE_PASSWORD(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Changes password of a JWT security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.JWT,
                self._visit_wrapper_change_password)

# ################################################################################################################################

    def get_channel_file_transfer_config(self, name:'str') -> 'stranydict':
        return self.generic_conn_api[COMMON_GENERIC.CONNECTION.TYPE.CHANNEL_FILE_TRANSFER][name]

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

    def _update_tls_outconns(self, material_type_id:'str', update_key:'str', msg:'bunch_') -> 'None':

        for config_dict, config_data in self.get_outconn_http_config_dicts():

            # Here, config_data is a string such as _zato_id_633 that points to an actual outconn name
            if isinstance(config_data, str):
                config_data = config_dict[config_data]

            if config_data.config[material_type_id] == msg.id:
                config_data.conn.config[update_key] = msg.full_path
                config_data.conn.https_adapter.clear_pool()

# ################################################################################################################################

    def _add_tls_from_msg(self, config_attr:'str', msg:'bunch_', msg_key:'str') -> 'None':
        config = getattr(self.worker_config, config_attr)
        config[msg.name] = Bunch(config=Bunch(value=msg[msg_key]))

    def update_tls_ca_cert(self, msg:'bunch_') -> 'None':
        msg.full_path = get_tls_ca_cert_full_path(self.server.tls_dir, get_tls_from_payload(msg.value))

    def update_tls_key_cert(self, msg:'bunch_') -> 'None':
        decrypted = self.server.decrypt(msg.auth_data)
        msg.full_path = get_tls_key_cert_full_path(self.server.tls_dir, get_tls_from_payload(decrypted, True))

# ################################################################################################################################

    def on_broker_msg_SECURITY_TLS_CHANNEL_SEC_CREATE(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Creates a new security definition basing on TLS client certificates.
        """
        # Parse it to be on the safe side
        list(parse_tls_channel_security_definition(msg.value))

        dispatcher.notify(broker_message.SECURITY.TLS_CHANNEL_SEC_CREATE.value, msg)

    def on_broker_msg_SECURITY_TLS_CHANNEL_SEC_EDIT(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Updates an existing security definition basing on TLS client certificates.
        """
        # Parse it to be on the safe side
        list(parse_tls_channel_security_definition(msg.value))

        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.TLS_CHANNEL_SEC,
                self._visit_wrapper_edit, keys=('name', 'value'))

    def on_broker_msg_SECURITY_TLS_CHANNEL_SEC_DELETE(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Deletes a security definition basing on TLS client certificates.
        """
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.TLS_CHANNEL_SEC, self._visit_wrapper_delete)

# ################################################################################################################################

    def on_broker_msg_SECURITY_TLS_KEY_CERT_CREATE(self, msg:'bunch_') -> 'None':
        self.update_tls_key_cert(msg)
        self._add_tls_from_msg('tls_key_cert', msg, 'auth_data')
        decrypted = self.server.decrypt(msg.auth_data)
        store_tls(self.server.tls_dir, decrypted, True)
        dispatcher.notify(broker_message.SECURITY.TLS_KEY_CERT_CREATE.value, msg)

    def on_broker_msg_SECURITY_TLS_KEY_CERT_EDIT(self, msg:'bunch_') -> 'None':
        self.update_tls_key_cert(msg)
        del self.worker_config.tls_key_cert[msg.old_name]
        self._add_tls_from_msg('tls_key_cert', msg, 'auth_data')
        decrypted = self.server.decrypt(msg.auth_data)
        store_tls(self.server.tls_dir, decrypted, True)
        self._update_tls_outconns('security_id', 'tls_key_cert_full_path', msg)
        dispatcher.notify(broker_message.SECURITY.TLS_KEY_CERT_EDIT.value, msg)

    def on_broker_msg_SECURITY_TLS_KEY_CERT_DELETE(self, msg:'bunch_') -> 'None':
        self.update_tls_key_cert(msg)
        dispatcher.notify(broker_message.SECURITY.TLS_KEY_CERT_DELETE.value, msg)

# ################################################################################################################################

    def on_broker_msg_SECURITY_TLS_CA_CERT_CREATE(self, msg:'bunch_') -> 'None':
        self.update_tls_ca_cert(msg)
        self._add_tls_from_msg('tls_ca_cert', msg, 'value')
        store_tls(self.server.tls_dir, msg.value)
        dispatcher.notify(broker_message.SECURITY.TLS_CA_CERT_CREATE.value, msg)

    def on_broker_msg_SECURITY_TLS_CA_CERT_EDIT(self, msg:'bunch_') -> 'None':
        self.update_tls_ca_cert(msg)
        del self.worker_config.tls_ca_cert[msg.old_name]
        self._add_tls_from_msg('tls_ca_cert', msg, 'value')
        store_tls(self.server.tls_dir, msg.value)
        self._update_tls_outconns('sec_tls_ca_cert_id', 'tls_verify', msg)
        dispatcher.notify(broker_message.SECURITY.TLS_CA_CERT_EDIT.value, msg)

    def on_broker_msg_SECURITY_TLS_CA_CERT_DELETE(self, msg:'bunch_') -> 'None':
        self.update_tls_ca_cert(msg)
        dispatcher.notify(broker_message.SECURITY.TLS_CA_CERT_DELETE.value, msg)

# ################################################################################################################################

    def wait_for_wss(self, name:'str', timeout:'int'=999999) -> 'bool':
        return wait_for_dict_key_by_get_func(self.wss_get, name, timeout, interval=0.5)

    def wss_get(self, name:'str') -> 'bunch_':
        """ Returns the configuration of the WSS definition of the given name.
        """
        self.request_dispatcher.url_data.wss_get(name)

    def on_broker_msg_SECURITY_WSS_CREATE(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Creates a new WS-Security definition.
        """
        dispatcher.notify(broker_message.SECURITY.WSS_CREATE.value, msg)

    def on_broker_msg_SECURITY_WSS_EDIT(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Updates an existing WS-Security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.WSS,
                self._visit_wrapper_edit, keys=('is_active', 'username', 'name',
                    'nonce_freshness_time', 'reject_expiry_limit', 'password_type',
                    'reject_empty_nonce_creat', 'reject_stale_tokens'))

    def on_broker_msg_SECURITY_WSS_DELETE(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Deletes a WS-Security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.WSS,
                self._visit_wrapper_delete)

    def on_broker_msg_SECURITY_WSS_CHANGE_PASSWORD(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Changes the password of a WS-Security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.WSS,
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

        if 'wsx' in msg:
            wsgi_environ['zato.wsx'] = msg['wsx']

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

            self.broker_client.invoke_async(cb_msg)

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

        # If statistics are disabled, all their related services will not be available
        # so if they are invoked via scheduler, they should be ignored. Ultimately,
        # the scheduler should not invoke them at all.
        if msg.name.startswith('zato.stats'):
            if not self.server.component_enabled.stats:
                return

        return self.on_message_invoke_service(msg, CHANNEL.SCHEDULER, 'SCHEDULER_JOB_EXECUTED', args)

# ################################################################################################################################

    def on_broker_msg_SCHEDULER_SET_SCHEDULER_ADDRESS(self, msg:'bunch_', args:'any_'=None) -> 'any_':
        self.invoke('zato.scheduler.set-scheduler-address-impl', msg)

# ################################################################################################################################

    def on_broker_msg_CHANNEL_ZMQ_MESSAGE_RECEIVED(self, msg:'bunch_', args:'any_'=None) -> 'any_':
        return self.on_message_invoke_service(msg, CHANNEL.ZMQ, 'CHANNEL_ZMQ_MESSAGE_RECEIVED', args)

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
            self.logger.warn('SQL connection not found -> `%s` (change-password)', msg['name'])

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
        return self._get_channel_rest(CONNECTION.CHANNEL, name)

# ################################################################################################################################

    def get_outconn_rest(self, name:'str') -> 'dictnone':
        self.wait_for_outconn_rest(name)
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
        self._visit_wrapper_change_password(item['conn'], {'password': password_decrypted}, check_name=False)

# ################################################################################################################################

    def on_broker_msg_SERVICE_DELETE(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Deletes the service from the service store and removes it from the filesystem
        if it's not an internal one.
        """
        # Delete the service from RBAC resources
        self.rbac.delete_resource(msg.id)

        # Where to delete it from in the second step
        deployment_info = self.server.service_store.get_deployment_info(msg.impl_name)

        # If the service is not deployed, there is nothing for us to do here
        if not deployment_info:
            return

        fs_location = deployment_info['fs_location']

        # Delete it from the service store
        self.server.service_store.delete_service_data(msg.name)

        # Remove rate limiting configuration
        self.server.delete_object_rate_limiting(RATE_LIMIT.OBJECT_TYPE.SERVICE, msg.name)

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
        response = self.on_broker_msg_hot_deploy(
            msg, 'zato.hot-deploy.create', {'package_id': msg.package_id}, 'CREATE_SERVICE', *args,
            serialize=False, needs_response=True)

        # If there were any services deployed, let pub/sub know that this service has been just deployed -
        # pub/sub will go through all of its topics and reconfigure any of its hooks that this service implements.
        services_deployed = response.get('zato_hot_deploy_create_response', '{}').get('services_deployed')
        if services_deployed:
            self.pubsub.on_broker_msg_HOT_DEPLOY_CREATE_SERVICE(services_deployed)

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

        # Update RBAC configuration
        self.rbac.create_resource(msg.service_id)

        # Redeploy services that depended on the service just deployed.
        # Uses .get below because the feature is new in 3.1 which is why it is optional.
        if self.server.fs_server_config.hot_deploy.get('redeploy_on_parent_change', True):
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

    def on_broker_msg_CLOUD_AWS_S3_CREATE_EDIT(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Creates or updates an AWS S3 connection.
        """
        S3Wrapper = None
        msg.password = self.server.decrypt(msg.password)

        self._update_aws_config(msg)
        self._on_broker_msg_cloud_create_edit(msg, 'AWS S3', self.worker_config.cloud_aws_s3, S3Wrapper)

    def on_broker_msg_CLOUD_AWS_S3_DELETE(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Closes and deletes an AWS S3 connection.
        """
        self._delete_config_close_wrapper(msg['name'], self.worker_config.cloud_aws_s3, 'AWS S3', logger.debug)

# ################################################################################################################################

    def on_broker_msg_OUTGOING_ODOO_CREATE(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Creates or updates an Odoo connection.
        """
        self._on_broker_msg_cloud_create_edit(msg, 'Odoo', self.worker_config.out_odoo, OdooWrapper)

    on_broker_msg_OUTGOING_ODOO_CHANGE_PASSWORD = on_broker_msg_OUTGOING_ODOO_EDIT = on_broker_msg_OUTGOING_ODOO_CREATE

    def on_broker_msg_OUTGOING_ODOO_DELETE(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Closes and deletes an Odoo connection.
        """
        self._delete_config_close_wrapper(msg['name'], self.worker_config.out_odoo, 'Odoo', logger.debug)

# ################################################################################################################################

    def on_broker_msg_OUTGOING_SAP_CREATE(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Creates or updates an SAP RFC connection.
        """
        self._on_broker_msg_cloud_create_edit(msg, 'SAP', self.worker_config.out_sap, SAPWrapper)

    on_broker_msg_OUTGOING_SAP_CHANGE_PASSWORD = on_broker_msg_OUTGOING_SAP_EDIT = on_broker_msg_OUTGOING_SAP_CREATE

    def on_broker_msg_OUTGOING_SAP_DELETE(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Closes and deletes an SAP RFC connection.
        """
        self._delete_config_close_wrapper(msg['name'], self.worker_config.out_sap, 'SAP', logger.debug)

# ################################################################################################################################

    def on_broker_msg_NOTIF_RUN_NOTIFIER(self, msg:'bunch_') -> 'None':
        self.on_message_invoke_service(loads(msg.request), CHANNEL.NOTIFIER_RUN, 'NOTIF_RUN_NOTIFIER')

# ################################################################################################################################

    def _on_broker_msg_NOTIF_SQL_CREATE_EDIT(self, msg:'bunch_', source_service_type:'str') -> 'None':
        msg.source_service_type = source_service_type
        self.create_edit_notifier(msg, 'NOTIF_SQL', self.server.worker_store.worker_config.notif_sql)

    def on_broker_msg_NOTIF_SQL_CREATE(self, msg:'bunch_') -> 'None':
        self._on_broker_msg_NOTIF_SQL_CREATE_EDIT(msg, 'create')

    def on_broker_msg_NOTIF_SQL_EDIT(self, msg:'bunch_') -> 'None':
        self._on_broker_msg_NOTIF_SQL_CREATE_EDIT(msg, 'edit')

    def on_broker_msg_NOTIF_SQL_DELETE(self, msg:'bunch_') -> 'None':
        del self.server.worker_store.worker_config.notif_sql[msg.name]

# ################################################################################################################################

    def update_cassandra_conn(self, msg:'bunch_') -> 'None':
        for name in 'tls_ca_certs', 'tls_client_cert', 'tls_client_priv_key':
            value = msg.get(name)
            if value:
                value = os.path.join(self.server.repo_location, 'tls', value)
                msg[name] = value

    def on_broker_msg_DEFINITION_CASSANDRA_CREATE(self, msg:'bunch_') -> 'None':
        self.cassandra_api.create_def(msg.name, msg)
        self.update_cassandra_conn(msg)

    def on_broker_msg_DEFINITION_CASSANDRA_EDIT(self, msg:'bunch_') -> 'None':
        # It might be a rename
        dispatcher.notify(broker_message.DEFINITION.CASSANDRA_EDIT.value, msg)
        old_name = msg.get('old_name')
        del_name = old_name if old_name else msg['name']
        self.update_cassandra_conn(msg)
        new_def = self.cassandra_api.edit_def(del_name, msg)
        self.cassandra_query_store.update_by_def(del_name, new_def)

    def on_broker_msg_DEFINITION_CASSANDRA_DELETE(self, msg:'bunch_') -> 'None':
        dispatcher.notify(broker_message.DEFINITION.CASSANDRA_DELETE.value, msg)
        self.cassandra_api.delete_def(msg.name)

    def on_broker_msg_DEFINITION_CASSANDRA_CHANGE_PASSWORD(self, msg:'bunch_') -> 'None':
        dispatcher.notify(broker_message.DEFINITION.CASSANDRA_CHANGE_PASSWORD.value, msg)
        self.cassandra_api.change_password_def(msg)

# ################################################################################################################################

    def on_broker_msg_QUERY_CASSANDRA_CREATE(self, msg:'bunch_') -> 'None':
        self.cassandra_query_api.create(msg.name, msg, def_=self.cassandra_api[msg.def_name])

    def on_broker_msg_QUERY_CASSANDRA_EDIT(self, msg:'bunch_') -> 'None':
        # It might be a rename
        old_name = msg.get('old_name')
        del_name = old_name if old_name else msg['name']
        self.cassandra_query_api.edit(del_name, msg, def_=self.cassandra_api[msg.def_name])

    def on_broker_msg_QUERY_CASSANDRA_DELETE(self, msg:'bunch_') -> 'None':
        self.cassandra_query_api.delete(msg.name)

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

    def on_broker_msg_SEARCH_SOLR_CREATE(self, msg:'bunch_') -> 'None':
        self._update_queue_build_cap(msg)
        self.search_solr_api.create(msg.name, msg)

    def on_broker_msg_SEARCH_SOLR_EDIT(self, msg:'bunch_') -> 'None':
        # It might be a rename
        old_name = msg.get('old_name')
        del_name = old_name if old_name else msg['name']
        self._update_queue_build_cap(msg)
        self.search_solr_api.edit(del_name, msg)

    def on_broker_msg_SEARCH_SOLR_DELETE(self, msg:'bunch_') -> 'None':
        self.search_solr_api.delete(msg.name)

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

    def on_broker_msg_RBAC_PERMISSION_CREATE(self, msg:'bunch_') -> 'None':
        self.rbac.create_permission(msg.id, msg.name)

    def on_broker_msg_RBAC_PERMISSION_EDIT(self, msg:'bunch_') -> 'None':
        self.rbac.edit_permission(msg.id, msg.name)

    def on_broker_msg_RBAC_PERMISSION_DELETE(self, msg:'bunch_') -> 'None':
        self.rbac.delete_permission(msg.id)

# ################################################################################################################################

    def on_broker_msg_RBAC_ROLE_CREATE(self, msg:'bunch_') -> 'None':
        self.rbac.create_role(msg.id, msg.name, msg.parent_id)

    def on_broker_msg_RBAC_ROLE_EDIT(self, msg:'bunch_') -> 'None':
        self.rbac.edit_role(msg.id, msg.old_name, msg.name, msg.parent_id)

    def on_broker_msg_RBAC_ROLE_DELETE(self, msg:'bunch_') -> 'None':
        self.rbac.delete_role(msg.id, msg.name)

# ################################################################################################################################

    def on_broker_msg_RBAC_CLIENT_ROLE_CREATE(self, msg:'bunch_') -> 'None':
        self.rbac.create_client_role(msg.client_def, msg.role_id)

    def on_broker_msg_RBAC_CLIENT_ROLE_DELETE(self, msg:'bunch_') -> 'None':
        self.rbac.delete_client_role(msg.client_def, msg.role_id)

# ################################################################################################################################

    def on_broker_msg_RBAC_ROLE_PERMISSION_CREATE(self, msg:'bunch_') -> 'None':
        self.rbac.create_role_permission_allow(msg.role_id, msg.perm_id, msg.service_id)

    def on_broker_msg_RBAC_ROLE_PERMISSION_DELETE(self, msg:'bunch_') -> 'None':
        self.rbac.delete_role_permission_allow(msg.role_id, msg.perm_id, msg.service_id)

# ################################################################################################################################

    def zmq_channel_create_edit(
        self,
        name,   # type: str
        msg,    # type: Bunch
        action, # type: str
        lock_timeout, # type: int
        start   # type: bool
    ) -> 'None':
        with self.server.zato_lock_manager(msg.config_cid, ttl=10, block=lock_timeout):
            self._set_up_zmq_channel(name, msg, action, start)

# ################################################################################################################################

    def zmq_channel_create(self, msg:'bunch_') -> 'None':
        self.zmq_channel_create_edit(msg.name, msg, 'create', 0, True)

# ################################################################################################################################

    def on_broker_msg_CHANNEL_ZMQ_CREATE(self, msg:'bunch_') -> 'None':
        if self.server.zato_lock_manager.acquire(msg.config_cid, ttl=10, block=False):
            start_connectors(self, 'zato.channel.zmq.start', msg)

# ################################################################################################################################

    def on_broker_msg_CHANNEL_ZMQ_EDIT(self, msg:'bunch_') -> 'None':

        # Each worker uses a unique bind port
        msg = bunchify(msg)
        update_bind_port(msg, self.worker_idx)

        self.zmq_channel_create_edit(msg.old_name, msg, 'edit', 5, False)

# ################################################################################################################################

    def on_broker_msg_CHANNEL_ZMQ_DELETE(self, msg:'bunch_') -> 'None':
        with self.server.zato_lock_manager(msg.config_cid, ttl=10, block=5):
            api = self.zmq_mdp_v01_api if msg.socket_type.startswith(ZMQ.MDP) else self.zmq_channel_api
            if msg.name in api.connectors:
                api.delete(msg.name)

# ################################################################################################################################

    def on_broker_msg_OUTGOING_ZMQ_CREATE(self, msg:'bunch_') -> 'None':
        self.zmq_out_api.create(msg.name, msg)

    def on_broker_msg_OUTGOING_ZMQ_EDIT(self, msg:'bunch_') -> 'None':
        # It might be a rename
        old_name = msg.get('old_name')
        del_name = old_name if old_name else msg['name']
        self.zmq_out_api.edit(del_name, msg)

    def on_broker_msg_OUTGOING_ZMQ_DELETE(self, msg:'bunch_') -> 'None':
        self.zmq_out_api.delete(msg.name)

# ################################################################################################################################

    def on_ipc_message(
        self,
        msg, # type: any_
        success=IPC.STATUS.SUCCESS, # type: str
        failure=IPC.STATUS.FAILURE  # type: str
    ) -> 'None':

        # If there is target_pid we cannot continue if we are not the recipient.
        if msg.target_pid and msg.target_pid != self.server.pid:
            return

        # By default, assume we will not succeed.
        status = failure
        response = 'default-ipc-response'

        # We get here if there is no target_pid or if there is one and it matched that of ours.
        try:
            response = self.invoke(
                msg.service,
                msg.payload,
                skip_response_elem=True,
                channel=CHANNEL.IPC,
                data_format=DATA_FORMAT.JSON,
                serialize=True,
            )
            response = response.getvalue() if isinstance(response, SimpleIOPayload) else response
            status = success
        except Exception:
            response = format_exc()
            status = failure
        finally:
            data = '{};{}'.format(status, response)

        try:
            with open(msg.reply_to_fifo, 'wb') as fifo:
                _ = fifo.write(data if isinstance(data, bytes) else data.encode('utf'))
        except Exception:
            logger.warning('Could not write to FIFO, m:`%s`, r:`%s`, s:`%s`, e:`%s`', msg, response, status, format_exc())

# ################################################################################################################################
