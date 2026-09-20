# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import ssl
from base64 import b64encode
from http.client import OK
from http.cookiejar import CookieJar
from typing import NamedTuple
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import build_opener, HTTPCookieProcessor, HTTPSHandler, OpenerDirector, Request

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, bytesnone, strlist, strstrdict

# ################################################################################################################################
# ################################################################################################################################

bytes_list      = list[bytes]
file_field_list = list['FileField']
multipart_body  = tuple[bytes, str]

# ################################################################################################################################
# ################################################################################################################################

# How long a single request may take, in seconds
Default_Timeout = 30

# How much of a body that was not what was expected an error quotes - enough to say what it was,
# not a whole page of HTML on every attempt of a wait
Error_Body_Limit = 1500

# The boundary multipart bodies are built with
_multipart_boundary = 'zato-live-hl7-boundary'

# ################################################################################################################################
# ################################################################################################################################

class HTTPResult(NamedTuple):
    status: int
    headers: 'strstrdict'
    body: bytes

# ################################################################################################################################

class FileField(NamedTuple):
    field_name: str
    file_name: str
    content: bytes
    content_type: str

# ################################################################################################################################
# ################################################################################################################################

def basic_auth(username:'str', password:'str') -> 'str':
    """ The value of an Authorization header for HTTP Basic.
    """
    raw = f'{username}:{password}'.encode('utf8')
    encoded = b64encode(raw).decode('ascii')

    out = f'Basic {encoded}'
    return out

# ################################################################################################################################

def encode_form(fields:'strstrdict') -> 'bytes':
    """ A URL-encoded form body.
    """
    out = urlencode(fields).encode('utf8')
    return out

# ################################################################################################################################

def encode_multipart(fields:'strstrdict', files:'file_field_list') -> 'multipart_body':
    """ A multipart/form-data body and its Content-Type.
    """
    parts:'bytes_list' = []
    boundary = _multipart_boundary.encode('ascii')

    for name, value in fields.items():
        parts.append(b'--' + boundary)
        parts.append(f'Content-Disposition: form-data; name="{name}"'.encode('utf8'))
        parts.append(b'')
        parts.append(value.encode('utf8'))

    for file_field in files:
        disposition = f'Content-Disposition: form-data; name="{file_field.field_name}"; filename="{file_field.file_name}"'
        parts.append(b'--' + boundary)
        parts.append(disposition.encode('utf8'))
        parts.append(f'Content-Type: {file_field.content_type}'.encode('utf8'))
        parts.append(b'')
        parts.append(file_field.content)

    parts.append(b'--' + boundary + b'--')
    parts.append(b'')

    body = b'\r\n'.join(parts)
    content_type = f'multipart/form-data; boundary={_multipart_boundary}'

    out = (body, content_type)
    return out

# ################################################################################################################################

def _build_opener(verify_tls:'bool', cookies:'CookieJar | None') -> 'OpenerDirector':
    """ An opener with the TLS policy asked for and, when given, a cookie jar.
    """
    handlers:'anylist' = []

    if not verify_tls:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        handlers.append(HTTPSHandler(context=context))

    if cookies is not None:
        handlers.append(HTTPCookieProcessor(cookies))

    out = build_opener(*handlers)
    return out

# ################################################################################################################################

def _send(opener:'OpenerDirector', method:'str', url:'str', body:'bytesnone', headers:'strstrdict', timeout:'int') -> 'HTTPResult':
    """ Sends one request and returns whatever came back, an error status included.
    """
    request = Request(url, data=body, headers=headers, method=method)

    try:
        with opener.open(request, timeout=timeout) as response:
            response_headers = dict(response.headers.items())
            out = HTTPResult(response.status, response_headers, response.read())

    except HTTPError as e:
        response_headers = dict(e.headers.items())
        out = HTTPResult(e.code, response_headers, e.read())

    return out

# ################################################################################################################################

def request(
    method:'str',
    url:'str',
    *,
    body:'bytesnone' = None,
    headers:'strstrdict | None' = None,
    verify_tls:'bool' = True,
    timeout:'int' = Default_Timeout,
    ) -> 'HTTPResult':
    """ One request without a session - each call stands on its own.
    """
    if headers is None:
        headers = {}

    opener = _build_opener(verify_tls, None)

    out = _send(opener, method, url, body, headers, timeout)
    return out

# ################################################################################################################################

def request_json(
    method:'str',
    url:'str',
    payload:'any_',
    *,
    headers:'strstrdict | None' = None,
    verify_tls:'bool' = True,
    ) -> 'HTTPResult':
    """ One request carrying a JSON body.
    """
    if headers is None:
        headers = {}

    headers['Content-Type'] = 'application/json'
    headers['Accept'] = 'application/json'
    body = json.dumps(payload).encode('utf8')

    out = request(method, url, body=body, headers=headers, verify_tls=verify_tls)
    return out

# ################################################################################################################################

def parse_json(result:'HTTPResult') -> 'any_':
    """ The body of a result as JSON, failing with the status and body when it is not JSON.
    """
    try:
        out = json.loads(result.body)
    except json.JSONDecodeError:
        body = result.body.decode('utf8', 'replace')[:Error_Body_Limit]
        raise Exception(f'Not a JSON response, status {result.status}, body: {body}')

    return out

# ################################################################################################################################

def is_http_ok(url:'str', *, verify_tls:'bool'=True, headers:'strstrdict | None'=None) -> 'bool':
    """ True when the URL answers with 200 - a refused connection or any other error is False.
    """
    try:
        result = request('GET', url, headers=headers, verify_tls=verify_tls)
    except (URLError, OSError):
        return False

    out = result.status == OK
    return out

