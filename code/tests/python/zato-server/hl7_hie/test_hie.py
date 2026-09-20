# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A ministry's exchange, driven live - facility B sends patient events through Zato to the interoperability
# layer in its container, which routes them to the shared record's front door, also Zato, and to the client
# registry, and logs every transaction. The front door files a registration through the record's patient API
# and hands anything else to the record's own HL7 queue. What the record made of each message is read back from
# the record itself, what the exchange saw from its transaction log.

# stdlib
import socket

# Live HL7
from hl7_client.python_client import parse_ack
from live_hl7.openhim.system import Channel_Disabled, Channel_Enabled, set_channel_status, transactions
from live_hl7.openmrs.system import find_patients, hl7_archive, hl7_errors, run_hl7_task
from live_hl7.system import Host as Container_Host

# Zato - the suite's own parts
from _enmasse import Facility_B_Connection, Facility_B_Registry_Down_Connection, Facility_B_SHR_Down_Connection
from _exchange import Registry_Route
from _messages import Patient, build_adt_a28, build_adt_a40, deliveries_with_control_id, new_control_id, \
    new_patient, recorded_with_control_id, wait_for
from _services import Send_Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import HIEEnvironment
    from live_hl7.system import Handle
    from zato.common.typing_ import anydict, anylist

# ################################################################################################################################
# ################################################################################################################################

# The acknowledgment code a message that was taken gets
Accepted = 'AA'

# What the exchange stores a route's outcome as
Route_OK = 200
Route_Failed = 500

# How long a probe waits for the channel behind a port to close on it before the channel is called open
Probe_Timeout = 2.0

# ################################################################################################################################
# ################################################################################################################################

def _send(hie:'HIEEnvironment', connection:'str', message:'str') -> 'anydict':
    """ Facility B sends one message through one of its connections and returns what came back.
    """
    out = hie.client.invoke(Send_Service, {'connection': connection, 'message': message})
    return out

# ################################################################################################################################

def _transaction_of(hie:'HIEEnvironment', channel_id:'str', control_id:'str') -> 'anydict':
    """ The transaction the exchange logged for one message, once it is there with its routes.
    """
    found:'anylist' = []

    def _is_logged() -> 'bool':
        found.clear()

        for transaction in transactions(hie.openhim_session, channel_id):
            if control_id in transaction['request']['body']:
                found.append(transaction)

        out = len(found) == 1
        return out

    wait_for(_is_logged, f'the transaction of {control_id}')

    out = found[0]
    return out

# ################################################################################################################################

def _route_named(transaction:'anydict', name:'str') -> 'anydict':
    """ One of the transaction's non-primary routes - the primary is the transaction's own response.
    """
    for route in transaction['routes']:
        if route['name'] == name:
            return route

    raise Exception(f'No route named {name} in transaction {transaction["_id"]}')

# ################################################################################################################################

def _wait_for_route(hie:'HIEEnvironment', channel_id:'str', control_id:'str', name:'str') -> 'anydict':
    """ The transaction of one message with the named route's outcome in it - the exchange logs a route
    once it has answered, which for the registry is after the primary has.
    """
    found:'anylist' = []

    def _has_route() -> 'bool':
        found.clear()

        transaction = _transaction_of(hie, channel_id, control_id)

        for route in transaction['routes']:
            if route['name'] == name:
                found.append(transaction)

        out = len(found) == 1
        return out

    wait_for(_has_route, f'route {name} of {control_id}')

    out = found[0]
    return out

# ################################################################################################################################

def _wait_for_record(hie:'HIEEnvironment', control_id:'str') -> 'None':
    """ Until the shared record's front door has recorded one message.
    """
    def _is_recorded() -> 'bool':
        recorded = recorded_with_control_id(hie.messages_file, control_id)

        out = len(recorded) == 1
        return out

    wait_for(_is_recorded, f'the front door recording {control_id}')

# ################################################################################################################################

def _wait_for_registry(hie:'HIEEnvironment', control_id:'str') -> 'None':
    """ Until the client registry has its copy of one message.
    """
    def _has_copy() -> 'bool':
        deliveries = deliveries_with_control_id(hie.registry.deliveries, control_id)

        out = len(deliveries) == 1
        return out

    wait_for(_has_copy, f'the registry receiving {control_id}')

# ################################################################################################################################

def _process_queue(hie:'HIEEnvironment') -> 'None':
    """ Runs the shared record's queue processor now rather than waiting for its scheduler.
    """
    run_hl7_task(hie.openmrs_session)

# ################################################################################################################################

