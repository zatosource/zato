# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from collections import OrderedDict
from dataclasses import dataclass
from numbers import Number

# Bunch
from bunch import Bunch

# Zato
from zato.common.defaults import http_plain_server_port

# ################################################################################################################################

if 0:
    from zato.common.ext.imbox import Imbox
    from zato.common.typing_ import any_
    Imbox = Imbox

# ################################################################################################################################

# SQL ODB
engine_def = '{engine}://{username}:{password}@{host}:{port}/{db_name}'
engine_def_sqlite = 'sqlite:///{sqlite_path}'

# Convenience access functions and constants.

class OS_Env:
    Zato_Enable_Memory_Profiler = 'Zato_Enable_Memory_Profiler'

megabyte = 10 ** 6

# Hook methods whose func.im_func.func_defaults contains this argument will be assumed to have not been overridden by users
# and ServiceStore will be allowed to override them with None so that they will not be called in Service.update_handle
# which significantly improves performance (~30%).
zato_no_op_marker = 'zato_no_op_marker'

SECRET_SHADOW = '******'
Secret_Shadow = SECRET_SHADOW

# TRACE1 logging level, even more details than DEBUG
TRACE1 = 6

SECONDS_IN_DAY = 86400 # 60 seconds * 60 minutes * 24 hours (and we ignore leap seconds)

scheduler_date_time_format = '%Y-%m-%d %H:%M:%S'

# TODO: Classes that have this attribute defined (no matter the value) will not be deployed
# onto servers.
DONT_DEPLOY_ATTR_NAME = 'zato_dont_import'

# A convenient constant used in several places, simplifies passing around
# arguments which are, well, not given (as opposed to being None, an empty string etc.)
ZATO_NOT_GIVEN = b'ZATO_NOT_GIVEN'
ZatoNotGiven = b'ZatoNotGiven'

# Separates command line arguments in shell commands.
CLI_ARG_SEP = 'Zato_Zato_Zato'

# Also used in a couple of places.
ZATO_OK = 'ZATO_OK'
ZATO_ERROR = 'ZATO_ERROR'
ZATO_WARNING = 'ZATO_WARNING'
ZATO_NONE = 'ZATO_NONE'
ZATO_DEFAULT = 'ZATO_DEFAULT'
Zato_None = ZATO_NONE
Zato_No_Security = 'zato-no-security'

# Default HTTP method outgoing connections use to ping resources
# TODO: Move it to MISC
DEFAULT_HTTP_PING_METHOD = 'HEAD'

# Default size of an outgoing HTTP connection's pool (plain, SOAP, any).
# This is a per-outconn setting
# TODO: Move it to MISC
DEFAULT_HTTP_POOL_SIZE = 20

# Used when there's a need for encrypting/decrypting a well-known data.
# TODO: Move it to MISC
ZATO_CRYPTO_WELL_KNOWN_DATA = 'ZATO'

# Used if it could not be established what remote address a request came from
NO_REMOTE_ADDRESS = '(None)'

# Pattern matching order
TRUE_FALSE = 'true_false'
FALSE_TRUE = 'false_true'

simple_types = (bytes, str, dict, list, tuple, bool, Number)

# ################################################################################################################################
# ################################################################################################################################

generic_attrs = (
    'data_encoding',
    'max_msg_size', 'read_buffer_size', 'recv_timeout', 'logging_level', 'should_log_messages', 'start_seq', 'end_seq',
    'max_wait_time', 'oauth_def', 'ping_interval', 'pings_missed_threshold', 'socket_read_timeout', 'socket_write_timeout',
    'security_group_count', 'security_group_member_count',
)

# ################################################################################################################################
# ################################################################################################################################

# These are used by web-admin only because servers and scheduler use sql.conf
ping_queries = {
    'db2': 'SELECT current_date FROM sysibm.sysdummy1',
    'mssql': 'SELECT 1',
    'mysql+pymysql': 'SELECT 1+1',
    'oracle': 'SELECT 1 FROM dual',
    'postgresql': 'SELECT 1',
    'postgresql+pg8000': 'SELECT 1',
    'sqlite': 'SELECT 1',
}

engine_display_name = {
    'db2': 'DB2',
    'mssql': 'MS SQL',
    'zato+mssql1': 'MS SQL',
    'mysql+pymysql': 'MySQL',
    'oracle': 'Oracle',
    'postgresql': 'PostgreSQL',
    'postgresql+pg8000': 'PostgreSQL',
    'sqlite': 'SQLite',
}

# ################################################################################################################################
# ################################################################################################################################

class EnvVariable:
    Key_Prefix = 'Zato_Config'
    Key_Missing_Suffix = '_Missing'
    Log_Env_Details = 'Zato_Log_Env_Details'

# ################################################################################################################################
# ################################################################################################################################

