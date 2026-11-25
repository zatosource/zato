# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The forwarding of the services that change configuration from a worker to the config process. The worker sends
# the request of an invocation with the parts of its request context that describe the HTTP request, the config process
# runs the service and returns its response or its exception, and the worker gives the caller that response
# or raises that exception, as if the service had run in the worker.

# stdlib
from json import loads

# Zato
from zato.common.exception import Inactive, Reportable, ZatoException
from zato.common.json_internal import dumps
from zato.server.config_audit import Invoker_Security_Username

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, stranydict
    from zato.server.base.parallel import ParallelServer
    from zato.server.service import Service

    any_ = any_
    anydict = anydict
    ParallelServer = ParallelServer
    Service = Service
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The keys of a request context that describe the HTTP request, which a forwarded invocation keeps
    Request_Ctx_Keys = {'REQUEST_METHOD', 'PATH_INFO', 'zato.http.GET', 'zato.http.POST', 'zato.http.path_params'}

    # The prefix of the keys of a request context that hold the headers of the HTTP request
    Header_Prefix = 'HTTP_'

# ################################################################################################################################
# ################################################################################################################################

def get_http_request_ctx(request_ctx:'stranydict') -> 'stranydict':
    """ Returns the parts of a request context that describe the HTTP request of an invocation.
    """
    out:'stranydict' = {}

    for key, value in request_ctx.items():
        if key in ModuleCtx.Request_Ctx_Keys or key.startswith(ModuleCtx.Header_Prefix):
            out[key] = value

    return out

# ################################################################################################################################

def new_forward_body(service:'Service', channel:'str', request_ctx:'stranydict') -> 'anydict':
    """ Returns what a worker sends to the config process to invoke a service there.
    """
    raw_request = service.request.raw_request

    # A request that arrived as text or bytes is parsed again in the config process, and any other is sent as JSON
    if isinstance(raw_request, bytes):
        payload = raw_request.decode('utf8')
        is_text = True

    elif isinstance(raw_request, str):
        payload = raw_request
        is_text = True

    else:
        payload = dumps(raw_request)
        is_text = False

    http_request_ctx = get_http_request_ctx(request_ctx)

    # The config process has no channel of its own, so the identity the invocation runs under travels with it,
    # either the one of the channel or the one the service invoker propagated, for the config-audit events to record.
    if identity := service.channel.security.username:
        http_request_ctx[Invoker_Security_Username] = identity

    elif identity := request_ctx.get(Invoker_Security_Username):
        http_request_ctx[Invoker_Security_Username] = identity

    out = {
        'name': service.name,
        'cid': service.cid,
        'channel': channel,
        'data_format': service.data_format,
        'transport': service.transport,
        'payload': payload,
        'is_text': is_text,
        'request_ctx': dumps(http_request_ctx),
    }

    return out

# ################################################################################################################################

def describe_error(error:'Exception') -> 'anydict':
    """ Returns what a worker needs to raise an exception of the same kind as one that a forwarded invocation raised.
    """
    out:'anydict' = {
        'is_reportable': False,
        'is_zato': False,
        'message': str(error),
        'status': 0,
        'needs_msg': False,
    }

    if isinstance(error, Reportable):
        out['is_reportable'] = True
        out['is_zato'] = True
        out['message'] = error.msg
        out['status'] = error.status
        out['needs_msg'] = error.needs_msg

    elif isinstance(error, ZatoException):
        out['is_zato'] = True
        out['message'] = error.msg

    return out

# ################################################################################################################################

def raise_error(cid:'str', error:'anydict') -> 'None':
    """ Raises in a worker the exception that a forwarded invocation raised in the config process.
    """
    message = error['message']

    if error['is_reportable']:
        raise Reportable(cid, message, error['status'], error['needs_msg'])

    elif error['is_zato']:
        raise ZatoException(cid, message)

    # .. any other exception has no kind of its own that a caller tells apart.
    else:
        raise Exception(message)

# ################################################################################################################################

def invoke_forwarded(server:'ParallelServer', body:'anydict') -> 'anydict':
    """ Runs in the config process an invocation that a worker forwarded and returns its result.
    """
    if body['is_text']:
        payload = body['payload']
    else:
        payload = loads(body['payload'])

    request_ctx = loads(body['request_ctx'])

    service, is_active = server.service_store.new_instance_by_name(body['name'])

    if not is_active:
        raise Inactive(service.get_name())

    response = service.update_handle(service.set_response_data, service, payload, body['channel'], body['data_format'],
        body['transport'], server, server.config_dispatcher, server.config_manager, body['cid'],
        serialize=False, request_ctx=request_ctx)

    out = {
        'payload': dumps(response),
        'status_code': service.response.status_code,
        'headers': dumps(service.response.headers),
        'content_type': service.response.content_type,
        'content_type_changed': service.response.content_type_changed,
    }

    return out

# ################################################################################################################################

def apply_forward_result(service:'Service', result:'anydict') -> 'None':
    """ Gives the response of a forwarded invocation to the service object of the worker, or raises its exception.
    """
    if 'error' in result:
        raise_error(service.cid, result['error'])

    response = service.response

    # The payload is the output of the service as the config process produced it already,
    # so the declaration of the output of the service does not apply to it a second time.
    response._has_io_output = False
    response.payload = loads(result['payload'])

    response.status_code = result['status_code']
    response.headers.update(loads(result['headers']))

    if result['content_type_changed']:
        response.content_type = result['content_type']

# ################################################################################################################################
# ################################################################################################################################
