# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The request contexts that the REST channel router and the request dispatcher are compared with, built the way
# the HTTP server builds them, and the strategies that generate them.

# stdlib
from base64 import b64encode
from typing import NamedTuple

# hypothesis
from hypothesis import strategies as st

# Zato
from router_environment import Credentials, Ignored_Path

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, strnone

# ################################################################################################################################
# ################################################################################################################################

class ChannelRequest(NamedTuple):
    method: 'str'
    path: 'str'
    query: 'str'
    accept: 'strnone'
    origin: 'strnone'
    authorization: 'strnone'
    api_key: 'strnone'
    body: 'bytes'
    user_agent: 'str'
    remote_addr: 'str'
    is_portal: 'bool'

# ################################################################################################################################

def basic_auth(username:'str', password:'str') -> 'str':
    """ Returns the Authorization header of HTTP Basic Auth credentials.
    """
    credentials = f'{username}:{password}'.encode('utf-8')
    encoded = b64encode(credentials).decode('ascii')

    out = f'Basic {encoded}'
    return out

# ################################################################################################################################

def make_request(method:'str', path:'str', **options:'any_') -> 'ChannelRequest':
    """ Returns a request with the options given replacing the defaults.
    """
    request = ChannelRequest(
        method=method,
        path=path,
        query='',
        accept=None,
        origin=None,
        authorization=None,
        api_key=None,
        body=b'',
        user_agent='curl/8.5.0',
        remote_addr='127.0.0.1',
        is_portal=False,
    )

    out = request._replace(**options)
    return out

# ################################################################################################################################

def build_request_ctx(request:'ChannelRequest') -> 'anydict':
    """ Returns the request context of a request, as the HTTP server builds it before dispatching it.
    """
    raw_uri = request.path

    if request.query:
        raw_uri = raw_uri + '?' + request.query

    out = {
        'REQUEST_METHOD': request.method,
        'PATH_INFO': request.path,
        'RAW_URI': raw_uri,
        'QUERY_STRING': request.query,
        'REMOTE_ADDR': request.remote_addr,
        'REMOTE_PORT': '50123',
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'HTTP_USER_AGENT': request.user_agent,
        'zato.http.raw_request': request.body,
        'zato.http.response.headers': {'X-Zato-CID': 'zcid-router-0001'},
        'zato.http.remote_addr': request.remote_addr,
    }

    if request.accept is not None:
        out['HTTP_ACCEPT'] = request.accept

    if request.origin is not None:
        out['HTTP_ORIGIN'] = request.origin

    if request.authorization is not None:
        out['HTTP_AUTHORIZATION'] = request.authorization

    if request.api_key is not None:
        out['HTTP_X_API_KEY'] = request.api_key

    if request.is_portal:
        out['zato.api_portal.caller'] = 'test.portal.caller'

    return out

# ################################################################################################################################
# ################################################################################################################################

_segment_text = st.text(alphabet='abcXYZ019_-.~%2F:@!$+,;=() ', min_size=0, max_size=8)

_paths = st.sampled_from([
    '/api/customer/123',
    '/api/customer/John Smith',
    '/api/customer/a/b',
    '/api/customer/',
    '/api/any/a/b/c',
    '/api/any/',
    '/api/orders',
    '/api/orders/',
    '/api/orders//',
    '/api/orders/./',
    '/api/./orders',
    '/api/x/../orders',
    '/api/%6Frders',
    '/api/orders/1/items/2',
    '/api/orders/1/items/a/b',
    Ignored_Path,
    '/api/basic',
    '/api/apikey',
    '/api/bearer',
    '/api/bearer-field',
    '/api/basic-inactive',
    '/api/limited',
    '/api/disallowed',
    '/api/sec-limited',
    '/api/sec-limited-self',
    '/api/deprecated',
    '/api/inactive',
    '/zato/ping',
    '/api/zato/ping',
    '/api/unknown',
    '/',
    '',
    '/api/customer/\udcff',
])

def _join_segments(segments:'list[str]') -> 'str':
    out = '/' + '/'.join(segments)
    return out

_generated_paths = st.lists(_segment_text, min_size=0, max_size=4).map(_join_segments)

_methods = st.sampled_from(['GET', 'GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD', 'TRACE', 'get'])

_accepts = st.sampled_from([None, '', '*/*', 'application/json', 'text/plain', 'application/*', 'text/\udcff'])

_origins = st.sampled_from([None, None, '', 'http://localhost:8080', 'https://zato.io', 'https://example.com', 'http://127.0.0.1',
    'http://localhost:\udcff'])

_authorizations = st.sampled_from([
    None,
    basic_auth(Credentials.Basic_Username, Credentials.Basic_Password),
    basic_auth(Credentials.Basic_Username, 'password.wrong'),
    basic_auth(Credentials.Limited_Username, Credentials.Limited_Password),
    basic_auth('', Credentials.Basic_Password),
    'Basic ' + 'am9obi5zbWl0aDpwYXNzd29yZC5iYXNpYw',
    'basic am9obi5zbWl0aDpwYXNzd29yZC5iYXNpYw==',
    'Basic !!!',
    'Bearer ' + Credentials.Static_Token,
    'bearer  ' + Credentials.Field_Token + ' ',
    'BEARER ' + Credentials.Field_Token,
    'Bearer token.wrong',
    'Bearer ',
    'Basic \udcff',
    'Bearer ' + Credentials.Static_Token + '\udcff',
])

_api_keys = st.sampled_from([None, Credentials.API_Key, 'key.wrong', '', Credentials.API_Key + '\udcff'])

_queries = st.sampled_from(['', 'customer_id=123', 'name=John%20Smith&x=\u0001'])

_user_agents = st.sampled_from(['curl/8.5.0', 'Agent\u0007', 'Agent \u017c', 'Agent\u009e', 'Agent\udcff'])

_remote_addrs = st.sampled_from(['127.0.0.1', '10.0.0.5'])

_bodies = st.sampled_from([b'', b'{"customer_id": 123, "name": "John Smith"}'])

requests = st.builds(
    ChannelRequest,
    method=_methods,
    path=st.one_of(_paths, _paths, _generated_paths),
    query=_queries,
    accept=_accepts,
    origin=_origins,
    authorization=_authorizations,
    api_key=_api_keys,
    body=_bodies,
    user_agent=_user_agents,
    remote_addr=_remote_addrs,
    is_portal=st.sampled_from([False, False, False, True]),
)

# ################################################################################################################################
# ################################################################################################################################