class EnvFile:
    Default = 'env.ini'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class EnvConfigCtx:
    component:'str'
    file_name:'str'
    missing_suffix:'str' = EnvVariable.Key_Missing_Suffix

# ################################################################################################################################
# ################################################################################################################################

class API_Key:
    Env_Key = 'Zato_API_Key_Name'
    Default_Header = 'X-API-Key'

# ################################################################################################################################
# ################################################################################################################################

# All URL types Zato understands.
class URL_TYPE:
    SOAP       = 'soap' # Used only by outgoing connections
    PLAIN_HTTP = 'plain_http'

    def __iter__(self):
        return iter([self.PLAIN_HTTP])

# ################################################################################################################################
# ################################################################################################################################

ZATO_FIELD_OPERATORS = {
    'is-equal-to': '==',
    'is-not-equal-to': '!=',
}

# ################################################################################################################################
# ################################################################################################################################

ZMQ_OUTGOING_TYPES = ('PUSH', 'PUB')

# ################################################################################################################################
# ################################################################################################################################

ZATO_ODB_POOL_NAME = 'ZATO_ODB'

# ################################################################################################################################
# ################################################################################################################################

SOAP_VERSIONS = ('1.1', '1.2')
SOAP_CHANNEL_VERSIONS = ('1.1',)

# ################################################################################################################################
# ################################################################################################################################

class SEARCH:
    class ES:
        class DEFAULTS:
            BODY_AS = 'POST'
            HOSTS = '127.0.0.1:9200\n'

# ################################################################################################################################
# ################################################################################################################################

class SEC_DEF_TYPE:
    APIKEY = 'apikey'
    BASIC_AUTH = 'basic_auth'
    NTLM = 'ntlm'
    OAUTH = 'oauth'

Sec_Def_Type = SEC_DEF_TYPE

# ################################################################################################################################
# ################################################################################################################################

SEC_DEF_TYPE_NAME = {
    SEC_DEF_TYPE.APIKEY: 'API key',
    SEC_DEF_TYPE.BASIC_AUTH: 'Basic Auth',
    SEC_DEF_TYPE.NTLM: 'NTLM',
    SEC_DEF_TYPE.OAUTH: 'Bearer token',
}

All_Sec_Def_Types = sorted(SEC_DEF_TYPE_NAME)

# ################################################################################################################################
# ################################################################################################################################

class AUTH_RESULT:
    class BASIC_AUTH:
        INVALID_PREFIX = 'invalid-prefix'
        NO_AUTH = 'no-auth'

# ################################################################################################################################
# ################################################################################################################################

class BATCH_DEFAULTS:
    PAGE_NO = 1
    SIZE = 25
    MAX_SIZE = 1000

# ################################################################################################################################
# ################################################################################################################################

class MSG_SOURCE:
    DUPLEX = 'duplex'

# ################################################################################################################################
# ################################################################################################################################

class NameId:
    """ Wraps both an attribute's name and its ID.
    """
    def __init__(self, name:'str', id:'str'=''):
        self.name = name
        self.id = id or name

    def __repr__(self):
        return '<{} at {}; name={}; id={}>'.format(self.__class__.__name__, hex(id(self)), self.name, self.id)

# ################################################################################################################################
# ################################################################################################################################

class NotGiven:
    pass

# ################################################################################################################################
# ################################################################################################################################

class Attrs(type):
    """ A container for class attributes that can be queried for an existence
    of an attribute using the .has class-method.
    """
    attrs = NotGiven

    @classmethod
    def has(cls, attr):
        if cls.attrs is NotGiven:
            cls.attrs = []
            for cls_attr in dir(cls):
                if cls_attr == cls_attr.upper():
                    cls.attrs.append(getattr(cls, cls_attr))

        return attr in cls.attrs

# ################################################################################################################################
# ################################################################################################################################

class DATA_FORMAT(Attrs):
    CSV = 'csv'
    DICT = 'dict'
    FORM_DATA = 'form'
    JSON = 'json'
    POST = 'post'

    def __iter__(self):
        # Note that DICT and other attributes aren't included because they're never exposed to the external world as-is,
        # they may at most only used so that services can invoke each other directly
        return iter((self.JSON, self.CSV, self.POST))

Data_Format = DATA_FORMAT

# ################################################################################################################################
# ################################################################################################################################

class DEPLOYMENT_STATUS(Attrs):
    DEPLOYED = 'deployed'
    AWAITING_DEPLOYMENT = 'awaiting-deployment'
    IGNORED = 'ignored'

# ################################################################################################################################
# ################################################################################################################################

class SERVER_JOIN_STATUS(Attrs):
    ACCEPTED = 'accepted'

# ################################################################################################################################
# ################################################################################################################################

class SERVER_UP_STATUS(Attrs):
    RUNNING = 'running'
    CLEAN_DOWN = 'clean-down'

# ################################################################################################################################
# ################################################################################################################################

