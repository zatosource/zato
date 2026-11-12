# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from datetime import timedelta
from http.client import HTTPMessage
from logging import INFO
from typing import NamedTuple

# requests
from requests.auth import _basic_auth_str
from requests.cookies import MockRequest, MockResponse, RequestsCookieJar
from requests.exceptions import ContentDecodingError
from requests.models import Request, RequestEncodingMixin
from requests.structures import CaseInsensitiveDict
from requests.utils import DEFAULT_CA_BUNDLE_PATH, get_encoding_from_headers, get_environ_proxies, get_netrc_auth

# urllib3
from urllib3.exceptions import DecodeError
from urllib3.response import HTTPResponse, _get_decoder

# Zato
from zato.common.api import NotGiven, URL_TYPE
from zato.common.typing_ import cast_
from zato.server.connection.http_soap.outgoing.common import logger, Response

# Rust core
from zato_server_core.zato_server_core import log_rest_line

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from requests.sessions import Session as RequestsSession
    from zato.common.typing_ import any_, anytuple, bytesnone, stranydict, strnone
    from zato_server_core.zato_server_core import HTTPTransport
    HTTPTransport = HTTPTransport
    RequestsSession = RequestsSession

# ################################################################################################################################
# ################################################################################################################################

# The environment variable that selects the transport of every outgoing REST invocation in the process
Transport_Env_Key = 'Zato_Outgoing_Transport'

# The value of the environment variable that sends every invocation through requests
Transport_Requests = 'requests'

# The environment variables requests reads its CA bundle from, in the order it reads them
_ca_bundle_env_keys = ('REQUESTS_CA_BUNDLE', 'CURL_CA_BUNDLE')

# The keyword argument of invoke_http the transport accepts, besides the ones invoke_http consumes itself
_params_key = 'params'

# The methods requests sends without a Content-Length header when they have no body
_methods_without_length = ('GET', 'HEAD')

# The response header that sets a cookie, as the cookie jar reads it
_set_cookie_header = 'Set-Cookie'

# How urllib3 reports a body it could not decode
_decode_error_message = 'Received response with content-encoding: {}, but failed to decode it.'

# How requests encodes the params of a call as a query string
_encode_params = cast_('any_', RequestEncodingMixin)._encode_params

# ################################################################################################################################
# ################################################################################################################################

def is_requests_selected() -> 'bool':
    """ Says whether the environment of the process selects requests for every outgoing REST invocation.
    """
    out = os.environ.get(Transport_Env_Key) == Transport_Requests
    return out

# ################################################################################################################################

def log_rest(message:'str') -> 'None':
    """ Writes a line of an outgoing REST invocation to the REST log of the server, or through the zato_rest logger
    in a process where the REST log is not initialized.
    """
    if logger.isEnabledFor(INFO):
        if not log_rest_line(message):
            logger.info(message)

# ################################################################################################################################

def get_basic_authorization(auth:'anytuple') -> 'strnone':
    """ Returns the Authorization header requests sends for a username and password, or None for credentials
    that requests encodes only when it sends a request, which it then reports itself.
    """
    username, password = auth

    try:
        out = _basic_auth_str(username, password)
    except UnicodeEncodeError:
        out = None

    return out

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

def get_ca_path(tls_verify:'any_', trust_env:'bool') -> 'any_':
    """ Returns what requests verifies TLS against with a given verify argument - None when it verifies nothing,
    otherwise the CA bundle from the environment or the certifi bundle for True, or the argument itself.
    """
    if tls_verify is False:
        return None

    if tls_verify is not True:
        return tls_verify

    if trust_env:
        for name in _ca_bundle_env_keys:
            if value := os.environ.get(name):
                return value

    return DEFAULT_CA_BUNDLE_PATH

# ################################################################################################################################

def is_ca_path_supported(ca_path:'any_') -> 'bool':
    """ Says whether the transport verifies TLS against what get_ca_path returned, which it does for no verification
    and for a path that is not a directory of certificates.
    """
    if ca_path is None:
        return True

    if not isinstance(ca_path, str):
        return False

    out = not os.path.isdir(ca_path)
    return out

# ################################################################################################################################

