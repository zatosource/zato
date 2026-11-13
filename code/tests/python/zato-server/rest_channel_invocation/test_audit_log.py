# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The audit log events of requests to REST channels with the audit log active and inactive.

# stdlib
import time
from http.client import OK

# Zato
from channel_definitions import Channels, Paths, Services
from channel_suite import read_audit_events, wait_until

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from channel_suite import Suite
    from zato.common.typing_ import anylist

# ################################################################################################################################
# ################################################################################################################################

_source_channel = 'rest-channel'
_source_service = 'service'

_request_received = 'request-received'
_response_sent = 'response-sent'

# How long the test waits for events that are not expected to appear, in seconds
_absence_wait = 3

_request_body = b'{"customer_id": 123, "name": "John Smith"}'

# ################################################################################################################################
# ################################################################################################################################

def _post(suite:'Suite', path:'str') -> 'str':
    """ Sends a request and returns its CID.
    """
    response = suite.client.request('POST', path, headers={'Content-Type': 'application/json'}, body=_request_body)
    assert response.status == OK

    out = response.json()['cid']
    return out

# ################################################################################################################################

def _events_of(events:'anylist', source:'str') -> 'anylist':
    out:'anylist' = []

    for event in events:
        if event['source'] == source:
            out.append(event)

    return out

# ################################################################################################################################

def _wait_for_events(suite:'Suite', cid:'str', source:'str', count:'int') -> 'anylist':

    def _condition() -> 'anylist':
        events = read_audit_events(suite.audit_db_path, cid)
        selected = _events_of(events, source)
        if len(selected) >= count:
            return selected
        return []

    out = wait_until(_condition)
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_audit_log_active(suite:'Suite') -> 'None':
    cid = _post(suite, Paths.Audit_Active)
    events = _wait_for_events(suite, cid, _source_channel, 2)

    request_event, response_event = events

    assert request_event['event_type'] == _request_received
    assert request_event['object_name'] == Channels.Audit_Active
    assert request_event['cid'] == cid
    assert request_event['status'] == ''
    assert request_event['outcome'] == 'ok'
    assert request_event['ext_client_id'] == ''
    assert 'John Smith' in request_event['data']

    assert response_event['event_type'] == _response_sent
    assert response_event['object_name'] == Channels.Audit_Active
    assert response_event['cid'] == cid
    assert response_event['status'] == '200 OK'
    assert response_event['outcome'] == 'ok'
    assert Channels.Audit_Active in response_event['data']

# ################################################################################################################################

def test_audit_log_inactive(suite:'Suite') -> 'None':
    cid = _post(suite, Paths.Audit_Inactive)

    # The service writes its own events regardless of the channel ..
    service_events = _wait_for_events(suite, cid, _source_service, 2)
    for event in service_events:
        assert event['object_name'] == Services.Echo

    # .. but the channel writes none.
    time.sleep(_absence_wait)
    events = read_audit_events(suite.audit_db_path, cid)

    assert _events_of(events, _source_channel) == []

# ################################################################################################################################
# ################################################################################################################################