class CACHE:

    class Default_Name:
        Main = 'default'
        Bearer_Token = 'zato.bearer.token'

    API_USERNAME = 'pub.zato.cache'

    class TYPE:
        BUILTIN = 'builtin'

    class BUILTIN_KV_DATA_TYPE:
        STR = NameId('String', 'str')
        INT = NameId('Integer', 'int')

        def __iter__(self):
            return iter((self.STR, self.INT))

    class STATE_CHANGED:

        CLEAR = 'CLEAR'

        DELETE = 'DELETE'
        DELETE_BY_PREFIX = 'DELETE_BY_PREFIX'
        DELETE_BY_SUFFIX= 'DELETE_BY_SUFFIX'
        DELETE_BY_REGEX = 'DELETE_BY_REGEX'
        DELETE_CONTAINS = 'DELETE_CONTAINS'
        DELETE_NOT_CONTAINS = 'DELETE_NOT_CONTAINS'
        DELETE_CONTAINS_ALL = 'DELETE_CONTAINS_ALL'
        DELETE_CONTAINS_ANY = 'DELETE_CONTAINS_ANY'

        EXPIRE = 'EXPIRE'
        EXPIRE_BY_PREFIX = 'EXPIRE_BY_PREFIX'
        EXPIRE_BY_SUFFIX = 'EXPIRE_BY_SUFFIX'
        EXPIRE_BY_REGEX = 'EXPIRE_BY_REGEX'
        EXPIRE_CONTAINS = 'EXPIRE_CONTAINS'
        EXPIRE_NOT_CONTAINS = 'EXPIRE_NOT_CONTAINS'
        EXPIRE_CONTAINS_ALL = 'EXPIRE_CONTAINS_ALL'
        EXPIRE_CONTAINS_ANY = 'EXPIRE_CONTAINS_ANY'

        GET = 'GET'

        SET = 'SET'
        SET_BY_PREFIX = 'SET_BY_PREFIX'
        SET_BY_SUFFIX = 'SET_BY_SUFFIX'
        SET_BY_REGEX = 'SET_BY_REGEX'
        SET_CONTAINS = 'SET_CONTAINS'
        SET_NOT_CONTAINS = 'SET_NOT_CONTAINS'
        SET_CONTAINS_ALL = 'SET_CONTAINS_ALL'
        SET_CONTAINS_ANY = 'SET_CONTAINS_ANY'

    class DEFAULT:
        MAX_SIZE = 10000
        MAX_ITEM_SIZE = 10000 # In characters for string/unicode, bytes otherwise

    class PERSISTENT_STORAGE:
        NO_PERSISTENT_STORAGE = NameId('No persistent storage', 'no-persistent-storage')
        SQL = NameId('SQL', 'sql')

        def __iter__(self):
            return iter((self.NO_PERSISTENT_STORAGE, self.SQL))

    class SYNC_METHOD:
        NO_SYNC = NameId('No synchronization', 'no-sync')
        IN_BACKGROUND = NameId('In background', 'in-background')

        def __iter__(self):
            return iter((self.NO_SYNC, self.IN_BACKGROUND))

# ################################################################################################################################
# ################################################################################################################################

