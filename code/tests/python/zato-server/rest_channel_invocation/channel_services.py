# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The user services behind the REST and SOAP channels of the suite. Each service either reports
# what it observed of its request or returns a response of a particular shape.

# stdlib
from dataclasses import dataclass
from time import perf_counter_ns

# gevent
from gevent import sleep as gevent_sleep

# Zato
from zato.common import SOAPMessage
from zato.common.exception import BadRequest, Forbidden, NotFound, Unauthorized
from zato.common.util.logging_ import current_cid, current_service_name
from zato.input_output import ServiceInput
from zato.server.service import Int, Model, Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, strdict

# ################################################################################################################################
# ################################################################################################################################

# The request context keys whose values the echo service reports when they are present
_reported_context_keys = (
    'CONTENT_LENGTH',
    'CONTENT_TYPE',
    'PATH_INFO',
    'QUERY_STRING',
    'RAW_URI',
    'REMOTE_ADDR',
    'REQUEST_METHOD',
    'SERVER_PROTOCOL',
    'zato.http.remote_addr',
)

# The value types reported as they are, everything else is reported as its string form
_plain_types = (str, int, float, bool, type(None))

# How many times the cost service invokes a handle method
_cost_iterations = 100_000

# ################################################################################################################################
# ################################################################################################################################

def describe_value(value:'any_') -> 'strdict':
    """ Returns the type name of a value along with a JSON-compatible form of it.
    """
    type_name = type(value).__name__

    if isinstance(value, bytes):
        reported = value.decode('utf-8', 'replace')

    elif isinstance(value, dict):
        reported = {}
        for key, item in value.items():
            reported[str(key)] = describe_value(item)

    elif isinstance(value, ServiceInput):
        reported = {}
        for key, item in value.items():
            reported[key] = describe_value(item)

    elif isinstance(value, (list, tuple)):
        reported = []
        for item in value:
            reported.append(describe_value(item))

    elif isinstance(value, _plain_types):
        reported = value

    else:
        reported = str(value)

    out = {'type': type_name, 'value': reported}
    return out

# ################################################################################################################################