# ################################################################################################################################

def is_status(url:'str', expected:'int', *, verify_tls:'bool'=True, headers:'strstrdict | None'=None) -> 'bool':
    """ True when the URL answers with exactly the expected status.
    """
    try:
        result = request('GET', url, headers=headers, verify_tls=verify_tls)
    except (URLError, OSError):
        return False

    out = result.status == expected
    return out

# ################################################################################################################################
# ################################################################################################################################

class Session:
    """ Requests sharing one cookie jar and one set of default headers - what a browser holds after logging in.
    """

    def __init__(self, base_url:'str', *, verify_tls:'bool'=True) -> 'None':
        self.base_url = base_url.rstrip('/')
        self.verify_tls = verify_tls
        self.cookies = CookieJar()
        self.headers:'strstrdict' = {}
        self.opener = _build_opener(verify_tls, self.cookies)

# ################################################################################################################################

    def url(self, path:'str') -> 'str':
        if path.startswith('http'):
            out = path
        else:
            out = self.base_url + path

        return out

# ################################################################################################################################

    def request(
        self,
        method:'str',
        path:'str',
        *,
        body:'bytesnone' = None,
        headers:'strstrdict | None' = None,
        timeout:'int' = Default_Timeout,
        ) -> 'HTTPResult':

        merged = dict(self.headers)
        if headers:
            merged.update(headers)

        url = self.url(path)

        out = _send(self.opener, method, url, body, merged, timeout)
        return out

# ################################################################################################################################

    def get(self, path:'str', *, headers:'strstrdict | None'=None) -> 'HTTPResult':
        out = self.request('GET', path, headers=headers)
        return out

# ################################################################################################################################

    def post_form(self, path:'str', fields:'strstrdict', *, headers:'strstrdict | None'=None) -> 'HTTPResult':
        body = encode_form(fields)

        merged:'strstrdict' = {'Content-Type': 'application/x-www-form-urlencoded'}
        if headers:
            merged.update(headers)

        out = self.request('POST', path, body=body, headers=merged)
        return out

# ################################################################################################################################

    def post_multipart(self, path:'str', fields:'strstrdict', files:'file_field_list') -> 'HTTPResult':
        body, content_type = encode_multipart(fields, files)
        headers:'strstrdict' = {'Content-Type': content_type}

        out = self.request('POST', path, body=body, headers=headers)
        return out

# ################################################################################################################################

    def request_json(self, method:'str', path:'str', payload:'any_', *, headers:'strstrdict | None'=None) -> 'HTTPResult':
        body = json.dumps(payload).encode('utf8')

        merged:'strstrdict' = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        if headers:
            merged.update(headers)

        out = self.request(method, path, body=body, headers=merged)
        return out

# ################################################################################################################################

    def post_json(self, path:'str', payload:'any_', *, headers:'strstrdict | None'=None) -> 'HTTPResult':
        out = self.request_json('POST', path, payload, headers=headers)
        return out

# ################################################################################################################################

    def put_json(self, path:'str', payload:'any_', *, headers:'strstrdict | None'=None) -> 'HTTPResult':
        out = self.request_json('PUT', path, payload, headers=headers)
        return out

# ################################################################################################################################

    def get_json(self, path:'str', *, headers:'strstrdict | None'=None) -> 'any_':
        result = self.get(path, headers=headers)

        out = parse_json(result)
        return out

# ################################################################################################################################
# ################################################################################################################################

def expect_status(result:'HTTPResult', expected:'int | tuple[int, ...]', what:'str') -> 'None':
    """ Fails with the body when a result does not carry the status expected, or one of the statuses when several
    are acceptable.
    """
    if isinstance(expected, int):
        expected = (expected,)

    if result.status not in expected:
        body = result.body.decode('utf8', 'replace')[:Error_Body_Limit]
        accepted = ' or '.join(str(status) for status in expected)
        raise Exception(f'{what} answered {result.status} instead of {accepted}: {body}')

# ################################################################################################################################

def extract_hidden_field(html:'str', name:'str') -> 'str':
    """ The value of a hidden input in a form, failing when the form has no such input.
    """
    marker = f'name="{name}"'
    single_quoted = f"name='{name}'"

    position = html.find(marker)
    if position < 0:
        position = html.find(single_quoted)

    if position < 0:
        raise Exception(f'No input named {name} in the page')

    # The value may come before or after the name within the same tag
    tag_start = html.rfind('<input', 0, position)
    tag_end = html.find('>', position)
    tag = html[tag_start:tag_end]

    out = _attribute_value(tag, 'value')
    return out

# ################################################################################################################################

def _attribute_value(tag:'str', attribute:'str') -> 'str':
    """ The value of one attribute inside one HTML tag, either quoting style.
    """
    for quote in ('"', "'"):
        marker = f'{attribute}={quote}'
        start = tag.find(marker)

        if start >= 0:
            value_start = start + len(marker)
            value_end = tag.find(quote, value_start)
            out = tag[value_start:value_end]
            break
    else:
        raise Exception(f'No attribute {attribute} in tag {tag}')

    return out

# ################################################################################################################################

def lines_of(result:'HTTPResult') -> 'strlist':
    """ The body of a result as text lines.
    """
    text = result.body.decode('utf8', 'replace')

    out = text.splitlines()
    return out

# ################################################################################################################################

def as_dict(result:'HTTPResult') -> 'anydict':
    """ The body of a result as a JSON object.
    """
    out = parse_json(result)
    return out

# ################################################################################################################################
# ################################################################################################################################
