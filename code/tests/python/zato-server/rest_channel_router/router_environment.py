# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The channels, security definitions and server objects that the REST channel router is compared against
# the request dispatcher with. Each side of a comparison receives a set of its own, so that neither side
# observes the rate limit counters or the memoized channel headers of the other.

# stdlib
import ast
import copy
import inspect
import logging
import textwrap

# Zato
from zato.common.ext.bunch import Bunch
from zato.common.rate_limiting.manager import RateLimitingManager
from zato.common.util.logging_ import current_cid, current_service_name, escape_nonprintable
from zato.common.util.url_dispatcher import build_methods_allowed_re, get_match_target, resolve_match_slash
from zato.server.connection.http_soap.channel import get_deprecation_headers, RequestDispatcher
from zato.server.connection.http_soap.url_data import _channel_sort_key, URLData
from zato.server.connection.http_soap.url_dispatcher import Matcher
from zato_server_core.zato_server_core import ChannelRouter

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, callable_, strdict

# ################################################################################################################################
# ################################################################################################################################

Methods_Allowed = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD']

Server_Name = 'test.router.server'

# The dispatcher of a comparison never invokes a service, so it has no request handler
_no_request_handler:'any_' = None

# A path whose incoming requests are not logged
Ignored_Path = '/api/ignored'

# The service that answers the rejections of its security definition rate limit itself
Self_Limited_Service = 'test.service.self-limited'

# A rule that admits a burst of two requests and then one request per second, for every address
_burst_rule = {
    'cidr_list': ['0.0.0.0/0'],
    'time_range': [{
        'is_all_day': True,
        'disabled': False,
        'disallowed': False,
        'rate': 1,
        'burst': 2,
        'limit': 100,
        'limit_unit': 'minute',
    }],
}

# A rule that refuses every address
_disallowed_rule = {
    'cidr_list': ['0.0.0.0/0'],
    'time_range': [{
        'is_all_day': True,
        'disabled': False,
        'disallowed': True,
        'rate': 1,
        'burst': 2,
        'limit': 100,
        'limit_unit': 'minute',
    }],
}

# ################################################################################################################################
# ################################################################################################################################

class Credentials:
    Basic_Username = 'john.smith'
    Basic_Password = 'password.basic'
    Limited_Username = 'maria.johnson'
    Limited_Password = 'password.limited'
    API_Key = 'key.apikey'
    Static_Token = 'token.static'
    Field_Token = 'token.field'

# ################################################################################################################################
# ################################################################################################################################

def _security_definitions() -> 'strdict':
    """ Returns the security definitions of the channels, by name.
    """
    out = {
        'test.basic': {
            'id': 101, 'name': 'test.basic', 'sec_type': 'basic_auth', 'is_active': True,
            'username': Credentials.Basic_Username, 'password': Credentials.Basic_Password, 'realm': 'Zato',
        },
        'test.basic.limited': {
            'id': 102, 'name': 'test.basic.limited', 'sec_type': 'basic_auth', 'is_active': True,
            'username': Credentials.Limited_Username, 'password': Credentials.Limited_Password, 'realm': 'Zato',
        },
        'test.apikey': {
            'id': 103, 'name': 'test.apikey', 'sec_type': 'apikey', 'is_active': True,
            'username': 'test.apikey', 'header': 'HTTP_X_API_KEY', 'password': Credentials.API_Key,
        },
        'test.bearer': {
            'id': 104, 'name': 'test.bearer', 'sec_type': 'oauth', 'is_active': True,
            'password': Credentials.Static_Token, 'is_static_token': True,
        },
        'test.bearer.field': {
            'id': 105, 'name': 'test.bearer.field', 'sec_type': 'oauth', 'is_active': True,
            'static_token': Credentials.Field_Token,
        },
        'test.basic.inactive': {
            'id': 106, 'name': 'test.basic.inactive', 'sec_type': 'basic_auth', 'is_active': False,
            'username': Credentials.Basic_Username, 'password': Credentials.Basic_Password, 'realm': 'Zato',
        },
    }

    return out

# ################################################################################################################################

def make_channel(name:'str', method:'str', url_path:'str', **options:'any_') -> 'anydict':
    """ Returns the definition of one REST channel, with the options given replacing the defaults.
    """
    out = {
        'id': 0,
        'name': name,
        'service_name': 'test.service.' + name,
        'method': method,
        'url_path': url_path,
        'http_accept': None,
        'match_slash': None,
        'is_active': True,
        'is_internal': False,
        'is_audit_log_active': False,
        'transport': 'plain_http',
        'data_format': 'json',
        'use_queue': False,
        'security': None,
    }
    out.update(options)

    return out

