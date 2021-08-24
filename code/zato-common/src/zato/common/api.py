# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from collections import OrderedDict
from io import StringIO
from numbers import Number
from sys import maxsize

# Bunch
from bunch import Bunch

# ################################################################################################################################

# SQL ODB
engine_def = '{engine}://{username}:{password}@{host}:{port}/{db_name}'
engine_def_sqlite = 'sqlite:///{sqlite_path}'

# Convenience access functions and constants.

megabyte = 10 ** 6

# Hook methods whose func.im_func.func_defaults contains this argument will be assumed to have not been overridden by users
# and ServiceStore will be allowed to override them with None so that they will not be called in Service.update_handle
# which significantly improves performance (~30%).
zato_no_op_marker = 'zato_no_op_marker'

SECRET_SHADOW = '******'

# TRACE1 logging level, even more details than DEBUG
TRACE1 = 6

SECONDS_IN_DAY = 86400 # 60 seconds * 60 minutes * 24 hours (and we ignore leap seconds)

scheduler_date_time_format = '%Y-%m-%d %H:%M:%S'
soap_date_time_format = '%Y-%m-%dT%H:%M:%S.%fZ'

# TODO: Classes that have this attribute defined (no matter the value) will not be deployed
# onto servers.
DONT_DEPLOY_ATTR_NAME = 'zato_dont_import'

# A convenient constant used in several places, simplifies passing around
# arguments which are, well, not given (as opposed to being None, an empty string etc.)
ZATO_NOT_GIVEN = b'ZATO_NOT_GIVEN'

# Separates command line arguments in shell commands.
CLI_ARG_SEP = 'ZATO_ZATO_ZATO'

# Also used in a couple of places.
ZATO_OK = 'ZATO_OK'
ZATO_ERROR = 'ZATO_ERROR'
ZATO_WARNING = 'ZATO_WARNING'
ZATO_NONE = 'ZATO_NONE'
ZATO_DEFAULT = 'ZATO_DEFAULT'
ZATO_SEC_USE_RBAC = 'ZATO_SEC_USE_RBAC'

DELEGATED_TO_RBAC = 'Delegated to RBAC'

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

generic_attrs = ('is_rate_limit_active', 'rate_limit_type', 'rate_limit_def', 'rate_limit_check_parent_def',
    'is_audit_log_sent_active', 'is_audit_log_received_active', 'max_len_messages_sent', 'max_len_messages_received',
    'max_bytes_per_message_sent', 'max_bytes_per_message_received', 'hl7_version', 'json_path', 'data_encoding',
    'max_msg_size', 'read_buffer_size', 'recv_timeout', 'logging_level', 'should_log_messages', 'start_seq', 'end_seq',
    'max_wait_time')

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
    'zato+mssql1': 'MS SQL (Direct)',
    'mysql+pymysql': 'MySQL',
    'oracle': 'Oracle',
    'postgresql': 'PostgreSQL',
    'postgresql+pg8000': 'PostgreSQL',
    'sqlite': 'SQLite',
}

# ################################################################################################################################
# ################################################################################################################################

# All URL types Zato understands.
class URL_TYPE:
    SOAP = 'soap'
    PLAIN_HTTP = 'plain_http'

    def __iter__(self):
        return iter((self.SOAP, self.PLAIN_HTTP))

# ################################################################################################################################
# ################################################################################################################################

# Whether WS-Security passwords are transmitted in clear-text or not.
ZATO_WSS_PASSWORD_CLEAR_TEXT = Bunch(name='clear_text', label='Clear text')
ZATO_WSS_PASSWORD_TYPES = {
    ZATO_WSS_PASSWORD_CLEAR_TEXT.name:ZATO_WSS_PASSWORD_CLEAR_TEXT.label,
}

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

class ZMQ:

    PULL = 'PULL'
    PUSH = 'PUSH'
    PUB = 'PUB'
    SUB = 'SUB'
    MDP = 'MDP'
    MDP01 = MDP + '01'

    MDP01_HUMAN = 'Majordomo 0.1 (MDP)'

    class POOL_STRATEGY_NAME:
        SINGLE = 'single'
        UNLIMITED = 'unlimited'

    class SERVICE_SOURCE_NAME:
        ZATO = 'zato'
        MDP01 = 'mdp01'

    CHANNEL = OrderedDict({
        PULL: 'Pull',
        SUB: 'Sub',
        MDP01: MDP01_HUMAN,
    })

    OUTGOING = OrderedDict({
        PUSH: 'Push',
        PUB: 'Pub',
    })

    class METHOD_NAME:
        BIND = 'bind'
        CONNECT = 'connect'

    METHOD = {
        METHOD_NAME.BIND: 'Bind',
        METHOD_NAME.CONNECT: 'Connect',
    }

    POOL_STRATEGY = OrderedDict({
        POOL_STRATEGY_NAME.SINGLE: 'Single',
        POOL_STRATEGY_NAME.UNLIMITED: 'Unlimited',
    })

    SERVICE_SOURCE = OrderedDict({
        SERVICE_SOURCE_NAME.ZATO: 'Zato',
        SERVICE_SOURCE_NAME.MDP01: MDP01_HUMAN,
    })

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

    class SOLR:
        class DEFAULTS:
            ADDRESS = 'http://127.0.0.1:8983/solr'
            PING_PATH = '/solr/admin/ping'
            TIMEOUT = '10'
            POOL_SIZE = '5'

    class ZATO:
        class DEFAULTS:
            PAGE_SIZE = 50
            PAGINATE_THRESHOLD = PAGE_SIZE + 1

# ################################################################################################################################
# ################################################################################################################################

class SEC_DEF_TYPE:
    APIKEY = 'apikey'
    AWS = 'aws'
    BASIC_AUTH = 'basic_auth'
    JWT = 'jwt'
    NTLM = 'ntlm'
    OAUTH = 'oauth'
    TLS_CHANNEL_SEC = 'tls_channel_sec'
    TLS_KEY_CERT = 'tls_key_cert'
    WSS = 'wss'
    VAULT = 'vault_conn_sec'
    XPATH_SEC = 'xpath_sec'

# ################################################################################################################################
# ################################################################################################################################

SEC_DEF_TYPE_NAME = {
    SEC_DEF_TYPE.APIKEY: 'API key',
    SEC_DEF_TYPE.AWS: 'AWS',
    SEC_DEF_TYPE.BASIC_AUTH: 'HTTP Basic Auth',
    SEC_DEF_TYPE.JWT: 'JWT',
    SEC_DEF_TYPE.NTLM: 'NTLM',
    SEC_DEF_TYPE.OAUTH: 'OAuth 1.0',
    SEC_DEF_TYPE.TLS_CHANNEL_SEC: 'TLS channel',
    SEC_DEF_TYPE.TLS_KEY_CERT: 'TLS key/cert',
    SEC_DEF_TYPE.WSS: 'WS-Security',
    SEC_DEF_TYPE.VAULT: 'Vault',
    SEC_DEF_TYPE.XPATH_SEC: 'XPath',
}

