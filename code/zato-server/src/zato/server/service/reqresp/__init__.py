# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from copy import deepcopy

# Bunch
from bunch import Bunch, bunchify

# lxml
from lxml.etree import _Element as EtreeElement
from lxml.objectify import ObjectifiedElement

# Zato
from zato.common.api import simple_types
from zato.common.marshal_.api import Model
from zato.common.json_internal import loads
from zato.common.util.api import make_repr
from zato.common.util.http import get_form_data as util_get_form_data

# Zato - Cython
from zato.simpleio import ServiceInput

# ################################################################################################################################
# ################################################################################################################################

if 0:

    # stdlib
    from logging import Logger

    # Arrow
    from arrow import Arrow

    # hl7apy
    from hl7apy.core import Message as hl7apy_Message

    # Kombu
    from kombu.message import Message as KombuAMQPMessage

    # Zato
    from zato.common.kvdb.api import KVDB as KVDBAPI
    from zato.common.odb.api import PoolStore
    from zato.common.typing_ import any_, stranydict
    from zato.hl7.mllp.server import ConnCtx as HL7ConnCtx
    from zato.server.config import ConfigDict, ConfigStore
    from zato.server.connection.email import EMailAPI
    from zato.server.connection.ftp import FTPStore
    from zato.server.connection.jms_wmq.outgoing import WMQFacade
    from zato.server.connection.search import SearchAPI
    from zato.server.connection.sms import SMSAPI
    from zato.server.connection.vault import VaultConnAPI
    from zato.server.connection.zmq_.outgoing import ZMQFacade
    from zato.server.service import AMQPFacade, Service

    # Zato - Cython
    from zato.simpleio import CySimpleIO

    AMQPFacade = AMQPFacade
    Arrow = Arrow
    ConfigDict = ConfigDict
    ConfigStore = ConfigStore
    CySimpleIO = CySimpleIO
    EMailAPI = EMailAPI
    FTPStore = FTPStore
    hl7apy_Message = hl7apy_Message
    HL7ConnCtx = HL7ConnCtx
    KombuAMQPMessage = KombuAMQPMessage
    KVDBAPI = KVDBAPI
    Logger = Logger
    PoolStore = PoolStore
    SearchAPI = SearchAPI
    SMSAPI = SMSAPI
    VaultConnAPI = VaultConnAPI
    WMQFacade = WMQFacade
    ZMQFacade = ZMQFacade

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

NOT_GIVEN = 'ZATO_NOT_GIVEN'

# ################################################################################################################################

direct_payload = simple_types + (EtreeElement, ObjectifiedElement)

# ################################################################################################################################

class HTTPRequestData:
    """ Data regarding an HTTP request.
    """
    __slots__ = 'method', 'GET', 'POST', 'path', 'params', 'user_agent', '_wsgi_environ'

    def __init__(self, _Bunch=Bunch):
        self.method = None # type: str
        self.GET = _Bunch()
        self.POST = _Bunch()
        self.path = None # type: str
        self.params = _Bunch()
        self.user_agent = ''
        self._wsgi_environ = None # type: dict

    def init(self, wsgi_environ=None):
        self._wsgi_environ = wsgi_environ or {}
        self.method = wsgi_environ.get('REQUEST_METHOD') # type: str
        self.GET.update(wsgi_environ.get('zato.http.GET', {})) # type: dict
        self.POST.update(wsgi_environ.get('zato.http.POST', {}))
        self.path = wsgi_environ.get('PATH_INFO') # type: str
        self.params.update(wsgi_environ.get('zato.http.path_params', {}))
        self.user_agent = wsgi_environ.get('HTTP_USER_AGENT')

    def get_form_data(self) -> 'stranydict':
        return util_get_form_data(self._wsgi_environ)

    def __repr__(self):
        return make_repr(self)

# ################################################################################################################################

