# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Runs one request through the request dispatcher alone and through the REST channel router followed by the
# dispatcher for the requests the router declines, and reduces what each produced to comparable values.

# stdlib
import logging
import re
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import NamedTuple
from unittest.mock import patch

# Zato
from router_requests import build_request_ctx
from zato.common.rate_limiting import headers as headers_module
from zato.common.rate_limiting.headers import Rate_Limit_Result_Key
from zato.server.connection.http_soap import channel as channel_module
from zato.common.util.logging_ import current_cid, current_service_name
from zato_server_core.zato_server_core import ChannelRouter

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from router_environment import Clock, RouterWorld
    from router_requests import ChannelRequest
    from zato.common.typing_ import any_, anydict, anylist, strdict

# ################################################################################################################################
# ################################################################################################################################

Test_CID = 'zcid-router-0001'
Test_Request_Timestamp = '2026-11-13T12:00:00'

# What a context variable holds when nothing has bound it
_unbound = '<unbound>'

# Object addresses differ between the two sides and are not part of what is compared
_address_pattern = re.compile(r' at 0x[0-9a-f]+')

# ################################################################################################################################
# ################################################################################################################################

class RecordView(NamedTuple):
    name: 'str'
    level: 'int'
    pathname: 'str'
    lineno: 'int'
    func_name: 'str'
    message: 'str'
    cid: 'str'
    service_name: 'str'

# ################################################################################################################################

class Invocation(NamedTuple):
    channel_name: 'str'
    url_params: 'strdict'

# ################################################################################################################################

class Outcome(NamedTuple):
    body: 'any_'
    request_ctx: 'anydict'
    records: 'anylist'
    invocation: 'Invocation | None'

# ################################################################################################################################

class _InvocationMarker:
    """ What the dispatcher returns in place of a service response.
    """

# ################################################################################################################################
# ################################################################################################################################

class RecordCollector(logging.Handler):
    """ Collects the log records of one side of a comparison, with the logging context at the time of each.
    """
    def __init__(self) -> 'None':
        super().__init__(logging.NOTSET)
        self.records:'anylist' = []

    def emit(self, record:'logging.LogRecord') -> 'None':
        message = record.getMessage()
        message = _address_pattern.sub(' at 0x', message)

        view = RecordView(
            name=record.name,
            level=record.levelno,
            pathname=record.pathname,
            lineno=record.lineno,
            func_name=record.funcName,
            message=message,
            cid=current_cid.get(_unbound),
            service_name=current_service_name.get(_unbound),
        )
        self.records.append(view)

# ################################################################################################################################
# ################################################################################################################################

def snapshot_request_ctx(request_ctx:'anydict') -> 'anydict':
    """ Returns the request context as comparable values, with each channel item reduced to its name.
    """
    out = {}

    for key, value in request_ctx.items():

        if key == 'zato.channel_item':
            if value is not None:
                value = value['name']

        elif key == 'zato.http.response.headers':
            value = dict(value)

        elif key == 'zato.sec_def':
            value = dict(value)
            value['impl'] = dict(value['impl'])

        elif key == Rate_Limit_Result_Key:
            value = (value.is_allowed, value.is_disallowed, value.limit, value.remaining, value.retry_after_us)

        out[key] = value

    return out

# ################################################################################################################################

def copy_request_ctx(request_ctx:'anydict') -> 'anydict':
    """ Returns a copy of a request context as the HTTP server builds it, with a response header dict of its own.
    """
    out = dict(request_ctx)
    out['zato.http.response.headers'] = dict(request_ctx['zato.http.response.headers'])

    return out

# ################################################################################################################################
# ################################################################################################################################

def _collect(collector:'RecordCollector') -> 'None':
    root = logging.getLogger()
    root.addHandler(collector)

# ################################################################################################################################

def _release(collector:'RecordCollector') -> 'None':
    root = logging.getLogger()
    root.removeHandler(collector)

# ################################################################################################################################