# ################################################################################################################################
# ################################################################################################################################

class AUTH_RESULT:
    class BASIC_AUTH:
        INVALID_PREFIX = 'invalid-prefix'
        NO_AUTH = 'no-auth'

# ################################################################################################################################
# ################################################################################################################################

DEFAULT_STATS_SETTINGS = {
    'scheduler_per_minute_aggr_interval':60,
    'scheduler_raw_times_interval':90,
    'scheduler_raw_times_batch':99999,
    'atttention_slow_threshold':2000,
    'atttention_top_threshold':10,
}

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
    def __init__(self, name, id=None):
        self.name = name
        self.id = id or name

    def __repr__(self):
        return '<{} at {}; name={}; id={}>'.format(self.__class__.__name__, hex(id(self)), self.name, self.id)

# ################################################################################################################################
# ################################################################################################################################

class NotGiven:
    pass # A marker for lazily-initialized attributes

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
    HL7  = 'hl7'
    JSON = 'json'
    POST = 'post'
    SOAP = 'soap'
    XML = 'xml'

    def __iter__(self):
        # Note that DICT and other attributes aren't included because they're never exposed to the external world as-is,
        # they may at most only used so that services can invoke each other directly
        return iter((self.XML, self.JSON, self.CSV, self.POST, self.HL7))


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

    API_USERNAME = 'pub.zato.cache'

    class TYPE:
        BUILTIN = 'builtin'
        MEMCACHED = 'memcached'

    class BUILTIN_KV_DATA_TYPE:
        STR = NameId('String/unicode', 'str')
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

class KVDB(Attrs):
    SEPARATOR = ':::'

    DICTIONARY_ITEM = 'zato:kvdb:data-dict:item'
    DICTIONARY_ITEM_ID = DICTIONARY_ITEM + ':id' # ID of the last created dictionary ID, always increasing.

    LOCK_PREFIX = 'zato:lock:'

    LOCK_SERVER_PREFIX = '{}server:'.format(LOCK_PREFIX)
    LOCK_SERVER_ALREADY_DEPLOYED = '{}already-deployed:'.format(LOCK_SERVER_PREFIX)
    LOCK_SERVER_STARTING = '{}starting:'.format(LOCK_SERVER_PREFIX)

    LOCK_PACKAGE_PREFIX = '{}package:'.format(LOCK_PREFIX)
    LOCK_PACKAGE_UPLOADING = '{}uploading:'.format(LOCK_PACKAGE_PREFIX)
    LOCK_PACKAGE_ALREADY_UPLOADED = '{}already-uploaded:'.format(LOCK_PACKAGE_PREFIX)

    LOCK_DELIVERY = '{}delivery:'.format(LOCK_PREFIX)
    LOCK_DELIVERY_AUTO_RESUBMIT = '{}auto-resubmit:'.format(LOCK_DELIVERY)

    LOCK_SERVICE_PREFIX = '{}service:'.format(LOCK_PREFIX)
    LOCK_CONFIG_PREFIX = '{}config:'.format(LOCK_PREFIX)

    LOCK_FANOUT_PATTERN = '{}fanout:{{}}'.format(LOCK_PREFIX)
    LOCK_PARALLEL_EXEC_PATTERN = '{}parallel-exec:{{}}'.format(LOCK_PREFIX)

    LOCK_ASYNC_INVOKE_WITH_TARGET_PATTERN = '{}async-invoke-with-pattern:{{}}:{{}}'.format(LOCK_PREFIX)

    TRANSLATION = 'zato:kvdb:data-dict:translation'
    TRANSLATION_ID = TRANSLATION + ':id'

    SERVICE_USAGE = 'zato:stats:service:usage:'
    SERVICE_TIME_BASIC = 'zato:stats:service:time:basic:'
    SERVICE_TIME_RAW = 'zato:stats:service:time:raw:'
    SERVICE_TIME_RAW_BY_MINUTE = 'zato:stats:service:time:raw-by-minute:'
    SERVICE_TIME_AGGREGATED_BY_MINUTE = 'zato:stats:service:time:aggr-by-minute:'
    SERVICE_TIME_AGGREGATED_BY_HOUR = 'zato:stats:service:time:aggr-by-hour:'
    SERVICE_TIME_AGGREGATED_BY_DAY = 'zato:stats:service:time:aggr-by-day:'
    SERVICE_TIME_AGGREGATED_BY_MONTH = 'zato:stats:service:time:aggr-by-month:'
    SERVICE_TIME_SLOW = 'zato:stats:service:time:slow:'

    SERVICE_SUMMARY_PREFIX_PATTERN = 'zato:stats:service:summary:{}:'
    SERVICE_SUMMARY_BY_DAY = 'zato:stats:service:summary:by-day:'
    SERVICE_SUMMARY_BY_WEEK = 'zato:stats:service:summary:by-week:'
    SERVICE_SUMMARY_BY_MONTH = 'zato:stats:service:summary:by-month:'
    SERVICE_SUMMARY_BY_YEAR = 'zato:stats:service:summary:by-year:'

    ZMQ_CONFIG_READY_PREFIX = 'zato:zmq.config.ready.{}'

    REQ_RESP_SAMPLE = 'zato:req-resp:sample:'
    RESP_SLOW = 'zato:resp:slow:'

    DELIVERY_PREFIX = 'zato:delivery:'
    DELIVERY_BY_TARGET_PREFIX = '{}by-target:'.format(DELIVERY_PREFIX)

    FANOUT_COUNTER_PATTERN = 'zato:fanout:counter:{}'
    FANOUT_DATA_PATTERN = 'zato:fanout:data:{}'

    PARALLEL_EXEC_COUNTER_PATTERN = 'zato:parallel-exec:counter:{}'
    PARALLEL_EXEC_DATA_PATTERN = 'zato:parallel-exec:data:{}'

    ASYNC_INVOKE_PROCESSED_FLAG_PATTERN = 'zato:async-invoke-with-pattern:processed:{}:{}'
    ASYNC_INVOKE_PROCESSED_FLAG = '1'

# ################################################################################################################################
# ################################################################################################################################

