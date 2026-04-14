# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from copy import deepcopy

# Bunch
from bunch import Bunch, bunchify

# Zato
from zato.common.api import simple_types
from zato.common.marshal_.api import Model
from zato.common.json_internal import loads
from zato.common.util.api import make_repr
from zato.common.util.http_ import get_form_data as util_get_form_data

# Rust
from zato_server_core import extract_headers
from zato_sio import ServiceInput

# ################################################################################################################################
# ################################################################################################################################

if 0:

    # stdlib
    from logging import Logger

    # Arrow
    from arrow import Arrow

    # Kombu
    from kombu.message import Message as KombuAMQPMessage

    # Zato
    from zato.common.sql_pool import PoolStore
    from zato.common.typing_ import any_, callable_, stranydict, strnone
    from zato.server.config import ConfigDict, ConfigStore
    from zato.server.connection.email import EMailAPI
    from zato.server.connection.ftp import FTPStore
    from zato.server.connection.search import SearchAPI
    from zato.server.service import AMQPFacade, Service

    # Zato - Rust SIO
    from zato_sio import SIOProcessor

    callable_ = callable_
    strnone = strnone
    AMQPFacade = AMQPFacade
    Arrow = Arrow
    ConfigDict = ConfigDict
    ConfigStore = ConfigStore
    SIOProcessor = SIOProcessor
    EMailAPI = EMailAPI
    FTPStore = FTPStore
    KombuAMQPMessage = KombuAMQPMessage
    Logger = Logger
    PoolStore = PoolStore
    SearchAPI = SearchAPI
    Service = Service

# ################################################################################################################################
# ################################################################################################################################

NOT_GIVEN = 'ZATO_NOT_GIVEN'

# ################################################################################################################################
# ################################################################################################################################

# ################################################################################################################################
# ################################################################################################################################

class HTTPRequestData:
    """ Data regarding an HTTP request.
    """
    __slots__ = 'method', 'GET', 'POST', 'path', 'params', 'user_agent', 'headers', '_http_environ'

    def __init__(self, _Bunch=Bunch):
        self.method = None # type: str
        self.GET = _Bunch()
        self.POST = _Bunch()
        self.path = None # type: str
        self.params = _Bunch()
        self.user_agent = ''
        self.headers = _Bunch()
        self._http_environ = None # type: dict

    def init(self, http_environ=None):
        self._http_environ = http_environ or {}
        self.method = http_environ.get('REQUEST_METHOD') # type: str
        self.GET.update(http_environ.get('zato.http.GET', {})) # type: dict
        self.POST.update(http_environ.get('zato.http.POST', {}))
        self.path = http_environ.get('PATH_INFO') # type: str
        self.params.update(http_environ.get('zato.http.path_params', {}))
        self.user_agent = http_environ.get('HTTP_USER_AGENT')
        self._extract_headers()

    def _extract_headers(self):
        self.headers.update(extract_headers(self._http_environ))

    def get_form_data(self) -> 'stranydict':
        return util_get_form_data(self._http_environ)

    def __repr__(self):
        return make_repr(self)

    def to_dict(self) -> 'stranydict':
        return {
            'method': self.method,
            'GET': dict(self.GET),
            'POST': dict(self.POST),
            'path': self.path,
            'params': dict(self.params),
            'user_agent': self.user_agent,
            'headers': dict(self.headers),
        }

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

class Request:
    """ Wraps a service request and adds some useful meta-data.
    """
    service: 'Service'
    logger: 'Logger'
    payload: 'any_'
    text: 'any_'
    input: 'any_'
    cid: 'str'
    data_format: 'str'
    transport: 'str'
    encrypt_func: 'callable_'
    encrypt_secrets: 'bool'
    bytes_to_str_encoding: 'str'
    _http_environ: 'stranydict'
    channel_params: 'stranydict'
    merge_channel_params: 'bool'
    http: 'HTTPRequestData'
    amqp: 'AMQPRequestData'

    __slots__ = ('service', 'logger', 'payload', 'text', 'input', 'cid', 'data_format', 'transport',
        'encrypt_func', 'encrypt_secrets', 'bytes_to_str_encoding', '_http_environ', 'channel_params',
        'merge_channel_params', 'http', 'amqp', 'enforce_string_encoding')

    def __init__(
        self,
        service, # type: Service
        simple_io_config=None, # type: any_
        data_format=None, # type: strnone
        transport=None    # type: strnone
    ) -> 'None':
        self.service = service
        self.logger = None
        self.payload = ''
        self.text = ''
        self.input = None
        self.cid = None
        self.data_format = data_format
        self.transport = transport
        self.http = HTTPRequestData()
        self._http_environ = None
        self.channel_params = {}
        self.merge_channel_params = True
        self.amqp = None
        self.encrypt_func = None
        self.encrypt_secrets = True
        self.bytes_to_str_encoding = None

# ################################################################################################################################

    def init(
        self,
        is_sio,       # type: bool
        cid,          # type: str
        sio,          # type: SIOProcessor
        data_format,  # type: str
        transport,    # type: str
        http_environ, # type: stranydict
        encrypt_func  # type: callable_
    ) -> 'None':
        """ Initializes the object with an invocation-specific data.
        """
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

    @property
    def raw_request(self) -> 'any_':
        return self.text

# ################################################################################################################################

    @raw_request.setter
    def raw_request(self, value:'any_') -> 'any_':
        self.text = value

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
    amqp: 'AMQPFacade'
    ftp: 'FTPStore'
    odoo: 'ConfigDict'
    plain_http: 'ConfigDict'
    rest: 'ConfigDict'
    soap: 'ConfigDict'
    sql: 'PoolStore'
    sap: 'ConfigDict'
    ldap: 'stranydict'
    mongodb: 'stranydict'
    redis: 'any_'

    __slots__ = ('amqp', 'ftp', 'odoo', 'plain_http', 'rest', 'soap', 'sql', 'sap', 'ldap', 'mongodb', 'redis')

    def __init__(self, amqp=None, odoo=None, plain_http=None, soap=None, sql=None,
            sap=None, ldap=None, mongodb=None, redis=None):

        self.amqp = amqp

        self.odoo = odoo

        self.rest = plain_http
        self.plain_http = self.rest

        self.soap  = soap
        self.sql   = sql

        self.sap  = sap
        self.ldap = ldap

        self.mongodb = mongodb

        self.redis = redis

# ################################################################################################################################
# ################################################################################################################################

class Cloud:
    """ A container for cloud-related connections a service can establish.
    """
    __slots__ = 'confluence', 'jira', 'salesforce', 'ms365'

    confluence: 'stranydict'
    jira: 'stranydict'
    salesforce: 'stranydict'
    ms365: 'stranydict'

# ################################################################################################################################
# ################################################################################################################################
