# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from copy import deepcopy

# Bunch
from zato.common.ext.bunch import Bunch, bunchify

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

# Zato
from zato.input_output import ServiceInput

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
    from zato.server.connection.cloud.aws import AWSClient
    from zato.server.connection.cloud.microsoft_365 import Microsoft365Client
    from zato.server.connection.cloud.microsoft_fabric import MicrosoftFabricClient
    from zato.server.connection.cloud.microsoft_power_automate import MicrosoftPowerAutomateClient
    from zato.server.connection.email import EMailAPI
    from zato.server.connection.facade import GraphQLFacade, KafkaFacade
    from zato.server.connection.ftp import FTPStore
    from zato.server.generic.api.outconn_llm import OutconnLLMWrapper
    from zato.server.service import AMQPFacade, Service

    # Zato
    from zato.input_output import IOProcessor

    callable_ = callable_
    strnone = strnone
    AMQPFacade = AMQPFacade
    Arrow = Arrow
    AWSClient = AWSClient
    Microsoft365Client = Microsoft365Client
    MicrosoftPowerAutomateClient = MicrosoftPowerAutomateClient
    ConfigDict = ConfigDict
    ConfigStore = ConfigStore
    IOProcessor = IOProcessor
    EMailAPI = EMailAPI
    FTPStore = FTPStore
    GraphQLFacade = GraphQLFacade
    KafkaFacade = KafkaFacade
    KombuAMQPMessage = KombuAMQPMessage
    Logger = Logger
    OutconnLLMWrapper = OutconnLLMWrapper
    PoolStore = PoolStore
    Service = Service

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
    __slots__ = 'method', 'GET', 'POST', 'path', 'params', 'user_agent', 'headers', '_wsgi_environ'

    def __init__(self, _Bunch=Bunch):
        self.method = None # type: str
        self.GET = _Bunch()
        self.POST = _Bunch()
        self.path = None # type: str
        self.params = _Bunch()
        self.user_agent = ''
        self.headers = _Bunch()
        self._wsgi_environ = None # type: dict

    def init(self, wsgi_environ=None):
        self._wsgi_environ = wsgi_environ or {}
        self.method = wsgi_environ.get('REQUEST_METHOD') # type: str
        self.GET.update(wsgi_environ.get('zato.http.GET', {})) # type: dict
        self.POST.update(wsgi_environ.get('zato.http.POST', {}))
        self.path = wsgi_environ.get('PATH_INFO') # type: str
        self.params.update(wsgi_environ.get('zato.http.path_params', {}))
        self.user_agent = wsgi_environ.get('HTTP_USER_AGENT')
        self._extract_headers()

    def _extract_headers(self):
        for key, value in self._wsgi_environ.items():
            if key.startswith('HTTP_'):
                header_name = key[5:].replace('_', '-').lower()
                self.headers[header_name] = value

    def get_form_data(self) -> 'stranydict':
        return util_get_form_data(self._wsgi_environ)

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
    payload: 'any_'
    raw: 'any_'

    __slots__ = ('service', 'logger', 'payload', 'raw', 'input', 'cid', 'data_format', 'transport',
        'encrypt_func', 'encrypt_secrets', 'bytes_to_str_encoding', '_wsgi_environ', 'channel_params',
        'merge_channel_params', 'http', 'amqp', 'soap', 'enforce_string_encoding', 'headers')

    def __init__(
        self,
        service, # type: Service
        data_format=None, # type: strnone
        transport=None    # type: strnone
    ) -> 'None':
        self.service = service
        self.logger = cast_('Logger', None) # This is populated in a service's update_handle
        self.payload = ''
        self.raw = ''
        self.input = None # type: any_
        self.cid = cast_('str', None)
        self.data_format = cast_('str', data_format)
        self.transport = cast_('str', transport)
        self.http = HTTPRequestData()
        self._wsgi_environ = cast_('stranydict', None)
        self.channel_params = cast_('stranydict', {})
        self.merge_channel_params = True
        self.amqp = cast_('AMQPRequestData', None)
        self.soap = None # type: any_

        # Message headers from queue bridge channels (e.g. IBM MQ MQMD and MQRFH2 fields)
        self.headers = {} # type: stranydict
        self.encrypt_func = None
        self.encrypt_secrets = True
        self.bytes_to_str_encoding = cast_('str', None)