class SCHEDULER:

    InitialSleepTime = 5
    DefaultHost = '127.0.0.1'
    DefaultPort = 31530

    class JOB_TYPE(Attrs):
        ONE_TIME = 'one_time'
        INTERVAL_BASED = 'interval_based'
        CRON_STYLE = 'cron_style'

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
    IPC = 'ipc'
    JSON_RPC = 'json-rpc'
    NEW_INSTANCE = 'new-instance'
    NOTIFIER_RUN = 'notifier-run'
    NOTIFIER_TARGET = 'notifier-target'
    PARALLEL_EXEC_CALL = 'parallel-exec-call'
    PARALLEL_EXEC_ON_TARGET = 'parallel-exec-on-target'
    PUBLISH = 'publish'
    SCHEDULER = 'scheduler'
    SCHEDULER_AFTER_ONE_TIME = 'scheduler-after-one-time'
    SERVICE = 'service'
    SSO_USER = 'sso-user'
    STARTUP_SERVICE = 'startup-service'
    URL_DATA = 'url-data'
    WEB_SOCKET = 'web-socket'
    IBM_MQ = 'websphere-mq'
    WORKER = 'worker'
    ZMQ = 'zmq'

# ################################################################################################################################
# ################################################################################################################################

class CONNECTION:
    CHANNEL = 'channel'
    OUTGOING = 'outgoing'

# ################################################################################################################################
# ################################################################################################################################

class INVOCATION_TARGET(Attrs):
    CHANNEL_AMQP = 'channel-amqp'
    CHANNEL_WMQ = 'channel-wmq'
    CHANNEL_ZMQ = 'channel-zmq'
    OUTCONN_AMQP = 'outconn-amqp'
    OUTCONN_WMQ = 'outconn-wmq'
    OUTCONN_ZMQ = 'outconn-zmq'
    SERVICE = 'service'

# ################################################################################################################################
# ################################################################################################################################

class DELIVERY_STATE(Attrs):
    IN_DOUBT = 'in-doubt'
    IN_PROGRESS_ANY = 'in-progress-any' # A wrapper for all in-progress-* states
    IN_PROGRESS_RESUBMITTED = 'in-progress-resubmitted'
    IN_PROGRESS_RESUBMITTED_AUTO = 'in-progress-resubmitted-auto'
    IN_PROGRESS_STARTED = 'in-progress'
    IN_PROGRESS_TARGET_OK = 'in-progress-target-ok'
    IN_PROGRESS_TARGET_FAILURE = 'in-progress-target-failure'
    CONFIRMED = 'confirmed'
    FAILED = 'failed'
    UNKNOWN = 'unknown'

# ################################################################################################################################
# ################################################################################################################################

class DELIVERY_CALLBACK_INVOKER(Attrs):
    SOURCE = 'source'
    TARGET = 'target'

# ################################################################################################################################
# ################################################################################################################################

class BROKER:
    DEFAULT_EXPIRATION = 15 # In seconds

# ################################################################################################################################
# ################################################################################################################################

class MISC:
    DEFAULT_HTTP_TIMEOUT=10
    OAUTH_SIG_METHODS = ['HMAC-SHA1', 'PLAINTEXT']
    PIDFILE = 'pidfile'
    SEPARATOR = ':::'

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

class MSG_MAPPER:
    DICT_TO_DICT = 'dict-to-dict'
    DICT_TO_XML = 'dict-to-xml'
    XML_TO_DICT = 'xml-to-dict'
    XML_TO_XML = 'xml-to-xml'

# ################################################################################################################################
# ################################################################################################################################

class CLOUD:
    class AWS:
        class S3:
            class STORAGE_CLASS:
                STANDARD = 'STANDARD'
                REDUCED_REDUNDANCY = 'REDUCED_REDUNDANCY'
                GLACIER = 'GLACIER'
                DEFAULT = STANDARD

                def __iter__(self):
                    return iter((self.STANDARD, self.REDUCED_REDUNDANCY, self.GLACIER))

            class DEFAULTS:
                ADDRESS = 'https://s3.amazonaws.com/'
                CONTENT_TYPE = 'application/octet-stream' # Taken from boto.s3.key.Key.DefaultContentType
                DEBUG_LEVEL = 0
                POOL_SIZE = 5
                PROVIDER = 'aws'

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

class NONCE_STORE:
    KEY_PATTERN = 'zato:nonce-store:{}:{}' # E.g. zato:nonce-store:oauth:27
    DEFAULT_MAX_LOG = 25000

# ################################################################################################################################
# ################################################################################################################################

class MSG_PATTERN_TYPE:
    JSON_POINTER = NameId('JSONPointer', 'json-pointer')
    XPATH = NameId('XPath', 'xpath')

    def __iter__(self):
        return iter((self.JSON_POINTER, self.XPATH))

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