def get_client_cert(tls_client_cert:'any_') -> 'anytuple':
    """ Returns the client certificate and its key from the cert argument of requests, each of them None if absent.
    """
    if tls_client_cert is None:
        out = (None, None)

    elif isinstance(tls_client_cert, tuple):
        tls_client_cert = cast_('anytuple', tls_client_cert)
        out = (tls_client_cert[0], tls_client_cert[1])

    else:
        out = (tls_client_cert, None)

    return out

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

def decode_content(content_encoding:'str', body:'bytes') -> 'bytes':
    """ Decodes a body sent with a Content-Encoding header the way urllib3 decodes it for requests.
    """
    content_encoding = content_encoding.lower()

    # An encoding urllib3 does not decode leaves the body as it is ..
    if content_encoding not in HTTPResponse.CONTENT_DECODERS:

        if ',' not in content_encoding:
            return body

        is_known = False

        for name in content_encoding.split(','):
            if name.strip() in HTTPResponse.CONTENT_DECODERS:
                is_known = True
                break

        if not is_known:
            return body

    # .. while one it decodes is decoded and flushed, as urllib3 does after the last part of a body.
    decoder = _get_decoder(content_encoding)

    try:
        out = decoder.decompress(body)
    except HTTPResponse.DECODER_ERROR_CLASSES as e:
        message = _decode_error_message.format(content_encoding)
        raise ContentDecodingError(DecodeError(message, e))

    out += decoder.decompress(b'')
    out += decoder.flush()

    return out

# ################################################################################################################################

def extract_cookies(jar:'RequestsCookieJar', url:'str', headers:'stranydict', set_cookie_list:'anytuple') -> 'None':
    """ Stores the cookies of a response in a jar, the way requests extracts them from a response it received.
    """
    message = HTTPMessage()

    # Each header is added rather than replaced, so a response that sets several cookies keeps all of them
    for value in set_cookie_list:
        message[_set_cookie_header] = value

    request = _CookieRequest(url, CaseInsensitiveDict(headers))

    cookie_response = cast_('any_', MockResponse(message))
    cookie_request = cast_('any_', MockRequest(cast_('any_', request)))

    jar.extract_cookies(cookie_response, cookie_request)

# ################################################################################################################################
# ################################################################################################################################

class _CookieRequest:
    """ What the cookie jar of requests reads of the request a response with cookies was received for.
    """
    def __init__(self, url:'str', headers:'CaseInsensitiveDict[any_]') -> 'None':
        self.url = url
        self.headers = headers

# ################################################################################################################################
# ################################################################################################################################

class TransportCall(NamedTuple):
    """ What the Rust transport sends for one invocation.
    """
    method: 'str'
    url: 'str'
    headers: 'stranydict'
    body: 'bytesnone'
    is_authorized: 'bool'

# ################################################################################################################################
# ################################################################################################################################

class TransportResponse(Response):
    """ A response received through the Rust transport, with the attributes and the methods of a response
    received through requests. The encoding, the cookies and the request are computed when first read,
    and the text is computed once for each body and encoding.
    """

    # The cookies the response set, as received
    _set_cookie_list:'anytuple' = ()

    # The session and the call the request is built from when it is read
    _session:'RequestsSession | None' = None
    _call:'TransportCall | None' = None
    _auth:'any_' = None

    # The text computed most recently, with the body and the encoding it was computed from
    _text:'str' = ''
    _text_content:'bytesnone' = None
    _text_encoding:'strnone' = None

    # What requests sets on each response it builds, given here so an instance built without its __init__ has it
    connection:'any_' = None

    # What requests.Response keeps about its body, assigned when the response is built
    _content_consumed:'bool'

    def __getattr__(self, name:'str') -> 'any_':

        # The encoding comes from the headers, as requests computes it ..
        if name == 'encoding':
            out = get_encoding_from_headers(self.headers)

        # .. the cookies come from the Set-Cookie headers ..
        elif name == 'cookies':
            out = self._build_cookies()

        # .. the request is prepared by the session, as requests prepares it ..
        elif name == 'request':
            out = self._build_request()

        # .. as is the request a redirect points to, which a redirect that is not followed still names ..
        elif name == '_next':
            out = self._build_next()

        # .. and anything else is not an attribute of a response.
        else:
            raise AttributeError(name)

        # The value is stored, so it is computed once, and anything assigned to it later replaces it
        self.__dict__[name] = out

        return out

