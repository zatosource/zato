# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from collections.abc import Mapping
from urllib.request import getproxies

# requests
from requests.cookies import get_cookie_header, merge_cookies, RequestsCookieJar
from requests.exceptions import RequestException
from requests import models as requests_models
from requests.models import PreparedRequest, RequestEncodingMixin
from requests.sessions import merge_setting
from requests.structures import CaseInsensitiveDict
from requests.utils import get_environ_proxies, prepend_scheme_if_needed, select_proxy

# urllib3
from urllib3.exceptions import LocationParseError
from urllib3.util.url import parse_url

# Zato
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from requests.sessions import Session as RequestsSession
    from zato.common.typing_ import any_, anytuple, bytesnone, stranydict, strnone
    RequestsSession = RequestsSession

# ################################################################################################################################
# ################################################################################################################################

# The Content-Type requests gives a body it encodes from the json argument
JSON_Content_Type = 'application/json'

# The Content-Type requests gives a body it encodes from a mapping or a sequence of pairs in the data argument
Form_Content_Type = 'application/x-www-form-urlencoded'

# The only scheme of a proxy the transport sends requests through
_proxy_scheme = 'http'

# The port urllib3 connects to for a proxy whose address has none
_default_proxy_port = 80

# The header requests sends the credentials of a proxy in
_proxy_authorization_header = 'Proxy-Authorization'

# The keyword argument of invoke_http the transport accepts, besides the ones invoke_http consumes itself
params_key = 'params'

# How requests encodes the params of a call as a query string and a form as a body
_encode_params = cast_('any_', RequestEncodingMixin)._encode_params

# The JSON module requests encodes the json argument with
_complexjson = cast_('any_', requests_models).complexjson

# ################################################################################################################################
# ################################################################################################################################

class CookieRequest:
    """ What the cookie jar of requests reads of a request - its address and its headers.
    """
    def __init__(self, url:'str', headers:'CaseInsensitiveDict[any_]') -> 'None':
        self.url = url
        self.headers = headers

# ################################################################################################################################
# ################################################################################################################################

def has_header(headers:'stranydict', name:'str') -> 'bool':
    """ Says whether a call gives a header, its name compared case-insensitively, with a value other than None,
    which requests treats as no header at all.
    """
    for key, value in headers.items():
        if value is not None:
            if key.lower() == name:
                return True

    return False

# ################################################################################################################################

def build_url(address:'str', params:'any_') -> 'str':
    """ Returns the address with the query string requests builds from params appended to it.
    """
    if not params:
        return address

    query = _encode_params(params)

    if not query:
        return address

    # A query string already in the address is extended rather than replaced
    if '?' in address:
        out = address + '&' + query
    else:
        out = address + '?' + query

    return out

# ################################################################################################################################

def prepare_url(url:'str') -> 'strnone':
    """ Returns the address as requests prepares it, or None for an address requests rejects, which it then reports itself.
    """
    request = PreparedRequest()

    try:
        request.prepare_url(url, None)
    except RequestException:
        return None

    out = cast_('str', request.url)
    return out

# ################################################################################################################################

def encode_json(value:'any_') -> 'bytesnone':
    """ Returns the body requests encodes from the json argument, or None for a value requests does not encode,
    which it then reports itself.
    """
    try:
        body = _complexjson.dumps(value)
    except (TypeError, ValueError):
        return None

    if isinstance(body, bytes):
        return body

    out = body.encode('utf-8')
    return out

# ################################################################################################################################

def encode_form(data:'any_') -> 'bytesnone':
    """ Returns the body requests encodes from a mapping or a sequence of pairs in the data argument, or None for data
    requests does not encode, which it then reports itself.
    """
    try:
        query = _encode_params(data)
    except (TypeError, ValueError):
        return None

    out = query.encode('latin-1')
    return out

# ################################################################################################################################

def get_body(data:'any_', json:'any_') -> 'anytuple | None':
    """ Returns the body requests sends for the data and json arguments with the Content-Type it gives the body,
    or None for a body the transport does not send.
    """
    content_type = None

    # A body given as data is sent as it is, text encoded as http.client encodes it, or as a form ..
    if data:

        if isinstance(data, bytes):
            body = data

        elif isinstance(data, str):
            try:
                body = data.encode('latin-1')
            except UnicodeEncodeError:
                return None

        # .. requests streams data of any other type ..
        elif isinstance(data, (Mapping, list, tuple)):
            body = encode_form(data)
            content_type = Form_Content_Type

        else:
            return None

    # .. it reads the json argument only when there is no data ..
    elif json is not None:
        body = encode_json(json)
        content_type = JSON_Content_Type

    # .. and without either of them, there is no body.
    else:
        return (None, None)

    if body is None:
        return None

    out = (body, content_type)
    return out

# ################################################################################################################################

def get_session_cookie(session:'RequestsSession', url:'str', headers:'stranydict') -> 'strnone':
    """ Returns the Cookie header requests builds from the cookie jar of the session for a request to a prepared address,
    or None if the jar has no cookie for it or the request has a Cookie header already.
    """
    merged_headers = merge_setting(headers, session.headers, dict_class=CaseInsensitiveDict)
    jar = merge_cookies(RequestsCookieJar(), session.cookies)

    request = CookieRequest(url, merged_headers)

    out = get_cookie_header(jar, request)
    return out

# ################################################################################################################################

def has_environ_proxies() -> 'bool':
    """ Says whether the environment of the process names any proxy.
    """
    out = bool(getproxies())
    return out

# ################################################################################################################################

def select_session_proxy(session:'RequestsSession', url:'str', has_env_proxies:'bool') -> 'strnone':
    """ Returns the proxy requests sends a request to a prepared address through, from the environment and the proxies
    of the session, or None if it sends the request directly.
    """
    proxies:'stranydict' = {}

    if session.trust_env and has_env_proxies:
        proxies.update(get_environ_proxies(url, no_proxy=None))

    proxies = merge_setting(proxies, session.proxies)

    out = select_proxy(url, proxies)
    return out

# ################################################################################################################################

def parse_proxy(session:'RequestsSession', url:'str', proxy:'str') -> 'anytuple | None':
    """ Returns the host, the port and the value of the Proxy-Authorization header of a proxy as the transport receives
    them, or None for a proxy the transport does not send requests through - a SOCKS or HTTPS proxy, one requests rejects,
    or one whose adapter adds headers other than the credentials.
    """
    try:
        proxy = prepend_scheme_if_needed(proxy, _proxy_scheme)
        proxy_url = parse_url(proxy)
    except LocationParseError:
        return None

    if proxy_url.scheme != _proxy_scheme:
        return None

    host = proxy_url.host
    if not host:
        return None

    # urllib3 connects to an IPv6 proxy by its address without brackets
    if host.startswith('[') and host.endswith(']'):
        host = host[1:-1]

    port = proxy_url.port
    if port is None:
        port = _default_proxy_port

    proxy_headers = dict(session.get_adapter(url).proxy_headers(proxy))
    authorization = proxy_headers.pop(_proxy_authorization_header, None)

    if proxy_headers:
        return None

    out = (host, port, authorization)
    return out

# ################################################################################################################################
# ################################################################################################################################