class SCHEDULER:

    InitialSleepTime = 0.1
    EmbeddedIndicator      = 'zato_embedded'
    EmbeddedIndicatorBytes = EmbeddedIndicator.encode('utf8')

    # This is what a server will invoke
    DefaultHost = '127.0.0.1'
    DefaultPort = 31530

    # This is what a scheduler will invoke
    Default_Server_Host = '127.0.0.1'
    Default_Server_Port = http_plain_server_port

    # This is what a scheduler will bind to
    DefaultBindHost = '0.0.0.0'
    DefaultBindPort = DefaultPort

    # This is the username of an API client that servers
    # will use when they invoke their scheduler.
    Default_API_Client_For_Server_Auth_Required = True
    Default_API_Client_For_Server_Username = 'server_api_client1'

    TLS_Enabled = False
    TLS_Verify = True
    TLS_Client_Certs = 'optional'

    TLS_Private_Key_Location  = 'zato-scheduler-priv-key.pem'
    TLS_Public_Key_Location   = 'zato-scheduler-pub-key.pem'
    TLS_Cert_Location         = 'zato-scheduler-cert.pem'
    TLS_CA_Certs_Key_Location = 'zato-scheduler-ca-certs.pem'

    TLS_Version_Default_Linux   = 'TLSv1_3'
    TLS_Version_Default_Windows = 'TLSv1_2'

    TLS_Ciphers_13 = 'TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256'
    TLS_Ciphers_12 = 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:' + \
                     'ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:'  + \
                     'DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384:DHE-RSA-CHACHA20-POLY1305'

    class Status:
        Active = 'Active'
        Paused = 'Paused'

    class Env:

        # Basic information about where the scheduler can be found
        Host = 'Zato_Scheduler_Host'
        Port = 'Zato_Scheduler_Port'

        # Whether the scheduler is active or paused
        Status = 'Zato_Scheduler_Status'

        Bind_Host = 'Zato_Scheduler_scheduler_conf_bind_host'
        Bind_Port = 'Zato_Scheduler_Bind_Port'
        Use_TLS = 'Zato_Scheduler_Use_TLS'
        TLS_Verify = 'Zato_Scheduler_TLS_Verify'
        TLS_Client_Certs = 'Zato_Scheduler_TLS_Client_Certs'

        TLS_Private_Key_Location  = 'Zato_Scheduler_TLS_Private_Key_Location'
        TLS_Public_Key_Location   = 'Zato_Scheduler_TLS_Public_Key_Location'
        TLS_Cert_Location         = 'Zato_Scheduler_TLS_Cert_Location'
        TLS_CA_Certs_Key_Location = 'Zato_Scheduler_TLS_CA_Certs_Key_Location'

        TLS_Version = 'Zato_Scheduler_TLS_Version'
        TLS_Ciphers = 'Zato_Scheduler_TLS_Ciphers'
        Path_Action_Prefix = 'Zato_Scheduler_Path_Action_'

        # These are used by servers to invoke the scheduler
        Server_Username = 'Zato_Scheduler_API_Client_For_Server_Username'
        Server_Password = 'Zato_Scheduler_API_Client_For_Server_Password'
        Server_Auth_Required = 'Zato_Scheduler_API_Client_For_Server_Auth_Required'

    class ConfigCommand:
        Pause = 'pause'
        Resume = 'resume'
        SetServer = 'set_server'

    JobsToIgnore = {}

    class JOB_TYPE(Attrs):
        ONE_TIME = 'one_time'
        INTERVAL_BASED = 'interval_based'

    class ON_MAX_RUNS_REACHED:
        DELETE = 'delete'
        INACTIVATE = 'inactivate'

# ################################################################################################################################
# ################################################################################################################################

class CHANNEL(Attrs):
    AMQP = 'amqp'
    DELIVERY = 'delivery'
    FANOUT_CALL = 'fanout-call'
    FANOUT_ON_FINAL = 'fanout-on-final'
    FANOUT_ON_TARGET = 'fanout-on-target'
    HTTP_SOAP = 'http-soap'
    INTERNAL_CHECK = 'internal-check'
    INVOKE = 'invoke'
    INVOKE_ASYNC = 'invoke-async'
    INVOKE_ASYNC_CALLBACK = 'invoke-async-callback'
    NEW_INSTANCE = 'new-instance'
    PARALLEL_EXEC_CALL = 'parallel-exec-call'
    PARALLEL_EXEC_ON_TARGET = 'parallel-exec-on_target'
    PUBLISH = 'publish'
    SCHEDULER = 'scheduler'
    SCHEDULER_AFTER_ONE_TIME = 'scheduler-after-one-time'
    SERVICE = 'service'
    STARTUP_SERVICE = 'startup-service'
    URL_DATA = 'url-data'
    WORKER = 'worker'

# ################################################################################################################################
# ################################################################################################################################

class CONNECTION:
    CHANNEL = 'channel'
    OUTGOING = 'outgoing'

# ################################################################################################################################
# ################################################################################################################################

class BROKER:
    DEFAULT_EXPIRATION = 15 # In seconds

# ################################################################################################################################
# ################################################################################################################################

class MISC:
    DEFAULT_HTTP_METHOD = ''
    DEFAULT_HTTP_TIMEOUT = 10
    OAUTH_SIG_METHODS = ['HMAC-SHA1', 'PLAINTEXT']
    PIDFILE = 'pidfile'
    SEPARATOR = ':::'
    DefaultAdminInvokeChannel = 'admin.invoke.json'
    Default_Cluster_ID = 1

# ################################################################################################################################
# ################################################################################################################################

class HTTP_SOAP:

    UNUSED_MARKER = 'unused'

    class ACCEPT:
        ANY = '*/*'
        ANY_INTERNAL = 'haany'

    class METHOD:
        ANY_INTERNAL = 'hmany'

# ################################################################################################################################
# ################################################################################################################################

class ADAPTER_PARAMS:
    APPLY_AFTER_REQUEST = 'apply-after-request'
    APPLY_BEFORE_REQUEST = 'apply-before-request'

# ################################################################################################################################
# ################################################################################################################################

class INFO_FORMAT:
    DICT = 'dict'
    TEXT = 'text'
    JSON = 'json'
    YAML = 'yaml'

# ################################################################################################################################
# ################################################################################################################################

class URL_PARAMS_PRIORITY:
    PATH_OVER_QS = 'path-over-qs'
    QS_OVER_PATH = 'qs-over-path'
    DEFAULT = QS_OVER_PATH

    class __metaclass__(type):
        def __iter__(self):
            return iter((self.PATH_OVER_QS, self.QS_OVER_PATH, self.DEFAULT))

