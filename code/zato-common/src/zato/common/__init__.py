# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import os
from collections import OrderedDict
from copy import deepcopy
from cStringIO import StringIO
from httplib import responses
from string import Template
from sys import maxint
from traceback import format_exc

# boto
from boto.s3.key import Key

# Bunch
from bunch import Bunch

# candv
from candv import Constants, ValueConstant

# lxml
from lxml import etree
from lxml.objectify import ObjectPath as _ObjectPath


# ##############################################################################
# Version
# ##############################################################################

try:
    curdir = os.path.dirname(os.path.abspath(__file__))
    _version_py = os.path.normpath(os.path.join(curdir, '..', '..', '..', '..', '.version.py'))
    _locals = {}
    execfile(_version_py, _locals)
    version = _locals['version']
except IOError:
    version = '2.0.7'

# The namespace for use in all Zato's own services.
zato_namespace = 'https://zato.io/ns/20130518'
zato_ns_map = {None: zato_namespace}

# SQL ODB
engine_def = '{engine}://{username}:{password}@{host}:{port}/{db_name}'
engine_def_sqlite = 'sqlite:///{sqlite_path}'

# Convenience access functions and constants.

soapenv11_namespace = 'http://schemas.xmlsoap.org/soap/envelope/'
soapenv12_namespace = 'http://www.w3.org/2003/05/soap-envelope'

wsse_namespace = 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd'
wsu_namespace = 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd'

common_namespaces = {
    'soapenv':soapenv11_namespace,
    'wsse':wsse_namespace,
    'wsu':wsu_namespace,
    'zato':zato_namespace
}

soap_doc = Template("""<soap:Envelope xmlns:soap='%s'><soap:Body>$body</soap:Body></soap:Envelope>""" % soapenv11_namespace)

soap_body_path = '/soapenv:Envelope/soapenv:Body'
soap_body_xpath = etree.XPath(soap_body_path, namespaces=common_namespaces)

soap_fault_path = '/soapenv:Envelope/soapenv:Body/soapenv:Fault'
soap_fault_xpath = etree.XPath(soap_fault_path, namespaces=common_namespaces)

wsse_password_type_text = 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText'
supported_wsse_password_types = (wsse_password_type_text,)

wsse_username_path = '/soapenv:Envelope/soapenv:Header/wsse:Security/wsse:UsernameToken/wsse:Username'
wsse_username_xpath = etree.XPath(wsse_username_path, namespaces=common_namespaces)

wsse_password_path = '/soapenv:Envelope/soapenv:Header/wsse:Security/wsse:UsernameToken/wsse:Password'
wsse_password_xpath = etree.XPath(wsse_password_path, namespaces=common_namespaces)

wsse_password_type_path = '/soapenv:Envelope/soapenv:Header/wsse:Security/wsse:UsernameToken/wsse:Password/@Type'
wsse_password_type_xpath = etree.XPath(wsse_password_type_path, namespaces=common_namespaces)

wsse_nonce_path = '/soapenv:Envelope/soapenv:Header/wsse:Security/wsse:UsernameToken/wsse:Nonce'
wsse_nonce_xpath = etree.XPath(wsse_nonce_path, namespaces=common_namespaces)

wsu_username_created_path = '/soapenv:Envelope/soapenv:Header/wsse:Security/wsse:UsernameToken/wsu:Created'
wsu_username_created_xpath = etree.XPath(wsu_username_created_path, namespaces=common_namespaces)

wsu_expires_path = '/soapenv:Envelope/soapenv:Header/wsse:Security/wsu:Timestamp/wsu:Expires'
wsu_expires_xpath = etree.XPath(wsu_expires_path, namespaces=common_namespaces)

wsse_username_objectify = '{}Security'.format(wsse_namespace)
wsse_username_token_objectify = '{}UsernameToken'.format(wsse_namespace)