def _wait_for_patient(hie:'HIEEnvironment', patient:'Patient') -> 'anydict':
    """ Until the shared record has a patient under the national id - the front door files one before it
    acknowledges, so this is a wait for the record's search to see them.
    """
    found:'anylist' = []

    def _is_filed() -> 'bool':
        found.clear()

        for candidate in find_patients(hie.openmrs_session, patient.patient_id):
            for identifier in candidate['identifiers']:
                if identifier['identifier'] == patient.patient_id:
                    found.append(candidate)

        out = len(found) == 1
        return out

    wait_for(_is_filed, f'the record filing patient {patient.patient_id}')

    out = found[0]
    return out

# ################################################################################################################################

def _wait_for_queue_error(hie:'HIEEnvironment', control_id:'str') -> 'str':
    """ Until the shared record's queue has filed one message as one it could not handle - returns the error.
    """
    found:'anylist' = []

    def _is_filed() -> 'bool':
        found.clear()
        _process_queue(hie)

        for row in hl7_errors(hie.openmrs):
            if row[0] == control_id:
                found.append(row[1])

        out = len(found) == 1
        return out

    wait_for(_is_filed, f'the record filing {control_id} as unhandled')

    out = found[0]
    return out

# ################################################################################################################################

def _is_channel_closed(port:'int') -> 'bool':
    """ True when the channel behind one of the exchange's ports closes a connection at once - an open channel
    holds it and waits for a message. Docker publishes the port whether or not anything in the container listens
    on it, so a channel that is off shows as a connection accepted and closed at once, with nothing said.
    """
    test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    test_socket.settimeout(Probe_Timeout)

    try:
        test_socket.connect((Container_Host, port))
        data = test_socket.recv(1)
        out = data == b''
    except TimeoutError:
        out = False
    except OSError:
        out = True
    finally:
        test_socket.close()

    return out

# ################################################################################################################################

def _wait_for_channel(port:'int', *, is_open:'bool') -> 'None':
    """ Until the channel behind one of the exchange's ports is open, or closed.
    """
    def _is_as_wanted() -> 'bool':
        is_closed = _is_channel_closed(port)

        out = is_closed != is_open
        return out

    if is_open:
        what = f'the channel on port {port} to open'
    else:
        what = f'the channel on port {port} to close'

    wait_for(_is_as_wanted, what)

# ################################################################################################################################

def _assert_accepted(result:'anydict', control_id:'str') -> 'None':
    """ The facility got the shared record's acknowledgment of its own message back through the exchange.
    """
    assert result['is_sent'], result['error_text']
    assert result['ack_code'] == Accepted, result

    ack = parse_ack(result['ack_text'])
    assert ack.msa_1 == Accepted
    assert ack.msa_2 == control_id

# ################################################################################################################################
# ################################################################################################################################

def test_facility_b(hie:'HIEEnvironment') -> 'None':
    """ Facility B registers a patient - the exchange delivers to the record and to the registry, answers
    the facility with the record's acknowledgment, the record files the patient and the transaction log
    has both routes as having succeeded.
    """
    patient = new_patient('Miller', 'Anna', '19850412', 'F')
    control_id = new_control_id()
    message = build_adt_a28(control_id, patient)

    result = _send(hie, Facility_B_Connection, message)
    _assert_accepted(result, control_id)

    # The front door took it and the registry got its copy ..
    _wait_for_record(hie, control_id)
    _wait_for_registry(hie, control_id)

    # .. the record has the patient under the national id and the name the message gave ..
    filed = _wait_for_patient(hie, patient)
    assert filed['person']['gender'] == patient.sex
    assert filed['person']['preferredName']['givenName'] == patient.given_name
    assert filed['person']['preferredName']['familyName'] == patient.family_name

    # .. and the exchange logged one transaction, the primary's acknowledgment as its response and the
    # registry's as the one route besides it.
    transaction = _wait_for_route(hie, hie.channels.national_adt, control_id, Registry_Route)

    assert transaction['response']['status'] == Route_OK
    assert f'MSA|{Accepted}|{control_id}' in transaction['response']['body']

    registry_route = _route_named(transaction, Registry_Route)
    assert registry_route['response']['status'] == Route_OK
    assert f'MSA|{Accepted}|{control_id}' in registry_route['response']['body']

# ################################################################################################################################

def test_registry_down(hie:'HIEEnvironment') -> 'None':
    """ The registry is down - the facility still gets the record's acknowledgment, the record files the
    patient, and the transaction log has the registry's route as having failed.
    """
    patient = new_patient('Johnson', 'Robert', '19720930', 'M')
    control_id = new_control_id()
    message = build_adt_a28(control_id, patient)

    result = _send(hie, Facility_B_Registry_Down_Connection, message)
    _assert_accepted(result, control_id)

    _wait_for_record(hie, control_id)
    _ = _wait_for_patient(hie, patient)

    transaction = _wait_for_route(hie, hie.channels.registry_down, control_id, Registry_Route)
    assert transaction['response']['status'] == Route_OK

    registry_route = _route_named(transaction, Registry_Route)
    assert registry_route['response']['status'] == Route_Failed
    assert registry_route['error']['message']

    # Nothing of it reached the registry
    deliveries = deliveries_with_control_id(hie.registry.deliveries, control_id)
    assert len(deliveries) == 0