# ################################################################################################################################

def channel_definitions() -> 'anylist':
    """ Returns the definitions of the channels the router and the dispatcher are compared with.
    """
    deprecation = {
        'is_deprecated': True,
        'deprecation_since': '2026-01-01T00:00:00+00:00',
        'deprecation_sunset': '2027-01-01',
        'deprecation_successor': '/api/v2/deprecated',
    }

    out = [
        make_channel('customer.get', 'GET', '/api/customer/{customer_id}', match_slash=False),
        make_channel('customer.json', 'POST', '/api/customer/{customer_id}', http_accept='application/json'),
        make_channel('customer.any', '', '/api/any/{path}'),
        make_channel('order.list', 'GET', '/api/orders'),
        make_channel('order.list.slash', 'GET', '/api/orders/'),
        make_channel('order.item', 'DELETE', '/api/orders/{order_id}/items/{item_id}', match_slash=''),
        make_channel('ignored', 'GET', Ignored_Path),
        make_channel('basic', 'GET', '/api/basic', security='test.basic'),
        make_channel('apikey', 'GET', '/api/apikey', security='test.apikey'),
        make_channel('bearer', 'GET', '/api/bearer', security='test.bearer'),
        make_channel('bearer.field', 'GET', '/api/bearer-field', security='test.bearer.field'),
        make_channel('basic.inactive', 'GET', '/api/basic-inactive', security='test.basic.inactive'),
        make_channel('limited', 'GET', '/api/limited', rate_limiting=[_burst_rule]),
        make_channel('disallowed', 'GET', '/api/disallowed', rate_limiting=[_disallowed_rule]),
        make_channel('sec.limited', 'GET', '/api/sec-limited', security='test.basic.limited'),
        make_channel('sec.limited.self', 'GET', '/api/sec-limited-self', security='test.basic.limited',
            service_name=Self_Limited_Service),
        make_channel('deprecated', 'GET', '/api/deprecated', **deprecation),
        make_channel('inactive', 'GET', '/api/inactive', is_active=False),
        make_channel('zato.ping', 'GET', '/zato/ping', is_internal=True),
    ]

    return out

# ################################################################################################################################

def declined_channel_definitions() -> 'anylist':
    """ Returns the definitions of channels whose requests the router always hands to the dispatcher.
    """
    out = [
        make_channel('queued', 'POST', '/api/queued', use_queue=True),
        make_channel('cached', 'GET', '/api/cached', response_cache={'is_enabled': True}),
        make_channel('form', 'POST', '/api/form', data_format='form'),
        make_channel('hl7', 'POST', '/api/hl7', data_format='hl7-v2'),
        make_channel('soap', 'POST', '/api/soap', transport='soap'),
        make_channel('audited', 'GET', '/api/audited', is_audit_log_active=True),
        make_channel('grouped', 'GET', '/api/grouped', security_groups_ctx=Bunch(name='test.group')),
    ]

    return out

# ################################################################################################################################
# ################################################################################################################################

def _find_logger_call_line(function:'callable_', method_name:'str', first_argument:'str') -> 'int':
    """ Returns the line of the call to a method of the module logger in a function, optionally the one with
    the given name as its first argument.
    """
    source_lines, start_line = inspect.getsourcelines(function)
    source = textwrap.dedent(''.join(source_lines))
    tree = ast.parse(source)

    for node in ast.walk(tree):

        if not isinstance(node, ast.Call):
            continue

        if not isinstance(node.func, ast.Attribute):
            continue

        if node.func.attr != method_name:
            continue

        if first_argument:
            first = node.args[0]
            if not isinstance(first, ast.Name):
                continue
            if first.id != first_argument:
                continue

        out = start_line + node.lineno - 1
        break

    else:
        raise Exception(f'No call to {method_name} found in {function.__name__}')

    return out

# ################################################################################################################################