zato_data_path = soap_data_path = '/soapenv:Envelope/soapenv:Body/*[1]'
zato_data_xpath = soap_data_xpath = etree.XPath(zato_data_path, namespaces=common_namespaces)

zato_result_path = '//zato:zato_env/zato:result'
zato_result_xpath = etree.XPath(zato_result_path, namespaces=common_namespaces)

zato_cid_path = '//zato:zato_env/zato:cid'
zato_cid_xpath = etree.XPath(zato_result_path, namespaces=common_namespaces)

zato_details_path = '//zato:zato_env/zato:details'
zato_details_xpath = etree.XPath(zato_details_path, namespaces=common_namespaces)

SECRET_SHADOW = '******'

# TRACE1 logging level, even more details than DEBUG
TRACE1 = 6

SECONDS_IN_DAY = 86400 # 60 seconds * 60 minutes * 24 hours (and we ignore leap seconds)

scheduler_date_time_format = '%Y-%m-%d %H:%M:%S'
soap_date_time_format = '%Y-%m-%dT%H:%M:%S.%fZ'

ACCESS_LOG_DT_FORMAT = '%d/%b/%Y:%H:%M:%S %z'

# TODO: Classes that have this attribute defined (no matter the value) will not be deployed
# onto servers.
DONT_DEPLOY_ATTR_NAME = 'zato_dont_import'

# A convenient constant used in several places, simplifies passing around
# arguments which are, well, not given (as opposed to being None, an empty string etc.)
ZATO_NOT_GIVEN = b'ZATO_NOT_GIVEN'

# Also used in a couple of places.
ZATO_OK = 'ZATO_OK'
ZATO_ERROR = 'ZATO_ERROR'
ZATO_WARNING = 'ZATO_WARNING'
ZATO_NONE = b'ZATO_NONE'

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

# https://tools.ietf.org/html/rfc6585
TOO_MANY_REQUESTS = 429

HTTP_RESPONSES = deepcopy(responses)
HTTP_RESPONSES[TOO_MANY_REQUESTS] = 'Too Many Requests'

# Pattern matching order
TRUE_FALSE = 'true_false'
FALSE_TRUE = 'false_true'

# Queries to use in pinging the databases.
ping_queries = {
    'access': 'SELECT 1',
    'db2': 'SELECT current_date FROM sysibm.sysdummy1',
    'firebird': 'SELECT current_timestamp FROM rdb$database',
    'informix': 'SELECT 1 FROM systables WHERE tabid=1',
    'mssql': 'SELECT 1',
    'mysql+pymysql': 'SELECT 1+1',
    'oracle': 'SELECT 1 FROM dual',
    'postgresql': 'SELECT 1',
    'postgresql+pg8000': 'SELECT 1',
    'sqlite': 'SELECT 1',
}

# All URL types Zato understands.
class URL_TYPE(object):
    SOAP = 'soap'
    PLAIN_HTTP = 'plain_http'

    class __metaclass__(type):
        def __iter__(self):
            return iter((self.SOAP, self.PLAIN_HTTP))

# Whether WS-Security passwords are transmitted in clear-text or not.
ZATO_WSS_PASSWORD_CLEAR_TEXT = Bunch(name='clear_text', label='Clear text')
ZATO_WSS_PASSWORD_TYPES = {
    ZATO_WSS_PASSWORD_CLEAR_TEXT.name:ZATO_WSS_PASSWORD_CLEAR_TEXT.label,
}

ZATO_FIELD_OPERATORS = {
    'is-equal-to': '==',
    'is-not-equal-to': '!=',
}

ZMQ_OUTGOING_TYPES = ('PUSH', 'PUB')
ZMQ_CHANNEL_TYPES = ('PULL', 'SUB')

ZATO_ODB_POOL_NAME = 'ZATO_ODB'

SOAP_VERSIONS = ('1.1', '1.2')
SOAP_CHANNEL_VERSIONS = ('1.1',)