def _dispatch(world:'RouterWorld', request_ctx:'anydict', user_agent:'str', remote_addr:'str', invocations:'anylist') -> 'any_':
    """ Dispatches one request, recording an invocation in place of invoking the service.
    """
    def invoke_and_format(
        cid:'any_',
        meta:'any_',
        url_match:'any_',
        channel_item:'any_',
        request_ctx:'any_',
        payload:'any_',
        post_data:'any_',
        config_manager:'any_',
        zato_response_headers_container:'any_',
    ) -> 'any_':
        invocation = Invocation(channel_name=channel_item['name'], url_params=dict(url_match))
        invocations.append(invocation)
        out = _InvocationMarker
        return out

    world.dispatcher._invoke_and_format = invoke_and_format

    out = world.dispatcher.dispatch(
        Test_CID, Test_Request_Timestamp, request_ctx, world.config_manager, user_agent, remote_addr)

    return out

# ################################################################################################################################

def run_dispatcher(world:'RouterWorld', request_ctx:'anydict', user_agent:'str', remote_addr:'str') -> 'Outcome':
    """ Runs a request through the dispatcher alone.
    """
    collector = RecordCollector()
    invocations:'anylist' = []

    _collect(collector)

    try:
        body = _dispatch(world, request_ctx, user_agent, remote_addr, invocations)
    finally:
        _release(collector)

    if invocations:
        invocation = invocations[0]
        body = None
    else:
        invocation = None

    out = Outcome(body, snapshot_request_ctx(request_ctx), collector.records, invocation)
    return out

# ################################################################################################################################

class RoutedOutcome(NamedTuple):
    code: 'int'
    outcome: 'Outcome'

# ################################################################################################################################

def run_router(world:'RouterWorld', request_ctx:'anydict', user_agent:'str', remote_addr:'str') -> 'RoutedOutcome':
    """ Runs a request through the router and, if the router declines it, through the dispatcher.

    A declined request must reach the dispatcher exactly as it arrived, with no log record emitted for it.
    """
    pristine = snapshot_request_ctx(request_ctx)

    cid_before = current_cid.get(_unbound)
    service_name_before = current_service_name.get(_unbound)

    collector = RecordCollector()
    _collect(collector)

    try:
        code, value = world.router.route(Test_CID, request_ctx, user_agent, remote_addr)
    finally:
        _release(collector)

    if current_cid.get(_unbound) != cid_before:
        raise Exception('The router did not restore the correlation ID of the logging context')

    if current_service_name.get(_unbound) != service_name_before:
        raise Exception('The router did not restore the service name of the logging context')

    if code == ChannelRouter.DISPATCHER:

        if snapshot_request_ctx(request_ctx) != pristine:
            raise Exception('The router changed the request context of a request it declined')

        if collector.records:
            raise Exception(f'The router logged a request it declined -> {collector.records}')

        outcome = run_dispatcher(world, request_ctx, user_agent, remote_addr)

    elif code == ChannelRouter.INVOKE:
        channel_item, url_params = value
        invocation = Invocation(channel_name=channel_item['name'], url_params=url_params)
        outcome = Outcome(None, snapshot_request_ctx(request_ctx), collector.records, invocation)

    else:
        outcome = Outcome(value, snapshot_request_ctx(request_ctx), collector.records, None)

    out = RoutedOutcome(code, outcome)
    return out

# ################################################################################################################################
# ################################################################################################################################

def _fixed_utcnow() -> 'datetime':
    out = datetime(2026, 11, 13, 12, 0, 0, tzinfo=timezone.utc)
    return out

# ################################################################################################################################

@contextmanager
def pinned_time(clock:'Clock') -> 'any_':
    """ Makes the dispatcher read the clock of the comparison and the same date for every Retry-After header.
    """
    with patch.object(channel_module, 'current_time_us', clock):
        with patch.object(headers_module, '_datetime_utcnow', _fixed_utcnow):
            yield

# ################################################################################################################################

def compare(dispatcher_world:'RouterWorld', router_world:'RouterWorld', request:'ChannelRequest') -> 'int':
    """ Runs one request through both sides, confirms they produced the same, and returns the code of the router.
    """
    dispatcher_ctx = build_request_ctx(request)
    router_ctx = build_request_ctx(request)

    expected = run_dispatcher(dispatcher_world, dispatcher_ctx, request.user_agent, request.remote_addr)
    routed = run_router(router_world, router_ctx, request.user_agent, request.remote_addr)

    assert routed.outcome.body == expected.body
    assert routed.outcome.invocation == expected.invocation
    assert routed.outcome.request_ctx == expected.request_ctx
    assert routed.outcome.records == expected.records

    out = routed.code
    return out

# ################################################################################################################################
# ################################################################################################################################