# ################################################################################################################################
# ################################################################################################################################

class PARAMS_PRIORITY:
    CHANNEL_PARAMS_OVER_MSG = 'channel-params-over-msg'
    MSG_OVER_CHANNEL_PARAMS = 'msg-over-channel-params'
    DEFAULT = CHANNEL_PARAMS_OVER_MSG

    def __iter__(self):
        return iter((self.CHANNEL_PARAMS_OVER_MSG, self.MSG_OVER_CHANNEL_PARAMS, self.DEFAULT))

# ################################################################################################################################
# ################################################################################################################################

class HTTP_SOAP_SERIALIZATION_TYPE:
    STRING_VALUE = NameId('String', 'string')
    SUDS = NameId('Suds', 'suds')
    DEFAULT = STRING_VALUE

    def __iter__(self):
        return iter((self.STRING_VALUE, self.SUDS))

# ################################################################################################################################
# ################################################################################################################################

class EMAIL:
    class DEFAULT:
        TIMEOUT = 10
        PING_ADDRESS = 'invalid@invalid'
        GET_CRITERIA = 'UNSEEN'
        FILTER_CRITERIA = 'isRead ne true'
        IMAP_DEBUG_LEVEL = 0

    class IMAP:

        class MODE:
            PLAIN = 'plain'
            SSL = 'ssl'

            def __iter__(self):
                return iter((self.SSL, self.PLAIN))

        class ServerType:
            Generic = 'generic'
            Microsoft365 = 'microsoft_365'

        ServerTypeHuman = {
            ServerType.Generic: 'Generic IMAP',
            ServerType.Microsoft365: 'Microsoft 365',
        }

    class SMTP:
        class MODE:
            PLAIN = 'plain'
            SSL = 'ssl'
            STARTTLS = 'starttls'

            def __iter__(self):
                return iter((self.PLAIN, self.SSL, self.STARTTLS))

# ################################################################################################################################
# ################################################################################################################################

class CommonObject:

    Prefix_Invalid = 'prefix-invalid'

    Invalid = 'invalid-invalid'
    Security_Basic_Auth = 'security-basic-auth'

# ################################################################################################################################
# ################################################################################################################################

class ODOO:

    class CLIENT_TYPE:
        OPENERP_CLIENT_LIB = 'openerp-client-lib'

    class DEFAULT:
        PORT = 8069
        POOL_SIZE = 3

    class PROTOCOL:
        XML_RPC = NameId('XML-RPC', 'xmlrpc')
        XML_RPCS = NameId('XML-RPCS', 'xmlrpcs')
        JSON_RPC = NameId('JSON-RPC', 'jsonrpc')
        JSON_RPCS = NameId('JSON-RPCS', 'jsonrpcs')

        def __iter__(self):
            return iter((self.XML_RPC, self.XML_RPCS, self.JSON_RPC, self.JSON_RPCS))

# ################################################################################################################################
# ################################################################################################################################

class SAP:
    class DEFAULT:
        INSTANCE = '00'
        POOL_SIZE = 1

# ################################################################################################################################
# ################################################################################################################################

CONTENT_TYPE = Bunch(
    JSON = 'application/json',
    PLAIN_XML = 'application/xml',
    SOAP11 = 'text/xml; charset=UTF-8',
    SOAP12 = 'application/soap+xml; charset=utf-8',
) # type: Bunch

class ContentType:
    FormURLEncoded = 'application/x-www-form-urlencoded'

# ################################################################################################################################
# ################################################################################################################################

class AMQP:
    class DEFAULT:
        POOL_SIZE = 10
        PRIORITY = 5
        PREFETCH_COUNT = 0

    class ACK_MODE:
        ACK = NameId('Ack', 'ack')
        REJECT = NameId('Reject', 'reject')

        def __iter__(self):
            return iter((self.ACK, self.REJECT))

# ################################################################################################################################
# ################################################################################################################################

class REDIS:
    class DEFAULT:
        PORT = 6379
        DB = 0

# ################################################################################################################################
# ################################################################################################################################

class SERVER_STARTUP:
    class PHASE:
        FS_CONFIG_ONLY = 'fs-config-only'
        IMPL_BEFORE_RUN = 'impl-before-run'
        ON_STARTING = 'on-starting'
        BEFORE_POST_FORK = 'before-post-fork'
        AFTER_POST_FORK = 'after-post-fork'
        IN_PROCESS_FIRST = 'in-process-first'
        IN_PROCESS_OTHER = 'in-process-other'
        AFTER_STARTED = 'after-started'

# ################################################################################################################################
# ################################################################################################################################