class SEARCH:
    class ES:
        class DEFAULTS(Constants):
            BODY_AS = ValueConstant('POST')
            HOSTS = ValueConstant('127.0.0.1:9200\n')

    class SOLR:
        class DEFAULTS(Constants):
            ADDRESS = ValueConstant('http://127.0.0.1:8983/solr')
            PING_PATH = ValueConstant('/solr/admin/ping')
            TIMEOUT = ValueConstant('10')
            POOL_SIZE = ValueConstant('5')

class SEC_DEF_TYPE:
    APIKEY = 'apikey'
    AWS = 'aws'
    BASIC_AUTH = 'basic_auth'
    NTLM = 'ntlm'
    OAUTH = 'oauth'
    OPENSTACK = 'openstack'
    TECH_ACCOUNT = 'tech_acc'
    TLS_CHANNEL_SEC = 'tls_channel_sec'
    TLS_KEY_CERT = 'tls_key_cert'
    WSS = 'wss'
    XPATH_SEC = 'xpath_sec'

SEC_DEF_TYPE_NAME = {
    SEC_DEF_TYPE.APIKEY: 'API key',
    SEC_DEF_TYPE.AWS: 'AWS',
    SEC_DEF_TYPE.BASIC_AUTH: 'HTTP Basic Auth',
    SEC_DEF_TYPE.NTLM: 'NTLM',
    SEC_DEF_TYPE.OAUTH: 'OAuth 1.0',
    SEC_DEF_TYPE.OPENSTACK: 'OpenStack',
    SEC_DEF_TYPE.TECH_ACCOUNT: 'Tech account',
    SEC_DEF_TYPE.WSS: 'WS-Security',
    SEC_DEF_TYPE.TLS_CHANNEL_SEC: 'TLS channel',
    SEC_DEF_TYPE.TLS_KEY_CERT: 'TLS key/cert',
    SEC_DEF_TYPE.XPATH_SEC: 'XPath',
}

# Name of the scheduler's job that will ensure a singleton server is always
# available in a cluster.
ENSURE_SINGLETON_JOB = 'zato.server.ensure-cluster-wide-singleton'

DEFAULT_STATS_SETTINGS = {
    'scheduler_per_minute_aggr_interval':60,
    'scheduler_raw_times_interval':90,
    'scheduler_raw_times_batch':99999,
    'atttention_slow_threshold':2000,
    'atttention_top_threshold':10,
}

class BATCH_DEFAULTS:
    PAGE_NO = 1
    SIZE = 25
    MAX_SIZE = 1000

class NameId(object):
    """ Wraps both an attribute's name and its ID.
    """
    def __init__(self, name, id):
        self.name = name
        self.id = id

class NotGiven(object):
    pass # A marker for lazily-initialized attributes

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

class DATA_FORMAT(Attrs):
    DICT = 'dict'
    XML = 'xml'
    JSON = 'json'
    CSV = 'csv'
    POST = 'post'

    class __metaclass__(type):
        def __iter__(self):
            # Note that DICT isn't included because it's never exposed to external world as-is,
            # it's only used so that services can invoke each other directly
            return iter((self.XML, self.JSON, self.CSV, self.POST))

# TODO: SIMPLE_IO.FORMAT should be done away with in favour of plain DATA_FORMAT
class SIMPLE_IO:
    class FORMAT(Attrs):
        XML = DATA_FORMAT.XML
        JSON = DATA_FORMAT.JSON

    class INT_PARAMETERS:
        VALUES = ['id']
        SUFFIXES = ['_id', '_count', '_size', '_timeout']

    class BOOL_PARAMETERS:
        SUFFIXES = ['is_', 'needs_', 'should_']

class DEPLOYMENT_STATUS(Attrs):
    DEPLOYED = 'deployed'
    AWAITING_DEPLOYMENT = 'awaiting-deployment'
    IGNORED = 'ignored'

class SERVER_JOIN_STATUS(Attrs):
    ACCEPTED = 'accepted'

class SERVER_UP_STATUS(Attrs):
    RUNNING = 'running'
    CLEAN_DOWN = 'clean-down'

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