class PUBSUB:

    SKIPPED_PATTERN_MATCHING = '<skipped>'

    # All float values are converted to strings of that precision
    # to make sure pg8000 does not round up the floats with loss of precision.
    FLOAT_STRING_CONVERT = '{:.7f}'

    class DATA_FORMAT:
        CSV  = NameId('CSV', DATA_FORMAT.CSV)
        DICT = NameId('Dict', DATA_FORMAT.DICT)
        JSON = NameId('JSON', DATA_FORMAT.JSON)
        POST = NameId('POST', DATA_FORMAT.POST)
        SOAP = NameId('SOAP', DATA_FORMAT.SOAP)
        XML  = NameId('XML', DATA_FORMAT.XML)

        def __iter__(self):
            return iter((self.CSV, self.DICT, self.JSON, self.POST, self.SOAP, self.XML))

    class HOOK_TYPE:
        BEFORE_PUBLISH = 'pubsub_before_publish'
        BEFORE_DELIVERY = 'pubsub_before_delivery'
        ON_OUTGOING_SOAP_INVOKE = 'pubsub_on_topic_outgoing_soap_invoke'
        ON_SUBSCRIBED = 'pubsub_on_subscribed'
        ON_UNSUBSCRIBED = 'pubsub_on_unsubscribed'

    class HOOK_ACTION:
        SKIP = 'skip'
        DELETE = 'delete'
        DELIVER = 'deliver'

        def __iter__(self):
            return iter((self.SKIP, self.DELETE, self.DELIVER))

    class DELIVER_BY:
        PRIORITY = 'priority'
        EXT_PUB_TIME = 'ext_pub_time'
        PUB_TIME = 'pub_time'

        def __iter__(self):
            return iter((self.PRIORITY, self.EXT_PUB_TIME, self.PUB_TIME))

    class ON_NO_SUBS_PUB:
        ACCEPT = NameId('Accept', 'accept')
        DROP = NameId('Drop', 'drop')

    class DEFAULT:
        DATA_FORMAT = 'text'
        MIME_TYPE = 'text/plain'
        TOPIC_MAX_DEPTH_GD = 10000
        TOPIC_MAX_DEPTH_NON_GD = 1000
        DEPTH_CHECK_FREQ = 100
        EXPIRATION = 2147483647 * 1000 # (2 ** 31 - 1) * 1000 milliseconds = around 70 years
        GET_BATCH_SIZE = 50
        DELIVERY_BATCH_SIZE = 500
        DELIVERY_MAX_RETRY = 123456789
        DELIVERY_MAX_SIZE = 500000 # 500 kB
        PUB_BUFFER_SIZE_GD = 0
        TASK_SYNC_INTERVAL = 500
        TASK_DELIVERY_INTERVAL = 2000
        WAIT_TIME_SOCKET_ERROR = 10
        WAIT_TIME_NON_SOCKET_ERROR = 3
        INTERNAL_ENDPOINT_NAME = 'zato.pubsub.default.internal.endpoint'
        ON_NO_SUBS_PUB = 'accept'
        SK_OPAQUE = ('deliver_to_sk', 'reply_to_sk')

    class SERVICE_SUBSCRIBER:
        NAME = 'zato.pubsub.service.endpoint'
        TOPICS_ALLOWED = 'sub=/zato/s/to/*'

    class TOPIC_PATTERN:
        TO_SERVICE = '/zato/s/to/{}'

    class QUEUE_TYPE:
        STAGING = 'staging'
        CURRENT = 'current'

        def __iter__(self):
            return iter((self.STAGING, self.CURRENT))

    class GD_CHOICE:
        DEFAULT_PER_TOPIC = NameId('----------', 'default-per-topic')
        YES = NameId('Yes', 'true')
        NO = NameId('No', 'false')

        def __iter__(self):
            return iter((self.DEFAULT_PER_TOPIC, self.YES, self.NO))

    class QUEUE_ACTIVE_STATUS:
        FULLY_ENABLED = NameId('Pub and sub', 'pub-sub')
        PUB_ONLY = NameId('Pub only', 'pub-only')
        SUB_ONLY = NameId('Sub only', 'sub-only')
        DISABLED = NameId('Disabled', 'disabled')

        def __iter__(self):
            return iter((self.FULLY_ENABLED, self.PUB_ONLY, self.SUB_ONLY, self.DISABLED))

    class DELIVERY_METHOD:
        NOTIFY = NameId('Notify', 'notify')
        PULL = NameId('Pull', 'pull')
        WEB_SOCKET = NameId('WebSocket', 'web-socket')

        def __iter__(self):
            # Note that WEB_SOCKET is not included because it's not shown in GUI for subscriptions
            return iter((self.NOTIFY, self.PULL))

    class DELIVERY_STATUS:
        DELIVERED = 1
        INITIALIZED = 2
        TO_DELETE = 3
        WAITING_FOR_CONFIRMATION = 4

    class PRIORITY:
        DEFAULT = 5
        MIN = 1
        MAX = 9

    class ROLE:
        PUBLISHER = NameId('Publisher', 'pub-only')
        SUBSCRIBER = NameId('Subscriber', 'sub-only')
        PUBLISHER_SUBSCRIBER = NameId('Publisher/subscriber', 'pub-sub')

        def __iter__(self):
            return iter((self.PUBLISHER, self.SUBSCRIBER, self.PUBLISHER_SUBSCRIBER))

    class RunDeliveryStatus:

        class StatusCode:
            OK = 1
            Warning = 2
            Error = 3

        class ReasonCode:
            Error_IO = 1
            Error_Other = 2
            No_Msg = 3

    class ENDPOINT_TYPE:
        AMQP = NameId('AMQP', 'amqp')
        FILES = NameId('Files', 'files')
        FTP = NameId('FTP', 'ftp')
        IMAP = NameId('IMAP', 'imap')
        INTERNAL = NameId('Internal', 'internal')
        REST = NameId('REST', 'rest')
        SERVICE = NameId('Service', 'srv')
        SMS_TWILIO = NameId('SMS - Twilio', 'smstw')
        SMTP = NameId('SMTP', 'smtp')
        SOAP = NameId('SOAP', 'soap')
        SQL = NameId('SQL', 'sql')
        WEB_SOCKETS = NameId('WebSockets', 'wsx')

        def __iter__(self):
            return iter((self.AMQP.id, self.INTERNAL.id, self.REST.id, self.SERVICE.id, self.SOAP.id,
                self.WEB_SOCKETS.id, self.SERVICE.id))

    class REDIS:
        META_TOPIC_LAST_KEY = 'zato.ps.meta.topic.last.%s.%s'
        META_ENDPOINT_PUB_KEY = 'zato.ps.meta.endpoint.pub.%s.%s'
        META_ENDPOINT_SUB_KEY = 'zato.ps.meta.endpoint.sub.%s.%s'

    class MIMEType:
        Zato = 'application/vnd.zato.ps.msg'

# ################################################################################################################################
# ################################################################################################################################

class _PUBSUB_SUBSCRIBE_CLASS:

    classes = {
        PUBSUB.ENDPOINT_TYPE.AMQP.id: 'zato.pubsub.subscription.subscribe-amqp',
        PUBSUB.ENDPOINT_TYPE.REST.id: 'zato.pubsub.subscription.subscribe-rest',
        PUBSUB.ENDPOINT_TYPE.SERVICE.id: 'zato.pubsub.subscription.subscribe-service',
        PUBSUB.ENDPOINT_TYPE.SOAP.id: 'zato.pubsub.subscription.subscribe-soap',
        PUBSUB.ENDPOINT_TYPE.WEB_SOCKETS.id: 'zato.pubsub.subscription.create-wsx-subscription',
    }

    @staticmethod
    def get(name):
        return _PUBSUB_SUBSCRIBE_CLASS.classes[name]

# ################################################################################################################################
# ################################################################################################################################

PUBSUB.SUBSCRIBE_CLASS = _PUBSUB_SUBSCRIBE_CLASS

# ################################################################################################################################
# ################################################################################################################################

# Not to be made available externally yet.
skip_endpoint_types = (
    PUBSUB.ENDPOINT_TYPE.FTP.id,
    PUBSUB.ENDPOINT_TYPE.INTERNAL.id,
    PUBSUB.ENDPOINT_TYPE.IMAP.id,
    PUBSUB.ENDPOINT_TYPE.SERVICE.id,
    PUBSUB.ENDPOINT_TYPE.SMS_TWILIO.id,
    PUBSUB.ENDPOINT_TYPE.SMTP.id,
    PUBSUB.ENDPOINT_TYPE.SQL.id,
    PUBSUB.ENDPOINT_TYPE.WEB_SOCKETS.id, # This will never be made because WSX clients need to use APIs to subscribe
)

# ################################################################################################################################
# ################################################################################################################################

