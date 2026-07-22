# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from base64 import b64encode
from importlib import import_module

# gRPC
import grpc
from grpc import StatusCode

# protobuf
from google.protobuf.json_format import MessageToJson, Parse
from google.protobuf.message_factory import GetMessageClass

# Zato
from zato.common.api import SEC_DEF_TYPE
from zato.common.exception import BadRequest, Conflict, Forbidden, InternalServerError, NotFound, ServiceUnavailable, \
    TooManyRequests, Unauthorized

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, stranydict
    from zato.server.base.config_manager import ConfigManager
    from zato.server.base.parallel import ParallelServer
    from zato.server.generic.api.outconn_grpc import OutconnGRPCWrapper

# ################################################################################################################################
# ################################################################################################################################

# The value gRPC servers expect in WWW-Authenticate-like challenges when authentication fails.
_auth_challenge = 'grpc'

# Maps gRPC status codes to the exceptions raised out of invokers - when such an exception
# bubbles up unhandled to a REST channel, the channel turns it into the matching HTTP status.
_status_code_to_exception = {
    StatusCode.INVALID_ARGUMENT:  BadRequest,
    StatusCode.NOT_FOUND:         NotFound,
    StatusCode.PERMISSION_DENIED: Forbidden,
    StatusCode.ALREADY_EXISTS:    Conflict,
    StatusCode.ABORTED:           Conflict,
    StatusCode.RESOURCE_EXHAUSTED: TooManyRequests,
    StatusCode.UNAVAILABLE:        ServiceUnavailable,
    StatusCode.DEADLINE_EXCEEDED:  ServiceUnavailable,
}

# The multi-callable types whose responses are streams to iterate over rather than single messages.
_response_streaming_types = (grpc.UnaryStreamMultiCallable, grpc.StreamStreamMultiCallable)

# ################################################################################################################################
# ################################################################################################################################

def exception_from_rpc_error(error:'grpc.RpcError', cid:'str') -> 'Exception':
    """ Turns a gRPC error into the matching Zato exception, keyed on the error's status code.
    """

    # A failed call is also a grpc.Call, which is what carries the code and the details.
    code = error.code()       # type: ignore
    details = error.details() # type: ignore

    message = f'gRPC error {code.name} -> {details}'

    # Authentication errors carry a challenge, hence the dedicated branch ..
    if code is StatusCode.UNAUTHENTICATED:
        out = Unauthorized(cid, message, _auth_challenge)

    # .. codes with a direct mapping produce their matching exception ..
    elif exception_class := _status_code_to_exception.get(code):
        out = exception_class(cid, message)

    # .. and anything else is reported as an internal server error.
    else:
        out = InternalServerError(cid, message)

    return out

# ################################################################################################################################
# ################################################################################################################################

def build_call_metadata(server:'ParallelServer', config:'stranydict') -> 'any_':
    """ Builds per-call gRPC metadata out of the security definition attached to a connection,
    or returns None if the connection has no security definition.
    """

    # No security definition means no metadata to send
    security_id = config.get('security_id')
    if not security_id:
        return None

    auth_type = config['auth_type']

    # Basic Auth credentials travel in the standard authorization header ..
    if auth_type == SEC_DEF_TYPE.BASIC_AUTH:
        sec_config = server.config_manager.basic_auth_get_by_id(security_id)
        credentials = f'{sec_config["username"]}:{sec_config["password"]}'
        encoded = b64encode(credentials.encode('utf8')).decode('utf8')
        out = (('authorization', f'Basic {encoded}'),)

    # .. an API key travels in the header the definition names - gRPC requires
    # .. metadata keys to be lowercase ..
    elif auth_type == SEC_DEF_TYPE.APIKEY:
        sec_config = server.config_manager.apikey_get_by_id(security_id)
        header_name = sec_config['username'].lower()
        out = ((header_name, sec_config['password']),)

    # .. and OAuth tokens are obtained, and refreshed as needed, by the server's own OAuth store.
    elif auth_type == SEC_DEF_TYPE.OAUTH:
        auth_header = server.oauth_store.get_auth_header(security_id)
        out = (('authorization', auth_header),)

    else:
        raise Exception(f'Unsupported security definition type for a gRPC connection -> {auth_type}')

    return out

# ################################################################################################################################
# ################################################################################################################################