class SCHEDULER:

    class JOB_TYPE(Attrs):
        ONE_TIME = 'one_time'
        INTERVAL_BASED = 'interval_based'
        CRON_STYLE = 'cron_style'

    class ON_MAX_RUNS_REACHED:
        DELETE = 'delete'
        INACTIVATE = 'inactivate'

class CHANNEL(Attrs):
    AMQP = 'amqp'
    AUDIT = 'audit'                                       # New in 2.0
    DELIVERY = 'delivery'                                 # New in 2.0
    FANOUT_CALL = 'fanout-call'                           # New in 2.0
    FANOUT_ON_FINAL = 'fanout-on-final'                   # New in 2.0
    FANOUT_ON_TARGET = 'fanout-on-target'                 # New in 2.0
    HTTP_SOAP = 'http-soap'
    INTERNAL_CHECK = 'internal-check'                     # New in 2.0
    INVOKE = 'invoke'
    INVOKE_ASYNC = 'invoke-async'
    INVOKE_ASYNC_CALLBACK = 'invoke-async-callback'       # New in 2.0
    JMS_WMQ = 'jms-wmq'
    NOTIFIER_RUN = 'notifier-run'                         # New in 2.0
    NOTIFIER_TARGET = 'notifier-target'                   # New in 2.0
    PARALLEL_EXEC_CALL = 'parallel-exec-call'             # New in 2.0
    PARALLEL_EXEC_ON_TARGET = 'parallel-exec-on-target'   # New in 2.0
    PUBLISH = 'publish'                                   # New in 2.0
    SCHEDULER = 'scheduler'
    SCHEDULER_AFTER_ONE_TIME = 'scheduler-after-one-time' # New in 2.0
    STARTUP_SERVICE = 'startup-service'                   # New in 2.0
    WORKER = 'worker'                                     # New in 2.0
    ZMQ = 'zmq'

class INVOCATION_TARGET(Attrs):
    CHANNEL_AMQP = 'channel-amqp'
    CHANNEL_WMQ = 'channel-wmq'
    CHANNEL_ZMQ = 'channel-zmq'
    OUTCONN_AMQP = 'outconn-amqp'
    OUTCONN_WMQ = 'outconn-wmq'
    OUTCONN_ZMQ = 'outconn-zmq'
    SERVICE = 'service'

class DELIVERY_HISTORY_ENTRY(Attrs):
    ENTERED_IN_DOUBT = b'entered-in-doubt'
    ENTERED_IN_PROGRESS = b'entered-in-progress'
    ENTERED_CONFIRMED = b'entered-confirmed'
    ENTERED_FAILED = b'entered-failed'
    ENTERED_RETRY = b'entered-retry'
    NONE = b'(None)'
    SENT_FROM_SOURCE = b'sent-from-source'
    SENT_FROM_SOURCE_RESUBMIT = b'sent-from-source-resubmit'
    SENT_FROM_SOURCE_RESUBMIT_AUTO = b'sent-from-source-resubmit-auto'
    TARGET_OK = b'target-ok'
    TARGET_FAILURE = b'target-failure'
    UPDATED = b'updated'

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

class DELIVERY_COUNTERS(Attrs):
    IN_DOUBT = 'in_doubt_count'
    IN_PROGRESS = 'in_progress_count'
    CONFIRMED = 'confirmed_count'
    FAILED = 'failed_count'
    TOTAL = 'total_count'

class DELIVERY_CALLBACK_INVOKER(Attrs):
    SOURCE = 'source'
    TARGET = 'target'

class BROKER:
    DEFAULT_EXPIRATION = 15 # In seconds

class MISC:
    DEFAULT_HTTP_TIMEOUT=10
    DEFAULT_AUDIT_BACK_LOG = 24 * 60 # 24 hours * 60 days ≅ 2 months
    DEFAULT_AUDIT_MAX_PAYLOAD = 0 # Using 0 means there's no limit
    OAUTH_SIG_METHODS = ['HMAC-SHA1', 'PLAINTEXT']
    PIDFILE = 'pidfile'
    SEPARATOR = ':::'