# ################################################################################################################################

    def init(
        self,
        is_io,       # type: bool
        cid,          # type: str
        io_processor,          # type: IOProcessor | None
        data_format,  # type: str
        transport,    # type: str
        wsgi_environ, # type: stranydict
        encrypt_func  # type: callable_
    ) -> 'None':
        """ Initializes the object with an invocation-specific data.
        """
        self.input = ServiceInput()
        self.encrypt_func = encrypt_func

        if is_io:

            parsed = io_processor.parse_input(self.payload or {}, data_format, extra=self.channel_params, service=self.service)

            if isinstance(parsed, Model):
                self.input = parsed
            else:
                if isinstance(parsed, dict):
                    self.input.update(parsed)
                for param, value in self.channel_params.items():
                    if param not in self.input:
                        self.input[param] = value

        # There is no I/O declaration - the parsed payload itself becomes the input.
        else:

            # A dict means parsed JSON - it is exposed through input directly ..
            if isinstance(self.payload, dict):
                self.input.update(self.payload)

                # .. with channel params merged in without overriding the payload ..
                if self.merge_channel_params:
                    for param, value in self.channel_params.items():
                        if param not in self.input:
                            self.input[param] = value

            # .. a list is parsed JSON as well and it becomes the input as it is ..
            elif isinstance(self.payload, list):
                self.input = self.payload

            # .. raw text or bytes are the input exactly as received, e.g. EDIFACT or ER7 ..
            elif isinstance(self.payload, (str, bytes)) and self.payload:
                self.input = self.payload

            # .. and with no payload at all, the input carries channel params only.
            else:
                if self.merge_channel_params:
                    self.input.update(self.channel_params)

# ################################################################################################################################

    @property
    def raw_request(self) -> 'any_':
        return self.raw

# ################################################################################################################################

    @raw_request.setter
    def raw_request(self, value:'any_') -> 'any_':
        self.raw = value

# ################################################################################################################################

    @property
    def text(self) -> 'any_':
        return self.raw

# ################################################################################################################################

    @text.setter
    def text(self, value:'any_') -> 'any_':
        self.raw = value

# ################################################################################################################################

    def to_bunch(self):
        """ Returns a bunchified (converted into bunch.Bunch) version of self.raw,
        deep copied if it's a dict (or a subclass). Note that it makes sense to use this method
        only with dicts or JSON input.
        """
        # We have a dict
        if isinstance(self.raw, dict):
            return bunchify(deepcopy(self.raw))

        # Must be a JSON input, raises exception when attempting to load it if it's not
        return bunchify(loads(self.raw))

    # Backward-compatibility
    bunchified = to_bunch

# ################################################################################################################################
# ################################################################################################################################

class Outgoing:
    """ A container for various outgoing connections a service can access. This in fact is a thin wrapper around data
    fetched from the service's config manager.
    """
    __slots__ = ('amqp', 'as2', 'as4', 'ftp', 'graphql', 'kafka', 'odoo', 'plain_http', 'rest', 'soap', 'sql', 'ldap',
        'redis')

    def __init__(self, amqp=None, graphql=None, kafka=None, odoo=None, plain_http=None, soap=None, sql=None,
            ldap=None, redis=None, as2=None, as4=None):

        self.amqp = cast_('AMQPFacade', amqp)

        self.as2 = cast_('stranydict', as2)

        self.as4 = cast_('ConfigDict', as4)

        self.graphql = cast_('GraphQLFacade', graphql)

        self.kafka = cast_('KafkaFacade', kafka)

        self.odoo = cast_('ConfigDict', odoo)

        self.rest = cast_('ConfigDict', plain_http)
        self.plain_http = self.rest

        self.soap  = cast_('ConfigDict', soap)
        self.sql   = cast_('PoolStore', sql)

        self.ldap = cast_('stranydict', ldap)

        self.redis = cast_('KVDBAPI', redis)

# ################################################################################################################################
# ################################################################################################################################

class Cloud:
    """ A container for cloud-related connections a service can establish.
    """
    __slots__ = 'confluence', 'jira', 'ms365', 'salesforce'

    confluence: 'stranydict'
    jira: 'stranydict'
    ms365: 'MS365Shim'
    salesforce: 'stranydict'

    def __init__(self) -> 'None':
        self.ms365 = MS365Shim()

# ################################################################################################################################
# ################################################################################################################################

