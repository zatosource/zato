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

# lxml
from lxml.etree import _Element as EtreeElement
from lxml.objectify import ObjectifiedElement

# Zato
from zato.common.api import simple_types
from zato.common.marshal_.api import Model
from zato.common.json_internal import loads
from zato.common.typing_ import cast_
from zato.common.util.api import make_repr
from zato.common.util.http_ import get_form_data as util_get_form_data

# Zato - Cython
from zato.simpleio import ServiceInput

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
    from zato.common.odb.api import PoolStore
    from zato.common.typing_ import any_, callable_, stranydict, strnone
    from zato.server.config import ConfigDict, ConfigStore
    from zato.server.connection.email import EMailAPI
    from zato.server.connection.ftp import FTPStore
    from zato.server.connection.search import SearchAPI
    from zato.server.service import AMQPFacade, Service

    # Zato - Cython
    from zato.simpleio import CySimpleIO

    callable_ = callable_
    strnone = strnone
    AMQPFacade = AMQPFacade
    Arrow = Arrow
    ConfigDict = ConfigDict
    ConfigStore = ConfigStore
    CySimpleIO = CySimpleIO
    EMailAPI = EMailAPI
    FTPStore = FTPStore
    KombuAMQPMessage = KombuAMQPMessage
    Logger = Logger
    PoolStore = PoolStore
    SearchAPI = SearchAPI
    Service = Service

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

NOT_GIVEN = 'ZATO_NOT_GIVEN'

# ################################################################################################################################
# ################################################################################################################################

direct_payload = simple_types + (EtreeElement, ObjectifiedElement)

# ################################################################################################################################
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

class Request:
    """ Wraps a service request and adds some useful meta-data.
    """
    text: 'any_'

    __slots__ = ('service', 'logger', 'payload', 'text', 'input', 'cid', 'data_format', 'transport',
        'encrypt_func', 'encrypt_secrets', 'bytes_to_str_encoding', '_wsgi_environ', 'channel_params',
        'merge_channel_params', 'http', 'amqp', 'enforce_string_encoding')

    def __init__(
        self,
        service, # type: Service
        simple_io_config=None, # type: any_
        data_format=None, # type: strnone
        transport=None    # type: strnone
    ) -> 'None':
        self.service = service
        self.logger = cast_('Logger', service.logger)
        self.payload = ''
        self.text = ''
        self.input = None # type: any_
        self.cid = cast_('str', None)
        self.data_format = cast_('str', data_format)
        self.transport = cast_('str', transport)
        self.http = HTTPRequestData()
        self._wsgi_environ = cast_('stranydict', None)
        self.channel_params = cast_('stranydict', {})
        self.merge_channel_params = True
        self.amqp = cast_('AMQPRequestData', None)
        self.encrypt_func = None
        self.encrypt_secrets = True
        self.bytes_to_str_encoding = cast_('str', None)

# ################################################################################################################################

    def init(
        self,
        is_sio,       # type: bool
        cid,          # type: str
        sio,          # type: CySimpleIO
        data_format,  # type: str
        transport,    # type: str
        wsgi_environ, # type: stranydict
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
    __slots__ = ('amqp', 'ftp', 'odoo', 'plain_http', 'rest', 'soap', 'sql', 'sap', 'ldap', 'mongodb', 'redis')

    def __init__(self, amqp=None, odoo=None, plain_http=None, soap=None, sql=None,
            sap=None, ldap=None, mongodb=None, redis=None):

        self.amqp = cast_('AMQPFacade', amqp)

        self.odoo = cast_('ConfigDict', odoo)

        self.rest = cast_('ConfigDict', plain_http)
        self.plain_http = self.rest

        self.soap  = cast_('ConfigDict', soap)
        self.sql   = cast_('PoolStore', sql)

        self.sap  = cast_('ConfigDict', sap)
        self.ldap = cast_('stranydict', ldap)

        self.mongodb = cast_('stranydict', mongodb)

        self.redis = cast_('KVDBAPI', redis)

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
