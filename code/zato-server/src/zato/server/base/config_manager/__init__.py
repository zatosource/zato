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
from threading import RLock
from traceback import format_exc

# Bunch
from zato.common.ext.bunch import bunchify

# gevent
from gevent import sleep

# orjson
from orjson import dumps

# Zato
from zato.common.ext.bunch import Bunch
from zato.common import broker_message
from zato.common.api import API_Key, AS4 as COMMON_AS4, CHANNEL, CONNECTION, DATA_FORMAT, GENERIC as COMMON_GENERIC, \
     HTTP_SOAP, PubSub, SEC_DEF_TYPE, simple_types, URL_TYPE, Wrapper_Name_Prefix_List, ZATO_ODB_POOL_NAME
from zato.common.audit_log.api import AuditEvent, AuditOutcome, AuditSource
from zato.common.broker_message import code_to_name, GENERIC as BROKER_MSG_GENERIC, SERVICE
from zato.common.const import SECRETS
from zato.common.dispatch import dispatcher
from zato.common.facade import _service_name_to_topic, _service_sub_key_prefix
from zato.common.json_internal import loads
from zato.common.odb.api import PoolStore, SessionWrapper
from zato.common.typing_ import cast_
from zato.common.pubsub.sql.backend import PublishResult
from zato.common.util.api import asbool, fs_safe_name, import_module_from_path, new_cid_server, new_msg_id, parse_datetime, \
    update_apikey_username_to_channel, utcnow, visit_py_source, wait_for_dict_key, wait_for_dict_key_by_get_func
from zato.common.util.retry import get_remaining_time, get_sleep_time
from zato.server.base.config_manager.common import ConfigManagerImpl
from zato.server.connection.amqp_ import ConnectorAMQP
from zato.server.connection.as4 import AS4Wrapper
from zato.server.connection.cache import CacheAPI
from zato.server.connection.connector import ConnectorStore, Connector_Type
from zato.server.connection.email import IMAPAPI, IMAPConnStore, SMTPAPI, SMTPConnStore
from zato.server.connection.ftp import FTPStore
from zato.server.connection.http_soap.channel import RequestDispatcher, RequestHandler
from zato.server.connection.http_soap.outgoing import HTTPSOAPWrapper
from zato.server.connection.http_soap.response_cache import purge_channel as purge_response_cache
from zato.server.connection.http_soap.url_data import URLData
from zato.server.connection.odoo import OdooWrapper
from zato.server.generic.api.channel_openapi import ChannelOpenAPIWrapper
from zato.server.generic.api.cloud_aws import CloudAWSWrapper
from zato.server.generic.api.cloud_confluence import CloudConfluenceWrapper
from zato.server.generic.api.cloud_jira import CloudJiraWrapper
from zato.server.generic.api.cloud_microsoft_365 import CloudMicrosoft365Wrapper
from zato.server.generic.api.cloud_microsoft_fabric import CloudMicrosoftFabricWrapper
from zato.server.generic.api.cloud_microsoft_power_automate import CloudMicrosoftPowerAutomateWrapper
from zato.server.generic.api.cloud_salesforce import CloudSalesforceWrapper
from zato.server.generic.api.gateway_mcp import GatewayMCPWrapper
from zato.server.generic.api.channel_hl7_mllp import ChannelHL7MLLPWrapper
from zato.server.generic.api.channel_ibm_mq import ChannelIBMMQWrapper
from zato.server.generic.api.channel_kafka import ChannelKafkaWrapper
from zato.server.generic.api.outconn_as2 import OutconnAS2Wrapper
from zato.server.generic.api.outconn_es import OutconnESWrapper
from zato.server.generic.api.outconn_graphql import OutconnGraphQLWrapper
from zato.server.generic.api.outconn_hl7_fhir import OutconnHL7FHIRWrapper
from zato.server.generic.api.outconn_hl7_mllp import OutconnHL7MLLPWrapper
from zato.server.generic.api.outconn_ibm_mq import OutconnIBMMQWrapper
from zato.server.generic.api.outconn_kafka import OutconnKafkaWrapper
from zato.server.generic.api.outconn_ldap import OutconnLDAPWrapper
from zato.server.generic.api.outconn_llm import OutconnLLMWrapper
from zato.server.generic.api.outconn_mongodb import OutconnMongoDBWrapper
from zato.server.generic.api.outconn_odata import OutconnODataWrapper
from zato.server.generic.api.outconn_sftp import OutconnSFTPWrapper
from zato.server.generic.api.outconn_smb import OutconnSMBWrapper

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.ext.bunch import Bunch as bunch_
    from kombu.transport.pyamqp import Message as KombuMessage
    from zato.common.config_dispatcher import ConfigDispatcher
    from zato.common.typing_ import any_, anylist, anytuple, callable_, dictnone, strdict, tupnone
    from zato.server.base.parallel import ParallelServer
    from zato.server.config import ConfigDict, ConfigStore
    from zato.server.service import Service
    from zato.server.store import BaseAPI
    ConfigStore    = ConfigStore
    ParallelServer = ParallelServer
    Service        = Service

# ################################################################################################################################
# ################################################################################################################################

_data_format_dict = DATA_FORMAT.DICT
_needs_details = asbool(os.environ.get('Zato_Needs_Details'))

# ################################################################################################################################
# ################################################################################################################################

_pubsub_max_retry_time = 20 # PubSub.Max_Retry_Time

# The service that AMQP channels dispatch to while they are referenced by an AMQP-backed topic
_pubsub_amqp_bridge_service = 'zato.pubsub.topic.on-amqp-message'

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
                if isclass(item) and issubclass(item, ConfigManagerImpl) and item is not ConfigManagerImpl:
                    out.append(item)

    return tuple(out) # type: ignore

# ################################################################################################################################
# ################################################################################################################################

_base_type = '_ConfigManagerBase'

# Dynamically adds as base classes everything found in current directory that subclasses ConfigManagerImpl
_ConfigManagerBase = type(_base_type, _get_base_classes(), {})

class ConfigManager(_ConfigManagerBase):
    """ Dispatches work between different pieces of configuration of an individual server.
    """
    config_dispatcher: 'ConfigDispatcher | None' = None

    # Assigned in init() - the declaration exists so that a config reload can check
    # whether a previous instance needs to be unregistered from the dispatcher.
    request_dispatcher: 'RequestDispatcher | None' = None

    def __init__(self, config_store:'ConfigStore', server:'ParallelServer') -> 'None':
        self.logger = logging.getLogger(self.__class__.__name__)
        self.is_ready = False
        self.config_store = config_store
        self.server = server
        self.update_lock = RLock()

        # To expedite look-ups
        self._simple_types = simple_types

        # Generic connections - Channel - OpenAPI
        self.channel_openapi = {}

        # Generic connections - Cloud - AWS
        self.cloud_aws = {}

        # Generic connections - Cloud - Confluence
        self.cloud_confluence = {}

        # Generic connections - Cloud - Dropbox
        self.cloud_dropbox = {}

        # Generic connections - Cloud - Jira
        self.cloud_jira = {}

        # Generic connections - Cloud - Microsoft 365
        self.cloud_microsoft_365 = {}

        # Generic connections - Cloud - Microsoft Fabric
        self.cloud_microsoft_fabric = {}

        # Generic connections - Cloud - Microsoft Power Automate
        self.cloud_microsoft_power_automate = {}

        # Generic connections - Cloud - Salesforce
        self.cloud_salesforce = {}

        # Generic connections - Gateway - MCP
        self.gateway_mcp = {}

        # Generic connections - AS2 outconns
        self.outconn_as2 = {}

        # Generic connections - GraphQL outconns
        self.outconn_graphql = {}

        # Generic connections - HL7 MLLP channels
        self.channel_hl7_mllp = {}

        # Generic connections - HL7 FHIR outconns
        self.outconn_hl7_fhir = {}

        # Generic connections - HL7 MLLP outconns
        self.outconn_hl7_mllp = {}

        # Generic connections - IBM MQ channels
        self.channel_ibm_mq = {}

        # Generic connections - IBM MQ outconns
        self.outconn_ibm_mq = {}

        # Generic connections - Kafka channels
        self.channel_kafka = {}

        # Generic connections - Kafka outconns
        self.outconn_kafka = {}

        # Generic connections - Elasticsearch outconns
        self.outconn_es = {}

        # Generic connections - LDAP outconns
        self.outconn_ldap = {}

        # Generic connections - LLM outconns
        self.outconn_llm = {}

        # Generic connections - MongoDB outconns
        self.outconn_mongodb = {}

        # Generic connections - OData outconns
        self.outconn_odata = {}

        # Generic connections - SAP outconns, running on the OData implementation
        self.outconn_sap = {}

        # Generic connections - SFTP outconns
        self.outconn_sftp = {}

        # Generic connections - SMB outconns
        self.outconn_smb = {}

        # Pub/sub push subscriptions keyed by sub_key -> list of sub config dicts
        self._push_subs = {} # type: dict[str, list]

        # Pub/sub topic backends keyed by topic_name -> backend config dict.
        # Only AMQP-backed topics have entries here, absence means the built-in backend.
        self._topic_backends = {} # type: dict[str, dict]

        # Cache of service names that have already had their topic auto-created
        self._service_topic_cache = set() # type: set[str]

        # Lock to serialize service-topic setup/teardown
        self._service_topic_lock = RLock()

        # Pub/sub topic manager for topic-level lookups
        from zato.common.pubsub.topic_manager import TopicManager
        session = server.odb.session()
        self.pubsub_topic_manager = TopicManager(session, server.cluster_id)