# ################################################################################################################################

    @property
    def text(self) -> 'str':

        content = self.content
        encoding = self.encoding

        # The text is computed again only if the body or the encoding changed since it was computed ..
        is_current = self._text_content is content

        if is_current:
            is_current = self._text_encoding == encoding

        # .. in which case requests computes it.
        if not is_current:
            self._text = super().text
            self._text_content = content
            self._text_encoding = encoding

        return self._text

# ################################################################################################################################

    def _build_cookies(self) -> 'RequestsCookieJar':

        out = RequestsCookieJar()

        if self._set_cookie_list:
            call = cast_('TransportCall', self._call)
            extract_cookies(out, call.url, call.headers, self._set_cookie_list)

        return out

# ################################################################################################################################

    def _build_request(self) -> 'any_':

        # A response restored from a pickle carries its request, so only a response received has to build one
        session = cast_('RequestsSession', self._session)
        call = cast_('TransportCall', self._call)

        request = Request(call.method, call.url, headers=call.headers, data=call.body, auth=self._auth)

        out = session.prepare_request(request)
        return out

# ################################################################################################################################

    def _build_next(self) -> 'any_':

        # Only a redirect received, and not one restored from a pickle, names a request to follow
        if self._session is None:
            return None

        if not self.is_redirect:
            return None

        redirects = self._session.resolve_redirects(self, self.request, yield_requests=True)

        out = next(redirects, None)
        return out

# ################################################################################################################################
# ################################################################################################################################

def build_response(
    result:'anytuple',
    session:'RequestsSession',
    call:'TransportCall',
    auth:'any_',
) -> 'TransportResponse':
    """ Builds a response from what the Rust transport returned and stores its cookies in the session.
    """
    status_code, reason, header_store, body, elapsed_us, set_cookie_list = result

    # The headers arrive in the form a CaseInsensitiveDict keeps them in, so none is copied
    headers = cast_('any_', CaseInsensitiveDict.__new__(CaseInsensitiveDict))
    headers._store = header_store

    # A body with a Content-Encoding header is decoded at once, as requests decodes it while reading it
    if content_encoding := header_store.get('content-encoding'):
        body = decode_content(content_encoding[1], body)

    out = TransportResponse.__new__(TransportResponse)

    out.status_code = status_code
    out.reason = reason
    out.headers = headers
    out.url = call.url
    out.elapsed = timedelta(microseconds=elapsed_us)
    out.history = []
    out.raw = None

    out._content = body
    out._content_consumed = True

    out._session = session
    out._call = call
    out._auth = auth

    # The session keeps the cookies of each response, as requests keeps them
    if set_cookie_list:
        out._set_cookie_list = set_cookie_list
        extract_cookies(session.cookies, call.url, call.headers, set_cookie_list)

    return out

# ################################################################################################################################
# ################################################################################################################################

class TransportMixin:
    """ How an outgoing connection decides which invocations the Rust transport sends and sends them.
    """

    config: 'stranydict'
    session: 'RequestsSession'
    transport: 'HTTPTransport'
    requests_auth: 'any_'

    def _configure_transport(self) -> 'None':
        """ Records the state of the requests session the transport was configured for and what of the configuration
        of the connection and of the environment decides that no invocation is sent through the transport.
        """
        session = self.session

        self._transport_session = session
        self._transport_adapters = tuple(session.adapters.values())

        # What was last passed to the transport, so each setting is passed again only when it changes
        self._transport_timeout:'any_' = NotGiven
        self._transport_headers:'any_' = None
        self._transport_headers_accepted = False
        self._transport_tls:'any_' = None
        self._transport_tls_supported = False

        self.can_use_transport = self._can_use_transport()

# ################################################################################################################################

    def _can_use_transport(self) -> 'bool':
        """ Says whether any invocation of the connection may be sent through the transport.
        """
        # The environment may select requests for the whole process ..
        if is_requests_selected():
            return False

        # .. SOAP invocations are sent through requests ..
        if self.config['transport'] == URL_TYPE.SOAP:
            return False

        # .. and so are invocations requests would send through a proxy or with credentials from a netrc file.
        address_host = self.config['address_host']

        if get_environ_proxies(address_host):
            return False

        if get_netrc_auth(address_host):
            return False

        return True