class EMAIL:
    class DEFAULT:
        TIMEOUT = 10
        PING_ADDRESS = 'invalid@invalid'
        GET_CRITERIA = 'UNSEEN'
        IMAP_DEBUG_LEVEL = 0

    class IMAP:
        class MODE:
            PLAIN = 'plain'
            SSL = 'ssl'

            def __iter__(self):
                return iter((self.PLAIN, self.SSL))

    class SMTP:
        class MODE:
            PLAIN = 'plain'
            SSL = 'ssl'
            STARTTLS = 'starttls'

            def __iter__(self):
                return iter((self.PLAIN, self.SSL, self.STARTTLS))

# ################################################################################################################################
# ################################################################################################################################

class NOTIF:
    class DEFAULT:
        CHECK_INTERVAL = 5 # In seconds
        CHECK_INTERVAL_SQL = 600 # In seconds
        NAME_PATTERN = '**'
        GET_DATA_PATTERN = '**'

    class TYPE:
        SQL = 'sql'

# ################################################################################################################################
# ################################################################################################################################

class CASSANDRA:
    class DEFAULT:
        CONTACT_POINTS = '127.0.0.1\n'
        EXEC_SIZE = 2
        PORT = 9042
        PROTOCOL_VERSION = 4
        KEYSPACE = 'not-set'

    class COMPRESSION:
        DISABLED = 'disabled'
        ENABLED_NEGOTIATED = 'enabled-negotiated'
        ENABLED_LZ4 = 'enabled-lz4'
        ENABLED_SNAPPY = 'enabled-snappy'

# ################################################################################################################################
# ################################################################################################################################

class TLS:
    # All the BEGIN/END blocks we don't want to store in logs.
    # Taken from https://github.com/openssl/openssl/blob/master/crypto/pem/pem.h
    # Note that the last one really is empty to denote 'BEGIN PRIVATE KEY' alone.
    BEGIN_END = ('ANY ', 'RSA ', 'DSA ', 'EC ', 'ENCRYPTED ', '')

    # Directories in a server's config/tls directory keeping the material
    DIR_CA_CERTS = 'ca-certs'
    DIR_KEYS_CERTS = 'keys-certs'

    class DEFAULT:
        VERSION = 'SSLv23'
        CIPHERS = 'ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:' \
                  'ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:' \
                  'ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA256'

    class VERSION:
        SSLv23  = NameId('SSLv23')
        TLSv1   = NameId('TLSv1')
        TLSv1_1 = NameId('TLSv1_1')
        TLSv1_2 = NameId('TLSv1_2')

        def __iter__(self):
            return iter((self.SSLv23, self.TLSv1, self.TLSv1_1, self.TLSv1_2))

    class CERT_VALIDATE:
        CERT_NONE     = NameId('Disabled', 'CERT_NONE')
        CERT_OPTIONAL = NameId('Optional', 'CERT_OPTIONAL')
        CERT_REQUIRED = NameId('Required', 'CERT_REQUIRED')

        def __iter__(self):
            return iter((self.CERT_NONE, self.CERT_OPTIONAL, self.CERT_REQUIRED))

class RATE_LIMIT:
    class TYPE:
        APPROXIMATE = NameId('Approximate', 'APPROXIMATE')
        EXACT       = NameId('Exact', 'EXACT')

        def __iter__(self):
            return iter((self.APPROXIMATE, self.EXACT))

    class OBJECT_TYPE:
        HTTP_SOAP = 'http_soap'
        SERVICE   = 'service'
        SEC_DEF   = 'sec_def'
        SSO_USER  = 'sso_user'

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

class STOMP:

    class DEFAULT:
        ADDRESS = '127.0.0.1:61613'
        PROTOCOL = '1.0'
        TIMEOUT = 10 # In seconds
        USERNAME = 'guest'
        ACK_MODE = 'client-individual'

# ################################################################################################################################
# ################################################################################################################################

CONTENT_TYPE = Bunch(
    JSON = 'application/json',
    PLAIN_XML = 'application/xml',
    SOAP11 = 'text/xml',
    SOAP12 = 'application/soap+xml; charset=utf-8',
)

# ################################################################################################################################
# ################################################################################################################################

class IPC:

    class ACTION:
        INVOKE_SERVICE = 'invoke-service'
        INVOKE_WORKER_STORE = 'invoke-worker-store'

    class STATUS:
        SUCCESS = 'zs'
        FAILURE = 'zf'
        LENGTH = 2 # Length of either success or failure messages

    class CONNECTOR:
        class USERNAME:
            FTP = 'zato.connector.ftp'
            IBM_MQ = 'zato.connector.wmq'
            SFTP   = 'zato.connector.sftp'

# ################################################################################################################################
# ################################################################################################################################

class WEB_SOCKET:

    AUDIT_KEY = 'wsx-connection'

    class DEFAULT:
        NEW_TOKEN_TIMEOUT = 5
        TOKEN_TTL = 3600
        FQDN_UNKNOWN = '(Unknown)'
        INTERACT_UPDATE_INTERVAL = 60 # 60 minutes = 1 hour
        PINGS_MISSED_THRESHOLD = 2
        PING_INTERVAL = 30

    class PATTERN:
        BY_EXT_ID = 'zato.by-ext-id.{}'
        BY_CHANNEL = 'zato.by-channel.{}'
        MSG_BROWSER_PREFIX = 'zato.msg-browser.' # This is used as a prefix in SQL queries
        MSG_BROWSER = MSG_BROWSER_PREFIX + '{}'

    class ACTION:
        CLIENT_RESPONSE = 'client-response'
        CREATE_SESSION = 'create-session'
        INVOKE_SERVICE = 'invoke-service'

    class OUT_MSG_TYPE:
        CONNECT = 'connect'
        MESSAGE = 'message'
        CLOSE = 'close'

    class HOOK_TYPE:
        ON_CONNECTED = 'wsx_on_connected'
        ON_DISCONNECTED = 'wsx_on_disconnected'
        ON_PUBSUB_RESPONSE = 'wsx_on_pubsub_response'
        ON_VAULT_MOUNT_POINT_NEEDED = 'wsx_on_vault_mount_point_needed'

# ################################################################################################################################
# ################################################################################################################################

class APISPEC:
    OPEN_API_V3 = 'openapi_v3'
    SOAP_12 = 'soap_12'
    NAMESPACE_NULL = ''
    DEFAULT_TAG = 'public'
    GENERIC_INVOKE_PATH = '/zato/api/invoke/{service_name}' # OpenAPI
    SOAP_INVOKE_PATH    = '/zato/api/soap/invoke'           # SOAP

# ################################################################################################################################
# ################################################################################################################################