class AMQPRequestData:
    """ Data regarding an AMQP request.
    """
    __slots__ = ('msg', 'ack', 'reject')

    def __init__(self, msg):
        # type: (KombuAMQPMessage)
        self.msg = msg
        self.ack = msg.ack
        self.reject = msg.reject

# ################################################################################################################################

class IBMMQRequestData:
    """ Metadata for IBM MQ requests.
    """
    __slots__ = ('ctx', 'data', 'msg_id', 'correlation_id', 'timestamp', 'put_date', 'put_time', 'reply_to', 'mqmd')

    def __init__(self, ctx):
        # type: dict
        self.ctx = ctx
        self.data = ctx['data'] # type: str
        self.msg_id = ctx['msg_id'] # type: str
        self.correlation_id = ctx['correlation_id'] # type: str
        self.timestamp = ctx['timestamp'] # type: Arrow
        self.put_date = ctx['put_date'] # type: str
        self.put_time = ctx['put_time'] # type: str
        self.reply_to = ctx['reply_to'] # type: str
        self.mqmd = ctx['mqmd'] # type: object

# Backward compatibility
WebSphereMQRequestData = IBMMQRequestData

# ################################################################################################################################

class HL7RequestData:
    """ Details of an individual HL7 request.
    """
    __slots__ = 'connection', 'data',

    def __init__(self, connection, data):
        # type: (HL7ConnCtx, hl7apy_Message) -> None
        self.connection = connection
        self.data = data

# ################################################################################################################################

class Request:
    """ Wraps a service request and adds some useful meta-data.
    """
    raw_request: 'any_'

    __slots__ = ('service', 'logger', 'payload', 'raw_request', 'input', 'cid', 'data_format', 'transport',
        'encrypt_func', 'encrypt_secrets', 'bytes_to_str_encoding', '_wsgi_environ', 'channel_params',
        'merge_channel_params', 'http', 'amqp', 'wmq', 'ibm_mq', 'hl7', 'enforce_string_encoding')

    def __init__(self, service, simple_io_config=None, data_format=None, transport=None):
        # type: (Service, object, str, str)
        self.service = service
        self.logger = service.logger # type: Logger
        self.payload = ''
        self.raw_request = ''
        self.input = None # type: any_
        self.cid = None # type: str
        self.data_format = data_format # type: str
        self.transport = transport # type: str
        self.http = HTTPRequestData()
        self._wsgi_environ = None # type: dict
        self.channel_params = {}
        self.merge_channel_params = True
        self.amqp = None # type: AMQPRequestData
        self.wmq = self.ibm_mq = None # type: IBMMQRequestData
        self.hl7 = None # type: HL7RequestData
        self.encrypt_func = None
        self.encrypt_secrets = True
        self.bytes_to_str_encoding = None # type: str

# ################################################################################################################################

    def init(self, is_sio, cid, sio, data_format, transport, wsgi_environ, encrypt_func):
        """ Initializes the object with an invocation-specific data.
        """
        # type: (bool, str, CySimpleIO, str, str, dict, object)
        self.input = ServiceInput()
        self.encrypt_func = encrypt_func

        if is_sio:

            parsed = sio.parse_input(self.payload or {}, data_format, extra=self.channel_params, service=self.service)

            if isinstance(parsed, Model):
                self.input = parsed
            else:
                if isinstance(parsed, dict):
                    self.input.update(parsed)
                for param, value in self.channel_params.items():
                    if param not in self.input:
                        self.input[param] = value

        # We merge channel params in if requested even if it's not SIO
        else:
            if self.merge_channel_params:
                self.input.update(self.channel_params)

# ################################################################################################################################

    def deepcopy(self):
        """ Returns a deep copy of self.
        """
        request = Request(None)
        request.logger = logging.getLogger(self.logger.name)

        for name in Request.__slots__:
            if name == 'logger':
                continue
            setattr(request, name, deepcopy(getattr(self, name)))

        return request