# ################################################################################################################################

    def _session_needs_requests(self, headers:'stranydict') -> 'bool':
        """ Says whether the state of the requests session changes what requests would send, in a way the transport
        does not reproduce.
        """
        session = self.session

        # A session replaced or reconfigured with settings of its own is used as it is ..
        if session is not self._transport_session:
            return True

        if session.auth is not None:
            return True

        if session.cert is not None:
            return True

        if session.params:
            return True

        if session.proxies:
            return True

        if session.stream:
            return True

        if session.hooks['response']:
            return True

        if tuple(session.adapters.values()) != self._transport_adapters:
            return True

        # .. the default headers of the session are sent by the transport too, once it accepts them ..
        if type(session.headers) is not CaseInsensitiveDict:
            return True

        default_headers = cast_('any_', session.headers)

        if default_headers._store != self._transport_headers:
            self._transport_headers = default_headers._store.copy()
            self._transport_headers_accepted = self.transport.set_default_headers(dict(session.headers))

        if not self._transport_headers_accepted:
            return True

        # .. and the cookies of the session are sent by requests, unless the call gives a Cookie header of its own.
        if session.cookies:
            if not has_header(headers, 'cookie'):
                return True

        return False

# ################################################################################################################################

    def _get_transport_call(
        self,
        method:'str',
        address:'str',
        data:'any_',
        json:'any_',
        headers:'stranydict',
        auth:'any_',
        hooks:'any_',
        allow_redirects:'any_',
        args:'anytuple',
        kwargs:'stranydict',
    ) -> 'TransportCall | None':
        """ Returns what the transport sends for an invocation, or None if requests is to send it.
        """
        if not self.can_use_transport:
            return None

        # Arguments the transport does not implement leave the invocation to requests ..
        if json is not None:
            return None

        if hooks:
            return None

        if args:
            return None

        if allow_redirects:
            return None

        for name in kwargs:
            if name != _params_key:
                return None

        # .. as do credentials other than Basic Auth ..
        if auth is None:
            is_authorized = False
        elif isinstance(auth, tuple):
            is_authorized = True
        else:
            return None

        # .. and bodies other than bytes and text that Latin-1 encodes, which is how http.client encodes text ..
        if not data:
            body = None

        elif isinstance(data, bytes):
            body = data

        elif isinstance(data, str):
            try:
                body = data.encode('latin-1')
            except UnicodeEncodeError:
                return None

        else:
            return None

        if self._session_needs_requests(headers):
            return None

        # .. whereas a query string is appended to the address the way requests appends it.
        url = build_url(address, kwargs.get(_params_key))

        out = TransportCall(method, url, headers, body, is_authorized)
        return out

# ################################################################################################################################

    def _invoke_with_transport(
        self,
        call:'TransportCall',
        tls_verify:'any_',
        tls_client_cert:'any_',
        timeout:'any_',
    ) -> 'TransportResponse | None':
        """ Sends an invocation through the transport, returning None if requests is to send it after all.
        """
        transport = self.transport

        # The timeout is passed on only when it changes ..
        if timeout != self._transport_timeout:
            transport.set_timeout(timeout)
            self._transport_timeout = timeout

        # .. and so are the TLS settings, which TLS requests only need.
        if call.url.startswith('https:'):
            ca_path = get_ca_path(tls_verify, self.session.trust_env)
            client_cert, client_key = get_client_cert(tls_client_cert)

            tls = (ca_path, client_cert, client_key)

            if tls != self._transport_tls:
                self._transport_tls = tls
                self._transport_tls_supported = is_ca_path_supported(ca_path)

                if self._transport_tls_supported:
                    transport.set_tls(ca_path, client_cert, client_key)

            if not self._transport_tls_supported:
                return None

        if call.is_authorized:
            auth = self.requests_auth
            result = transport.invoke_with_auth(call.method, call.url, call.headers, call.body)
        else:
            auth = None
            result = transport.invoke(call.method, call.url, call.headers, call.body)

        if result is None:
            return None

        out = build_response(result, self.session, call, auth)
        return out

# ################################################################################################################################
# ################################################################################################################################