# ################################################################################################################################

    def init(self) -> 'None':

        # E-mail
        self.email_smtp_api = SMTPAPI(SMTPConnStore())
        self.email_imap_api = IMAPAPI(IMAPConnStore(self.server.name))

        # AMQP
        self.amqp_api = ConnectorStore(Connector_Type.duplex.amqp, ConnectorAMQP, self.server)
        self.amqp_out_name_to_def = {} # Maps outgoing connection names to definition names, i.e. to connector names

        # Caches
        self.cache_api = self._build_cache_api()

        # Maps generic connection types to their API handler objects
        self.generic_conn_api = {
            COMMON_GENERIC.CONNECTION.TYPE.CHANNEL_OPENAPI: self.channel_openapi,
            COMMON_GENERIC.CONNECTION.TYPE.CLOUD_AWS: self.cloud_aws,
            COMMON_GENERIC.CONNECTION.TYPE.CLOUD_CONFLUENCE: self.cloud_confluence,
            COMMON_GENERIC.CONNECTION.TYPE.CLOUD_JIRA: self.cloud_jira,
            COMMON_GENERIC.CONNECTION.TYPE.CLOUD_MICROSOFT_365: self.cloud_microsoft_365,
            COMMON_GENERIC.CONNECTION.TYPE.CLOUD_MICROSOFT_FABRIC: self.cloud_microsoft_fabric,
            COMMON_GENERIC.CONNECTION.TYPE.CLOUD_MICROSOFT_POWER_AUTOMATE: self.cloud_microsoft_power_automate,
            COMMON_GENERIC.CONNECTION.TYPE.CLOUD_SALESFORCE: self.cloud_salesforce,
            COMMON_GENERIC.CONNECTION.TYPE.GATEWAY_MCP: self.gateway_mcp,
            COMMON_GENERIC.CONNECTION.TYPE.CHANNEL_HL7_MLLP: self.channel_hl7_mllp,
            COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_AS2: self.outconn_as2,
            COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_ES: self.outconn_es,
            COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_GRAPHQL: self.outconn_graphql,
            COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_HL7_FHIR: self.outconn_hl7_fhir,
            COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_HL7_MLLP: self.outconn_hl7_mllp,
            COMMON_GENERIC.CONNECTION.TYPE.CHANNEL_IBM_MQ: self.channel_ibm_mq,
            COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_IBM_MQ: self.outconn_ibm_mq,
            COMMON_GENERIC.CONNECTION.TYPE.CHANNEL_KAFKA: self.channel_kafka,
            COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_KAFKA: self.outconn_kafka,
            COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_LDAP: self.outconn_ldap,
            COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_LLM: self.outconn_llm,
            COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_MONGODB: self.outconn_mongodb,
            COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_ODATA: self.outconn_odata,
            COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_SAP: self.outconn_sap,
            COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_SFTP: self.outconn_sftp,
            COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_SMB: self.outconn_smb,
        }

        self._generic_conn_handler = {
            COMMON_GENERIC.CONNECTION.TYPE.CHANNEL_OPENAPI: ChannelOpenAPIWrapper,
            COMMON_GENERIC.CONNECTION.TYPE.CLOUD_AWS: CloudAWSWrapper,
            COMMON_GENERIC.CONNECTION.TYPE.CLOUD_CONFLUENCE: CloudConfluenceWrapper,
            COMMON_GENERIC.CONNECTION.TYPE.CLOUD_JIRA: CloudJiraWrapper,
            COMMON_GENERIC.CONNECTION.TYPE.CLOUD_MICROSOFT_365: CloudMicrosoft365Wrapper,
            COMMON_GENERIC.CONNECTION.TYPE.CLOUD_MICROSOFT_FABRIC: CloudMicrosoftFabricWrapper,
            COMMON_GENERIC.CONNECTION.TYPE.CLOUD_MICROSOFT_POWER_AUTOMATE: CloudMicrosoftPowerAutomateWrapper,
            COMMON_GENERIC.CONNECTION.TYPE.CLOUD_SALESFORCE: CloudSalesforceWrapper,
            COMMON_GENERIC.CONNECTION.TYPE.GATEWAY_MCP: GatewayMCPWrapper,
            COMMON_GENERIC.CONNECTION.TYPE.CHANNEL_HL7_MLLP: ChannelHL7MLLPWrapper,
            COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_AS2: OutconnAS2Wrapper,
            COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_ES: OutconnESWrapper,
            COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_GRAPHQL: OutconnGraphQLWrapper,
            COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_HL7_FHIR: OutconnHL7FHIRWrapper,
            COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_HL7_MLLP: OutconnHL7MLLPWrapper,
            COMMON_GENERIC.CONNECTION.TYPE.CHANNEL_IBM_MQ: ChannelIBMMQWrapper,
            COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_IBM_MQ: OutconnIBMMQWrapper,
            COMMON_GENERIC.CONNECTION.TYPE.CHANNEL_KAFKA: ChannelKafkaWrapper,
            COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_KAFKA: OutconnKafkaWrapper,
            COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_LDAP: OutconnLDAPWrapper,
            COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_LLM: OutconnLLMWrapper,
            COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_MONGODB: OutconnMongoDBWrapper,
            COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_ODATA: OutconnODataWrapper,
            COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_SAP: OutconnODataWrapper,
            COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_SFTP: OutconnSFTPWrapper,
            COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_SMB: OutconnSMBWrapper,
        }

        # Maps message actions against generic connection types and their message handlers
        self.generic_impl_func_map = {}

        # E-mail
        self.init_email_smtp()
        self.init_email_imap()

        # Odoo
        self.init_odoo()

        # API keys
        self.update_apikeys()

        # During a config reload, the previous URLData instance is still registered with the dispatcher,
        # so it needs to be unregistered first - otherwise each security event would be handled twice,
        # e.g. API key headers would be transformed to their WSGI form two times ('HTTP_HTTP_X_API_KEY').
        if self.request_dispatcher:
            dispatcher.unlisten(self.request_dispatcher.url_data.dispatcher_callback)

        request_handler = RequestHandler(self.server)
        url_data = URLData(
            self,
            self.config_store.http_soap,
            self._get_channel_url_sec(),
            self.config_store.basic_auth,
            self.config_store.mtls,
            self.config_store.ntlm,
            self.config_store.oauth,
            self.config_store.apikey,
            self.config_store.wss,
            self.config_dispatcher,
            self.server.odb,
        )

        # Request dispatcher - matches URLs, checks security and dispatches HTTP requests to services.
        self.request_dispatcher = RequestDispatcher(
            server = self.server,
            url_data = url_data,
            request_handler = request_handler,
            return_tracebacks = self.server.return_tracebacks,
            default_error_message = self.server.default_error_message,
            http_methods_allowed = self.server.http_methods_allowed
        )

        # Security groups - add details of each one to REST channels
        self._populate_channel_security_groups_info(self.config_store.http_soap)

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

    def _config_to_dict(self, config_list:'anylist', key:'str'='name') -> 'strdict':
        """ Converts a list of dictionaries produced by ConfigDict instances to a dictionary keyed with 'key' elements.
        """
        out = {}
        for elem in config_list:
            out[elem[key]] = elem
        return out

# ################################################################################################################################

    def set_config_dispatcher(self, config_dispatcher:'ConfigDispatcher') -> 'None':
        self.config_dispatcher = config_dispatcher

# ################################################################################################################################

    def after_config_dispatcher_set(self) -> 'None':

        # Pub/sub
        self.init_pubsub()

# ################################################################################################################################

    def filter(self, msg:'bunch_') -> 'bool':
        return True

# ################################################################################################################################

    def _update_queue_build_cap(self, item:'any_') -> 'None':
        item.queue_build_cap = float(self.server.fs_server_config.misc.queue_build_cap)

# ################################################################################################################################

    def _as4_wrapper_from_config(self, config:'bunch_') -> 'AS4Wrapper':
        """ Creates a new AS4 connection wrapper out of a configuration dictionary.
        The private keys stay encrypted here - the wrapper decrypts them on first use.
        """
        # The ODB columns are an integer and a boolean but a config event published
        # by an edit in the Dashboard carries the raw form values, which are strings.
        timeout = config['timeout']
        if isinstance(timeout, str):
            timeout = int(timeout)

        validate_tls = config['validate_tls']
        if isinstance(validate_tls, str):
            validate_tls = validate_tls == 'True'

        wrapper_config = {
            'id':config['id'],
            'name':config['name'],
            'is_active':config['is_active'],
            'transport':config['transport'],
            'address_host':config['host'],
            'address_url_path':config['url_path'],
            'timeout':timeout,
            'validate_tls':validate_tls,
        }

        for name in COMMON_AS4.Common_Fields + COMMON_AS4.Outgoing_Fields:
            wrapper_config[name] = config[name]

        out = AS4Wrapper(self.server, wrapper_config)
        return out

# ################################################################################################################################

    def _http_soap_wrapper_from_config(self, config:'bunch_', *, has_sec_config:'bool'=True) -> 'any_':
        """ Creates a new HTTP/SOAP connection wrapper out of a configuration dictionary.
        """

        # AS4 connections have their own wrapper class - everything they need
        # is in their own configuration fields, not in security definitions.
        if config['transport'] == URL_TYPE.AS4:
            out = self._as4_wrapper_from_config(config)
            return out

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

            # API key definitions keep a placeholder username in the ODB while the actual
            # header name is an opaque attribute of the definition, so it is resolved here.
            if sec_config['sec_type'] == SEC_DEF_TYPE.APIKEY:
                apikey_config = self.request_dispatcher.url_data.apikey_get(security_name).config
                sec_config['orig_username'] = apikey_config['orig_header']

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
            'is_internal':config.is_internal,
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
            'validate_tls':config.validate_tls,

            # Whether this connection's traffic goes to the audit log - it arrives as an opaque attribute
            'is_audit_log_active':config.get('is_audit_log_active'),

            # SOAP-specific and mutual-TLS details - they arrive as opaque attributes
            # and are absent from connections created before these fields existed.
            'use_ws_addressing':config.get('use_ws_addressing'),
            'use_mtom':config.get('use_mtom'),
            'body_credentials':config.get('body_credentials'),
            'tls_client_cert':config.get('tls_client_cert'),
            'tls_client_key':config.get('tls_client_key'),
            'wsa_action':config.get('wsa_action'),
            'wsa_to':config.get('wsa_to'),
            'wsa_reply_to':config.get('wsa_reply_to'),
        }

        # The declarative invocation profile - these also arrive as opaque attributes
        # and are absent from connections that never set them.
        for field_name in HTTP_SOAP.Invocation.FieldList:
            wrapper_config[field_name] = config.get(field_name)

        wrapper_config.update(sec_config)

        # A WS-Security definition carries its whole mode-specific configuration - the wrapper
        # passes it to the SOAP client, which applies it to each outgoing envelope.
        if sec_config['sec_type'] == SEC_DEF_TYPE.WSS and _sec_config:
            wrapper_config['security'] = dict(_sec_config)

        # An mTLS definition carries paths to the client certificate material - the wrapper
        # maps them to its TLS fields itself when it sets up its authentication.
        if sec_config['sec_type'] == SEC_DEF_TYPE.MTLS and security_name:
            mtls_config = self.request_dispatcher.url_data.mtls_get(security_name).config
            wrapper_config['cert_path'] = mtls_config.get('cert_path')
            wrapper_config['key_path'] = mtls_config.get('key_path')
            wrapper_config['ca_certs_path'] = mtls_config.get('ca_certs_path')

        return HTTPSOAPWrapper(self.server, wrapper_config)

# ################################################################################################################################

    def get_outconn_http_config_dicts(self) -> 'any_':

        out:'any_' = []

        for transport in('soap', 'plain_http', 'as4'):
            config_dict = getattr(self.config_store, 'out_' + transport)
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
        self.sql_pool_store[ZATO_ODB_POOL_NAME] = self.config_store.odb_data
        self.odb = SessionWrapper()
        self.odb.init_session(ZATO_ODB_POOL_NAME, self.config_store.odb_data, self.sql_pool_store[ZATO_ODB_POOL_NAME].pool)

        # Any user-defined SQL connections left?
        for pool_name in self.config_store.out_sql:
            config = self.config_store.out_sql[pool_name]['config']
            config['fs_sql_config'] = self.server.fs_sql_config
            self.sql_pool_store[pool_name] = config

    def init_ftp(self) -> 'None':
        """ Initializes FTP connections. The method replaces whatever value self.out_ftp
        previously had (initially this would be a ConfigDict of connection definitions).
        """
        config_list = self.config_store.out_ftp.get_config_list()
        self.config_store.out_ftp = FTPStore() # type: ignore
        self.config_store.out_ftp.add_params(config_list)

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

    def init_email_smtp(self) -> 'None':
        self.init_simple(self.config_store.email_smtp, self.email_smtp_api, 'an SMTP')

# ################################################################################################################################

    def init_email_imap(self) -> 'None':
        self.init_simple(self.config_store.email_imap, self.email_imap_api, 'an IMAP')

# ################################################################################################################################

    def init_amqp(self) -> 'None':
        """ Initializes all AMQP connections.
        """
        '''
        def _name_matches(def_name:'str') -> 'callable_':
            def _inner(config:'strdict') -> 'bool':
                return config['def_name']==def_name
            return _inner

        for def_name, data in self.config_store.definition_amqp.items():

            channels = self.config_store.channel_amqp.get_config_list(_name_matches(def_name))
            outconns = self.config_store.out_amqp.get_config_list(_name_matches(def_name))

            for outconn in outconns:
                self.amqp_out_name_to_def[outconn['name']] = def_name

            # Create a new AMQP connector definition ..
            config = AMQPConnectorConfig.from_dict(data.config)

            # .. AMQP definitions as such are always active. It is channels or outconns that can be inactive.
            config.is_active = True

            self.amqp_api.create(def_name, config, self.invoke,
                channels=self._config_to_dict(channels), outconns=self._config_to_dict(outconns))
        '''

        channels = self.config_store.channel_amqp.get_config_list()
        outconns = self.config_store.out_amqp.get_config_list()

        for item in channels:
            name = item['name']
            try:
                self.amqp_api.create(name, item, self.invoke, needs_start=True)
                self.amqp_api.create_channel(name, item)
            except Exception:
                logger.warning('Could not create AMQP channel `%s`, e:`%s`', name, format_exc())

        for item in outconns:
            name = item['name']
            try:
                self.amqp_api.create(name, item, self.invoke, needs_start=True)
                self.amqp_api.create_outconn(name, item)
            except Exception:
                logger.warning('Could not create AMQP outconn `%s`, e:`%s`', name, format_exc())

