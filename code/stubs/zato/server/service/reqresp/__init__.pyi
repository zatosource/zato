from typing import Any, TYPE_CHECKING

import logging
from copy import deepcopy
from bunch import Bunch, bunchify
from lxml.etree import _Element as EtreeElement
from lxml.objectify import ObjectifiedElement
from zato.common.api import simple_types
from zato.common.marshal_.api import Model
from zato.common.json_internal import loads
from zato.common.typing_ import cast_
from zato.common.util.api import make_repr
from zato.common.util.http_ import get_form_data as util_get_form_data
from zato.simpleio import ServiceInput
from logging import Logger
from arrow import Arrow
from kombu.message import Message as KombuAMQPMessage
from zato.common.odb.api import PoolStore
from zato.common.typing_ import any_, callable_, stranydict, strnone
from zato.server.config import ConfigDict, ConfigStore
from zato.server.connection.email import EMailAPI
from zato.server.connection.ftp import FTPStore
from zato.server.connection.search import SearchAPI
from zato.simpleio import CySimpleIO

if TYPE_CHECKING:
    from zato.server.service import AMQPFacade, Service


class HTTPRequestData:
    method: Any
    GET: _Bunch
    POST: _Bunch
    path: Any
    params: _Bunch
    user_agent: Any
    headers: _Bunch
    _wsgi_environ: Any
    def __init__(self: Any, _Bunch: Any = ...) -> None: ...
    def init(self: Any, wsgi_environ: Any = ...) -> None: ...
    def _extract_headers(self: Any) -> None: ...
    def get_form_data(self: Any) -> stranydict: ...
    def __repr__(self: Any) -> None: ...
    def to_dict(self: Any) -> stranydict: ...

class AMQPRequestData:
    msg: Any
    ack: Any
    reject: Any
    def __init__(self: Any, msg: Any) -> None: ...

class Request:
    text: Any
    service: Any
    logger: Logger
    payload: Any
    text: Any
    input: Any
    cid: str
    data_format: str
    transport: str
    encrypt_func: Any
    encrypt_secrets: Any
    bytes_to_str_encoding: str
    _wsgi_environ: stranydict
    channel_params: stranydict
    merge_channel_params: Any
    http: HTTPRequestData
    amqp: AMQPRequestData
    enforce_string_encoding: Any
    bunchified: Any
    def __init__(self: Any, service: Any, simple_io_config: Any = ..., data_format: Any = ..., transport: Any = ...) -> None: ...
    def init(self: Any, is_sio: Any, cid: Any, sio: Any, data_format: Any, transport: Any, wsgi_environ: Any, encrypt_func: Any) -> None: ...
    @property
    def raw_request(self: Any) -> any_: ...
    def raw_request(self: Any, value: any_) -> any_: ...
    def to_bunch(self: Any) -> None: ...

class Outgoing:
    amqp: AMQPFacade
    ftp: Any
    odoo: ConfigDict
    plain_http: Any
    rest: ConfigDict
    soap: ConfigDict
    sql: PoolStore
    sap: ConfigDict
    ldap: stranydict
    mongodb: stranydict
    redis: Any
    def __init__(self: Any, amqp: Any = ..., odoo: Any = ..., plain_http: Any = ..., soap: Any = ..., sql: Any = ..., sap: Any = ..., ldap: Any = ..., mongodb: Any = ..., redis: Any = ...) -> None: ...

class Cloud:
    confluence: Any
    jira: Any
    salesforce: Any
    ms365: Any
    confluence: stranydict
    jira: stranydict
    salesforce: stranydict
    ms365: stranydict