class ADAPTER_PARAMS:
    APPLY_AFTER_REQUEST = 'apply-after-request'
    APPLY_BEFORE_REQUEST = 'apply-before-request'

class AUDIT_LOG:
    REPLACE_WITH = SECRET_SHADOW

class INFO_FORMAT:
    DICT = 'dict'
    TEXT = 'text'
    JSON = 'json'
    YAML = 'yaml'

class MSG_MAPPER:
    DICT_TO_DICT = 'dict-to-dict'
    DICT_TO_XML = 'dict-to-xml'
    XML_TO_DICT = 'xml-to-dict'
    XML_TO_XML = 'xml-to-xml'

class CLOUD:
    class OPENSTACK:
        class SWIFT:
            class DEFAULTS:
                AUTH_VERSION = '1'
                BACKOFF_STARTING = 1
                BACKOFF_MAX = 64
                POOL_SIZE = 5
                RETRIES = 5

    class AWS:
        class S3:
            class STORAGE_CLASS:
                STANDARD = 'STANDARD'
                REDUCED_REDUNDANCY = 'REDUCED_REDUNDANCY'
                GLACIER = 'GLACIER'
                DEFAULT = STANDARD

                class __metaclass__(type):
                    def __iter__(self):
                        return iter((self.STANDARD, self.REDUCED_REDUNDANCY, self.GLACIER))

            class DEFAULTS:
                ADDRESS = 'https://s3.amazonaws.com/'
                CONTENT_TYPE = Key.DefaultContentType
                DEBUG_LEVEL = 0
                POOL_SIZE = 5
                PROVIDER = 'aws'

class URL_PARAMS_PRIORITY:
    PATH_OVER_QS = 'path-over-qs'
    QS_OVER_PATH = 'qs-over-path'
    DEFAULT = QS_OVER_PATH

    class __metaclass__(type):
        def __iter__(self):
            return iter((self.PATH_OVER_QS, self.QS_OVER_PATH, self.DEFAULT))

class PARAMS_PRIORITY:
    CHANNEL_PARAMS_OVER_MSG = 'channel-params-over-msg'
    MSG_OVER_CHANNEL_PARAMS = 'msg-over-channel-params'
    DEFAULT = CHANNEL_PARAMS_OVER_MSG

    class __metaclass__(type):
        def __iter__(self):
            return iter((self.CHANNEL_PARAMS_OVER_MSG, self.MSG_OVER_CHANNEL_PARAMS, self.DEFAULT))

class NONCE_STORE:
    KEY_PATTERN = 'zato:nonce-store:{}:{}' # E.g. zato:nonce-store:oauth:27
    DEFAULT_MAX_LOG = 25000

class MSG_PATTERN_TYPE:
    JSON_POINTER = NameId('JSONPointer', 'json-pointer')
    XPATH = NameId('XPath', 'xpath')

    class __metaclass__(type):
        def __iter__(self):
            return iter((self.JSON_POINTER, self.XPATH))

class HTTP_SOAP_SERIALIZATION_TYPE:
    STRING_VALUE = NameId('String', 'string')
    SUDS = NameId('Suds', 'suds')
    DEFAULT = STRING_VALUE

    class __metaclass__(type):
        def __iter__(self):
            return iter((self.STRING_VALUE, self.SUDS))