# ################################################################################################################################

    def init_odoo(self) -> 'None':
        names = self.config_store.out_odoo.keys()
        for name in names:
            item = config = self.config_store.out_odoo[name]
            config = item['config']
            config.queue_build_cap = float(self.server.fs_server_config.misc.queue_build_cap)
            item.conn = OdooWrapper(config, self.server)
            item.conn.build_queue()

# ################################################################################################################################

    def _build_cache_redis_conn(self) -> 'any_':
        """ Builds a Redis client out of the server's current [redis] configuration, SSL included.
        """
        from zato.common.redis_env import get_redis_conn_from_values, get_redis_values_from_section

        values = get_redis_values_from_section(self.server.fs_server_config.redis)
        out = get_redis_conn_from_values(values, decode_responses=True)

        return out

# ################################################################################################################################

    def _build_cache_api(self) -> 'CacheAPI':
        """ Creates a Redis-backed CacheAPI using the server's [redis] configuration.
        """
        redis_client = self._build_cache_redis_conn()

        out = CacheAPI(redis_client, config_manager=self)
        return out

# ################################################################################################################################

    def reconfigure_redis_cache(self) -> 'None':
        """ Rebuilds the cache's Redis client from the current [redis] configuration -
        called after the configuration was changed at runtime so self.cache
        immediately talks to the newly configured server.
        """
        self.cache_api.redis = self._build_cache_redis_conn()

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
            basic_auth_config=self.config_store.basic_auth,
            mtls_config=self.config_store.mtls,
            ntlm_config=self.config_store.ntlm,
            oauth_config=self.config_store.oauth,
            apikey_config=self.config_store.apikey,
            wss_config=self.config_store.wss,
        )

        # .. now, initialize connections that may depend on what we have just loaded ..
        self.init_http_soap(has_sec_config=False)

# ################################################################################################################################

    def update_apikeys(self) -> 'None':
        """ API keys need to be upper-cased and in the format that WSGI environment will have them in.
        """
        for config_dict in self.config_store.apikey.values():
            config_dict.config.orig_header = config_dict.config.get('header') or API_Key.Default_Header
            update_apikey_username_to_channel(config_dict.config)

# ################################################################################################################################

    def _update_auth(
        self,
        msg,           # type: Bunch
        action_name,   # type: str
        sec_type,      # type: str
        visit_wrapper, # type: callable_
        keys:'tupnone'=None
    ) -> 'None':
        """ A common method for updating auth-related configuration.
        """
        with self.update_lock:

            handler = getattr(self.request_dispatcher.url_data, 'on_config_event_' + action_name)
            handler(msg)

            for transport in ['plain_http', 'soap']:
                config_dict = getattr(self.config_store, 'out_' + transport)

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
        config_dict = getattr(self.config_store, 'out_' + wrapper.config['transport'])
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

    def _update_pubsub_security_rename(self, msg:'bunch_') -> 'None':
        """ Updates pub/sub in-memory state when a security definition's username or name changes.
        """
        old_username = msg['old_username']
        new_username = msg['username']

        if old_username != new_username:
            self.server.pubsub_subscriptions.update_username(old_username, new_username)
            self.server.pubsub_pattern_matcher.change_client_id(old_username, new_username)

        old_name = msg['old_name']
        new_name = msg['name']

        if old_name != new_name:
            self.server.pubsub_subscriptions.update_sec_name(old_name, new_name)

# ################################################################################################################################

    def init_generic_connections(self) -> 'None':

        # MCP gateways are built after services are deployed in _build_mcp_tool_registries
        to_skip = {COMMON_GENERIC.CONNECTION.TYPE.GATEWAY_MCP}

        for config_dict in self.config_store.generic_connection.values():

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
        channel_hl7_mllp_map = self.generic_impl_func_map.setdefault(COMMON_GENERIC.CONNECTION.TYPE.CHANNEL_HL7_MLLP, {})
        channel_ibm_mq_map = self.generic_impl_func_map.setdefault(COMMON_GENERIC.CONNECTION.TYPE.CHANNEL_IBM_MQ, {})
        channel_kafka_map = self.generic_impl_func_map.setdefault(COMMON_GENERIC.CONNECTION.TYPE.CHANNEL_KAFKA, {})
        channel_openapi_map = self.generic_impl_func_map.setdefault(COMMON_GENERIC.CONNECTION.TYPE.CHANNEL_OPENAPI, {})
        cloud_aws_map = self.generic_impl_func_map.setdefault(COMMON_GENERIC.CONNECTION.TYPE.CLOUD_AWS, {})
        cloud_confluence_map = self.generic_impl_func_map.setdefault(COMMON_GENERIC.CONNECTION.TYPE.CLOUD_CONFLUENCE, {})
        cloud_jira_map = self.generic_impl_func_map.setdefault(COMMON_GENERIC.CONNECTION.TYPE.CLOUD_JIRA, {})
        cloud_microsoft_365_map = self.generic_impl_func_map.setdefault(COMMON_GENERIC.CONNECTION.TYPE.CLOUD_MICROSOFT_365, {})
        cloud_microsoft_fabric_map = self.generic_impl_func_map.setdefault(
            COMMON_GENERIC.CONNECTION.TYPE.CLOUD_MICROSOFT_FABRIC, {})
        cloud_microsoft_power_automate_map = self.generic_impl_func_map.setdefault(
            COMMON_GENERIC.CONNECTION.TYPE.CLOUD_MICROSOFT_POWER_AUTOMATE, {})
        cloud_salesforce_map = self.generic_impl_func_map.setdefault(COMMON_GENERIC.CONNECTION.TYPE.CLOUD_SALESFORCE, {})
        gateway_mcp_map = self.generic_impl_func_map.setdefault(COMMON_GENERIC.CONNECTION.TYPE.GATEWAY_MCP, {})
        outconn_as2_map = self.generic_impl_func_map.setdefault(COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_AS2, {})
        outconn_es_map = self.generic_impl_func_map.setdefault(COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_ES, {})
        outconn_graphql_map = self.generic_impl_func_map.setdefault(COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_GRAPHQL, {})
        outconn_hl7_fhir_map = self.generic_impl_func_map.setdefault(COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_HL7_FHIR, {})
        outconn_hl7_mllp_map = self.generic_impl_func_map.setdefault(COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_HL7_MLLP, {})
        outconn_ibm_mq_map = self.generic_impl_func_map.setdefault(COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_IBM_MQ, {})
        outconn_kafka_map = self.generic_impl_func_map.setdefault(COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_KAFKA, {})
        outconn_ldap_map = self.generic_impl_func_map.setdefault(COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_LDAP, {})
        outconn_llm_map = self.generic_impl_func_map.setdefault(COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_LLM, {})
        outconn_mongodb_map = self.generic_impl_func_map.setdefault(COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_MONGODB, {})
        outconn_odata_map = self.generic_impl_func_map.setdefault(COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_ODATA, {})
        outconn_sap_map = self.generic_impl_func_map.setdefault(COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_SAP, {})
        outconn_sftp_map = self.generic_impl_func_map.setdefault(COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_SFTP, {})
        outconn_smb_map = self.generic_impl_func_map.setdefault(COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_SMB, {})

        # These generic connections are regular - they use common API methods for such connections
        regular_maps = [
            channel_hl7_mllp_map,
            channel_ibm_mq_map,
            channel_kafka_map,
            channel_openapi_map,
            cloud_aws_map,
            cloud_confluence_map,
            cloud_jira_map,
            cloud_microsoft_365_map,
            cloud_microsoft_fabric_map,
            cloud_microsoft_power_automate_map,
            cloud_salesforce_map,
            gateway_mcp_map,
            outconn_as2_map,
            outconn_es_map,
            outconn_graphql_map,
            outconn_hl7_fhir_map,
            outconn_hl7_mllp_map,
            outconn_ibm_mq_map,
            outconn_kafka_map,
            outconn_ldap_map,
            outconn_llm_map,
            outconn_mongodb_map,
            outconn_odata_map,
            outconn_sap_map,
            outconn_sftp_map,
            outconn_smb_map,
        ]

        password_maps = [
            cloud_aws_map,
            cloud_microsoft_fabric_map,
            cloud_microsoft_power_automate_map,
            outconn_es_map,
            outconn_hl7_fhir_map,
            outconn_ibm_mq_map,
            outconn_kafka_map,
            outconn_ldap_map,
            outconn_llm_map,
            outconn_mongodb_map,
            outconn_odata_map,
            outconn_sap_map,
            outconn_sftp_map,
            outconn_smb_map,
        ]

        for regular_item in regular_maps:
            regular_item[_generic_msg.create] = self._create_generic_connection
            regular_item[_generic_msg.edit]   = self._edit_generic_connection
            regular_item[_generic_msg.delete] = self._delete_generic_connection

        for password_item in password_maps:
            password_item[_generic_msg.change_password] = self._change_password_generic_connection

        channel_kafka_map[_generic_msg.create] = self._create_kafka_channel
        channel_kafka_map[_generic_msg.edit]   = self._edit_kafka_channel
        channel_kafka_map[_generic_msg.delete] = self._delete_kafka_channel

        outconn_kafka_map[_generic_msg.create] = self._create_kafka_outconn
        outconn_kafka_map[_generic_msg.edit]   = self._edit_kafka_outconn
        outconn_kafka_map[_generic_msg.delete] = self._delete_kafka_outconn

        channel_ibm_mq_map[_generic_msg.create] = self._create_ibm_mq_channel
        channel_ibm_mq_map[_generic_msg.edit]   = self._edit_ibm_mq_channel
        channel_ibm_mq_map[_generic_msg.delete] = self._delete_ibm_mq_channel

        outconn_ibm_mq_map[_generic_msg.create] = self._create_ibm_mq_outconn
        outconn_ibm_mq_map[_generic_msg.edit]   = self._edit_ibm_mq_outconn
        outconn_ibm_mq_map[_generic_msg.delete] = self._delete_ibm_mq_outconn