def build_log_sites() -> 'strdict':
    """ Returns the source locations of the dispatcher that the log records of the router are attributed to.
    """
    pathname = RequestDispatcher._dispatch.__code__.co_filename

    incoming_function = RequestDispatcher._log_incoming_request
    dispatch_function = RequestDispatcher._dispatch

    incoming_line = _find_logger_call_line(incoming_function, 'info', '')
    not_found_line = _find_logger_call_line(dispatch_function, 'warning', 'response_404_log')
    method_not_allowed_line = _find_logger_call_line(dispatch_function, 'warning', 'response_405_log')

    out = {
        'incoming': (pathname, incoming_line, incoming_function.__name__),
        'not_found': (pathname, not_found_line, dispatch_function.__name__),
        'method_not_allowed': (pathname, method_not_allowed_line, dispatch_function.__name__),
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

class Clock:
    """ The time both sides of a comparison read, advanced by the test between requests.
    """
    def __init__(self, now_us:'int') -> 'None':
        self.now_us = now_us

    def __call__(self) -> 'int':
        out = self.now_us
        return out

    def advance(self, microseconds:'int') -> 'None':
        self.now_us += microseconds

# ################################################################################################################################

class _SelfLimitedService:
    handles_rate_limit_rejection = True
    handles_auth_rejection = False

# ################################################################################################################################

class _ServiceStore:
    """ The deployed services, of which only the one answering its own rate limit rejections matters.
    """
    def __init__(self) -> 'None':
        self.name_to_impl_name = {}
        self.services = {Self_Limited_Service: {'service_class': _SelfLimitedService}}

# ################################################################################################################################

class _Server:
    """ The parts of a server that the dispatcher reads.
    """
    def __init__(self) -> 'None':
        self.name = Server_Name
        self.rest_log_ignore = {Ignored_Path}
        self.rate_limiting_manager = RateLimitingManager()
        self.service_store = _ServiceStore()
        self.fs_server_config = Bunch(misc=Bunch(return_tracebacks=False))

# ################################################################################################################################

class _ConfigManager:
    """ The parts of a configuration manager that the dispatcher reads.
    """
    def __init__(self) -> 'None':
        self.cache_api = None

# ################################################################################################################################
# ################################################################################################################################

class RouterWorld:
    """ One complete set of channels, security definitions, a dispatcher and a router built on them.
    """
    def __init__(self, definitions:'anylist', clock:'Clock') -> 'None':

        self.server = _Server()
        self.config_manager:'any_' = _ConfigManager()

        sec_defs = _security_definitions()
        methods_allowed_re = build_methods_allowed_re(Methods_Allowed)

        channel_data = []
        url_sec = {}

        for channel_id, definition in enumerate(definitions, 1):
            item = self._build_channel_item(channel_id, definition, methods_allowed_re)
            channel_data.append(item)

            security = definition['security']

            if security:
                sec_def = Bunch(copy.deepcopy(sec_defs[security]))
            else:
                sec_def = 'ZATO_NONE'

            url_sec[item['match_target']] = Bunch(sec_def=sec_def)

            if rate_limiting := definition.get('rate_limiting'):
                self.server.rate_limiting_manager.set_channel_config(channel_id, rate_limiting)

        limited_sec_def = sec_defs['test.basic.limited']
        self.server.rate_limiting_manager.set_sec_def_config(limited_sec_def['id'], [_burst_rule])

        channel_data.sort(key=_channel_sort_key)

        self.url_data = URLData(self.config_manager, channel_data=channel_data, url_sec=url_sec)

        self.dispatcher = RequestDispatcher(
            server=self.server,
            url_data=self.url_data,
            request_handler=_no_request_handler,
            return_tracebacks=False,
            default_error_message='Internal server error',
            http_methods_allowed=Methods_Allowed,
        )

        router_config = {
            'http_methods_allowed': Methods_Allowed,
            'logger': logging.getLogger('zato_rest'),
            'log_sites': build_log_sites(),
            'rest_log_ignore': self.server.rest_log_ignore,
            'escape_nonprintable': escape_nonprintable,
            'rate_limiting_manager': self.server.rate_limiting_manager,
            'dispatcher': self.dispatcher,
            'url_data': self.url_data,
            'current_cid': current_cid,
            'current_service_name': current_service_name,
            'current_time_us': clock,
            'get_deprecation_headers': get_deprecation_headers,
        }

        self.router = ChannelRouter(router_config)
        self.router.load(self.url_data.channel_data)

# ################################################################################################################################

    def _build_channel_item(self, channel_id:'int', definition:'anydict', methods_allowed_re:'str') -> 'Bunch':
        """ Builds a channel item from a definition, as the server builds it from its configuration.
        """
        item = Bunch(copy.deepcopy(definition))
        _ = item.pop('security')
        _ = item.pop('rate_limiting', None)

        item['id'] = channel_id
        item['match_target'] = get_match_target(item, http_methods_allowed_re=methods_allowed_re)

        match_slash = resolve_match_slash(item.get('match_slash'))
        item['match_target_compiled'] = Matcher(item['match_target'], match_slash)

        return item

# ################################################################################################################################
# ################################################################################################################################