# ################################################################################################################################

    def to_bunch(self):
        """ Returns a bunchified (converted into bunch.Bunch) version of self.raw_request,
        deep copied if it's a dict (or a subclass). Note that it makes sense to use this method
        only with dicts or JSON input.
        """
        # We have a dict
        if isinstance(self.raw_request, dict):
            return bunchify(deepcopy(self.raw_request))

        # Must be a JSON input, raises exception when attempting to load it if it's not
        return bunchify(loads(self.raw_request))

    # Backward-compatibility
    bunchified = to_bunch

# ################################################################################################################################
# ################################################################################################################################

class Outgoing:
    """ A container for various outgoing connections a service can access. This in fact is a thin wrapper around data
    fetched from the service's self.worker_store.
    """
    __slots__ = ('amqp', 'ftp', 'ibm_mq', 'jms_wmq', 'wmq', 'odoo', 'plain_http', 'rest', 'soap', 'sql', 'zmq', 'wsx', 'vault',
        'sms', 'sap', 'sftp', 'ldap', 'mongodb', 'def_kafka', 'hl7', 'redis')

    def __init__(self, amqp=None, ftp=None, jms_wmq=None, odoo=None, plain_http=None, soap=None, sql=None, zmq=None,
            wsx=None, vault=None, sms=None, sap=None, sftp=None, ldap=None, mongodb=None, def_kafka=None,
            redis=None, hl7=None):

        self.amqp = amqp # type: AMQPFacade
        self.ftp  = ftp  # type: FTPStore

        # Backward compat with 2.0, self.ibm_mq is now preferred
        self.ibm_mq = self.wmq = self.jms_wmq = jms_wmq # type: WMQFacade

        self.odoo       = odoo # type: ConfigDict
        self.plain_http = self.rest = plain_http # type: ConfigDict

        self.soap  = soap  # type: ConfigDict
        self.sql   = sql   # type: PoolStore
        self.zmq   = zmq   # type: ZMQFacade
        self.wsx   = wsx   # type: dict
        self.vault = vault # type: VaultConnAPI

        self.sms  = sms  # type: SMSAPI
        self.sap  = sap  # type: ConfigDict
        self.sftp = sftp # type: ConfigDict
        self.ldap = ldap # type: dict

        self.mongodb = mongodb # type: dict
        self.def_kafka = None  # type: dict

        self.redis = redis # type: KVDBAPI
        self.hl7   = hl7   # type: HL7API

# ################################################################################################################################
# ################################################################################################################################

class AWS:
    __slots__ = 's3',

    s3: 'ConfigDict'

# ################################################################################################################################
# ################################################################################################################################

class Cloud:
    """ A container for cloud-related connections a service can establish.
    """
    __slots__ = 'aws', 'confluence', 'dropbox', 'jira', 'salesforce'

    aws: 'AWS'
    confluence: 'stranydict'
    dropbox: 'stranydict'
    jira: 'stranydict'
    salesforce: 'stranydict'

    def __init__(self) -> 'None':
        self.aws = AWS()

# ################################################################################################################################
# ################################################################################################################################

class Definition:
    """ A container for connection definitions a service has access to.
    """
    __slots__ = 'kafka',
    kafka: 'stranydict'

# ################################################################################################################################
# ################################################################################################################################

class InstantMessaging:
    """ A container for Instant Messaging connections, e.g. Slack or Telegram.
    """
    __slots__ = 'slack', 'telegram'

    slack: 'stranydict'
    telegram: 'stranydict'

# ################################################################################################################################
# ################################################################################################################################

class MLLP:
    pass

# ################################################################################################################################
# ################################################################################################################################

class HL7API:
    """ A container for HL7 connections a service can establish.
    """
    __slots__ = 'fhir', 'mllp'

    fhir: 'stranydict'
    mllp: 'stranydict'

    def __init__(self, fhir:'stranydict', mllp:'stranydict') -> None:
        self.fhir = fhir
        self.mllp = mllp

# ################################################################################################################################
# ################################################################################################################################