class PADDING:
    LEFT = 'left'
    RIGHT = 'right'

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

    class CONNECTION:
        class TYPE:
            CHANNEL_FILE_TRANSFER = 'channel-file-transfer'
            CHANNEL_HL7_MLLP = 'channel-hl7-mllp'
            CLOUD_DROPBOX = 'cloud-dropbox'
            DEF_KAFKA = 'def-kafka'
            OUTCONN_HL7_MLLP = 'outconn-hl7-mllp'
            OUTCONN_IM_SLACK = 'outconn-im-slack'
            OUTCONN_IM_TELEGRAM = 'outconn-im-telegram'
            OUTCONN_LDAP = 'outconn-ldap'
            OUTCONN_MONGODB = 'outconn-mongodb'
            OUTCONN_SFTP = 'outconn-sftp'
            OUTCONN_WSX = 'outconn-wsx'

# ################################################################################################################################
# ################################################################################################################################

class AuditLog:

    class Direction:
        received = 'received'
        sent     = 'sent'

    class Default:
        max_len_messages = 50
        max_data_stored_per_message = 500 # In kilobytes

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
        POOL_SIZE = 10

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

# ################################################################################################################################
# ################################################################################################################################

class KAFKA:

    class DEFAULT:
        BROKER_VERSION = '0.9.0'
        SERVER_LIST    = '127.0.0.1:2181'

        class TIMEOUT:
            SOCKET = 1
            OFFSETS = 10

# ################################################################################################################################
# ################################################################################################################################

class TELEGRAM:
    class DEFAULT:
        ADDRESS = 'https://api.telegram.org/bot{token}/{method}'

    class TIMEOUT:
        CONNECT = 5
        INVOKE = 10

# ################################################################################################################################
# ################################################################################################################################

class SFTP:

    class DEFAULT:
        BANDWIDTH_LIMIT = 10
        BUFFER_SIZE = 32768
        COMMAND_SFTP = 'sftp'
        COMMAND_PING = 'ls .'
        PORT = 22

    class LOG_LEVEL:
        LEVEL0 = NameId('0', '0')
        LEVEL1 = NameId('1', '1')
        LEVEL2 = NameId('2', '2')
        LEVEL3 = NameId('3', '3')
        LEVEL4 = NameId('4', '4')

        def __iter__(self):
            return iter((self.LEVEL0, self.LEVEL1, self.LEVEL2, self.LEVEL3, self.LEVEL4))

        def is_valid(self, value):
            return value in (elem.id for elem in self)

    class IP_TYPE:
        IPV4 = NameId('IPv4', 'ipv4')
        IPV6 = NameId('IPv6', 'ipv6')

        def __iter__(self):
            return iter((self.IPV4, self.IPV6))

        def is_valid(self, value):
            return value in (elem.id for elem in self)

# ################################################################################################################################
# ################################################################################################################################

class DROPBOX:
    class DEFAULT:
        MAX_RETRIES_ON_ERROR = 5
        MAX_RETRIES_ON_RATE_LIMIT = None
        OAUTH2_ACCESS_TOKEN_EXPIRATION = None
        POOL_SIZE = 10
        TIMEOUT = 60
        USER_AGENT = None

# ################################################################################################################################
# ################################################################################################################################

class JSON_RPC:
    class PREFIX:
        CHANNEL = 'json.rpc.channel'
        OUTGOING = 'json.rpc.outconn'

# ################################################################################################################################
# ################################################################################################################################

class CONFIG_FILE:
    USER_DEFINED = 'user-defined'

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

class FILE_TRANSFER:

    SCHEDULER_SERVICE = 'pub.zato.channel.file-transfer.handler'

    class DEFAULT:
        FILE_PATTERNS = '*'
        ENCODING = 'utf-8'

    class SOURCE_TYPE:
        LOCAL = NameId('Local', 'local')
        FTP = NameId('FTP', 'ftp')
        SFTP = NameId('SFTP', 'sftp')

        def __iter__(self):
            return iter((self.LOCAL, self.FTP, self.SFTP))

    class SOURCE_TYPE_IMPL:
        LOCAL_INOTIFY  = 'local-inotify'
        LOCAL_SNAPSHOT = 'local-snapshot'

# ################################################################################################################################
# ################################################################################################################################

class HL7:

    class Default:
        """ Default values for HL7 objects.
        """
        # Default TCP port for MLLP connections
        address = '0.0.0.0:30901'

        # Assume that UTF-8 is sent in by default
        data_encoding = 'utf-8'

        # Each message may be of at most that many bytes
        max_msg_size = '1_000_000'

        # How many seconds to wait for HL7 MLLP responses when invoking a remote end
        max_wait_time = 60

        # At most that many bytes will be read from a socket at a time
        read_buffer_size = 2048

        # We wait at most that many milliseconds for data from a socket in each iteration of the main loop
        recv_timeout = 250

        # At what level to log messages (Python logging)
        logging_level = 'INFO'

        # Should we store the contents of messages in logs (Python logging)
        should_log_messages = False

        # How many concurrent outgoing connections we allow
        pool_size = 10

        # An MLLP message may begin with these bytes ..
        start_seq = '0b'

        # .. and end with these below.
        end_seq = '1c 0d'

    class Const:
        """ Various HL7-related constants.
        """

        class Version:

            # A generic v2 message, without an indication of a specific release.
            v2 = NameId('HL7 v2', 'hl7-v2')

            def __iter__(self):
                return iter((self.v2,))

        class LoggingLevel:
            Info  = NameId('INFO',  'INFO')
            Debug = NameId('DEBUG', 'DEBUG')

            def __iter__(self):
                return iter((self.Info, self.Debug))

        class ImplClass:
            hl7apy = 'hl7apy'
            zato   = 'Zato'

# ################################################################################################################################
# ################################################################################################################################

# TODO: SIMPLE_IO.FORMAT should be removed with in favour of plain DATA_FORMAT
class SIMPLE_IO:

    class FORMAT(Attrs):
        JSON = DATA_FORMAT.JSON
        XML = DATA_FORMAT.XML

    COMMON_FORMAT = OrderedDict()
    COMMON_FORMAT[DATA_FORMAT.JSON] = 'JSON'
    COMMON_FORMAT[DATA_FORMAT.XML] = 'XML'

    HTTP_SOAP_FORMAT = OrderedDict()
    HTTP_SOAP_FORMAT[DATA_FORMAT.JSON] = 'JSON'
    HTTP_SOAP_FORMAT[DATA_FORMAT.XML] = 'XML'
    HTTP_SOAP_FORMAT[HL7.Const.Version.v2.id] = HL7.Const.Version.v2.name

# ################################################################################################################################
# ################################################################################################################################

class UNITTEST:
    SQL_ENGINE = 'zato+unittest'
    HTTP       = 'zato+unittest'
    VAULT_URL  = 'https://zato+unittest'

class HotDeploy:
    UserPrefix = 'hot-deploy.user'

# ################################################################################################################################
# ################################################################################################################################