class PUB_SUB:
    PRIORITY_MIN = 1
    PRIORITY_MAX = 9

    DEFAULT_PRIORITY = 5
    DEFAULT_MIME_TYPE = 'text/plain'
    DEFAULT_EXPIRATION = 60.0 # In seconds
    DEFAULT_GET_MAX_BATCH_SIZE = 100
    DEFAULT_IS_FIFO = True
    DEFAULT_MAX_DEPTH = 500
    DEFAULT_MAX_BACKLOG = 1000

    class QUEUE_TYPE:
        MESSAGE = 'message'
        IN_FLIGHT = 'in-flight'

    class GET_DIR:
        FIFO = 'fifo'
        LIFO = 'lifo'

    class MOVE_RESULT:
        MOVED = 'moved'
        OVERFLOW = 'overflow'

    class CALLBACK_TYPE:
        OUTCONN_PLAIN_HTTP = 'outconn-plain-http'
        OUTCONN_SOAP = 'outconn-soap'

    class DELIVERY_MODE:
        PULL = NameId('Pull', 'pull')
        CALLBACK_URL = NameId('Callback URL', 'callback-url')

        class __metaclass__(type):
            def __iter__(self):
                return iter((self.PULL, self.CALLBACK_URL))

    class MESSAGE_SOURCE:
        TOPIC = NameId('Topic', 'topic')
        CONSUMER_QUEUE = NameId('Consumer queue', 'consumer-queue')

        class __metaclass__(type):
            def __iter__(self):
                return iter((self.TOPIC, self.CONSUMER_QUEUE))

    class GET_FORMAT:
        OBJECT = NameId('Object', 'object')
        JSON = NameId('JSON', 'json')
        XML = NameId('XML', 'xml')
        DEFAULT = JSON

        class __metaclass__(type):
            def __iter__(self):
                return iter((self.OBJECT, self.JSON, self.XML))

    class URL_ITEM_TYPE:
        TOPIC = NameId('Topic', 'topic')
        MESSAGES = NameId('Messages', 'msg')

        class __metaclass__(type):
            def __iter__(self):
                return iter((self.TOPIC.id, self.MESSAGES.id))

class EMAIL:
    class DEFAULT:
        TIMEOUT = 10
        PING_ADDRESS = 'invalid@invalid'
        GET_CRITERIA = 'UNSEEN'
        IMAP_DEBUG_LEVEL = 0

    class IMAP:
        class MODE(Constants):
            PLAIN = ValueConstant('plain')
            SSL = ValueConstant('ssl')

    class SMTP:
        class MODE(Constants):
            PLAIN = ValueConstant('plain')
            SSL = ValueConstant('ssl')
            STARTTLS = ValueConstant('starttls')

class NOTIF:
    class DEFAULT:
        CHECK_INTERVAL = 5 # In seconds
        CHECK_INTERVAL_SQL = 600 # In seconds
        NAME_PATTERN = '**'
        GET_DATA_PATTERN = '**'

    class TYPE:
        OPENSTACK_SWIFT = 'openstack_swift'
        SQL = 'sql'

class CASSANDRA:
    class DEFAULT(Constants):
        CONTACT_POINTS = ValueConstant('127.0.0.1\n')
        EXEC_SIZE = ValueConstant(2)
        PORT = ValueConstant(9042)
        PROTOCOL_VERSION = ValueConstant(4)
        KEYSPACE = ValueConstant('not-set')

    class COMPRESSION(Constants):
        DISABLED = ValueConstant('disabled')
        ENABLED_NEGOTIATED = ValueConstant('enabled-negotiated')
        ENABLED_LZ4 = ValueConstant('enabled-lz4')
        ENABLED_SNAPPY = ValueConstant('enabled-snappy')

class TLS:
    # All the BEGIN/END blocks we don't want to store in logs.
    # Taken from https://github.com/openssl/openssl/blob/master/crypto/pem/pem.h
    # Note that the last one really is empty to denote 'BEGIN PRIVATE KEY' alone.
    BEGIN_END = ('ANY ', 'RSA ', 'DSA ', 'EC ', 'ENCRYPTED ', '')

    # Directories in a server's config/tls directory keeping the material
    DIR_CA_CERTS = 'ca-certs'
    DIR_KEYS_CERTS = 'keys-certs'