class GENERIC:
    ATTR_NAME = 'opaque1'
    DeleteReason = 'DeleteGenericConnection'
    DeleteReasonBytes = DeleteReason.encode('utf8')
    InitialReason = 'ReasonInitial'

    class CONNECTION:
        class TYPE:
            CLOUD_CONFLUENCE = 'cloud-confluence'
            CLOUD_JIRA = 'cloud-jira'
            CLOUD_MICROSOFT_365 = 'cloud-microsoft-365'
            CLOUD_SALESFORCE = 'cloud-salesforce'
            OUTCONN_LDAP = 'outconn-ldap'
            OUTCONN_MONGODB = 'outconn-mongodb'

# ################################################################################################################################
# ################################################################################################################################

class Groups:
    class Type:
        Group_Parent    = 'zato-group'
        Group_Member    = 'zato-group-member'
        API_Clients     = 'zato-api-creds'
        Organizations   = 'zato-org'

    class Membership_Action:
        Add    = 'add'
        Remove = 'remove'

# ################################################################################################################################
# ################################################################################################################################

class TOTP:
    default_label = '<default-label>'

# ################################################################################################################################
# ################################################################################################################################

class LDAP:

    class DEFAULT:
        CONNECT_TIMEOUT  = 10
        POOL_EXHAUST_TIMEOUT = 5
        POOL_KEEP_ALIVE = 30
        POOL_LIFETIME = 3600
        POOL_MAX_CYCLES  = 1
        POOL_SIZE = 1
        Server_List = 'localhost:1389'
        Username = 'cn=admin,dc=example,dc=org'

    class AUTH_TYPE:
        NTLM   = NameId('NTLM', 'NTLM')
        SIMPLE = NameId('Simple', 'SIMPLE')

        def __iter__(self):
            return iter((self.SIMPLE, self.NTLM))

    class AUTO_BIND:
        DEFAULT         = NameId('Default', 'DEFAULT')
        NO_TLS          = NameId('No TLS', 'NO_TLS')
        NONE            = NameId('None', 'NONE')
        TLS_AFTER_BIND  = NameId('Bind -> TLS', 'TLS_AFTER_BIND')
        TLS_BEFORE_BIND = NameId('TLS -> Bind', 'TLS_BEFORE_BIND')

        def __iter__(self):
            return iter((self.DEFAULT, self.NONE, self.NO_TLS, self.TLS_AFTER_BIND, self.TLS_BEFORE_BIND))

    class GET_INFO:
        ALL    = NameId('All', 'ALL')
        DSA    = NameId('DSA', 'DSA')
        NONE   = NameId('None', 'NONE')
        SCHEMA = NameId('Schema', 'SCHEMA')
        OFFLINE_EDIR_8_8_8  = NameId('EDIR 8.8.8', 'OFFLINE_EDIR_8_8_8')
        OFFLINE_AD_2012_R2  = NameId('AD 2012.R2', 'OFFLINE_AD_2012_R2')
        OFFLINE_SLAPD_2_4   = NameId('SLAPD 2.4', 'OFFLINE_SLAPD_2_4')
        OFFLINE_DS389_1_3_3 = NameId('DS 389.1.3.3', 'OFFLINE_DS389_1_3_3')

        def __iter__(self):
            return iter((self.NONE, self.ALL, self.SCHEMA, self.DSA,
                self.OFFLINE_EDIR_8_8_8, self.OFFLINE_AD_2012_R2, self.OFFLINE_SLAPD_2_4, self.OFFLINE_DS389_1_3_3))

    class IP_MODE:
        IP_V4_ONLY        = NameId('Only IPv4', 'IP_V4_ONLY')
        IP_V6_ONLY        = NameId('Only IPv6', 'IP_V6_ONLY')
        IP_V4_PREFERRED   = NameId('Prefer IPv4', 'IP_V4_PREFERRED')
        IP_V6_PREFERRED   = NameId('Prefer IPv6', 'IP_V6_PREFERRED')
        IP_SYSTEM_DEFAULT = NameId('System default', 'IP_SYSTEM_DEFAULT')

        def __iter__(self):
            return iter((self.IP_V4_ONLY, self.IP_V6_ONLY, self.IP_V4_PREFERRED, self.IP_V6_PREFERRED, self.IP_SYSTEM_DEFAULT))

    class POOL_HA_STRATEGY:
        FIRST       = NameId('First', 'FIRST')
        RANDOM      = NameId('Random', 'RANDOM')
        ROUND_ROBIN = NameId('Round robin', 'ROUND_ROBIN')

        def __iter__(self):
            return iter((self.FIRST, self.RANDOM, self.ROUND_ROBIN))

    class SASL_MECHANISM:
        GSSAPI = NameId('GSS-API', 'GSSAPI')
        EXTERNAL = NameId('External', 'EXTERNAL')

        def __iter__(self):
            return iter((self.EXTERNAL, self.GSSAPI))

# ################################################################################################################################
# ################################################################################################################################

