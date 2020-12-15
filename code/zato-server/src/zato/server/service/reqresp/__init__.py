# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from cgi import FieldStorage
from copy import deepcopy
from io import BytesIO

# Bunch
from bunch import Bunch, bunchify

# lxml
from lxml.etree import _Element as EtreeElement
from lxml.objectify import ObjectifiedElement

# Python 2/3 compatibility
from future.utils import iteritems

# Zato
from zato.common.api import simple_types
from zato.common.json_internal import loads
from zato.common.util.api import make_repr

# Zato - Cython
from zato.simpleio import ServiceInput

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
    from zato.common.odb.api import PoolStore
    from zato.server.config import ConfigDict, ConfigStore
    from zato.server.connection.email import EMailAPI
    from zato.server.connection.ftp import FTPStore
    from zato.server.connection.jms_wmq.outgoing import WMQFacade
    from zato.server.connection.search import SearchAPI
    from zato.server.connection.sms import SMSAPI
    from zato.server.connection.vault import VaultConnAPI
    from zato.server.connection.zmq_.outgoing import ZMQFacade
    from zato.server.service import AMQPFacade

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
    KombuAMQPMessage = KombuAMQPMessage
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

class HTTPRequestData(object):
    """ Data regarding an HTTP request.
    """
    __slots__ = 'method', 'GET', 'POST', 'path', 'params', '_wsgi_environ'

    def __init__(self, _Bunch=Bunch):
        self.method = None # type: str
        self.GET = _Bunch()
        self.POST = _Bunch()
        self.path = None # type: str
        self.params = _Bunch()
        self._wsgi_environ = None # type: dict

    def init(self, wsgi_environ=None):
        self._wsgi_environ = wsgi_environ or {}
        self.method = wsgi_environ.get('REQUEST_METHOD') # type: str
        self.GET.update(wsgi_environ.get('zato.http.GET', {})) # type: dict
        self.POST.update(wsgi_environ.get('zato.http.POST', {}))
        self.path = wsgi_environ.get('PATH_INFO') # type: str
        self.params.update(wsgi_environ.get('zato.http.path_params', {}))

    def get_form_data(self):
        # type: () -> FieldStorage

        # This is the form data uploaded to the service
        data = self._wsgi_environ['zato.http.raw_request'] # type: str

        # Create a buffer to hold the form data and write the form to it
        buff = BytesIO()
        buff.write(data)
        buff.seek(0)

        # Output to return
        form = FieldStorage(fp=buff, environ=self._wsgi_environ, keep_blank_values=True)

        # Clean up
        buff.close()

        # Return the parsed form data
        return form

    def __repr__(self):
        return make_repr(self)

# ################################################################################################################################

class AMQPRequestData(object):
    """ Data regarding an AMQP request.
    """
    __slots__ = ('msg', 'ack', 'reject')

    def __init__(self, msg):
        # type: (KombuAMQPMessage)
        self.msg = msg
        self.ack = msg.ack
        self.reject = msg.reject

# ################################################################################################################################

class IBMMQRequestData(object):
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

class HL7RequestData(object):
    """ Details of an individual HL7 request.
    """
    __slots__ = 'data',

    def __init__(self, data):
        # type: (hl7apy_Message) -> None
        self.data = data

# ################################################################################################################################

class Request(object):
    """ Wraps a service request and adds some useful meta-data.
    """
    __slots__ = ('logger', 'payload', 'raw_request', 'input', 'cid', 'data_format', 'transport',
        'encrypt_func', 'encrypt_secrets', 'bytes_to_str_encoding', '_wsgi_environ', 'channel_params',
        'merge_channel_params', 'http', 'amqp', 'wmq', 'ibm_mq', 'hl7', 'enforce_string_encoding')

    def __init__(self, logger, simple_io_config=None, data_format=None, transport=None):
        # type: (Logger, object, str, str)
        self.logger = logger
        self.payload = ''
        self.raw_request = ''
        self.input = {} # Will be overwritten in self.init if necessary
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

            if self.payload:
                parsed = sio.parse_input(self.payload, data_format)
                self.input.update(parsed)

            for param, value in iteritems(self.channel_params):
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

class Outgoing(object):
    """ A container for various outgoing connections a service can access. This in fact is a thin wrapper around data
    fetched from the service's self.worker_store.
    """
    __slots__ = ('amqp', 'ftp', 'ibm_mq', 'jms_wmq', 'wmq', 'odoo', 'plain_http', 'soap', 'sql', 'zmq', 'wsx', 'vault',
        'sms', 'sap', 'sftp', 'ldap', 'mongodb', 'def_kafka')

    def __init__(self, amqp=None, ftp=None, jms_wmq=None, odoo=None, plain_http=None, soap=None, sql=None, zmq=None,
            wsx=None, vault=None, sms=None, sap=None, sftp=None, ldap=None, mongodb=None, def_kafka=None):

        self.amqp = amqp # type: AMQPFacade
        self.ftp = ftp   # type: FTPStore

        # Backward compat with 2.0, self.ibm_mq is now preferred
        self.ibm_mq = self.wmq = self.jms_wmq = jms_wmq # type: WMQFacade

        self.odoo = odoo # type: ConfigDict
        self.plain_http = plain_http # type: ConfigDict
        self.soap = soap # type: ConfigDict
        self.sql = sql   # type: PoolStore
        self.zmq = zmq     # type: ZMQFacade
        self.wsx = wsx     # type: dict
        self.vault = vault # type: VaultConnAPI
        self.sms = sms   # type: SMSAPI
        self.sap = sap   # type: ConfigDict
        self.sftp = sftp # type: ConfigDict
        self.ldap = ldap # type: dict
        self.mongodb = mongodb # type: dict
        self.def_kafka = None # type: dict

# ################################################################################################################################
# ################################################################################################################################

class AWS(object):
    def __init__(self, s3=None):
        self.s3 = s3

# ################################################################################################################################
# ################################################################################################################################

class OpenStack(object):
    def __init__(self, swift=None):
        self.swift = swift

# ################################################################################################################################
# ################################################################################################################################

class Cloud(object):
    """ A container for cloud-related connections a service can establish.
    """
    __slots__ = 'aws', 'dropbox', 'openstack'

    def __init__(self, aws=None, dropbox=None, openstack=None):
        self.aws = aws or AWS()
        self.dropbox = dropbox
        self.openstack = openstack or OpenStack()

# ################################################################################################################################
# ################################################################################################################################

class Definition(object):
    """ A container for connection definitions a service has access to.
    """
    __slots__ = 'kafka',

    def __init__(self, kafka=None):
        # type: (dict)
        self.kafka = kafka

# ################################################################################################################################
# ################################################################################################################################

class InstantMessaging(object):
    """ A container for Instant Messaging connections, e.g. Slack or Telegram.
    """
    __slots__ = 'slack', 'telegram'

    def __init__(self, slack=None, telegram=None):
        # type: (dict, dict)
        self.slack = slack
        self.telegram = telegram

# ################################################################################################################################
# ################################################################################################################################
