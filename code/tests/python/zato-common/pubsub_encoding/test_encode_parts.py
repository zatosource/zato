# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import loads

# hypothesis
from hypothesis import given, settings, strategies as st

# pytest
import pytest

# Zato - Rust
from zato_common_core.zato_common_core import encode_push_envelope_parts, escape_push_payload

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, any_, byteslist

    anydict = anydict
    byteslist = byteslist

# ################################################################################################################################
# ################################################################################################################################

_payload_key = 'data'

# The range of the integer fields of an envelope
_int_min = -(2 ** 63)
_int_max = 2 ** 63 - 1

# How many generated envelopes each property test checks
_max_examples = 300

# The code points of the control characters, which JSON strings escape
_control_characters_end = 0x20

# ################################################################################################################################
# ################################################################################################################################

def _new_payload_of_every_escape_class() -> 'str':
    """ Returns a payload with every class of characters that JSON escapes and with characters that it writes as they are.
    """
    out = 'Order "12345" for C:\\customers\\john.smith - '

    for code_point in range(_control_characters_end):
        out += chr(code_point)

    out += '\u2028\U0001F680 naïve café /path'
    return out

# ################################################################################################################################

_payload_of_every_escape_class = _new_payload_of_every_escape_class()

# ################################################################################################################################

def _new_envelope(data:'str', delivery_attempt:'int') -> 'anydict':
    """ Returns an envelope in the shape of a message that push delivery sends, without its delivery row.
    """
    out = {
        'msg_id': 'zpsm.0192d3a1b2c3d4e5f60718293a4b5c6d',
        'sequence_id': 12345,
        'topic_name': '/customers/orders',
        'data': data,
        'data_class': '',
        'data_preview': 'Order 12345 preview',
        'data_size': len(data),
        'priority': 5,
        'expiration': 86400000,
        'pub_time_iso': '2026-11-23T19:04:00.123456+00:00',
        'recv_time_iso': '2026-11-23T19:04:00.124001+00:00',
        'expiration_time_iso': None,
        'publisher': 'crm.orders',
        'correl_id': 'Order 12345 for John Smith',
        'delivery_attempt': delivery_attempt,
    }
    return out

# ################################################################################################################################

def _encode_value(value:'any_') -> 'bytes':
    """ Encodes one value of an envelope as compact JSON.
    """
    if value is None:
        out = b'null'

    elif isinstance(value, int):
        text = str(value)
        out = text.encode('ascii')

    else:
        out = escape_push_payload(value)

    return out

# ################################################################################################################################

def _encode_whole(envelope:'anydict') -> 'bytes':
    """ Encodes a whole envelope as compact JSON, one member after another, in the order of its keys.
    """
    members:'byteslist' = []

    for key, value in envelope.items():
        encoded_key = escape_push_payload(key)
        encoded_value = _encode_value(value)
        members.append(encoded_key + b':' + encoded_value)

    out = b'{' + b','.join(members) + b'}'
    return out

# ################################################################################################################################

def _join_parts(envelope:'anydict') -> 'bytes':
    """ Encodes an envelope as push delivery sends it, its prefix, its escaped payload and its suffix.
    """
    prefix, suffix = encode_push_envelope_parts(envelope, _payload_key)
    escaped = escape_push_payload(envelope[_payload_key])

    out = prefix + escaped + suffix
    return out

# ################################################################################################################################
# ################################################################################################################################

_field_values = st.one_of(
    st.none(),
    st.integers(min_value=_int_min, max_value=_int_max),
    st.text(),
)

def _is_not_payload_key(key:'str') -> 'bool':
    out = key != _payload_key
    return out

_field_keys = st.text().filter(_is_not_payload_key)

_other_fields = st.dictionaries(_field_keys, _field_values, max_size=16)

# ################################################################################################################################
# ################################################################################################################################

@given(data=st.text(), fields_before=_other_fields, fields_after=_other_fields)
@settings(max_examples=_max_examples, deadline=None)
def test_joined_parts_equal_the_whole_envelope(data:'str', fields_before:'anydict', fields_after:'anydict') -> 'None':

    # The payload goes between the two groups of fields, in the order in which they are set ..
    envelope:'anydict' = {}

    for key, value in fields_before.items():
        envelope[key] = value

    envelope[_payload_key] = data

    for key, value in fields_after.items():
        if key not in envelope:
            envelope[key] = value

    # .. the parts joined are the whole envelope, byte for byte ..
    joined = _join_parts(envelope)
    assert joined == _encode_whole(envelope)

    # .. and they decode to the envelope, with its keys in their order.
    decoded = loads(joined)
    assert decoded == envelope
    assert list(decoded) == list(envelope)

# ################################################################################################################################

def test_envelope_of_a_message() -> 'None':

    for delivery_attempt in (1, 2, 10):
        envelope = _new_envelope(_payload_of_every_escape_class, delivery_attempt)

        joined = _join_parts(envelope)
        assert joined == _encode_whole(envelope)

        decoded = loads(joined)
        assert decoded == envelope

# ################################################################################################################################

def test_the_escaped_payload_is_shared_by_every_attempt() -> 'None':

    # The prefix and the suffix differ between the attempts, whereas the payload escaped once fits each of them
    escaped = escape_push_payload(_payload_of_every_escape_class)

    first = _new_envelope(_payload_of_every_escape_class, 1)
    second = _new_envelope(_payload_of_every_escape_class, 2)

    first_prefix, first_suffix = encode_push_envelope_parts(first, _payload_key)
    second_prefix, second_suffix = encode_push_envelope_parts(second, _payload_key)

    assert first_prefix + escaped + first_suffix == _encode_whole(first)
    assert second_prefix + escaped + second_suffix == _encode_whole(second)
    assert first_suffix != second_suffix

# ################################################################################################################################

def test_the_payload_is_not_in_the_parts() -> 'None':
    envelope = _new_envelope(_payload_of_every_escape_class, 1)
    escaped = escape_push_payload(_payload_of_every_escape_class)

    prefix, suffix = encode_push_envelope_parts(envelope, _payload_key)

    assert prefix.endswith(b'"data":')
    assert escaped not in prefix
    assert escaped not in suffix

# ################################################################################################################################

def test_an_envelope_without_its_payload_is_rejected() -> 'None':
    envelope = _new_envelope(_payload_of_every_escape_class, 1)
    del envelope[_payload_key]

    with pytest.raises(KeyError):
        _ = encode_push_envelope_parts(envelope, _payload_key)

# ################################################################################################################################

def test_a_field_of_an_unsupported_type_is_rejected() -> 'None':
    envelope = _new_envelope(_payload_of_every_escape_class, 1)
    envelope['priority'] = 5.5

    with pytest.raises(TypeError):
        _ = encode_push_envelope_parts(envelope, _payload_key)

# ################################################################################################################################
# ################################################################################################################################