def invoke_unary_from_json(wrapper:'OutconnGRPCWrapper', method_name:'str', request_json:'str', cid:'str') -> 'str':
    """ Invokes a unary method of a gRPC connection with a request built out of JSON,
    returning the response as JSON too. This is what dashboard test invocations use.
    """

    # Accessing the client builds the underlying channel and stub if they do not exist yet
    stub = wrapper.client
    stub_class = stub.__class__

    # The module with message classes sits next to the module the stub class came from -
    # this is how the protobuf compiler always lays the generated modules out.
    grpc_module_name = stub_class.__module__
    pb2_module_name = grpc_module_name[:-len('_grpc')]
    pb2_module = import_module(pb2_module_name)

    # The stub class is always named after the service it covers
    service_name = stub_class.__name__[:-len('Stub')]

    # Find the method's descriptor to learn what its request message looks like
    service_descriptor = pb2_module.DESCRIPTOR.services_by_name[service_name]
    method_descriptor = service_descriptor.methods_by_name[method_name]

    # Streaming methods cannot be represented as a single JSON document each way
    is_streaming = method_descriptor.client_streaming or method_descriptor.server_streaming
    if is_streaming:
        raise Exception(f'Only unary methods can be invoked this way and `{method_name}` is a streaming one')

    # Build the request message out of the JSON input ..
    request_class = GetMessageClass(method_descriptor.input_type)
    request = Parse(request_json, request_class())

    # .. security metadata comes from the connection's security definition ..
    metadata = build_call_metadata(wrapper.server, wrapper.config)

    kwargs = {}
    if metadata:
        kwargs['metadata'] = metadata

    # .. invoke the method now ..
    method = getattr(stub, method_name)

    try:
        response = method(request, **kwargs)
    except grpc.RpcError as error:
        raise exception_from_rpc_error(error, cid) from None

    # .. and return the response as JSON.
    out = MessageToJson(response, indent=2)
    return out

# ################################################################################################################################
# ################################################################################################################################

class _GRPCMethodProxy:
    """ Wraps one method of a gRPC stub, adding per-call security metadata
    and mapping gRPC errors to Zato exceptions.
    """
    def __init__(self, wrapper:'OutconnGRPCWrapper', method_name:'str', cid:'str') -> 'None':
        self._wrapper = wrapper
        self._method_name = method_name
        self._cid = cid

# ################################################################################################################################

    def __repr__(self) -> 'str':
        out = f'_GRPCMethodProxy({self._wrapper.config["name"]}.{self._method_name} at {hex(id(self))})'
        return out

# ################################################################################################################################

    def _wrap_response_stream(self, response_iterator:'any_') -> 'any_':
        """ Yields messages from a streaming response as they arrive - errors raised
        mid-iteration are mapped the same way unary errors are.
        """
        try:
            for item in response_iterator:
                yield item
        except grpc.RpcError as error:
            raise exception_from_rpc_error(error, self._cid) from None

# ################################################################################################################################

    def __call__(self, request:'any_'=None, **kwargs:'any_') -> 'any_':

        # Accessing the client builds the underlying channel and stub if they do not exist yet
        stub = self._wrapper.client
        method = getattr(stub, self._method_name)

        # Security metadata comes from the connection's security definition, resolved per call
        # so that refreshed credentials, e.g. new OAuth tokens, are always current.
        metadata = build_call_metadata(self._wrapper.server, self._wrapper.config)

        if metadata:
            kwargs.setdefault('metadata', metadata)

        # Invoke the method now - for response-streaming calls this returns an iterator
        # without blocking, for unary responses it blocks until the response arrives.
        try:
            response = method(request, **kwargs)
        except grpc.RpcError as error:
            raise exception_from_rpc_error(error, self._cid) from None

        # Streaming responses are wrapped so that messages are yielded as they arrive,
        # never buffered into a list, and errors raised mid-stream are mapped too.
        if isinstance(method, _response_streaming_types):
            out = self._wrap_response_stream(response)
        else:
            out = response

        return out

# ################################################################################################################################
# ################################################################################################################################

class GRPCInvoker:
    """ Wraps a single gRPC outgoing connection for use from services - attribute access
    resolves to the methods of the underlying stub.
    """
    def __init__(self, wrapper:'OutconnGRPCWrapper', cid:'str') -> 'None':
        self._wrapper = wrapper
        self._cid = cid

# ################################################################################################################################

    def __repr__(self) -> 'str':
        out = f'GRPCInvoker({self._wrapper.config["name"]} at {hex(id(self))})'
        return out

# ################################################################################################################################

    def __getattr__(self, method_name:'str') -> '_GRPCMethodProxy':
        out = _GRPCMethodProxy(self._wrapper, method_name, self._cid)
        return out

# ################################################################################################################################
# ################################################################################################################################

class GRPCFacade:
    """ Provides dict-like access to gRPC outgoing connections from services via self.grpc.
    """
    cid: 'str'
    _outconn_grpc: 'anydict'

    def init(self, cid:'str', config_manager:'ConfigManager') -> 'None':
        self.cid = cid
        self._outconn_grpc = config_manager.outconn_grpc

# ################################################################################################################################

    def __getitem__(self, name:'str') -> 'GRPCInvoker':

        # This will raise a KeyError if there is no such connection
        item = self._outconn_grpc[name]

        # The wrapper holds the underlying channel and stub
        wrapper = item['conn']

        out = GRPCInvoker(wrapper, self.cid)
        return out

# ################################################################################################################################
# ################################################################################################################################