# ################################################################################################################################

    def _notify_queue_bridge_channel(self, action:'str', msg:'any_') -> 'None':
        bridge = getattr(self.server, '_queue_bridge', None)
        if not bridge:
            return
        try:
            name = msg.get('name', '')
            self.logger.info('Queue bridge channel %s: %s', action, name)
            config = dict(msg)
            self.server._enrich_queue_bridge_config(config)
            if action == 'create':
                bridge.add_channel(config)
            elif action == 'edit':
                bridge.edit_channel(config)
            elif action == 'delete':
                bridge.delete_channel(name)
        except Exception:
            self.logger.warning('Could not notify queue bridge about channel %s=%s: %s', action, msg.get('name', ''), format_exc())

    def _notify_queue_bridge_outconn(self, action:'str', msg:'any_') -> 'None':
        bridge = getattr(self.server, '_queue_bridge', None)
        if not bridge:
            return
        try:
            name = msg.get('name', '')
            self.logger.info('Queue bridge outconn %s: %s', action, name)
            config = dict(msg)
            self.server._enrich_queue_bridge_config(config)
            if action == 'create':
                bridge.add_outgoing(config)
            elif action == 'edit':
                bridge.edit_outgoing(config)
            elif action == 'delete':
                bridge.delete_outgoing(name)
        except Exception:
            self.logger.warning('Could not notify queue bridge about outconn %s=%s: %s', action, msg.get('name', ''), format_exc())

    def _create_kafka_channel(self, msg:'any_', *args:'any_', **kwargs:'any_') -> 'None':
        self._create_generic_connection(msg, *args, **kwargs)
        self._notify_queue_bridge_channel('create', msg)

    def _edit_kafka_channel(self, msg:'any_', *args:'any_', **kwargs:'any_') -> 'None':
        self._edit_generic_connection(msg, *args, **kwargs)
        self._notify_queue_bridge_channel('edit', msg)

    def _delete_kafka_channel(self, msg:'any_', *args:'any_', **kwargs:'any_') -> 'None':
        self._delete_generic_connection(msg, *args, **kwargs)
        self._notify_queue_bridge_channel('delete', msg)

    def _create_kafka_outconn(self, msg:'any_', *args:'any_', **kwargs:'any_') -> 'None':
        self._create_generic_connection(msg, *args, **kwargs)
        self._notify_queue_bridge_outconn('create', msg)

    def _edit_kafka_outconn(self, msg:'any_', *args:'any_', **kwargs:'any_') -> 'None':
        self._edit_generic_connection(msg, *args, **kwargs)
        self._notify_queue_bridge_outconn('edit', msg)

    def _delete_kafka_outconn(self, msg:'any_', *args:'any_', **kwargs:'any_') -> 'None':
        self._delete_generic_connection(msg, *args, **kwargs)
        self._notify_queue_bridge_outconn('delete', msg)

    def _create_ibm_mq_channel(self, msg:'any_', *args:'any_', **kwargs:'any_') -> 'None':
        self._create_generic_connection(msg, *args, **kwargs)
        self._notify_queue_bridge_channel('create', msg)

    def _edit_ibm_mq_channel(self, msg:'any_', *args:'any_', **kwargs:'any_') -> 'None':
        self._edit_generic_connection(msg, *args, **kwargs)
        self._notify_queue_bridge_channel('edit', msg)

    def _delete_ibm_mq_channel(self, msg:'any_', *args:'any_', **kwargs:'any_') -> 'None':
        self._delete_generic_connection(msg, *args, **kwargs)
        self._notify_queue_bridge_channel('delete', msg)

    def _create_ibm_mq_outconn(self, msg:'any_', *args:'any_', **kwargs:'any_') -> 'None':
        self._create_generic_connection(msg, *args, **kwargs)
        self._notify_queue_bridge_outconn('create', msg)

    def _edit_ibm_mq_outconn(self, msg:'any_', *args:'any_', **kwargs:'any_') -> 'None':
        self._edit_generic_connection(msg, *args, **kwargs)
        self._notify_queue_bridge_outconn('edit', msg)

    def _delete_ibm_mq_outconn(self, msg:'any_', *args:'any_', **kwargs:'any_') -> 'None':
        self._delete_generic_connection(msg, *args, **kwargs)
        self._notify_queue_bridge_outconn('delete', msg)

# ################################################################################################################################

    def _handle_pubsub_public_message(
        self,
        body:'any_',
        delivery_count:'int',
        config:'strdict'
    ) -> 'None':

        # Enrich the body with our own metadata ..
        _zato_meta = body['_zato_meta'] = {}
        _zato_meta['sub_key'] = config['queue']
        _zato_meta['delivery_count'] = delivery_count

        # .. our delivery service - it will decide how to deliver the message ..
        service = 'zato.pubsub.subscription.handle-delivery'

        # .. do invoke it now.
        _ = self.invoke(service, body)

# ################################################################################################################################

    def on_pubsub_public_message_callback(self, body:'any_', msg:'KombuMessage', sec_name:'str', config:'strdict') -> 'None':

        # Local variables
        application_headers = msg.properties['application_headers']

        # .. this will be increasing ..
        delivery_count = application_headers.get('x-delivery-count') or 0

        # .. but we count from 0 so we need to add 1 to get a human-friendly number ..
        delivery_count += 1

        # .. try to deliver our message ..
        try:

            # .. invoke the callback ..
            self._handle_pubsub_public_message(body, delivery_count, config)

            # .. if we are here, it means everything went fine so we can acknoledge the message with the broker ..
            msg.ack()

            # .. and let's return explicitly.
            return

        except Exception as e:

            # OK, we have an exception so we will potentially retry the delivery ..
            e = e

            # .. topic name is the same as the routing key for this message ..
            topic_name = msg.delivery_info['routing_key']

            # .. we can extract our consumer from its consumer tag ..
            subscriber = msg.delivery_info['consumer_tag']
            subscriber = subscriber.split('/')
            subscriber = subscriber[0]
            subscriber = subscriber.split('.')
            subscriber = subscriber[0]

            # .. this may be missing in case someone sent a message manually ..
            msg_id = application_headers.get('zato_msg_id') or 'zpsm.NotGiven'

            # .. we need to know when the message was published ..
            pub_time = application_headers.get('zato_pub_time') or ''

            # .. this may not exist if someone publishes a message directly to a queue ..
            if not pub_time:
                pub_time = utcnow()

            else:
                # .. make sure we have a timezone available ..
                if '+' not in pub_time:
                    pub_time += '+00:00'

                # .. otherwse, make use of it ..
                else:
                    pub_time = parse_datetime(pub_time)

            # .. OK, do we have any time left for retries ..
            remaining_time = get_remaining_time(pub_time, _pubsub_max_retry_time)

            # .. if yes, check for how long we should sleep ..
            sleep_time = get_sleep_time(pub_time, _pubsub_max_retry_time, delivery_count)

            has_time_left = remaining_time.total_seconds() > 0
            has_sleep_time = sleep_time > 0

            if has_time_left and has_sleep_time:

                log_msg = f'Subscriber: `{subscriber}`' + \
                          f' -> topic: `{topic_name}`' + \
                          f' -> Msg ID: `{msg_id}`' + \
                          f' -> sleeping for {sleep_time:.1f}s' + \
                          f' (attempt={delivery_count} -> remaining={remaining_time})' + \
                          f' e=`{format_exc()}`'
                logger.info(log_msg)

                # .. do sleep now ..
                sleep(sleep_time)

                # .. and then reject and enqueue the message, thus ensuring it will be redelivered ..
                msg.reject(requeue=True)

            # .. if we go here, it means we run out of time, so we need to accept that message ..
            # .. so it won't be redelivered anymore.
            else:
                log_msg = f'Subscriber: `{subscriber}` -> topic: `{topic_name}`' + \
                          f' -> Msg ID: `{msg_id}` -> Max wait time reached (attempts={delivery_count})'
                logger.info(log_msg)
                msg.ack()

# ################################################################################################################################

    def init_pubsub(self) -> 'None':
        pass

# ################################################################################################################################

    def _sync_pubsub_subscriptions(self) -> 'None':

        from contextlib import closing
        from zato.common.odb.model import HTTPSOAP, PubSubSubscription, PubSubSubscriptionTopic, PubSubTopic, SecurityBase

        _push = PubSub.Delivery_Type.Push

        logger.info('Syncing ODB subscriptions to Redis pub/sub backend')

        with closing(self.server.odb.session()) as session:

            rows = session.query(
                PubSubSubscription.sub_key,
                PubSubSubscription.delivery_type,
                PubSubSubscription.push_type,
                PubSubSubscription.push_service_name,
                PubSubSubscription.rest_push_endpoint_id,
                PubSubTopic.name,
                SecurityBase.username,
                SecurityBase.name.label('sec_name'),
            ).join(
                PubSubSubscriptionTopic, PubSubSubscriptionTopic.subscription_id == PubSubSubscription.id
            ).join(
                PubSubTopic, PubSubTopic.id == PubSubSubscriptionTopic.topic_id
            ).join(
                SecurityBase, SecurityBase.id == PubSubSubscription.sec_base_id
            ).filter(
                PubSubSubscription.cluster_id == self.server.cluster_id
            ).all()

            synced = 0
            push_subs = {} # type: dict[str, list]

            for row in rows:
                topic_name = row.name
                sub_key = row.sub_key
                self.server.pubsub_backend.subscribe(sub_key, topic_name)
                synced += 1

                if row.delivery_type == _push:
                    sub_config = {
                        'sub_key': sub_key,
                        'topic_name': topic_name,
                        'push_type': row.push_type,
                        'push_service_name': row.push_service_name,
                        'rest_push_endpoint_id': row.rest_push_endpoint_id,
                    }

                    if row.push_type == 'rest' and row.rest_push_endpoint_id:
                        endpoint = session.query(HTTPSOAP).filter(
                            HTTPSOAP.id == row.rest_push_endpoint_id
                        ).first()
                        if endpoint:
                            sub_config['rest_push_url'] = (endpoint.host or '') + endpoint.url_path

                    if sub_key not in push_subs:
                        push_subs[sub_key] = []
                    push_subs[sub_key].append(sub_config)

            self._push_subs = push_subs

        noun = 'pair' if synced == 1 else 'pairs'
        push_count = sum(len(v) for v in push_subs.values())
        logger.info('Synced %d ODB subscription-topic %s to Redis (%d push)', synced, noun, push_count)

# ################################################################################################################################

    def _sync_pubsub_topics(self) -> 'None':
        """ Loads AMQP-backed topics from ODB into the in-memory backend registry,
        applies channel overrides for topics that reference an AMQP channel
        and registers topics whose audit log was turned off.
        """
        from contextlib import closing
        from zato.common.odb.model import PubSubTopic
        from zato.common.util.sql import parse_instance_opaque_attr

        _amqp = PubSub.Backend_Type.AMQP

        with closing(self.server.odb.session()) as session:

            rows = session.query(PubSubTopic).filter(
                PubSubTopic.cluster_id == self.server.cluster_id).all()

            topic_backends = {} # type: dict[str, dict]

            for row in rows:

                opaque = parse_instance_opaque_attr(row)

                # A topic whose audit log was turned off explicitly writes no audit events
                if opaque.get('is_audit_log_active') is False:
                    self.server.pubsub_backend.set_topic_audit_flag(row.name, False)

                # Topics without opaque attributes predate backend types and are built-in,
                # and built-in topics never have registry entries.
                if 'backend_type' not in opaque:
                    continue

                if opaque['backend_type'] != _amqp:
                    continue

                topic_backends[row.name] = {
                    'backend_type': _amqp,
                    'amqp_outconn_name': opaque['amqp_outconn_name'],
                    'amqp_exchange': opaque['amqp_exchange'],
                    'amqp_routing_key': opaque['amqp_routing_key'],
                    'amqp_channel_name': opaque['amqp_channel_name'],
                    'original_service_name': '',
                }

        self._topic_backends = topic_backends

        # Each topic that points to an AMQP channel needs that channel's consumers
        # to dispatch to the bridge service instead of the channel's own service.
        for backend_config in self._topic_backends.values():
            if backend_config['amqp_channel_name']:
                self._apply_amqp_channel_override(backend_config)

        topic_count = len(self._topic_backends)
        suffix = 'topic' if topic_count == 1 else 'topics'
        logger.info('Synced %d AMQP-backed pub/sub %s to the backend registry', topic_count, suffix)

# ################################################################################################################################

    def _apply_amqp_channel_override(self, backend_config:'strdict') -> 'None':
        """ Points an AMQP channel's in-memory service at the pub/sub bridge, remembering the original
        service name so it can be restored later. The channel's database row is never touched.
        """
        channel_name = backend_config['amqp_channel_name']

        # The channel may not exist, e.g. the topic was configured before the channel was created.
        connector = self.amqp_api.connectors.get(channel_name)
        if not connector:
            logger.warning('AMQP channel `%s` not found, pub/sub bridge override not applied', channel_name)
            return

        channel_config = connector.channels[channel_name]

        # Remember the original service so it can be restored when the topic no longer uses this channel.
        backend_config['original_service_name'] = channel_config['service_name']

        # Consumers read the service name from this shared config object for each message,
        # so mutating it here takes effect immediately for all of them.
        channel_config['service_name'] = _pubsub_amqp_bridge_service

        logger.info('Applied pub/sub bridge override to AMQP channel `%s` (was `%s`)',
            channel_name, backend_config['original_service_name'])

# ################################################################################################################################

    def _remove_amqp_channel_override(self, backend_config:'strdict') -> 'None':
        """ Restores an AMQP channel's original in-memory service name after the topic
        that referenced the channel was edited or deleted.
        """
        channel_name = backend_config['amqp_channel_name']

        # The channel itself may have been deleted in the meantime.
        connector = self.amqp_api.connectors.get(channel_name)
        if not connector:
            return

        channel_config = connector.channels[channel_name]
        channel_config['service_name'] = backend_config['original_service_name']

        logger.info('Removed pub/sub bridge override from AMQP channel `%s` (restored `%s`)',
            channel_name, backend_config['original_service_name'])