class MONGODB:

    class DEFAULT:
        AUTH_SOURCE      = 'admin'
        HB_FREQUENCY     = 10
        MAX_IDLE_TIME    = 600
        MAX_STALENESS    = -1
        POOL_SIZE_MIN    = 0
        POOL_SIZE_MAX    = 5
        SERVER_LIST      = '127.0.0.1:27017'
        WRITE_TO_REPLICA = ''
        WRITE_TIMEOUT    = 5
        ZLIB_LEVEL       = -1

        class TIMEOUT:
            CONNECT = 10
            SERVER_SELECT  = 5
            SOCKET  = 30
            WAIT_QUEUE  = 10

    class READ_PREF:
        PRIMARY = NameId('Primary', 'primary')
        PRIMARY_PREFERRED = NameId('Primary pref.', 'primaryPreferred')
        SECONDARY = NameId('Secondary', 'secondary')
        SECONDARY_PREFERRED = NameId('Secondary pref.', 'secondaryPreferred')
        NEAREST = NameId('Nearest', 'nearest')

        def __iter__(self):
            return iter((self.PRIMARY, self.PRIMARY_PREFERRED, self.SECONDARY, self.SECONDARY_PREFERRED, self.NEAREST))

    class AUTH_MECHANISM:
        SCRAM_SHA_1 = NameId('SCRAM-SHA-1')
        SCRAM_SHA_256 = NameId('SCRAM-SHA-256')

        def __iter__(self):
            return iter((self.SCRAM_SHA_1, self.SCRAM_SHA_256))

# We need to use such a constant because we can sometimes be interested in setting
# default values which evaluate to boolean False.
NO_DEFAULT_VALUE = 'NO_DEFAULT_VALUE'
PLACEHOLDER = 'zato_placeholder'

# ################################################################################################################################
# ################################################################################################################################

class MS_SQL:
    ZATO_DIRECT = 'zato+mssql1'
    EXTRA_KWARGS = 'login_timeout', 'appname', 'blocksize', 'use_mars', 'readonly', 'use_tz', 'bytes_to_unicode', \
        'cafile', 'validate_host'

# ################################################################################################################################
# ################################################################################################################################

class SALESFORCE:

    class Default:
        Address = 'https://example.my.salesforce.com'
        API_Version = '54.0'

# ################################################################################################################################
# ################################################################################################################################

class Atlassian:

    class Default:
        Address = 'https://example.atlassian.net'
        API_Version = '3'

# ################################################################################################################################
# ################################################################################################################################

class Microsoft365:

    class Default:
        Auth_Redirect_URL = 'https://zato.io/ext/redirect/oauth2'
        Scopes = [
            'https://graph.microsoft.com/.default'
        ]

# ################################################################################################################################
# ################################################################################################################################

class OAuth:

    class Default:
        Auth_Server_URL = 'https://example.com/oauth2/token'
        Scopes = [] # There are no default scopes
        Client_ID_Field = 'client_id'
        Client_Secret_Field = 'client_secret'
        Grant_Type = 'client_credentials'

# ################################################################################################################################
# ################################################################################################################################

# TODO: SIMPLE_IO.FORMAT should be removed in favour of plain DATA_FORMAT
class SIMPLE_IO:

    class FORMAT(Attrs):
        FORM_DATA = DATA_FORMAT.FORM_DATA
        JSON = DATA_FORMAT.JSON

    COMMON_FORMAT = OrderedDict()
    COMMON_FORMAT[DATA_FORMAT.JSON] = 'JSON'

    HTTP_SOAP_FORMAT = OrderedDict()
    HTTP_SOAP_FORMAT[DATA_FORMAT.JSON] = 'JSON'
    HTTP_SOAP_FORMAT[DATA_FORMAT.FORM_DATA] = 'Form data'

    Bearer_Token_Format = [
        NameId('JSON', DATA_FORMAT.JSON),
        NameId('Form data', DATA_FORMAT.FORM_DATA)
    ]

# ################################################################################################################################
# ################################################################################################################################

class UNITTEST:
    SQL_ENGINE = 'zato+unittest'
    HTTP       = 'zato+unittest'

class HotDeploy:
    UserPrefix = 'hot-deploy.user'
    UserConfPrefix = 'user_conf'
    Source_Directory = 'src'
    User_Conf_Directory = 'user-conf'
    Enmasse_File_Pattern = 'enmasse'
    Default_Patterns = [User_Conf_Directory, Enmasse_File_Pattern]

    class Env:
        Pickup_Patterns = 'Zato_Hot_Deploy_Pickup_Patterns'

# ################################################################################################################################
# ################################################################################################################################

ZATO_INFO_FILE = '.zato-info'

# ################################################################################################################################
# ################################################################################################################################