class MS365ConnShim:
    """ A thin shim that lets the old Microsoft 365 API run on top of Microsoft365Client - it covers
    item.conn, conn.client(), the with statement and client.refresh(), all of which map to the same client.
    """
    __slots__ = ('impl',)

    impl: 'Microsoft365Client'

    def __init__(self, impl:'Microsoft365Client') -> 'None':
        self.impl = impl

    @property
    def conn(self) -> 'MS365ConnShim':
        # The old API read .conn on the item returned by .get() - it all maps to the same object now.
        return self

    def client(self) -> 'MS365ConnShim':
        # The old API obtained a new client from the connection - it all maps to the same object now.
        return self

    def __enter__(self) -> 'MS365ConnShim':
        return self

    def __exit__(self, *ignored_args:'any_') -> 'None':
        pass

    def refresh(self) -> 'None':
        # Tokens are renewed automatically by Microsoft365Client so there is nothing to do here.
        pass

# ################################################################################################################################
# ################################################################################################################################

class MS365Shim:
    """ A thin shim that translates the old self.cloud.ms365[name] access into self.microsoft.cloud[name].
    """
    __slots__ = ('microsoft_cloud',)

    microsoft_cloud: 'MicrosoftCloudFacade'

    def get(self, name:'str') -> 'MS365ConnShim':
        client = self.microsoft_cloud[name]
        return MS365ConnShim(client)

    def __getitem__(self, name:'str') -> 'MS365ConnShim':
        return self.get(name)

# ################################################################################################################################
# ################################################################################################################################

class MicrosoftCloudFacade:
    """ The API through which Microsoft cloud connections are accessed by their names,
    e.g. self.microsoft.cloud['My Connection'].
    """
    __slots__ = ('conn_dict',)

    conn_dict: 'stranydict'

    def __getitem__(self, name:'str') -> 'Microsoft365Client':

        # Look up the connection's configuration ..
        item = self.conn_dict[name]

        # .. and hand back the client that its wrapper maintains.
        out = item.conn.shared_client
        return out

# ################################################################################################################################
# ################################################################################################################################

class MicrosoftPowerPlatformFacade:
    """ The API through which Microsoft Power Platform connections are accessed by their names,
    e.g. self.microsoft.power_platform['My Connection'].
    """
    __slots__ = ('conn_dict',)

    conn_dict: 'stranydict'

    def __getitem__(self, name:'str') -> 'MicrosoftPowerAutomateClient':

        # Look up the connection's configuration ..
        item = self.conn_dict[name]

        # .. and hand back the client that its wrapper maintains.
        out = item.conn.shared_client
        return out

# ################################################################################################################################
# ################################################################################################################################

class MicrosoftFabricFacade:
    """ The API through which Microsoft Fabric connections are accessed by their names,
    e.g. self.microsoft.fabric['My Connection'].
    """
    __slots__ = ('conn_dict',)

    conn_dict: 'stranydict'

    def __getitem__(self, name:'str') -> 'MicrosoftFabricClient':

        # Look up the connection's configuration ..
        item = self.conn_dict[name]

        # .. and hand back the client that its wrapper maintains.
        out = item.conn.shared_client
        return out

# ################################################################################################################################
# ################################################################################################################################

class Microsoft:
    """ A container for Microsoft connections a service can establish.
    """
    __slots__ = 'cloud', 'fabric', 'power_platform'

    cloud: 'MicrosoftCloudFacade'
    fabric: 'MicrosoftFabricFacade'
    power_platform: 'MicrosoftPowerPlatformFacade'

    def __init__(self) -> 'None':
        self.cloud = MicrosoftCloudFacade()
        self.fabric = MicrosoftFabricFacade()
        self.power_platform = MicrosoftPowerPlatformFacade()

# ################################################################################################################################
# ################################################################################################################################

class AWSFacade:
    """ The API through which AWS connections are accessed by their names, e.g. self.aws['My AWS'].
    """
    __slots__ = ('conn_dict',)

    conn_dict: 'stranydict'

    def __getitem__(self, name:'str') -> 'AWSClient':

        # Look up the connection's configuration ..
        item = self.conn_dict[name]

        # .. and hand back the client that its wrapper maintains.
        out = item.conn.shared_client
        return out

# ################################################################################################################################
# ################################################################################################################################

class LLMFacade:
    """ The API through which LLM connections are accessed by their names, e.g. self.llm['My OpenAI'].
    """
    __slots__ = ('conn_dict',)

    conn_dict: 'stranydict'

    def __getitem__(self, name:'str') -> 'OutconnLLMWrapper':

        # Look up the connection's configuration ..
        item = self.conn_dict[name]

        # .. and hand back its wrapper, whose invoke, chat and ping check a client out of the queue internally.
        out = item.conn
        return out

# ################################################################################################################################
# ################################################################################################################################