class ZatoKVDB:

    SlowResponsesName  = 'zato.service.slow_responses'
    UsageSamplesName   = 'zato.service.usage_samples'
    CurrentUsageName   = 'zato.service.current_usage'
    PubSubMetadataName = 'zato.pubsub.metadata'

    SlowResponsesPath  = SlowResponsesName  + '.json'
    UsageSamplesPath   = UsageSamplesName   + '.json'
    CurrentUsagePath   = CurrentUsageName   + '.json'
    PubSubMetadataPath = PubSubMetadataName + '.json'

    DefaultSyncThreshold = 3_000
    DefaultSyncInterval  = 3

# ################################################################################################################################
# ################################################################################################################################

class Stats:

    # This is in milliseconds, for how long do we keep old statistics in persistent storage. Defaults to two years.
    # 1k ms * 60 s * 60 min * 24 hours * 365 days * 2 years = 94_608_000_000 milliseconds (or two years).
    # We use milliseconds because that makes it easier to construct tests.
    MaxRetention = 1000 * 60 * 60 * 24 * 365 * 2

    # By default, statistics will be aggregated into time buckets of that duration
    DefaultAggrTimeFreq = '5min' # Five minutes

    # We always tabulate by object_id (e.g. service name)
    TabulateAggr = 'object_id'

# ################################################################################################################################
# ################################################################################################################################

class StatsKey:
    CurrentValue = 'current_value'

    PerKeyMin   = 'min'
    PerKeyMax   = 'max'
    PerKeyMean  = 'mean'

    PerKeyValue         = 'value'
    PerKeyLastTimestamp = 'last_timestamp'
    PerKeyLastDuration  = 'last_duration'

# ################################################################################################################################
# ################################################################################################################################

class SSO:
    class EmailTemplate:
        SignupConfirm = 'signup-confirm.txt'
        SignupWelcome = 'signup-welcome.txt'
        PasswordResetLink = 'password-reset-link.txt'

# ################################################################################################################################
# ################################################################################################################################

ZATO_INFO_FILE = '.zato-info'

# ################################################################################################################################
# ################################################################################################################################

class SourceCodeInfo:
    """ A bunch of attributes dealing the service's source code.
    """
    __slots__ = 'source', 'source_html', 'len_source', 'path', 'hash', 'hash_method', 'server_name'

    def __init__(self):
        self.source = ''        # type: str
        self.source_html = ''   # type: str
        self.len_source = 0     # type: int
        self.path = None        # type: str
        self.hash = None        # type: str
        self.hash_method = None # type: str
        self.server_name = None # type: str

# ################################################################################################################################
# ################################################################################################################################

class StatsElem:
    """ A single element of a statistics query result concerning a particular service.
    All values make sense only within the time interval of the original query, e.g. a 'min_resp_time'
    may be 18 ms in this element because it represents statistics regarding, say,
    the last hour yet in a different period the 'min_resp_time' may be a completely
    different value. Likewise, 'all' in the description of parameters below means
    'all that matched given query criteria' rather than 'all that ever existed'.

    service_name - name of the service this element describes
    usage - how many times the service has been invoked
    mean - an arithmetical average of all the mean response times  (in ms)
    rate - usage rate in requests/s (up to 1 decimal point)
    time - time spent by this service on processing the messages (in ms)
    usage_trend - a CSV list of values representing the service usage
    usage_trend_int - a list of integers representing the service usage
    mean_trend - a CSV list of values representing mean response times (in ms)
    mean_trend_int - a list of integers representing mean response times (in ms)
    min_resp_time - minimum service response time (in ms)
    max_resp_time - maximum service response time (in ms)
    all_services_usage - how many times all the services have been invoked
    all_services_time - how much time all the services spent on processing the messages (in ms)
    mean_all_services - an arithmetical average of all the mean response times  of all services (in ms)
    usage_perc_all_services - this service's usage as a percentage of all_services_usage (up to 2 decimal points)
    time_perc_all_services - this service's share as a percentage of all_services_time (up to 2 decimal points)
    expected_time_elems - an OrderedDict of all the time slots mapped to a mean time and rate
    temp_rate - a temporary place for keeping request rates, needed to get a weighted mean of uneven execution periods
    temp_mean - just like temp_rate but for mean response times
    temp_mean_count - how many periods containing a mean rate there were
    """
    def __init__(self, service_name=None, mean=None):
        self.service_name = service_name
        self.usage = 0
        self.mean = mean
        self.rate = 0.0
        self.time = 0
        self.usage_trend_int = []
        self.mean_trend_int = []
        self.min_resp_time = maxsize # Assuming that there sure will be at least one response time lower than that
        self.max_resp_time = 0
        self.all_services_usage = 0
        self.all_services_time = 0
        self.mean_all_services = 0
        self.usage_perc_all_services = 0
        self.time_perc_all_services = 0
        self.expected_time_elems = OrderedDict()
        self.temp_rate = 0
        self.temp_mean = 0
        self.temp_mean_count = 0

    def get_attrs(self, ignore=[]):
        for attr in dir(self):
            if attr.startswith('__') or attr.startswith('temp_') or callable(getattr(self, attr)) or attr in ignore:
                continue
            yield attr

    def to_dict(self, ignore=None):
        if not ignore:
            ignore = ['expected_time_elems', 'mean_trend_int', 'usage_trend_int']
        return {attr: getattr(self, attr) for attr in self.get_attrs(ignore)}

    @staticmethod
    def from_json(item):
        stats_elem = StatsElem()
        for k, v in item.items():
            setattr(stats_elem, k, v)

        return stats_elem

    @staticmethod
    def from_xml(item):
        stats_elem = StatsElem()
        for child in item.getchildren():
            setattr(stats_elem, child.xpath('local-name()'), child.pyval)

        return stats_elem

    def __repr__(self):
        buff = StringIO()
        buff.write('<{} at {} '.format(self.__class__.__name__, hex(id(self))))

        attrs = ('{}=[{}]'.format(attr, getattr(self, attr)) for attr in self.get_attrs())
        buff.write(', '.join(attrs))

        buff.write('>')

        value = buff.getvalue()
        buff.close()

        return value

    def __iadd__(self, other):
        self.max_resp_time = max(self.max_resp_time, other.max_resp_time)
        self.min_resp_time = min(self.min_resp_time, other.min_resp_time)
        self.usage += other.usage

        return self

    def __bool__(self):
        return bool(self.service_name) # Empty stats_elems won't have a service name set

# ################################################################################################################################
# ################################################################################################################################

class SMTPMessage:
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

class IDEDeploy:
    Username = 'ide_publisher'

# ################################################################################################################################
# ################################################################################################################################

class IMAPMessage:
    def __init__(self, uid, conn, data):
        self.uid = uid
        self.conn = conn
        self.data = data

    def __repr__(self):
        return '<{} at {}, uid:`{}`, conn.config:`{}`>'.format(
            self.__class__.__name__, hex(id(self)), self.uid, self.conn.config_no_sensitive)

    def delete(self):
        self.conn.delete(self.uid)

    def mark_seen(self):
        self.conn.mark_seen(self.uid)

