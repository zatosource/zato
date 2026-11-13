# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The building blocks of the REST channel router return what their Python counterparts return for the same input.

# stdlib
import base64
import json
from datetime import date, datetime, timezone
from decimal import Decimal

# hypothesis
from hypothesis import given, settings, strategies as st

# Zato
from zato.common.bearer_token_verifier import extract_bearer_token
from zato.common.json_ import _default_handler, dumps
from zato.common.util.auth import extract_basic_auth
from zato.common.util.url_dispatcher import build_methods_allowed_re, get_match_target, normalize_path_info, \
    to_internal_accept
from zato.server.connection.http_soap.cors import is_allowed_origin
from zato_server_core.zato_server_core import ChannelRouter

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, callable_

# ################################################################################################################################
# ################################################################################################################################

_examples = settings(max_examples=1000, deadline=None)

_path_alphabet = 'abcXYZ019/._-~%2Ff:@!$&+,;=() \u017c\u00e9'

_paths = st.text(alphabet=_path_alphabet, max_size=24)

_percent_paths = st.lists(
    st.one_of(
        st.sampled_from(['/', '.', '..', '%', '%2F', '%2f', '%c5%bc', '%C5', '%zz', '%e2%82', 'a', '\u017c']),
        st.text(alphabet=_path_alphabet, max_size=3),
    ),
    max_size=10,
).map(''.join)

_any_text = st.text(st.characters(exclude_categories=()), max_size=24)

# The text of a request header, which the HTTP server never builds with lone surrogates
_header_text = st.text(st.characters(exclude_categories=('Cs',)), max_size=24)

_methods_allowed = st.lists(st.sampled_from(['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD']),
    min_size=1, max_size=7, unique=True)

# ################################################################################################################################
# ################################################################################################################################

def _outcome(function:'callable_', *args:'any_') -> 'any_':
    """ Returns what a function returned, or the type and text of the exception it raised.
    """
    try:
        value = function(*args)
    except Exception as e:
        out = ('exception', type(e), str(e))
    else:
        out = ('value', repr(value))

    return out

# ################################################################################################################################
# ################################################################################################################################

@_examples
@given(st.one_of(_paths, _percent_paths))
def test_normalize_path_info(path_info:'str') -> 'None':
    assert ChannelRouter.normalize_path_info(path_info) == normalize_path_info(path_info)

# ################################################################################################################################

@_examples
@given(st.one_of(st.none(), st.sampled_from(['', '*/*', 'application/json', 'text/*', '*']), _header_text))
def test_to_internal_accept(http_accept:'str | None') -> 'None':
    assert ChannelRouter.to_internal_accept(http_accept) == to_internal_accept(http_accept)

# ################################################################################################################################

@_examples
@given(
    st.sampled_from(['', 'GET', 'POST', 'DELETE']),
    st.one_of(st.none(), st.sampled_from(['', '*/*', 'application/json', 'application/vnd.api+json', 'text/(x)'])),
    st.text(alphabet='/abc{}_-.+*?()[]^$|\\: ', max_size=24),
    _methods_allowed,
)
def test_get_match_target(method:'str', http_accept:'str | None', url_path:'str', methods_allowed:'list[str]') -> 'None':
    config = {'method': method, 'http_accept': http_accept, 'url_path': url_path}
    expected = get_match_target(config, http_methods_allowed_re=build_methods_allowed_re(methods_allowed))

    assert ChannelRouter.get_match_target(method, http_accept, url_path, methods_allowed) == expected

# ################################################################################################################################
# ################################################################################################################################

_json_scalars = st.one_of(
    st.none(),
    st.booleans(),
    st.integers(),
    st.integers(min_value=-10**40, max_value=10**40),
    st.floats(allow_nan=True, allow_infinity=True),
    _any_text,
)

def _json_containers(children:'any_') -> 'any_':
    out = st.one_of(
        st.lists(children, max_size=4),
        st.dictionaries(_any_text, children, max_size=4),
    )
    return out

_json_values = st.recursive(_json_scalars, _json_containers, max_leaves=24)

_json_documents = st.builds(
    json.dumps,
    _json_values,
    ensure_ascii=st.booleans(),
    indent=st.sampled_from([None, 0, 2, '\t']),
    separators=st.sampled_from([None, (',', ':'), (' , ', ' : ')]),
)

_json_fragments = st.lists(
    st.sampled_from([
        '{', '}', '[', ']', ',', ':', ' ', '\n', '"', '\\', '\\u', '\\ud800', '\\udc00', '\\n', 'true', 'false', 'null',
        'NaN', 'Infinity', '-Infinity', '-', '0', '01', '1.', '.5', '1e', '1E+2', '1e-400', '1e400', '123456789012345678901',
        'a', '\u017c', '\x00', '\x1f', '\ufeff',
    ]),
    max_size=16,
).map(''.join)

_encodings = st.sampled_from(['utf-8', 'utf-8-sig', 'utf-16', 'utf-16-le', 'utf-32'])

# ################################################################################################################################

def _encode(text:'str', encoding:'str') -> 'bytes':
    out = text.encode(encoding, 'surrogatepass')
    return out

# ################################################################################################################################

@_examples
@given(st.one_of(
    st.builds(_encode, _json_documents, st.just('utf-8')),
    st.builds(_encode, _json_documents, _encodings),
    st.builds(_encode, _json_fragments, st.just('utf-8')),
    st.binary(max_size=24),
))
def test_parse_json(payload:'bytes') -> 'None':
    assert _outcome(ChannelRouter.parse_json, payload) == _outcome(json.loads, payload)