def describe_request(service:'Service') -> 'anydict':
    """ Returns everything a service observes of the HTTP request that invoked it.
    """
    request_ctx = service.request_ctx
    http = service.request.http

    context:'strdict' = {}

    for key in _reported_context_keys:
        if key in request_ctx:
            context[key] = describe_value(request_ctx[key])

    context_keys:'anylist' = []
    for key in request_ctx:
        context_keys.append(key)
    context_keys.sort()

    out = {
        'cid': service.cid,
        'logging_cid': current_cid.get(),
        'logging_service_name': current_service_name.get(),
        'service_name': service.name,
        'method': http.method,
        'path': http.path,
        'params': dict(http.params),
        'GET': dict(http.GET),
        'POST': dict(http.POST),
        'headers': dict(http.headers),
        'user_agent': http.user_agent,
        'http_to_dict': http.to_dict(),
        'payload': describe_value(service.request.payload),
        'raw_request': describe_value(service.request.raw_request),
        'input': describe_value(service.request.input),
        'channel_params': dict(service.request.channel_params),
        'channel': service.channel.to_dict(),
        'channel_type': service.channel.type,
        'data_format': service.data_format,
        'transport': service.transport,
        'request_timestamp_utc': str(request_ctx['zato.request_timestamp_utc']),
        'request_timestamp': str(request_ctx['zato.request_timestamp']),
        'context': context,
        'context_keys': context_keys,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class CustomerRequest(Model):
    customer_id: int
    name: str

# ################################################################################################################################

@dataclass(init=False)
class CustomerResponse(Model):
    customer_id: int
    name: str
    is_active: bool

# ################################################################################################################################
# ################################################################################################################################

class Echo(Service):
    """ Returns everything it observed of its request.
    """
    name = 'test.channel.echo'

    def handle(self) -> 'None':
        self.response.payload = describe_request(self)

# ################################################################################################################################

class Ping(Service):
    """ Returns a small constant response.
    """
    name = 'test.channel.ping'

    def handle(self) -> 'None':
        self.response.payload = {'customer_id': 123, 'status': 'active'}

# ################################################################################################################################

class DeclaredInput(Service):
    """ Returns the input it declared, as parsed from the request.
    """
    name = 'test.channel.input.declared'
    input = Int('customer_id'), 'name', '-segment'

    def handle(self) -> 'None':
        self.response.payload = {
            'customer_id': describe_value(self.request.input.customer_id),
            'name': describe_value(self.request.input.name),
            'segment': describe_value(self.request.input.segment),
        }

# ################################################################################################################################

class ModelInput(Service):
    """ Returns the fields of the model its request was parsed into.
    """
    name = 'test.channel.input.model'
    input = CustomerRequest

    def handle(self) -> 'None':
        request:'CustomerRequest' = self.request.input
        self.response.payload = {
            'type': type(request).__name__,
            'customer_id': describe_value(request.customer_id),
            'name': describe_value(request.name),
        }

# ################################################################################################################################
# ################################################################################################################################

class ResponseDict(Service):
    name = 'test.channel.response.dict'

    def handle(self) -> 'None':
        self.response.payload = {
            'customer_id': 123,
            'name': 'John Smith',
            'city': 'Zürich',
            'is_active': True,
            'balance': 1.5,
            'note': None,
            'tags': ['retail', 'priority'],
            'address': {'street': 'Main Street', 'number': 10},
        }

# ################################################################################################################################

class ResponseList(Service):
    name = 'test.channel.response.list'

    def handle(self) -> 'None':
        self.response.payload = [{'customer_id': 1, 'name': 'John Smith'}, {'customer_id': 2, 'name': 'Mary Johnson'}]

# ################################################################################################################################

class ResponseString(Service):
    name = 'test.channel.response.string'

    def handle(self) -> 'None':
        self.response.payload = 'Customer record accepted'

# ################################################################################################################################

class ResponseBytes(Service):
    name = 'test.channel.response.bytes'

    def handle(self) -> 'None':
        self.response.payload = b'Customer record accepted'

# ################################################################################################################################

class ResponseNone(Service):
    name = 'test.channel.response.none'

    def handle(self) -> 'None':
        pass

# ################################################################################################################################

class ResponseDotAccess(Service):
    name = 'test.channel.response.dot-access'

    def handle(self) -> 'None':
        self.response.payload.customer.details.customer_id = 123

# ################################################################################################################################

class ResponseModel(Service):
    name = 'test.channel.response.model'

    def handle(self) -> 'None':
        response = CustomerResponse()
        response.customer_id = 123
        response.name = 'John Smith'
        response.is_active = True
        self.response.payload = response

# ################################################################################################################################

class ResponseModelList(Service):
    name = 'test.channel.response.model-list'

    def handle(self) -> 'None':

        first = CustomerResponse()
        first.customer_id = 1
        first.name = 'John Smith'
        first.is_active = True

        second = CustomerResponse()
        second.customer_id = 2
        second.name = 'Mary Johnson'
        second.is_active = False

        self.response.payload = [first, second]

# ################################################################################################################################

class ResponseStatusHeaders(Service):
    name = 'test.channel.response.status-headers'

    def handle(self) -> 'None':
        self.response.status_code = 201
        self.response.headers['X-Customer-ID'] = '123'
        self.response.headers['Location'] = '/customers/123'
        self.response.payload = {'customer_id': 123}

# ################################################################################################################################

class ResponseContentType(Service):
    name = 'test.channel.response.content-type'

    def handle(self) -> 'None':
        self.response.content_type = 'application/xml'
        self.response.payload = '<customer><id>123</id></customer>'

# ################################################################################################################################

class ResponseErrorStatus(Service):
    name = 'test.channel.response.error-status'

    def handle(self) -> 'None':
        self.response.status_code = 422
        self.response.payload = {'error': 'Customer ID is invalid'}

# ################################################################################################################################
# ################################################################################################################################

class ErrorException(Service):
    name = 'test.channel.error.exception'

    def handle(self) -> 'None':
        raise Exception('Customer database is unavailable')

# ################################################################################################################################

class ErrorBadRequest(Service):
    name = 'test.channel.error.bad-request'

    def handle(self) -> 'None':
        raise BadRequest(self.cid, 'Customer ID is missing')

# ################################################################################################################################

class ErrorUnauthorized(Service):
    name = 'test.channel.error.unauthorized'

    def handle(self) -> 'None':
        raise Unauthorized(self.cid, 'Customer token expired', 'Bearer')

# ################################################################################################################################

class ErrorForbidden(Service):
    name = 'test.channel.error.forbidden'

    def handle(self) -> 'None':
        raise Forbidden(self.cid, 'Customer account is locked')

# ################################################################################################################################

class ErrorNotFound(Service):
    name = 'test.channel.error.not-found'

    def handle(self) -> 'None':
        raise NotFound(self.cid, 'Customer not found')

# ################################################################################################################################

class ErrorAfterHeaders(Service):
    name = 'test.channel.error.after-headers'

    def handle(self) -> 'None':
        self.response.headers['X-Customer-ID'] = '123'
        self.response.status_code = 201
        raise Exception('Customer database is unavailable')

# ################################################################################################################################
# ################################################################################################################################

class Hooks(Service):
    """ Reports the order in which its hooks and its handle method ran.
    """
    name = 'test.channel.hooks'

    def before_handle(self, *args:'any_', **kwargs:'any_') -> 'None':
        self.environ['calls'] = ['before_handle']

    def handle(self) -> 'None':
        self.environ['calls'].append('handle')
        self.response.payload = {'calls': self.environ['calls']}

    def after_handle(self, *args:'any_', **kwargs:'any_') -> 'None':
        self.environ['calls'].append('after_handle')
        self.response.payload = {'calls': self.environ['calls']}

# ################################################################################################################################

class NotAccepted(Service):
    """ Refuses every request in its accept method.
    """
    name = 'test.channel.not-accepted'

    def accept(self, *args:'any_', **kwargs:'any_') -> 'bool':
        out = False
        return out

    def handle(self) -> 'None':
        self.response.payload = {'is_handled': True}

# ################################################################################################################################

class Verbs(Service):
    """ Implements GET and POST through handlers of their own, and no other method.
    """
    name = 'test.channel.verbs'

    def handle_GET(self) -> 'None':
        self.response.payload = {'verb': 'GET'}

    def handle_POST(self) -> 'None':
        self.response.payload = {'verb': 'POST', 'payload': describe_value(self.request.payload)}

# ################################################################################################################################

class Sleep(Service):
    """ Sleeps cooperatively for the number of seconds the query string names.
    """
    name = 'test.channel.sleep'

    def handle(self) -> 'None':
        seconds = float(self.request.http.GET['seconds'])
        gevent_sleep(seconds)
        self.response.payload = {'slept': seconds}

# ################################################################################################################################

class AuthRejection(Service):
    """ Accepts requests whose credentials did not authenticate and reports what it observed.
    """
    name = 'test.channel.auth-rejection'
    handles_auth_rejection = True

    def handle(self) -> 'None':
        self.response.payload = {'security': self.channel.security.to_dict(), 'echo': describe_request(self)}

# ################################################################################################################################
# ################################################################################################################################

class SOAPEcho(Service):
    """ Returns the operation and the payload of its SOAP request in a SOAP response.
    """
    name = 'test.channel.soap.echo'

    def handle(self) -> 'None':
        request:'SOAPMessage' = self.request.payload

        response = SOAPMessage()
        response.operation = self.request.soap.operation
        response.soap_version = self.request.soap.soap_version
        response.customer_id = request.customer_id
        response.name = request.name

        self.response.payload = response

# ################################################################################################################################

class SOAPError(Service):
    name = 'test.channel.soap.error'

    def handle(self) -> 'None':
        raise Exception('Customer database is unavailable')

# ################################################################################################################################

class SOAPBadRequest(Service):
    name = 'test.channel.soap.bad-request'

    def handle(self) -> 'None':
        raise BadRequest(self.cid, 'Customer ID is missing')

# ################################################################################################################################
# ################################################################################################################################

class HandleCost(Service):
    """ Measures how long the handle method of the ping service takes on its own.
    """
    name = 'test.channel.handle-cost'

    def handle(self) -> 'None':
        impl_name = self.server.service_store.name_to_impl_name[Ping.name]
        instance, _ = self.server.service_store.new_instance(impl_name)

        start = perf_counter_ns()

        for _ in range(_cost_iterations):
            instance.handle()

        elapsed = perf_counter_ns() - start

        self.response.payload = {'nanoseconds_per_call': elapsed / _cost_iterations}

# ################################################################################################################################
# ################################################################################################################################