# ################################################################################################################################
# ################################################################################################################################

class IBMMQCallData:
    """ Metadata for information returned by IBM MQ in response to underlying MQPUT calls.
    """
    __slots__ = ('msg_id', 'correlation_id')

    def __init__(self, msg_id, correlation_id):
        self.msg_id = msg_id
        self.correlation_id = correlation_id

# For compatibility with Zato < 3.2
WebSphereMQCallData = IBMMQCallData

# ################################################################################################################################
# ################################################################################################################################

default_internal_modules = {
    'zato.server.service.internal': True,
    'zato.server.service.internal.apispec': True,
    'zato.server.service.internal.audit_log': True,
    'zato.server.service.internal.cache.builtin': True,
    'zato.server.service.internal.cache.builtin.entry': True,
    'zato.server.service.internal.cache.builtin.pubapi': True,
    'zato.server.service.internal.cache.memcached': True,
    'zato.server.service.internal.channel.amqp_': True,
    'zato.server.service.internal.channel.file_transfer': True,
    'zato.server.service.internal.channel.jms_wmq': True,
    'zato.server.service.internal.channel.json_rpc': True,
    'zato.server.service.internal.channel.web_socket': True,
    'zato.server.service.internal.channel.web_socket.cleanup': True,
    'zato.server.service.internal.channel.web_socket.client': True,
    'zato.server.service.internal.channel.web_socket.subscription': True,
    'zato.server.service.internal.channel.zmq': True,
    'zato.server.service.internal.cloud.aws.s3': True,
    'zato.server.service.internal.connector.amqp_': True,
    'zato.server.service.internal.crypto': True,
    'zato.server.service.internal.definition.amqp_': True,
    'zato.server.service.internal.definition.cassandra': True,
    'zato.server.service.internal.definition.jms_wmq': True,
    'zato.server.service.internal.email.imap': True,
    'zato.server.service.internal.email.smtp': True,
    'zato.server.service.internal.generic.connection': True,
    'zato.server.service.internal.helpers': True,
    'zato.server.service.internal.hot_deploy': True,
    'zato.server.service.internal.ide_deploy': True,
    'zato.server.service.internal.info': True,
    'zato.server.service.internal.http_soap': True,
    'zato.server.service.internal.kv_data': True,
    'zato.server.service.internal.kvdb': True,
    'zato.server.service.internal.kvdb.data_dict.dictionary': True,
    'zato.server.service.internal.kvdb.data_dict.impexp': True,
    'zato.server.service.internal.kvdb.data_dict.translation': True,
    'zato.server.service.internal.message.namespace': True,
    'zato.server.service.internal.message.xpath': True,
    'zato.server.service.internal.message.json_pointer': True,
    'zato.server.service.internal.notif': True,
    'zato.server.service.internal.notif.sql': True,
    'zato.server.service.internal.outgoing.amqp_': True,
    'zato.server.service.internal.outgoing.ftp': True,
    'zato.server.service.internal.outgoing.jms_wmq': True,
    'zato.server.service.internal.outgoing.odoo': True,
    'zato.server.service.internal.outgoing.redis': True,
    'zato.server.service.internal.outgoing.sql': True,
    'zato.server.service.internal.outgoing.sap': True,
    'zato.server.service.internal.outgoing.sftp': True,
    'zato.server.service.internal.outgoing.zmq': True,
    'zato.server.service.internal.pattern': True,
    'zato.server.service.internal.pickup': True,
    'zato.server.service.internal.pattern.invoke_retry': True,
    'zato.server.service.internal.pubsub': True,
    'zato.server.service.internal.pubsub.delivery': True,
    'zato.server.service.internal.pubsub.endpoint': True,
    'zato.server.service.internal.pubsub.hook': True,
    'zato.server.service.internal.pubsub.message': True,
    'zato.server.service.internal.pubsub.migrate': True,
    'zato.server.service.internal.pubsub.pubapi': True,
    'zato.server.service.internal.pubsub.publish': True,
    'zato.server.service.internal.pubsub.subscription': True,
    'zato.server.service.internal.pubsub.queue': True,
    'zato.server.service.internal.pubsub.task': True,
    'zato.server.service.internal.pubsub.task.delivery': True,
    'zato.server.service.internal.pubsub.task.delivery.message': True,
    'zato.server.service.internal.pubsub.task.delivery.server': True,
    'zato.server.service.internal.pubsub.task.sync': True,
    'zato.server.service.internal.pubsub.topic': True,
    'zato.server.service.internal.query.cassandra': True,
    'zato.server.service.internal.scheduler': True,
    'zato.server.service.internal.search.es': True,
    'zato.server.service.internal.search.solr': True,
    'zato.server.service.internal.security': True,
    'zato.server.service.internal.security.apikey': True,
    'zato.server.service.internal.security.aws': True,
    'zato.server.service.internal.security.basic_auth': True,
    'zato.server.service.internal.security.jwt': True,
    'zato.server.service.internal.security.ntlm': True,
    'zato.server.service.internal.security.oauth': True,
    'zato.server.service.internal.security.rbac': True,
    'zato.server.service.internal.security.rbac.client_role': True,
    'zato.server.service.internal.security.rbac.permission': True,
    'zato.server.service.internal.security.rbac.role': True,
    'zato.server.service.internal.security.rbac.role_permission': True,
    'zato.server.service.internal.security.tls.ca_cert': True,
    'zato.server.service.internal.security.tls.channel': True,
    'zato.server.service.internal.security.tls.key_cert': True,
    'zato.server.service.internal.security.wss': True,
    'zato.server.service.internal.security.vault.connection': True,
    'zato.server.service.internal.security.vault.policy': True,
    'zato.server.service.internal.security.xpath': True,
    'zato.server.service.internal.server': True,
    'zato.server.service.internal.service': True,
    'zato.server.service.internal.sms': True,
    'zato.server.service.internal.sms.twilio': True,
    'zato.server.service.internal.sso': True,
    'zato.server.service.internal.sso.cleanup': True,
    'zato.server.service.internal.sso.password_reset': True,
    'zato.server.service.internal.sso.session': True,
    'zato.server.service.internal.sso.session_attr': True,
    'zato.server.service.internal.sso.signup': True,
    'zato.server.service.internal.sso.user': True,
    'zato.server.service.internal.sso.user_attr': True,
    'zato.server.service.internal.stats': True,
    'zato.server.service.internal.stats.summary': True,
    'zato.server.service.internal.stats.trends': True,
    'zato.server.service.internal.updates': True,
}

# ################################################################################################################################
# ################################################################################################################################