# ################################################################################################################################

def test_parse_json_depth() -> 'None':
    for depth in [199, 200, 201, 2000]:
        payload = ('[' * depth + ']' * depth).encode('utf-8')
        assert _outcome(ChannelRouter.parse_json, payload) == _outcome(json.loads, payload)

# ################################################################################################################################
# ################################################################################################################################

class _Customer:
    """ An object with a dict form, as the models that responses are built from have.
    """
    def __init__(self, name:'str') -> 'None':
        self.name = name

    def to_dict(self) -> 'dict[str, str]':
        out = {'name': self.name}
        return out

# ################################################################################################################################

_dump_scalars = st.one_of(
    _json_scalars,
    st.dates(),
    st.datetimes(),
    st.datetimes(timezones=st.just(timezone.utc)),
    st.decimals(allow_nan=False),
    st.binary(max_size=6),
    st.builds(_Customer, st.sampled_from(['John Smith', 'Maria Garcia'])),
    st.sampled_from([date(2026, 11, 13), datetime(2026, 11, 13, 12, 0), Decimal('12.50'), {1, 2}, object]),
)

_dump_keys = st.one_of(_any_text, st.integers(), st.floats(), st.booleans(), st.none(), st.just((1, 2)))

def _dump_containers(children:'any_') -> 'any_':
    out = st.one_of(
        st.lists(children, max_size=4),
        st.lists(children, max_size=4).map(tuple),
        st.dictionaries(_dump_keys, children, max_size=4),
    )
    return out

_dump_values = st.recursive(_dump_scalars, _dump_containers, max_leaves=24)

# ################################################################################################################################

def _dump_with_router(value:'any_') -> 'str':
    out = ChannelRouter.dump_json(value, _default_handler)
    return out

# ################################################################################################################################

@_examples
@given(_dump_values)
def test_dump_json(value:'any_') -> 'None':
    assert _outcome(_dump_with_router, value) == _outcome(dumps, value)

# ################################################################################################################################

def test_dump_json_circular() -> 'None':
    value = []
    value.append(value)

    assert _outcome(_dump_with_router, value) == _outcome(dumps, value)

# ################################################################################################################################
# ################################################################################################################################

_base64_alphabet = 'ABCabc0189+/=  \n-_!\u017c'

_base64_texts = st.one_of(
    st.text(alphabet=_base64_alphabet, max_size=16),
    st.binary(max_size=16).map(base64.b64encode).map(bytes.decode),
)

# ################################################################################################################################

def _decode_with_python(text:'str') -> 'bytes | None':
    try:
        out = base64.b64decode(text)
    except ValueError:
        out = None
    return out

# ################################################################################################################################

@_examples
@given(_base64_texts)
def test_decode_base64(text:'str') -> 'None':
    assert ChannelRouter.decode_base64(text) == _decode_with_python(text)

# ################################################################################################################################

_credentials = st.text(st.characters(exclude_categories=('Cs',)), max_size=8)

def _basic_header(username:'str', password:'str', prefix:'str', padding:'str') -> 'str':
    encoded = base64.b64encode(f'{username}:{password}'.encode('utf-8')).decode('ascii')
    out = f'{prefix}{padding}{encoded}{padding}'
    return out

_basic_headers = st.one_of(
    st.builds(
        _basic_header,
        _credentials,
        _credentials,
        st.sampled_from(['Basic ', 'basic ', 'Basic', 'Bearer ']),
        st.sampled_from(['', ' ', '\t', '\u3000', '\x1c']),
    ),
    st.builds(str.__add__, st.just('Basic '), _base64_texts),
    _header_text,
)

# ################################################################################################################################

def _extract_with_python(header:'str') -> 'tuple[str, str] | None':
    result = extract_basic_auth('zcid-router-0001', header)

    if result[0] is None:
        out = None
    else:
        out = result

    return out

# ################################################################################################################################

@_examples
@given(_basic_headers)
def test_extract_basic_auth(header:'str') -> 'None':
    assert ChannelRouter.extract_basic_auth(header) == _extract_with_python(header)

# ################################################################################################################################

_bearer_headers = st.one_of(
    st.builds(
        str.__add__,
        st.sampled_from(['Bearer ', 'bearer ', 'BEARER ', 'BeArEr ', 'Bearer', 'Basic ', 'Bearer\t', '\u0130earer ']),
        st.text(alphabet='abc.019 \t\u3000\x1c-_', max_size=12),
    ),
    _header_text,
)

@_examples
@given(_bearer_headers)
def test_extract_bearer_token(header:'str') -> 'None':
    assert ChannelRouter.extract_bearer_token(header) == extract_bearer_token(header)

# ################################################################################################################################

_origins = st.one_of(
    st.sampled_from([
        '', 'https://zato.io', 'https://zato.io/', 'http://localhost', 'http://localhost:8080', 'http://localhost.evil',
        'http://127.0.0.1', 'http://127.0.0.1:17010', 'https://localhost:443', 'https://example.com',
    ]),
    _header_text,
)

@_examples
@given(_origins)
def test_is_allowed_origin(origin:'str') -> 'None':
    assert ChannelRouter.is_allowed_origin(origin) == is_allowed_origin(origin)

# ################################################################################################################################
# ################################################################################################################################