class SourceCodeInfo:
    """ Attributes describing the service's source code file.
    """
    __slots__ = 'source', 'source_html', 'len_source', 'path', 'hash', 'hash_method', 'server_name', 'line_number'

    def __init__(self):
        self.source = b''       # type: bytes
        self.source_html = ''   # type: str
        self.len_source = 0     # type: int
        self.path = None        # type: str
        self.hash = None        # type: str
        self.hash_method = None # type: str
        self.server_name = None # type: str
        self.line_number = 0    # type: int

# ################################################################################################################################
# ################################################################################################################################

class IDEDeploy:
    Username = 'ide_publisher'

# ################################################################################################################################
# ################################################################################################################################

class SMTPMessage:

    from_: 'any_'
    to: 'any_'
    subject: 'any_'
    body: 'any_'
    attachments: 'any_'
    cc: 'any_'
    bcc: 'any_'
    is_html: 'any_'
    headers: 'any_'
    charset: 'any_'
    is_rfc2231: 'any_'

    def __init__(self, from_=None, to=None, subject='', body='', attachments=None, cc=None, bcc=None, is_html=False, headers=None,
            charset='utf8', is_rfc2231=True):
        self.from_ = from_
        self.to = to
        self.subject = subject
        self.body = body
        self.attachments = attachments or []
        self.cc = cc
        self.bcc = bcc
        self.is_html = is_html
        self.headers = headers or {}
        self.charset = charset
        self.is_rfc2231 = is_rfc2231

    def attach(self, name, contents):
        self.attachments.append({'name':name, 'contents':contents})

# ################################################################################################################################
# ################################################################################################################################

class IMAPMessage:
    def __init__(self, uid, conn, data):
        self.uid = uid   # type: str
        self.conn = conn # type: Imbox
        self.data = data

    def __repr__(self):
        class_name = self.__class__.__name__
        self_id = hex(id(self))
        return '<{} at {}, uid:`{}`, conn.config:`{}`>'.format(class_name, self_id, self.uid, self.conn.config_no_sensitive)

    def delete(self):
        raise NotImplementedError('Must be implemented by subclasses')

    def mark_seen(self):
        raise NotImplementedError('Must be implemented by subclasses')

# ################################################################################################################################
# ################################################################################################################################

class Name_Prefix:
    Keysight_Hawkeye = 'KeysightHawkeye.'
    Keysight_Vision  = 'KeysightVision.'

Wrapper_Name_Prefix_List = {
    Name_Prefix.Keysight_Hawkeye,
    Name_Prefix.Keysight_Vision,
}

# ################################################################################################################################
# ################################################################################################################################

class Wrapper_Type:
    Keysight_Hawkeye = 'KeysightHawkeye'
    Keysight_Vision  = 'KeysightVision'

# ################################################################################################################################
# ################################################################################################################################

class HAProxy:
    Default_Memory_Limit = '1024' # In megabytes = 1 GB

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class URLInfo:
    address: 'str'
    host: 'str'
    port: 'int'
    use_tls: 'bool'

# ################################################################################################################################
# ################################################################################################################################

class RESTAdapterResponse:
    def __init__(self, data:'any_', raw_response:'any_') -> 'None':
        self.data = data
        self.raw_response = raw_response

# ################################################################################################################################
# ################################################################################################################################

Default_Service_File_Data = """
# -*- coding: utf-8 -*-

# File path: {full_path}

# Zato
from zato.server.service import Service

class MyService(Service):

    # I/O definition
    input = '-name'
    output = 'salutation'

    def handle(self):

        # Local variables
        name = self.request.input.name or 'partner'

        # Our response to produce
        message = f'Howdy {{name}}!'

        # Reply to our caller
        self.response.payload.salutation = message
""".lstrip()

# ################################################################################################################################
# ################################################################################################################################


class PubSub:

    # About 3 years if we repeat delivery attempts once per second
    Max_Repeats = 100_000_000

    # 90 days in seconds
    Max_Retry_Time = 365 * 24 * 3600

    class Timeout:

        # How many seconds a consumer will wait in its drain_events call
        Consumer = 1 # 51224

        # Must be bigger than the Consumer timeout to give a consumer enough time
        # to drain its events.
        Invoke_Sync = Consumer * 3

    class API_Client:
        Publisher = 'publisher'
        Subscriber = 'subscriber'
        Publisher_Subscriber = 'publisher-subscriber'

    class Delivery_Type:
        Pull = 'pull'
        Push = 'push'

    class Push_Type:
        REST = 'rest'
        Service = 'service'

    class Prefix:
        Msg_ID = 'zpsm'
        Sub_Key = 'zpsk.rest'

    class REST_Server:
        Default_Port = 44556
        Default_Host = '0.0.0.0'
        Default_Threads = 1

    class Message:
        Default_Priority = 5
        Default_Expiration = 86400 * 365  # 24 hours * 365 days = 1 year in seconds

    class Repeats:
        Max = 500

# ################################################################################################################################
# ################################################################################################################################
