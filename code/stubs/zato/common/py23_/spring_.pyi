from typing import Any, TYPE_CHECKING

from six import PY2
import http.client as http_client
import socket
import ssl
import logging
import sys
import traceback
from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from xmlrpclib import ServerProxy, Transport
from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from xmlrpc.client import ServerProxy, Transport


class CAValidatingHTTPSConnection(http_client.HTTPConnection):
    ca_certs: Any
    keyfile: Any
    certfile: Any
    cert_reqs: Any
    ssl_version: Any
    def __init__(self: Any, host: Any, port: Any = ..., ca_certs: Any = ..., keyfile: Any = ..., certfile: Any = ..., cert_reqs: Any = ..., strict: Any = ..., ssl_version: Any = ..., timeout: Any = ...) -> None: ...
    def connect(self: Any) -> None: ...
    def wrap_socket(self: Any, sock: Any) -> None: ...

class CAValidatingHTTPS(http_client.HTTPConnection):
    _connection_class: Any
    def __init__(self: Any, host: Any = ..., port: Any = ..., strict: Any = ..., ca_certs: Any = ..., keyfile: Any = ..., certfile: Any = ..., cert_reqs: Any = ..., ssl_version: Any = ..., timeout: Any = ...) -> None: ...

class VerificationException(Exception):
    ...

class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths: Any
    def setup(self: Any) -> None: ...

class SSLServer(SimpleXMLRPCServer):
    keyfile: Any
    certfile: Any
    ca_certs: Any
    cert_reqs: Any
    ssl_version: Any
    do_handshake_on_connect: Any
    suppress_ragged_eofs: Any
    ciphers: Any
    logRequests: Any
    verify_fields: kwargs.get
    def __init__(self: Any, host: Any = ..., port: Any = ..., keyfile: Any = ..., certfile: Any = ..., ca_certs: Any = ..., cert_reqs: Any = ..., ssl_version: Any = ..., do_handshake_on_connect: Any = ..., suppress_ragged_eofs: Any = ..., ciphers: Any = ..., log_requests: Any = ..., **kwargs: Any) -> None: ...
    def get_request(self: Any) -> None: ...
    def verify_request(self: Any, sock: Any, from_addr: Any) -> None: ...
    def verify_peer(self: Any, cert: Any, from_addr: Any) -> None: ...
    def register_functions(self: Any) -> None: ...

class SSLClientTransport(Transport):
    user_agent: Any
    ca_certs: Any
    keyfile: Any
    certfile: Any
    cert_reqs: Any
    ssl_version: Any
    timeout: Any
    strict: Any
    def __init__(self: Any, ca_certs: Any = ..., keyfile: Any = ..., certfile: Any = ..., cert_reqs: Any = ..., ssl_version: Any = ..., timeout: Any = ..., strict: Any = ...) -> None: ...
    def make_connection(self: Any, host: Any) -> None: ...

class SSLClient(ServerProxy):
    logger: logging.getLogger
    def __init__(self: Any, uri: Any = ..., ca_certs: Any = ..., keyfile: Any = ..., certfile: Any = ..., cert_reqs: Any = ..., ssl_version: Any = ..., transport: Any = ..., encoding: Any = ..., verbose: Any = ..., allow_none: Any = ..., use_datetime: Any = ..., timeout: Any = ..., strict: Any = ...) -> None: ...