# ################################################################################################################################

def test_shr_down(hie:'HIEEnvironment') -> 'None':
    """ The shared record is down - the facility's send fails, the transaction log has the failure and
    neither the front door nor the registry gets the message.
    """
    patient = new_patient('Davis', 'Emily', '19910203', 'F')
    control_id = new_control_id()
    message = build_adt_a28(control_id, patient)

    result = _send(hie, Facility_B_SHR_Down_Connection, message)

    assert not result['is_sent'], result
    assert result['error_text']

    transaction = _wait_for_route(hie, hie.channels.shr_down, control_id, Registry_Route)
    assert transaction['response']['status'] == Route_Failed
    assert transaction['error']['message']

    recorded = recorded_with_control_id(hie.messages_file, control_id)
    assert len(recorded) == 0

    # The exchange writes the failure of a primary route that refuses the connection over the message before it
    # writes the other routes, so the registry gets the exchange's error text and no message
    deliveries = deliveries_with_control_id(hie.registry.deliveries, control_id)
    assert len(deliveries) == 0

# ################################################################################################################################

def test_disabled_channel(hie:'HIEEnvironment') -> 'None':
    """ The exchange switches the national feed off - a disabled tcp channel listens no more, so the facility's
    connection is closed before a byte is answered and its send fails, nothing is logged and nothing reaches the
    record, and once the feed is back on the same message goes through.
    """
    patient = new_patient('Wilson', 'James', '19680715', 'M')
    control_id = new_control_id()
    message = build_adt_a28(control_id, patient)

    channel_id = hie.channels.national_adt
    port = hie.openhim.port('channel_1')

    set_channel_status(hie.openhim_session, channel_id, Channel_Disabled)
    _wait_for_channel(port, is_open=False)

    try:
        result = _send(hie, Facility_B_Connection, message)

        assert not result['is_sent'], result
        assert result['error_text']

        for transaction in transactions(hie.openhim_session, channel_id):
            assert control_id not in transaction['request']['body']

        recorded = recorded_with_control_id(hie.messages_file, control_id)
        assert len(recorded) == 0

    finally:
        set_channel_status(hie.openhim_session, channel_id, Channel_Enabled)
        _wait_for_channel(port, is_open=True)

    result = _send(hie, Facility_B_Connection, message)
    _assert_accepted(result, control_id)

    _wait_for_record(hie, control_id)
    _ = _wait_for_patient(hie, patient)

# ################################################################################################################################

def test_merge_is_logged_and_forwarded(hie:'HIEEnvironment') -> 'None':
    """ Facility B merges two records - the exchange routes the merge to the record and the registry, the front
    door hands it to the record's queue, which files it as one it has no handler for, and the transaction log holds
    the whole message.
    """
    surviving = new_patient('Brown', 'Michael', '19790522', 'M')
    prior = new_patient('Brown', 'Michael', '19790522', 'M')

    # Both records exist before they are merged
    for patient in (surviving, prior):
        registration_id = new_control_id()
        result = _send(hie, Facility_B_Connection, build_adt_a28(registration_id, patient))
        _assert_accepted(result, registration_id)
        _ = _wait_for_patient(hie, patient)

    control_id = new_control_id()
    message = build_adt_a40(control_id, surviving, prior)

    result = _send(hie, Facility_B_Connection, message)
    _assert_accepted(result, control_id)

    _wait_for_record(hie, control_id)
    _wait_for_registry(hie, control_id)

    # The record took the message into its queue and then filed it as one it cannot handle ..
    error = _wait_for_queue_error(hie, control_id)
    assert error

    archived = _archived_control_ids(hie.openmrs)
    assert control_id not in archived

    # .. and the exchange holds the message as the facility sent it, segment by segment.
    transaction = _wait_for_route(hie, hie.channels.national_adt, control_id, Registry_Route)
    body = transaction['request']['body']

    for segment in message.split('\r'):
        assert segment in body

# ################################################################################################################################

def _archived_control_ids(openmrs:'Handle') -> 'anylist':
    """ The control ids of everything the record's queue handled.
    """
    out:'anylist' = []

    for row in hl7_archive(openmrs):
        out.append(row[0])

    return out

# ################################################################################################################################
# ################################################################################################################################