# ################################################################################################################################

    def get_pubsub_topic_backend(self, topic_name:'str') -> 'dictnone':
        """ Returns the backend config for an AMQP-backed topic or None for built-in topics.
        """
        return self._topic_backends.get(topic_name)

# ################################################################################################################################

    def pubsub_publish_to_amqp(self, backend_config:'strdict', data:'any_', topic_name:'str', cid:'str') -> 'PublishResult':
        """ Publishes a message to the AMQP broker configured for a topic. Returns the same
        result shape as the built-in Redis backend so the caller-facing API is identical.
        """
        _ = self.amqp_invoke(
            backend_config['amqp_outconn_name'],
            data,
            exchange=backend_config['amqp_exchange'],
            routing_key=backend_config['amqp_routing_key'],
        )

        # The broker does not return any identifier so a new one is generated here.
        result = PublishResult()
        result.msg_id = new_msg_id()

        # The audit log stores payloads as text so free-text search covers them.
        if isinstance(data, str):
            audit_data = data
        else:
            audit_data = dumps(data).decode('utf-8')

        # The publish target, in one field, so it reads like an address.
        endpoint = '{} -> {} -> {}'.format(
            backend_config['amqp_outconn_name'],
            backend_config['amqp_exchange'],
            backend_config['amqp_routing_key'],
        )

        # Record the publish in the audit log.
        self.server.pubsub_backend.audit_log.insert(AuditSource.PubSub, AuditEvent.Published, topic_name,
            cid=cid,
            msg_id=result.msg_id,
            endpoint=endpoint,
            size=len(audit_data),
            outcome=AuditOutcome.OK,
            data=audit_data,
        )

        return result

# ################################################################################################################################

    def get_pubsub_topic_by_amqp_channel(self, channel_name:'str') -> 'str':
        """ Returns the name of the AMQP-backed topic that consumes from the given channel.
        """
        for topic_name, backend_config in self._topic_backends.items():
            if backend_config['amqp_channel_name'] == channel_name:
                return topic_name

        raise Exception('No AMQP-backed topic found for channel `{}`'.format(channel_name))

# ################################################################################################################################

    def pubsub_deliver_amqp_message(self, topic_name:'str', body:'any_', cid:'str') -> 'None':
        """ Delivers a message consumed from an AMQP channel directly to all push subscribers
        of its topic, without Redis involvement. Any delivery failure propagates to the caller
        so the AMQP message is not acked and the broker redelivers it.
        """
        from json import dumps as json_dumps
        from requests import post as requests_post

        _push_type_service = PubSub.Push_Type.Service
        _push_type_rest = PubSub.Push_Type.REST

        audit_log = self.server.pubsub_backend.audit_log

        # The audit log stores payloads as text so free-text search covers them.
        if isinstance(body, str):
            audit_data = body
        else:
            audit_data = json_dumps(body)

        for config_list in self._push_subs.values():
            for sub_config in config_list:

                # Only subscribers of this particular topic are of interest.
                if sub_config['topic_name'] != topic_name:
                    continue

                # The delivery target is either a service or a REST endpoint.
                if sub_config['push_type'] == _push_type_service:
                    endpoint = sub_config['push_service_name']
                else:
                    endpoint = sub_config['rest_push_url']

                # Deliver the message, recording the outcome in the audit log either way.
                # A failed delivery re-raises so the AMQP message is not acked and the broker redelivers it.
                try:
                    if sub_config['push_type'] == _push_type_service:
                        _ = self.server.invoke(sub_config['push_service_name'], body)

                    elif sub_config['push_type'] == _push_type_rest:

                        # Dicts are serialized to JSON, strings and bytes go out as they are.
                        if isinstance(body, (dict, list)):
                            payload = json_dumps(body)
                        else:
                            payload = body

                        response = requests_post(
                            sub_config['rest_push_url'],
                            data=payload,
                            headers={'Content-Type': 'application/json'},
                        )
                        response.raise_for_status()

                except Exception:
                    audit_log.insert(AuditSource.PubSub, AuditEvent.Delivery_Failed, topic_name,
                        cid=cid,
                        endpoint=endpoint,
                        sub_key=sub_config['sub_key'],
                        size=len(audit_data),
                        outcome=AuditOutcome.Error,
                        data=audit_data,
                    )
                    raise

                else:
                    audit_log.insert(AuditSource.PubSub, AuditEvent.Delivered, topic_name,
                        cid=cid,
                        endpoint=endpoint,
                        sub_key=sub_config['sub_key'],
                        size=len(audit_data),
                        outcome=AuditOutcome.OK,
                        data=audit_data,
                    )

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

    def get_pubsub_sub_config(self, sub_key:'str') -> 'strdict':

        # Local variables
        not_applicable = {}

        for topic_name, sub_list in self.config_store.pubsub_subs.items():
            for sub_config in sub_list:
                config_sub_key = sub_config['sub_key']
                if config_sub_key == sub_key:
                    return sub_config
                else:
                    not_applicable[config_sub_key] = topic_name
        else:
            subs = sorted(not_applicable.items())
            msg = f'No such sub_key `{sub_key}` among `{subs}`'
            raise Exception(msg)

# ################################################################################################################################

    def is_pubsub_topic_active(self, topic_name:'str') -> 'bool':
        """ Returns True if the topic exists and is active.
        """
        out = self.pubsub_topic_manager.is_topic_active(topic_name)
        return out

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

    def on_config_event_SECURITY_BASIC_AUTH_CREATE(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Creates a new HTTP Basic Auth security definition
        """
        dispatcher.notify(broker_message.SECURITY.BASIC_AUTH_CREATE.value, msg)

# ################################################################################################################################

    def on_config_event_SECURITY_BASIC_AUTH_EDIT(self, msg:'bunch_', *args:'any_') -> 'None':
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

        # .. update pub/sub in-memory state if username or sec def name changed.
        self._update_pubsub_security_rename(msg)

# ################################################################################################################################

    def on_config_event_SECURITY_BASIC_AUTH_DELETE(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Deletes an HTTP Basic Auth security definition.
        """
        # Update channels and outgoing connections ..
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.BASIC_AUTH, self._visit_wrapper_delete)

        # .. update security groups.
        for security_groups_ctx in self._yield_security_groups_ctx_items(): # type: ignore
            security_groups_ctx.on_basic_auth_deleted(msg.id)