class ODOO:
    class DEFAULT:
        PORT = 8069
        POOL_SIZE = 3

    class PROTOCOL:
        XML_RPC = NameId('XML-RPC', 'xmlrpc')
        XML_RPCS = NameId('XML-RPCS', 'xmlrpcs')
        JSON_RPC = NameId('JSON-RPC', 'jsonrpc')
        JSON_RPCS = NameId('JSON-RPCS', 'jsonrpcs')

        class __metaclass__(type):
            def __iter__(self):
                return iter((self.XML_RPC, self.XML_RPCS, self.JSON_RPC, self.JSON_RPCS))

# Need to use such a constant because we can sometimes be interested in setting
# default values which evaluate to boolean False.
NO_DEFAULT_VALUE = 'NO_DEFAULT_VALUE'

ZATO_INFO_FILE = b'.zato-info'

class path(object):
    def __init__(self, path, raise_on_not_found=False, ns='', text_only=False):
        self.path = path
        self.ns = ns
        self.raise_on_not_found = raise_on_not_found
        self.text_only = text_only
        self.children_only = False
        self.children_only_idx = None

    def get_from(self, elem):
        if self.ns:
            _path = '{{{}}}{}'.format(self.ns, self.path)
        else:
            _path = self.path
        try:
            if self.children_only:
                elem = elem.getchildren()[self.children_only_idx]
            value = _ObjectPath(_path)(elem)
            if self.text_only:
                return value.text
            return value
        except(ValueError, AttributeError), e:
            if self.raise_on_not_found:
                raise ParsingException(None, format_exc(e))
            else:
                return None

class zato_path(path):
    def __init__(self, path, raise_on_not_found=False, text_only=False):
        super(zato_path, self).__init__(path, raise_on_not_found, zato_namespace, text_only)
        self.children_only = True
        self.children_only_idx = 1 # 0 is zato_env

class ZatoException(Exception):
    """ Base class for all Zato custom exceptions.
    """
    def __init__(self, cid=None, msg=None):
        super(ZatoException, self).__init__(msg)
        self.cid = cid
        self.msg = msg

class ClientSecurityException(ZatoException):
    """ An exception for signalling errors stemming from security problems
    on the client side, such as invalid username or password.
    """

class ConnectionException(ZatoException):
    """ Encountered a problem with an external connections, such as to AMQP brokers.
    """

class TimeoutException(ConnectionException):
    pass

class HTTPException(ZatoException):
    """ Raised when the underlying error condition can be easily expressed
    as one of the HTTP status codes.
    """
    def __init__(self, cid, msg, status):
        super(HTTPException, self).__init__(cid, msg)
        self.status = status
        self.reason = HTTP_RESPONSES[status]

    def __repr__(self):
        return '<{} at {} cid:`{}`, status:`{}`, msg:`{}`>'.format(
            self.__class__.__name__, hex(id(self)), self.cid, self.status, self.msg)

class ParsingException(ZatoException):
    """ Raised when the error is to do with parsing of documents, such as an input
    XML document.
    """

class NoDistributionFound(ZatoException):
    """ Raised when an attempt is made to import services from a Distutils2 archive
    or directory but they don't contain a proper Distutils2 distribution.
    """
    def __init__(self, path):
        super(NoDistributionFound, self).__init__(None, 'No Disutils distribution in path:[{}]'.format(path))

class Inactive(ZatoException):
    """ Raised when an attempt was made to use an inactive resource, such
    as an outgoing connection or a channel.
    """
    def __init__(self, name):
        super(Inactive, self).__init__(None, '`{}` is inactive'.format(name))

class SourceInfo(object):
    """ A bunch of attributes dealing the service's source code.
    """
    def __init__(self):
        self.source = None
        self.source_html = None
        self.path = None
        self.hash = None
        self.hash_method = None
        self.server_name = None

class StatsElem(object):
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
        self.min_resp_time = maxint # Assuming that there sure will be at least one response time lower than that
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

class SMTPMessage(object):
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

class IMAPMessage(object):
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
