# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from collections import OrderedDict
from cStringIO import StringIO
from httplib import responses
from string import Template
from sys import maxint
from traceback import format_exc

# lxml
from lxml import etree
from lxml.objectify import ObjectPath as _ObjectPath

# Bunch
from bunch import Bunch

# The namespace for use in all Zato's own services.
zato_namespace = 'https://zato.io/ns/20130518'
zato_ns_map = {None: zato_namespace}

# Convenience access functions and constants.

soapenv_namespace = 'http://schemas.xmlsoap.org/soap/envelope/'
wsse_namespace = 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd'
wsu_namespace = 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd'

common_namespaces = {
    'soapenv':soapenv_namespace,
    'wsse':wsse_namespace,
    'wsu':wsu_namespace,
    'zato':zato_namespace
}

soap_doc = Template("""<soap:Envelope xmlns:soap='%s'><soap:Body>$body</soap:Body></soap:Envelope>""" % soapenv_namespace)

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

PASSWORD_SHADOW = '***'

SECONDS_IN_DAY = 86400 # 60 seconds * 60 minutes * 24 hours (and we ignore leap seconds)

#iso8601_format = '%Y-%m-%dT%H:%M:%S.%fZ'
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
DEFAULT_HTTP_PING_METHOD = 'HEAD'

# Default size of an outgoing HTTP connection's pool (plain, SOAP, any).
# This is a per-outconn setting
DEFAULT_HTTP_POOL_SIZE = 200

# Used when there's a need for encrypting/decrypting a well-known data.
ZATO_CRYPTO_WELL_KNOWN_DATA = 'ZATO'

# All URL types Zato understands.
class URL_TYPE:
    SOAP = 'soap'
    PLAIN_HTTP = 'plain_http'

# Whether WS-Security passwords are transmitted in clear-text or not.
ZATO_WSS_PASSWORD_CLEAR_TEXT = Bunch(name='clear_text', label='Clear text')
ZATO_WSS_PASSWORD_TYPES = {
    ZATO_WSS_PASSWORD_CLEAR_TEXT.name:ZATO_WSS_PASSWORD_CLEAR_TEXT.label,
}

ZATO_FIELD_OPERATORS = {
    'is-equal-to': '==',
    'is-not-equal-to': '!=',
}

ZMQ_OUTGOING_TYPES = ('PUSH',)
ZMQ_CHANNEL_TYPES = ('PULL', 'SUB')

ZATO_ODB_POOL_NAME = 'ZATO_ODB'

SOAP_VERSIONS = ('1.1', '1.2')
SOAP_CHANNEL_VERSIONS = ('1.1',)

SECURITY_TYPES = {
    'basic_auth':'HTTP Basic Auth',
    'oauth': 'OAuth 1.0',
    'tech_acc':'Tech account',
    'wss':'WS-Security'
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
    XML = 'xml'
    JSON = 'json'
    CSV = 'csv'
    POST = 'post'

    class __metaclass__(type):
        def __iter__(self):
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

class SCHEDULER_JOB_TYPE(Attrs):
    ONE_TIME = 'one_time'
    INTERVAL_BASED = 'interval_based'
    CRON_STYLE = 'cron_style'

class CHANNEL(Attrs):
    AMQP = 'amqp'
    AUDIT = 'audit' # New in 1.2
    DELIVERY = 'delivery' # New in 1.2
    HTTP_SOAP = 'http-soap'
    INTERNAL_CHECK = 'internal-check' # New in 1.2
    INVOKE = 'invoke'
    INVOKE_ASYNC = 'invoke-async'
    JMS_WMQ = 'jms-wmq'
    SCHEDULER = 'scheduler'
    ZMQ = 'zmq'
    STARTUP_SERVICE = 'startup-service'

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
    SEPARATOR = ':::'
    OAUTH_SIG_METHODS = ['HMAC-SHA1', 'PLAINTEXT']
    DEFAULT_AUDIT_BACK_LOG = 24 * 60 # 24 hours * 60 days ≅ 2 months
    DEFAULT_AUDIT_MAX_PAYLOAD = 0 # Using 0 means there's no limit

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
            return iter((self.CHANNEL_PARAMS_OVER_MSG, self.MSG_OVER_CHANNEL_PARAMS))

class NONCE_STORE:
    KEY_PATTERN = 'zato:nonce-store:{}:{}' # E.g. zato:nonce-store:oauth:27
    DEFAULT_MAX_LOG = 25000

class MSG_PATTERN_TYPE:
    ELEM_PATH = NameId('ElemPath', 'elem-path')
    XPATH = NameId('XPath', 'xpath')
    
    class __metaclass__(type):
        def __iter__(self):
            return iter((self.ELEM_PATH, self.XPATH))

# Need to use such a constant because we can sometimes be interested in setting
# default values which evaluate to boolean False.
NO_DEFAULT_VALUE = 'NO_DEFAULT_VALUE'

# ##############################################################################
# Version
# ##############################################################################

major = 1
minor = 1

class VersionInfo(object):
    def __init__(self, major, minor):
        self.major = major
        self.minor = minor

version_info = VersionInfo(major, minor)
version_raw = '{}.{}'.format(version_info.major, version_info.minor)
version = 'Zato {}'.format(version_raw)


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

class HTTPException(ZatoException):
    """ Raised when the underlying error condition can be easily expressed
    as one of the HTTP status codes.
    """
    def __init__(self, cid, msg, status):
        super(HTTPException, self).__init__(cid, msg)
        self.status = status
        self.reason = responses[status]

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
        super(Inactive, self).__init__(None, '[{}] is inactive'.format(name))

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