# ################################################################################################################################

    def on_config_event_SECURITY_BASIC_AUTH_CHANGE_PASSWORD(self, msg:'bunch_', *args:'any_') -> 'None':
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

    def on_config_event_SECURITY_BASIC_AUTH_RATE_LIMITING_EDIT(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Updates rate limiting configuration for a Basic Auth security definition.
        """
        sec_def_id = msg['id']
        rule_dicts = msg['rule_dicts']
        logger.info(
            'on_config_event_SECURITY_BASIC_AUTH_RATE_LIMITING_EDIT; sec_def_id:%s (type:%s), rule_dicts:%s',
            sec_def_id, type(sec_def_id).__name__, rule_dicts)
        self.server.rate_limiting_manager.set_sec_def_config(sec_def_id, rule_dicts)

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

    def on_config_event_SECURITY_APIKEY_CREATE(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Creates a new API key security definition.
        """
        dispatcher.notify(broker_message.SECURITY.APIKEY_CREATE.value, msg)

# ################################################################################################################################

    def on_config_event_SECURITY_APIKEY_EDIT(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Updates an existing API key security definition.
        """
        # Update channels and outgoing connections ..
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.APIKEY, self._visit_wrapper_edit, keys=('username', 'name'))

        # .. the call above already updated URL data, so the definition's header is the current one ..
        sec_def = self.apikey_get_by_id(msg.id)

        # .. and now security groups can be updated with the possibly new header.
        for security_groups_ctx in self._yield_security_groups_ctx_items(): # type: ignore
            security_groups_ctx.set_current_apikey_header(msg.id, sec_def['header'])

# ################################################################################################################################

    def on_config_event_SECURITY_APIKEY_DELETE(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Deletes an API key security definition.
        """
        # Update channels and outgoing connections ..
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.APIKEY, self._visit_wrapper_delete)

        # .. update security groups.
        for security_groups_ctx in self._yield_security_groups_ctx_items(): # type: ignore
            security_groups_ctx.on_apikey_deleted(msg.id)

# ################################################################################################################################

    def on_config_event_SECURITY_APIKEY_CHANGE_PASSWORD(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Changes password of an API key security definition.
        """
        # Update channels and outgoing connections ..
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.APIKEY, self._visit_wrapper_change_password)

        # .. and update security groups.
        for security_groups_ctx in self._yield_security_groups_ctx_items(): # type: ignore
            security_groups_ctx.set_current_apikey(msg.id, msg.password)

# ################################################################################################################################

    def on_config_event_SECURITY_APIKEY_RATE_LIMITING_EDIT(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Updates rate limiting configuration for an API key security definition.
        """
        sec_def_id = msg['id']
        rule_dicts = msg['rule_dicts']
        logger.info('on_config_event_SECURITY_APIKEY_RATE_LIMITING_EDIT; sec_def_id:%s, rule_dicts:%s', sec_def_id, rule_dicts)
        self.server.rate_limiting_manager.set_sec_def_config(sec_def_id, rule_dicts)

# ################################################################################################################################

    def on_config_event_SECURITY_QUOTA_TIER_EDIT(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Re-resolves all quota tier references after a tier, a tier assignment or a group membership changed.
        """
        logger.info('on_config_event_SECURITY_QUOTA_TIER_EDIT; id:%s', msg['id'])
        self.server.quota_tiers_manager.install_tier_assignments()

# ################################################################################################################################

    def wait_for_ntlm(self, name:'str', timeout:'int'=999999) -> 'bool':
        return wait_for_dict_key_by_get_func(self.ntlm_get, name, timeout, interval=0.5)

    def ntlm_get(self, name:'str') -> 'bunch_':
        """ Returns the configuration of the NTLM security definition
        of the given name.
        """
        return self.request_dispatcher.url_data.ntlm_get(name)

    def on_config_event_SECURITY_NTLM_CREATE(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Creates a new NTLM security definition
        """
        dispatcher.notify(broker_message.SECURITY.NTLM_CREATE.value, msg)

    def on_config_event_SECURITY_NTLM_EDIT(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Updates an existing NTLM security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.NTLM,
                self._visit_wrapper_edit, keys=('username', 'name'))

    def on_config_event_SECURITY_NTLM_DELETE(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Deletes an NTLM security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.NTLM,
                self._visit_wrapper_delete)

    def on_config_event_SECURITY_NTLM_CHANGE_PASSWORD(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Changes password of an NTLM security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.NTLM,
                self._visit_wrapper_change_password)

# ################################################################################################################################

    def wait_for_mtls(self, name:'str', timeout:'int'=999999) -> 'bool':
        return wait_for_dict_key_by_get_func(self.mtls_get, name, timeout, interval=0.5)

    def mtls_get(self, name:'str') -> 'bunch_':
        """ Returns the configuration of the mTLS security definition
        of the given name.
        """
        return self.request_dispatcher.url_data.mtls_get(name)

    def mtls_get_by_id(self, def_id:'int') -> 'bunch_':
        """ Same as mtls_get but by definition ID.
        """
        return self.request_dispatcher.url_data.mtls_get_by_id(def_id)

    def on_config_event_SECURITY_MTLS_CREATE(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Creates a new mTLS security definition.
        """
        dispatcher.notify(broker_message.SECURITY.MTLS_CREATE.value, msg)

    def on_config_event_SECURITY_MTLS_EDIT(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Updates an existing mTLS security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.MTLS,
                self._visit_wrapper_edit, keys=('name', 'cert_path', 'key_path', 'ca_certs_path'))

    def on_config_event_SECURITY_MTLS_DELETE(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Deletes an mTLS security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.MTLS,
                self._visit_wrapper_delete)

# ################################################################################################################################

    def wait_for_wss(self, name:'str', timeout:'int'=999999) -> 'bool':
        return wait_for_dict_key_by_get_func(self.wss_get, name, timeout, interval=0.5)

    def wss_get(self, name:'str') -> 'bunch_':
        """ Returns the configuration of the WS-Security definition
        of the given name.
        """
        return self.request_dispatcher.url_data.wss_get(name)

    def wss_get_by_id(self, def_id:'int') -> 'bunch_':
        """ Same as wss_get but by definition ID.
        """
        return self.request_dispatcher.url_data.wss_get_by_id(def_id)

    def on_config_event_SECURITY_WSS_CREATE(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Creates a new WS-Security definition.
        """
        dispatcher.notify(broker_message.SECURITY.WSS_CREATE.value, msg)

    def on_config_event_SECURITY_WSS_EDIT(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Updates an existing WS-Security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.WSS,
                self._visit_wrapper_edit, keys=('username', 'name'))

    def on_config_event_SECURITY_WSS_DELETE(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Deletes a WS-Security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.WSS,
                self._visit_wrapper_delete)

    def on_config_event_SECURITY_WSS_CHANGE_PASSWORD(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Changes password of a WS-Security definition.
        """
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.WSS,
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

    def on_config_event_SECURITY_OAUTH_CREATE(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Creates a new OAuth security definition
        """
        dispatcher.notify(broker_message.SECURITY.OAUTH_CREATE.value, msg)

    def on_config_event_SECURITY_OAUTH_EDIT(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Updates an existing OAuth security definition.
        """
        # Update channels and outgoing connections ..
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.OAUTH,
                self._visit_wrapper_edit, keys=('username', 'name'))

        # .. extract the newest information  ..
        sec_def = self.oauth_get_by_id(msg.id)

        # .. and update security groups.
        for security_groups_ctx in self._yield_security_groups_ctx_items(): # type: ignore
            security_groups_ctx.set_current_bearer_token(msg.id, sec_def)

    def on_config_event_SECURITY_OAUTH_DELETE(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Deletes an OAuth security definition.
        """
        # Update channels and outgoing connections ..
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.OAUTH,
                self._visit_wrapper_delete)

        # .. and update security groups.
        for security_groups_ctx in self._yield_security_groups_ctx_items(): # type: ignore
            security_groups_ctx.on_bearer_token_deleted(msg.id)

    def on_config_event_SECURITY_OAUTH_CHANGE_PASSWORD(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Changes password of an OAuth security definition.
        """
        # Update channels and outgoing connections ..
        self._update_auth(msg, code_to_name[msg.action], SEC_DEF_TYPE.OAUTH,
                self._visit_wrapper_change_password)

        # .. extract the newest information  ..
        if msg.id:
            sec_def = self.oauth_get_by_id(msg.id)

            # .. and update security groups.
            for security_groups_ctx in self._yield_security_groups_ctx_items(): # type: ignore
                security_groups_ctx.set_current_bearer_token(msg.id, sec_def)

# ################################################################################################################################

    def invoke(self, service:'str', payload:'any_', **kwargs:'any_') -> 'any_':
        """ Invokes a service by its name with request on input.
        """
        channel = kwargs.get('channel', CHANNEL.INVOKE)

        if 'serialize' in kwargs:
            serialize = kwargs.get('serialize')
        else:
            serialize = True

        return self.on_message_invoke_service({
            'channel': channel,
            'payload': payload,
            'data_format': kwargs.get('data_format'),
            'service': service,
            'cid': new_cid_server(),
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
            wsgi_environ['zato.zato_ctx'] = zato_ctx

        # Extra WSGI environ keys given by the caller, e.g. queue bridge message headers
        extra_environ = msg.get('wsgi_environ')
        if extra_environ:
            wsgi_environ.update(extra_environ)

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
            channel, data_format, transport, self.server, self.config_dispatcher, self, cid,
            job_type=msg.get('job_type'), wsgi_environ=wsgi_environ,
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
            cb_msg['cid'] = new_cid_server()
            cb_msg['channel'] = CHANNEL.INVOKE_ASYNC_CALLBACK
            cb_msg['data_format'] = data_format
            cb_msg['transport'] = transport
            cb_msg['is_async'] = True
            cb_msg['in_reply_to'] = cid

            self.config_dispatcher.invoke_async(cb_msg) # type: ignore

        if kwargs.get('needs_response'):
            if skip_response_elem:
                return response
            else:
                if isinstance(response, dict):
                    return response

                response = service.response.payload

                if hasattr(response, 'getvalue'):
                    response = response.getvalue()

                return response

# ################################################################################################################################

    def on_config_event_SCHEDULER_JOB_EXECUTED(self, msg:'bunch_', args:'any_'=None) -> 'any_':
        return self.on_message_invoke_service(msg, CHANNEL.SCHEDULER, 'SCHEDULER_JOB_EXECUTED', args)

# ################################################################################################################################

    def on_config_event_OUTGOING_SQL_CREATE_EDIT(self, msg:'bunch_', *args:'any_') -> 'None':
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

    def on_config_event_OUTGOING_SQL_CHANGE_PASSWORD(self, msg:'bunch_', *args:'any_') -> 'None':
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

    def on_config_event_OUTGOING_SQL_DELETE(self, msg:'bunch_', *args:'any_') -> 'None':
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
            for outconn_value in self.config_store.out_plain_http.values():
                if isinstance(outconn_value, dict):
                    config = outconn_value['config'] # type: dict
                    if config[item_key] == value:
                        return outconn_value

# ################################################################################################################################

    def wait_for_outconn_rest(self, name:'str', timeout:'int'=999999) -> 'bool':
        return wait_for_dict_key(self.config_store.out_plain_http, name, timeout, interval=0.5)

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

    def on_config_event_CHANNEL_HTTP_SOAP_CREATE_EDIT(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Creates or updates an HTTP/SOAP channel.
        """
        channel_id = msg['id']
        gateway_service_list = msg.get('gateway_service_list') or ''
        allowed = set(line.strip() for line in gateway_service_list.splitlines() if line.strip())

        with self.server.gateway_services_allowed_lock:
            self.server.gateway_services_allowed[channel_id] = allowed

        self.request_dispatcher.url_data.on_config_event_CHANNEL_HTTP_SOAP_CREATE_EDIT(msg, *args)

        # A config change must not leave stale cached responses behind
        purge_response_cache(self.cache_api, channel_id)

        # The channel change may alter the OpenAPI document, so it is rebuilt now
        from zato.server.openapi_console.cache import rebuild_spec_cache
        rebuild_spec_cache(self.server)

    def on_config_event_CHANNEL_HTTP_SOAP_RATE_LIMITING_EDIT(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Updates rate limiting configuration for an HTTP/SOAP channel.
        """
        channel_id = msg['id']
        rule_dicts = msg['rule_dicts']
        logger.info('on_config_event_CHANNEL_HTTP_SOAP_RATE_LIMITING_EDIT; channel_id:%s, rule_dicts:%s', channel_id, rule_dicts)
        self.server.rate_limiting_manager.set_channel_config(channel_id, rule_dicts)

    def on_config_event_CHANNEL_HTTP_SOAP_RESPONSE_CACHE_EDIT(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Updates response caching configuration for an HTTP/SOAP channel.
        """
        channel_id = msg['id']
        config = msg['response_cache']
        logger.info('on_config_event_CHANNEL_HTTP_SOAP_RESPONSE_CACHE_EDIT; channel_id:%s, config:%s', channel_id, config)

        # Update the in-memory channel item so the change applies without a restart ..
        item = self._get_channel_rest(CONNECTION.CHANNEL, channel_id, by_name=False)

        if item:
            item['response_cache'] = config

            # .. dropping the memoized parsed form along the way ..
            _ = item.pop('response_cache_parsed', None)

        # .. and purge the channel's entries so stale responses cannot outlive the config change.
        purge_response_cache(self.cache_api, channel_id)

    def on_config_event_CHANNEL_HTTP_SOAP_DELETE(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Deletes an HTTP/SOAP channel.
        """
        item = self.get_channel_rest(msg.name) or {}
        channel_id = item['id']
        with self.server.gateway_services_allowed_lock:
            _ = self.server.gateway_services_allowed.pop(channel_id, None)

        # Delete the channel object now
        self.request_dispatcher.url_data.on_config_event_CHANNEL_HTTP_SOAP_DELETE(msg, *args)

        # A deleted channel leaves no cached responses behind
        purge_response_cache(self.cache_api, channel_id)

        # The channel is gone, so the OpenAPI document is rebuilt without it now
        from zato.server.openapi_console.cache import rebuild_spec_cache
        rebuild_spec_cache(self.server)

# ################################################################################################################################

    def _delete_config_close_wrapper(
        self,
        name,        # type: str
        config_dict:'ConfigDict',
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
        config_dict = getattr(self.config_store, 'out_' + transport)

        self._delete_config_close_wrapper(name, config_dict, 'an outgoing HTTP/SOAP connection', log_func)

    def on_config_event_OUTGOING_HTTP_SOAP_CREATE_EDIT(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Creates or updates an outgoing HTTP/SOAP connection.
        """
        # It might be a rename
        old_name = msg.get('old_name')
        del_name = old_name if old_name else msg['name']

        # .. delete the connection if it exists ..
        self._delete_config_close_wrapper_http_soap(del_name, msg['transport'], logger.debug)

        # .. and create a new one
        wrapper = self._http_soap_wrapper_from_config(msg, has_sec_config=False)
        config_dict = getattr(self.config_store, 'out_' + msg['transport'])
        config_dict[msg['name']] = Bunch()
        config_dict[msg['name']].config = msg
        config_dict[msg['name']].conn = wrapper
        config_dict[msg['name']].ping = wrapper.ping # (just like in self.init_http)

        # Store mapping of ID -> name
        config_dict.set_key_id_data(msg)

    def on_config_event_OUTGOING_HTTP_SOAP_DELETE(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Deletes an outgoing HTTP/SOAP connection (actually delegates the
        task to self._delete_config_close_wrapper_http_soap.
        """
        self._delete_config_close_wrapper_http_soap(msg['name'], msg['transport'], logger.error)

# ################################################################################################################################

    def on_config_event_OUTGOING_REST_WRAPPER_CHANGE_PASSWORD(self, msg:'bunch_', *args:'any_') -> 'None':

        # Reusable
        password = msg.password
        password_decrypted = self.server.decrypt(password)

        # All outgoing REST connections
        out_plain_http = self.config_store.out_plain_http

        # .. get the one that we need ..
        item = out_plain_http.get_by_id(msg.id)

        # .. update its dict configuration ..
        item['config']['password'] = password

        # .. and its wrapper's configuration too.
        self._visit_wrapper_change_password(item['conn'], {'password': password_decrypted}, check_name=False) # type: ignore

# ################################################################################################################################

    def on_config_event_SERVICE_DELETE(self, msg:'bunch_', *args:'any_') -> 'None':
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

# ################################################################################################################################

    def on_config_event_SERVICE_EDIT(self, msg:'bunch_', *args:'any_') -> 'None':
        del msg['action']
        self.server.service_store.edit_service_data(msg)

# ################################################################################################################################

    def on_config_event_SERVICE_INVOKE(self, msg:'bunch_', *args:'any_') -> 'strdict | None':
        try:
            response = self.on_message_invoke_service(msg, CHANNEL.PUBLISH, 'SERVICE_INVOKE', args, needs_response=True)
        except Exception as e:
            exc = format_exc()
            logger.warning(exc)
            return {'error': str(e)}
        else:
            return response

# ################################################################################################################################

    def on_config_event_OUTGOING_FTP_CREATE_EDIT(self, msg:'bunch_', *args:'any_') -> 'None':
        out_ftp = cast_('FTPStore', self.config_store.out_ftp)
        out_ftp.create_edit(msg, msg.get('old_name'))

    def on_config_event_OUTGOING_FTP_DELETE(self, msg:'bunch_', *args:'any_') -> 'None':
        out_ftp = cast_('FTPStore', self.config_store.out_ftp)
        out_ftp.delete(msg.name)

    def on_config_event_OUTGOING_FTP_CHANGE_PASSWORD(self, msg:'bunch_', *args:'any_') -> 'None':
        out_ftp = cast_('FTPStore', self.config_store.out_ftp)
        out_ftp.change_password(msg.name, msg.password)

# ################################################################################################################################

    def on_config_event_hot_deploy(
        self,
        msg,     # type: Bunch
        service, # type: str
        payload, # type: any_
        action,  # type: str
        *args,   # type: any_
        **kwargs # type: any_
    ) -> 'any_':
        msg.cid = new_cid_server()
        msg.service = service
        msg.payload = payload

        from zato.server.metrics import zato_server_config_last_reload_timestamp_seconds, \
            zato_server_config_reloads_total

        try:
            result = self.on_message_invoke_service(msg, 'hot-deploy', 'HOT_DEPLOY_{}'.format(action), args, **kwargs)
        except Exception:
            _ = zato_server_config_reloads_total.labels(result='failure').inc()
            raise
        else:
            _ = zato_server_config_reloads_total.labels(result='success').inc()

            import time as time_mod
            _ = zato_server_config_last_reload_timestamp_seconds.set(time_mod.time())

            return result

# ################################################################################################################################

    def on_config_event_HOT_DEPLOY_CREATE_SERVICE(self, msg:'bunch_', *args:'any_') -> 'None':

        # Uploads the service
        _ = self.on_config_event_hot_deploy(
            msg, 'zato.hot-deploy.create', {'payload_name': msg.payload_name, 'payload':msg.payload}, 'CREATE_SERVICE', *args,
            serialize=False, needs_response=True)


# ################################################################################################################################

    def on_config_event_HOT_DEPLOY_UPDATE_ENMASSE(self, msg:'bunch_', *args:'any_') -> 'None':

        # Uploads the service
        _ = self.server.invoke('zato.pickup.update-enmasse', msg)

# ################################################################################################################################

    def on_config_event_HOT_DEPLOY_CREATE_STATIC(self, msg:'bunch_', *args:'any_') -> 'None':
        return self.on_config_event_hot_deploy(msg, 'zato.pickup.on-update-static', {
            'data': msg.data,
            'file_name': msg.file_name,
            'full_path': msg.full_path,
            'relative_dir': msg.get('relative_dir'),
        }, 'CREATE_STATIC', *args)

# ################################################################################################################################

    def on_config_event_HOT_DEPLOY_CREATE_USER_CONF(self, msg:'bunch_', *args:'any_') -> 'None':
        return self.on_config_event_hot_deploy(msg, 'zato.pickup.on-update-user-conf', {
            'data': msg.data,
            'file_name': msg.file_name,
            'full_path': msg.full_path,
            'relative_dir': msg.get('relative_dir'),
        }, 'CREATE_USER_CONF', *args)

# ################################################################################################################################

    def on_config_event_HOT_DEPLOY_AFTER_DEPLOY(self, msg:'bunch_', *args:'any_') -> 'None':

        # Redeploy services that depended on the service just deployed.
        if self.server.fs_server_config.hot_deploy.redeploy_on_parent_change:
            self.server.service_store.redeploy_on_parent_changed(msg.service_name, msg.service_impl_name)

# ################################################################################################################################

    def on_config_event_SERVICE_PUBLISH(self, msg:'bunch_', args:'any_'=None) -> 'None':
        return self.on_message_invoke_service(msg, msg.get('channel') or CHANNEL.INVOKE_ASYNC, 'SERVICE_PUBLISH', args)

# ################################################################################################################################

    def _on_config_event_cloud_create_edit(
        self,
        msg,          # type: Bunch
        conn_type,    # type: str
        config_dict:'ConfigDict',
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

    def on_config_event_OUTGOING_ODOO_CREATE(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Creates or updates an Odoo connection.
        """
        _ = self._on_config_event_cloud_create_edit(msg, 'Odoo', self.config_store.out_odoo, OdooWrapper)

    on_config_event_OUTGOING_ODOO_CHANGE_PASSWORD = on_config_event_OUTGOING_ODOO_EDIT = on_config_event_OUTGOING_ODOO_CREATE

    def on_config_event_OUTGOING_ODOO_DELETE(self, msg:'bunch_', *args:'any_') -> 'None':
        """ Closes and deletes an Odoo connection.
        """
        self._delete_config_close_wrapper(msg['name'], self.config_store.out_odoo, 'Odoo', logger.debug)

# ################################################################################################################################

    def on_config_event_EMAIL_SMTP_CREATE(self, msg:'bunch_') -> 'None':
        self.email_smtp_api.create(msg.name, msg)

    def on_config_event_EMAIL_SMTP_EDIT(self, msg:'bunch_') -> 'None':
        # It might be a rename
        old_name = msg.get('old_name')
        del_name = old_name if old_name else msg['name']
        msg.password = self.email_smtp_api.get(del_name, True).config.password
        self.email_smtp_api.edit(del_name, msg)

    def on_config_event_EMAIL_SMTP_DELETE(self, msg:'bunch_') -> 'None':
        self.email_smtp_api.delete(msg.name)

    def on_config_event_EMAIL_SMTP_CHANGE_PASSWORD(self, msg:'bunch_') -> 'None':
        self.email_smtp_api.change_password(msg)

# ################################################################################################################################

    def on_config_event_EMAIL_IMAP_CREATE(self, msg:'bunch_') -> 'None':
        self.email_imap_api.create(msg.name, msg)

    def on_config_event_EMAIL_IMAP_EDIT(self, msg:'bunch_') -> 'None':
        # It might be a rename
        old_name = msg.get('old_name')
        del_name = old_name if old_name else msg['name']
        msg.password = self.email_imap_api.get(del_name, True).config.password
        self.email_imap_api.edit(del_name, msg)

    def on_config_event_EMAIL_IMAP_DELETE(self, msg:'bunch_') -> 'None':
        self.email_imap_api.delete(msg.name)

    def on_config_event_EMAIL_IMAP_CHANGE_PASSWORD(self, msg:'bunch_') -> 'None':
        self.email_imap_api.change_password(msg)

# ################################################################################################################################

    def on_config_event_PUBSUB_SUBSCRIPTION_CREATE(self, msg:'bunch_') -> 'None':

        sub_key = msg.sub_key
        sec_name = msg.sec_name
        username = msg.username
        delivery_type = msg.delivery_type

        self.server.pubsub_subscriptions.register_user(username, sec_name, sub_key)

        for topic_item in msg.topic_name_list:
            topic_name = topic_item['topic_name'] if isinstance(topic_item, dict) else topic_item.topic_name
            self._add_pubsub_sub_config(sub_key, topic_name, delivery_type, msg)

            # .. set up the Redis consumer group so the subscriber can immediately
            # .. receive messages published after this point.
            self.server.pubsub_backend.subscribe(sub_key, topic_name)

        # .. and if this is a push subscription, its delivery greenlet needs to run
        # .. from the moment the subscription exists, without waiting for an edit or a restart.
        if delivery_type == PubSub.Delivery_Type.Push:
            self._setup_push_delivery(sub_key, msg)

    def on_config_event_PUBSUB_SUBSCRIPTION_EDIT(self, msg:'bunch_') -> 'None':

        sub_key = msg.sub_key
        delivery_type = msg.delivery_type

        # Collect old topic names before we remove them from memory ..
        old_topic_names:'list[str]' = []

        for topic_name, sub_list in self.config_store.pubsub_subs.items():
            for item in sub_list:
                if item['sub_key'] == sub_key:
                    old_topic_names.append(topic_name)

        # .. unsubscribe from old topics in Redis (GAP 12) ..
        for topic_name in old_topic_names:
            self.server.pubsub_backend.unsubscribe(sub_key, topic_name)

        # .. remove old in-memory configs ..
        self._remove_pubsub_sub_configs_by_sub_key(sub_key)

        # .. add new in-memory configs and subscribe in Redis (GAP 13) ..
        for topic_item in msg.topic_name_list:
            topic_name = topic_item['topic_name'] if isinstance(topic_item, dict) else topic_item.topic_name
            self._add_pubsub_sub_config(sub_key, topic_name, delivery_type, msg)
            self.server.pubsub_backend.subscribe(sub_key, topic_name)

        # .. stop the old delivery greenlet (GAP 15) ..
        self.server.pubsub_push_delivery.stop_sub_key(sub_key)

        # .. remove old push delivery config (GAP 14) ..
        _ = self._push_subs.pop(sub_key, None)

        # .. if the new delivery type is push, rebuild _push_subs and start the greenlet (GAP 14 + 15).
        if delivery_type == PubSub.Delivery_Type.Push:
            self._setup_push_delivery(sub_key, msg)

# ################################################################################################################################

    def _setup_push_delivery(self, sub_key:'str', msg:'bunch_') -> 'None':
        """ Fills in _push_subs for a push subscription and starts its delivery greenlet.
        """
        push_type = getattr(msg, 'push_type', None)
        push_service_name = getattr(msg, 'push_service_name', None)
        rest_push_endpoint_id = getattr(msg, 'rest_push_endpoint_id', None)

        # .. resolve the REST endpoint URL from ODB if needed ..
        rest_push_url = ''

        if push_type == PubSub.Push_Type.REST:
            if rest_push_endpoint_id:
                from contextlib import closing as closing_
                from zato.common.odb.model import HTTPSOAP
                with closing_(self.server.odb.session()) as session:
                    endpoint = session.query(HTTPSOAP).filter(
                        HTTPSOAP.id == rest_push_endpoint_id
                    ).first()
                    if endpoint:
                        host = endpoint.host or ''
                        rest_push_url = host + endpoint.url_path

        self._push_subs[sub_key] = []

        for topic_item in msg.topic_name_list:
            topic_name = topic_item['topic_name'] if isinstance(topic_item, dict) else topic_item.topic_name
            sub_config = {
                'sub_key': sub_key,
                'topic_name': topic_name,
                'push_type': push_type,
                'push_service_name': push_service_name,
                'rest_push_endpoint_id': rest_push_endpoint_id,
                'rest_push_url': rest_push_url,
            }
            self._push_subs[sub_key].append(sub_config)

        self.server.pubsub_push_delivery.start_sub_key(sub_key)

    def cleanup_subscription(self, sub_key:'str', username:'str') -> 'None':
        """ Cleans up all in-memory and Redis state for a single subscription.
        """
        # .. collect topic names this sub_key belongs to before we remove them from memory ..
        topic_names = [
            topic_name for topic_name, sub_list in self.config_store.pubsub_subs.items()
            if any(item['sub_key'] == sub_key for item in sub_list)
        ]

        # .. clean up Redis state for each topic ..
        for topic_name in topic_names:
            self.server.pubsub_backend.unsubscribe(sub_key, topic_name)

        # .. remove in-memory subscription configs ..
        self._remove_pubsub_sub_configs_by_sub_key(sub_key)

        # .. remove user from the subscriptions store ..
        self.server.pubsub_subscriptions.remove_user(username)

        # .. remove push delivery config ..
        _ = self._push_subs.pop(sub_key, None)

        # .. stop the delivery greenlet for this sub_key ..
        self.server.pubsub_push_delivery.stop_sub_key(sub_key)

# ################################################################################################################################

    def cleanup_security_pubsub(self, session:'any_', sec_base_id:'int', username:'str') -> 'None':
        """ Cleans up all pub/sub state for subscriptions and permissions tied to a security definition.
        Called before the security definition is cascade-deleted from ODB.
        """
        from zato.common.odb.query import pubsub_subscriptions_by_sec_base

        # .. find all subscriptions for this security definition ..
        subscriptions = pubsub_subscriptions_by_sec_base(session, sec_base_id, self.server.cluster_id)

        # .. clean up each subscription's in-memory and Redis state ..
        for sub in subscriptions:
            self.cleanup_subscription(sub.sub_key, username)

        # .. remove the client from the pattern matcher ..
        self.server.pubsub_pattern_matcher.remove_client(username)

# ################################################################################################################################

    def cleanup_rest_endpoint_pubsub(self, session:'any_', rest_endpoint_id:'int') -> 'None':
        """ Cleans up all pub/sub state for subscriptions whose push endpoint is the given HTTPSOAP connection.
        Called before the HTTPSOAP row is cascade-deleted from ODB.
        """
        from zato.common.odb.model import SecurityBase
        from zato.common.odb.query import pubsub_subscriptions_by_rest_endpoint

        # .. find all subscriptions pointing at this REST endpoint ..
        subscriptions = pubsub_subscriptions_by_rest_endpoint(session, rest_endpoint_id, self.server.cluster_id)

        # .. clean up each subscription's in-memory and Redis state ..
        for sub in subscriptions:

            # .. look up the username from the subscription's security definition ..
            sec_def = session.query(SecurityBase).\
                filter(SecurityBase.id == sub.sec_base_id).\
                one()

            self.cleanup_subscription(sub.sub_key, sec_def.username)

# ################################################################################################################################

    def on_config_event_PUBSUB_SUBSCRIPTION_DELETE(self, msg:'bunch_') -> 'None':
        self.cleanup_subscription(msg.sub_key, msg.username)

# ################################################################################################################################

    def on_config_event_PUBSUB_TOPIC_CREATE(self, msg:'bunch_') -> 'None':

        # Every new topic announces its audit log state ..
        self.server.pubsub_backend.set_topic_audit_flag(msg.topic_name, msg.is_audit_log_active)

        # .. and AMQP-backed topics additionally get a registry entry
        # .. along with the channel override if one is needed.
        if msg.backend_type == PubSub.Backend_Type.AMQP:

            backend_config = {
                'backend_type': msg.backend_type,
                'amqp_outconn_name': msg.amqp_outconn_name,
                'amqp_exchange': msg.amqp_exchange,
                'amqp_routing_key': msg.amqp_routing_key,
                'amqp_channel_name': msg.amqp_channel_name,
                'original_service_name': '',
            }
            self._topic_backends[msg.topic_name] = backend_config

            if backend_config['amqp_channel_name']:
                self._apply_amqp_channel_override(backend_config)

# ################################################################################################################################

    def on_config_event_PUBSUB_TOPIC_EDIT(self, msg:'bunch_') -> 'None':

        old_name = msg.old_topic_name
        new_name = msg.new_topic_name
        is_active = getattr(msg, 'is_active', None)

        # Re-register the audit log state under the topic's current name,
        # which also covers renames since the old name is forgotten first.
        self.server.pubsub_backend.delete_topic_audit_flag(old_name)
        self.server.pubsub_backend.set_topic_audit_flag(new_name, msg.is_audit_log_active)

        # Handle name change ..
        if old_name != new_name:

            # .. update in-memory pattern matcher ..
            matcher = self.server.pubsub_pattern_matcher
            for client_id in list(matcher._clients):
                matcher.rename_topic(client_id, old_name, new_name)

            # .. rename Redis keys and subscriber sets ..
            self.server.pubsub_backend.rename_topic(old_name, new_name)

            # .. re-key pubsub_subs from old topic name to new topic name ..
            sub_configs = self.config_store.pubsub_subs.pop(old_name, None)
            if sub_configs:
                for sub_config in sub_configs:
                    sub_config['topic_name'] = new_name
                self.config_store.pubsub_subs[new_name] = sub_configs

            # .. update topic_name inside each _push_subs entry.
            for sub_key_configs in self._push_subs.values():
                for sub_config in sub_key_configs:
                    if sub_config['topic_name'] == old_name:
                        sub_config['topic_name'] = new_name

        # Handle is_active change ..
        if is_active is False:

            # .. the topic name to use is the new name (which may be the same as old) ..
            topic_name = new_name

            # .. remove in-memory subscription and push delivery configs for this topic.
            self._remove_topic_sub_configs(topic_name)

        elif is_active is True:

            # .. re-activation: re-sync subscriptions for this topic from ODB.
            self._resync_topic_subscriptions(new_name)

        # Handle backend changes - the entry is rebuilt from scratch, which also covers renames
        # and moving the override from one channel to another ..
        backend_type = getattr(msg, 'backend_type', None)

        # .. messages without backend fields come from paths that do not manage backends ..
        if backend_type is not None:

            # .. drop the previous entry, restoring the previously overridden channel, if any ..
            old_entry = self._topic_backends.pop(old_name, None)
            if old_entry and old_entry['amqp_channel_name']:
                self._remove_amqp_channel_override(old_entry)

            # .. and re-register under the new name if the topic is still AMQP-backed.
            if backend_type == PubSub.Backend_Type.AMQP:

                backend_config = {
                    'backend_type': backend_type,
                    'amqp_outconn_name': msg.amqp_outconn_name,
                    'amqp_exchange': msg.amqp_exchange,
                    'amqp_routing_key': msg.amqp_routing_key,
                    'amqp_channel_name': msg.amqp_channel_name,
                    'original_service_name': '',
                }
                self._topic_backends[new_name] = backend_config

                if backend_config['amqp_channel_name']:
                    self._apply_amqp_channel_override(backend_config)

# ################################################################################################################################

    def _resync_topic_subscriptions(self, topic_name:'str') -> 'None':
        """ Re-populates in-memory subscription state for a single topic from ODB.
        """
        from contextlib import closing
        from zato.common.odb.model import PubSubSubscription, PubSubSubscriptionTopic, PubSubTopic

        with closing(self.server.odb.session()) as session:

            rows = session.query(
                PubSubSubscription.sub_key,
                PubSubSubscription.delivery_type,
                PubSubSubscription.push_type,
                PubSubSubscription.push_service_name,
                PubSubSubscription.rest_push_endpoint_id,
                PubSubTopic.name,
            ).join(
                PubSubSubscriptionTopic, PubSubSubscription.id == PubSubSubscriptionTopic.subscription_id
            ).join(
                PubSubTopic, PubSubSubscriptionTopic.topic_id == PubSubTopic.id
            ).filter(
                PubSubTopic.name == topic_name,
                PubSubTopic.is_active == True, # noqa: E712
                PubSubSubscription.cluster_id == self.server.cluster_id,
            ).all()

            for row in rows:

                # .. re-add to pubsub_subs ..
                self._add_pubsub_sub_config(row.sub_key, topic_name, row.delivery_type, Bunch({
                    'push_type': row.push_type,
                    'push_service_name': row.push_service_name,
                    'rest_push_endpoint_id': row.rest_push_endpoint_id,
                }))

                # .. re-add push delivery if needed ..
                if row.delivery_type == 'push':
                    sub_config = {
                        'sub_key': row.sub_key,
                        'topic_name': topic_name,
                        'push_type': row.push_type,
                        'push_service_name': row.push_service_name,
                        'rest_push_endpoint_id': row.rest_push_endpoint_id,
                    }

                    if row.sub_key not in self._push_subs:
                        self._push_subs[row.sub_key] = []
                    self._push_subs[row.sub_key].append(sub_config)

                    self.server.pubsub_push_delivery.start_sub_key(row.sub_key)

# ################################################################################################################################

    def on_config_event_PUBSUB_TOPIC_DELETE(self, msg:'bunch_') -> 'None':

        topic_name = msg.topic_name

        # .. forget about the topic's audit log state ..
        self.server.pubsub_backend.delete_topic_audit_flag(topic_name)

        # .. update in-memory pattern matcher ..
        matcher = self.server.pubsub_pattern_matcher
        for client_id in list(matcher._clients):
            matcher.delete_topic(client_id, topic_name)

        # .. delete Redis keys, subscriber sets, and disk files ..
        self.server.pubsub_backend.delete_topic(topic_name)

        # .. remove in-memory subscription and push delivery configs for this topic ..
        self._remove_topic_sub_configs(topic_name)

        # .. and if the topic was AMQP-backed, drop its registry entry
        # .. and restore the channel it overrode, if any.
        old_entry = self._topic_backends.pop(topic_name, None)
        if old_entry and old_entry['amqp_channel_name']:
            self._remove_amqp_channel_override(old_entry)

# ################################################################################################################################

    def on_config_event_PUBSUB_PERMISSION_CREATE(self, msg:'bunch_') -> 'None':
        self._update_pubsub_permissions(msg)

    def on_config_event_PUBSUB_PERMISSION_EDIT(self, msg:'bunch_') -> 'None':
        self._update_pubsub_permissions(msg)

    def on_config_event_PUBSUB_PERMISSION_DELETE(self, msg:'bunch_') -> 'None':
        if hasattr(msg, 'username') and msg.username:
            self.server.pubsub_pattern_matcher.remove_client(msg.username)

# ################################################################################################################################

    def _add_pubsub_sub_config(self, sub_key:'str', topic_name:'str', delivery_type:'str', msg:'bunch_') -> 'None':
        sub_config = Bunch()
        sub_config.sub_key = sub_key
        sub_config.topic_name = topic_name
        sub_config.delivery_type = delivery_type
        sub_config.push_type = getattr(msg, 'push_type', None)
        sub_config.push_service_name = getattr(msg, 'push_service_name', None)
        sub_config.rest_push_endpoint_id = getattr(msg, 'rest_push_endpoint_id', None)

        if topic_name not in self.config_store.pubsub_subs:
            self.config_store.pubsub_subs[topic_name] = []
        self.config_store.pubsub_subs[topic_name].append(sub_config)

    def _remove_pubsub_sub_configs_by_sub_key(self, sub_key:'str') -> 'None':
        empty_topics = []
        for topic_name, sub_list in self.config_store.pubsub_subs.items():
            sub_list[:] = [item for item in sub_list if item['sub_key'] != sub_key]
            if not sub_list:
                empty_topics.append(topic_name)
        for topic_name in empty_topics:
            del self.config_store.pubsub_subs[topic_name]

    def _remove_topic_sub_configs(self, topic_name:'str') -> 'None':
        """ Removes in-memory subscription and push delivery configs for a topic.
        """
        # .. remove subscription configs for this topic ..
        _ = self.config_store.pubsub_subs.pop(topic_name, None)

        # .. stop push delivery greenlets referencing this topic ..
        sub_keys_to_remove:'list' = []

        for sub_key, config_list in self._push_subs.items():
            for sub_config in config_list:
                if sub_config['topic_name'] == topic_name:
                    sub_keys_to_remove.append(sub_key)
                    break

        for sub_key in sub_keys_to_remove:
            _ = self._push_subs.pop(sub_key, None)
            self.server.pubsub_push_delivery.stop_sub_key(sub_key)

    def _update_pubsub_permissions(self, msg:'bunch_') -> 'None':
        if hasattr(msg, 'username') and msg.username:
            permissions = []
            if hasattr(msg, 'pattern') and msg.pattern:
                for line in msg.pattern.split('\n'):
                    line = line.strip()
                    if line.startswith('pub='):
                        permissions.append({
                            'pattern': line[4:],
                            'access_type': PubSub.API_Client.Publisher,
                        })
                    elif line.startswith('sub='):
                        permissions.append({
                            'pattern': line[4:],
                            'access_type': PubSub.API_Client.Subscriber,
                        })
            self.server.pubsub_pattern_matcher.set_permissions(msg.username, permissions)

# ################################################################################################################################

    def invalidate_service_topic(self, service_name:'str') -> 'None':

        # Get a reference to the server ..
        server = self.server

        # .. acquire the lock to prevent races with the setup path ..
        with self._service_topic_lock:

            # .. if this service was never set up, there is nothing to do ..
            if service_name not in self._service_topic_cache:
                return

            # .. build the subscription key and topic name ..
            sub_key = _service_sub_key_prefix + service_name
            topic_name = _service_name_to_topic(service_name)

            # .. remove the Redis consumer group and subscription sets ..
            server.pubsub_backend.unsubscribe(sub_key, topic_name)

            # .. remove push delivery config ..
            _ = self._push_subs.pop(sub_key, None)

            # .. stop the delivery greenlet for this sub_key ..
            server.pubsub_push_delivery.stop_sub_key(sub_key)

            # .. and remove from cache.
            self._service_topic_cache.discard(service_name)

# ################################################################################################################################
# ################################################################################################################################
