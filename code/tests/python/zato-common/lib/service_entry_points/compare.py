# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The invocation of the services under test through the drivers, the reading of their records and the comparison
# of each record and each response with the reference that self.invoke produced. The client is any client
# with an invoke method that takes a service name and a dict and returns the parsed response of the service.

# stdlib
import time
from typing import NamedTuple

# Zato
from zato.common.soap.message import parse, to_plain_dict
from zato.common.test.service_entry_points.models import RecordKey, ResponseKey, ServiceName
from zato.common.util.xml_.core import parse_xml

# Service entry points
from service_entry_points.requests import new_request, new_request_id, SOAP

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from service_entry_points.requests import Target
    from zato.common.typing_ import any_, anydict, dictlist

# ################################################################################################################################
# ################################################################################################################################

# How long a record of a delivery by pub/sub may take to appear, in seconds
Record_Timeout = 60

# How long to wait between reads of the records
_poll_interval = 0.5

# What a request ID is replaced with before two records or two responses are compared
_request_id_placeholder = '{request_id}'

# HL7 v2 separates segments with a carriage return, which an editor or a transport may write as a line feed
_hl7_segment_separator = '\r'
_line_endings = ('\r\n', '\n')

# The local name of the body of a SOAP envelope
_soap_body = 'Body'

# The keys of a record that every entry point must produce identically, the channel being what differs
_compared_keys = (RecordKey.Service, RecordKey.Input, RecordKey.Result)

# ################################################################################################################################
# ################################################################################################################################

class Reference(NamedTuple):
    """ The record and the response of a service under test invoked through self.invoke.
    """
    request_id: 'str'
    record: 'anydict'
    response: 'any_'

# ################################################################################################################################

references_dict = dict[str, Reference]

# ################################################################################################################################
# ################################################################################################################################

def invoke_through_driver(client:'any_', service_name:'str', payload:'any_') -> 'any_':
    """ Invokes a service with self.invoke through the driver and returns the response of the service.
    """
    request = {
        'target': service_name,
        'payload': payload,
    }

    response = client.invoke(ServiceName.Invoke_Driver, request)

    out = response[ResponseKey.Response]
    return out

# ################################################################################################################################

def publish_through_driver(client:'any_', destination:'str', payload:'any_', *, should_publish_model:'bool'=False) -> 'None':
    """ Publishes a request with self.pubsub through the driver, to a topic or to a service by its name.
    """
    request = {
        'destination': destination,
        'payload': payload,
        'should_publish_model': should_publish_model,
    }

    _ = client.invoke(ServiceName.Publish_Driver, request)

# ################################################################################################################################
# ################################################################################################################################

def read_records(client:'any_') -> 'dictlist':
    """ Every record that the services under test wrote.
    """
    response = client.invoke(ServiceName.Read)

    out = response[ResponseKey.Records]
    return out

# ################################################################################################################################

def find_records(client:'any_', request_id:'str') -> 'dictlist':
    """ The records of one request, one per invocation of the service that the request reached.
    """
    out = []

    for item in read_records(client):
        if item[RecordKey.Request_ID] == request_id:
            out.append(item)

    return out

# ################################################################################################################################

def wait_for_record(client:'any_', request_id:'str', timeout:'float'=Record_Timeout) -> 'anydict':
    """ Waits until the record of a request appears and returns it, and fails if the request reached its service
    more than once.
    """
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:

        records = find_records(client, request_id)

        if records:
            assert len(records) == 1, f'Request `{request_id}` was recorded {len(records)} times -> {records}'
            out = records[0]
            return out

        time.sleep(_poll_interval)

    raise Exception(f'No record of request `{request_id}` appeared within {timeout}s')

# ################################################################################################################################
# ################################################################################################################################

def take_reference(client:'any_', target:'Target') -> 'Reference':
    """ Invokes a service under test with self.invoke and returns what it recorded and responded.
    """
    request_id = new_request_id()
    payload = new_request(target, request_id)

    response = invoke_through_driver(client, target.service_name, payload)
    record = wait_for_record(client, request_id)

    out = Reference(request_id, record, response)
    return out

# ################################################################################################################################
# ################################################################################################################################

def normalize(value:'any_', request_id:'str') -> 'any_':
    """ A value with its request ID replaced by a placeholder, and the segments of HL7 v2 text separated
    by a carriage return, so that values of different requests compare equal when nothing else differs.
    """
    if isinstance(value, dict):
        out = {}

        for key, item in value.items():
            out[key] = normalize(item, request_id)

    elif isinstance(value, list):
        out = []

        for item in value:
            normalized = normalize(item, request_id)
            out.append(normalized)

    elif isinstance(value, str):
        out = value.replace(request_id, _request_id_placeholder)

        for line_ending in _line_endings:
            out = out.replace(line_ending, _hl7_segment_separator)

        out = out.strip(_hl7_segment_separator)

    else:
        out = value

    return out

# ################################################################################################################################

def _get_compared_part(record:'anydict') -> 'anydict':
    """ The part of a record that every entry point must produce identically.
    """
    out = {}

    for key in _compared_keys:
        out[key] = record[key]

    return out

# ################################################################################################################################

def assert_same_record(reference:'Reference', record:'anydict', entry_point:'str') -> 'None':
    """ Fails unless a record equals the reference in what the service received and what it computed.
    """
    expected = normalize(_get_compared_part(reference.record), reference.request_id)
    actual = normalize(_get_compared_part(record), record[RecordKey.Request_ID])

    assert actual == expected, f'The record of {entry_point} differs from that of self.invoke\n' + \
        f'expected: {expected}\nactual:   {actual}'

# ################################################################################################################################

def assert_same_response(reference:'Reference', response:'any_', request_id:'str', entry_point:'str') -> 'None':
    """ Fails unless a response equals the response of the reference.
    """
    expected = normalize(reference.response, reference.request_id)
    actual = normalize(response, request_id)

    assert actual == expected, f'The response of {entry_point} differs from that of self.invoke\n' + \
        f'expected: {expected}\nactual:   {actual}'

# ################################################################################################################################

def assert_same_invocation(reference:'Reference', client:'any_', request_id:'str', response:'any_', entry_point:'str') -> 'None':
    """ Fails unless both the record and the response of a request equal those of the reference.
    """
    record = wait_for_record(client, request_id)

    assert_same_record(reference, record, entry_point)
    assert_same_response(reference, response, request_id, entry_point)

# ################################################################################################################################
# ################################################################################################################################

def parse_soap_response(body:'bytes') -> 'anydict':
    """ The children of the response element of a SOAP envelope as a dict, which is the response of the service.
    """
    envelope = parse_xml(body)
    operation:'any_' = None

    for child in envelope:
        if child.tag.rpartition('}')[2] == _soap_body:
            operation = child[0]
            break

    assert operation is not None, f'No SOAP body in {body!r}'

    operation_name = operation.tag.rpartition('}')[2]
    assert operation_name == SOAP.Response_Element, f'Unexpected response element `{operation_name}` in {body!r}'

    message = parse(operation)

    out = to_plain_dict(message)
    return out

# ################################################################################################################################
# ################################################################################################################################
