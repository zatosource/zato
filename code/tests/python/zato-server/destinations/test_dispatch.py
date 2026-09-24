# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import dumps

# pytest
import pytest

# Zato
from zato.common.audit_log.common import AuditClassification
from zato.common.destination.constants import DestinationType
from zato.common.destination.model import new_entry, DestinationException
from zato.common.typing_ import cast_
from zato.server.destination.dispatch import send

from service_stub import ServiceStub, FHIR_Response, MLLP_Rejected_Status, MLLP_Rejected_Text, MLLP_Response, \
    REST_Queued_Response, REST_Rejected_Response, REST_Rejected_Status, REST_Rejected_Text, REST_Response, SMTP_Response

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

# The connections the destinations point at
_rest_connection = 'rest.billing'
_mllp_connection = 'hl7.forward.ehr'
_fhir_connection = 'fhir.ehr'
_smtp_connection = 'smtp.notifications'

# What arrived on the channel
_request_payload = 'MSH|^~\\&|SENDER|FACILITY|RECEIVER|FACILITY|20260101120000||ADT^A01|MSG00001|P|2.5'

# Where an email destination sends and under what subject line
_recipient = 'admissions@example.com'
_subject = 'A new admission arrived'

# ################################################################################################################################
# ################################################################################################################################

def _new_service(*, has_email:'bool'=True) -> 'ServiceStub':
    out = ServiceStub(_request_payload, has_email=has_email)
    return out

# ################################################################################################################################

def _as_service(stub:'ServiceStub') -> 'Service':
    """ The dispatcher takes a service, and everything it reaches for on one the stub offers.
    """
    out = cast_('Service', stub)
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestREST:

    def test_a_rest_destination_is_delivered_to_with_the_method_it_names(self) -> 'None':
        stub = _new_service()
        service = _as_service(stub)

        entry = new_entry(_rest_connection, DestinationType.REST, _rest_connection, options={'method': 'PUT'})

        result = send(service, entry, _request_payload)
        response = result.response

        assert response == REST_Response

        connection, method, args, _ = stub.rest.calls[0]

        assert connection == _rest_connection
        assert method == 'put'
        assert args == (_request_payload,)

# ################################################################################################################################

    def test_a_rest_destination_that_names_no_method_posts(self) -> 'None':
        stub = _new_service()
        service = _as_service(stub)

        entry = new_entry(_rest_connection, DestinationType.REST, _rest_connection)

        _ = send(service, entry, _request_payload)

        _, method, _, _ = stub.rest.calls[0]

        assert method == 'post'

# ################################################################################################################################

    def test_a_method_with_no_body_carries_nothing_beyond_the_call(self) -> 'None':
        stub = _new_service()
        service = _as_service(stub)

        entry = new_entry(_rest_connection, DestinationType.REST, _rest_connection, options={'method': 'GET'})

        _ = send(service, entry, _request_payload)

        _, method, args, _ = stub.rest.calls[0]

        assert method == 'get'
        assert args == ()

# ################################################################################################################################

    def test_the_connection_does_not_record_a_delivery_the_engine_records(self) -> 'None':
        stub = _new_service()
        service = _as_service(stub)

        entry = new_entry(_rest_connection, DestinationType.REST, _rest_connection)

        _ = send(service, entry, _request_payload)

        _, _, _, kwargs = stub.rest.calls[0]

        assert kwargs == {'needs_audit': False}

# ################################################################################################################################

    def test_a_method_nothing_can_be_delivered_with_is_refused(self) -> 'None':
        stub = _new_service()
        service = _as_service(stub)

        entry = new_entry(_rest_connection, DestinationType.REST, _rest_connection, options={'method': 'TRACE'})

        with pytest.raises(DestinationException) as raised:
            _ = send(service, entry, _request_payload)

        assert 'with method `TRACE`' in str(raised.value)

# ################################################################################################################################
# ################################################################################################################################

class TestMLLP:

    def test_an_mllp_destination_is_sent_the_message_and_answers_with_its_acknowledgment(self) -> 'None':
        stub = _new_service()
        service = _as_service(stub)

        entry = new_entry(_mllp_connection, DestinationType.MLLP, _mllp_connection)

        result = send(service, entry, _request_payload)
        response = result.response

        assert response == MLLP_Response

        connection, payload, needs_audit = stub.mllp.calls[0]

        assert connection == _mllp_connection
        assert payload == _request_payload
        assert needs_audit is False

# ################################################################################################################################
# ################################################################################################################################

class TestFHIR:

    def test_a_fhir_destination_is_delivered_to_with_the_method_and_the_path_it_names(self) -> 'None':
        stub = _new_service()
        service = _as_service(stub)

        resource = {'resourceType': 'Patient', 'id': '12345'}

        entry = new_entry(_fhir_connection, DestinationType.FHIR, _fhir_connection,
            options={'method': 'PUT', 'path': '/Patient'})

        result = send(service, entry, resource)
        response = result.response

        assert response == FHIR_Response

        connection, method, path, data, needs_audit = stub.fhir.calls[0]

        assert connection == _fhir_connection
        assert method == 'PUT'
        assert path == '/Patient'
        assert data == resource
        assert needs_audit is False

# ################################################################################################################################

    def test_a_fhir_resource_arriving_as_text_goes_out_as_the_document_it_is(self) -> 'None':
        stub = _new_service()
        service = _as_service(stub)

        resource = {'resourceType': 'Patient', 'id': '12345'}

        entry = new_entry(_fhir_connection, DestinationType.FHIR, _fhir_connection, options={'path': '/Patient'})

        _ = send(service, entry, dumps(resource))

        _, method, _, data, _ = stub.fhir.calls[0]

        assert method == 'POST'
        assert data == resource

# ################################################################################################################################

    def test_a_fhir_destination_with_no_path_is_refused(self) -> 'None':
        stub = _new_service()
        service = _as_service(stub)

        entry = new_entry(_fhir_connection, DestinationType.FHIR, _fhir_connection)

        with pytest.raises(DestinationException) as raised:
            _ = send(service, entry, {'resourceType': 'Patient'})

        assert 'has no path' in str(raised.value)

# ################################################################################################################################
# ################################################################################################################################

class TestEmail:

    def test_an_email_destination_is_sent_the_message_as_the_body(self) -> 'None':
        stub = _new_service()
        service = _as_service(stub)

        entry = new_entry(_smtp_connection, DestinationType.SMTP, _smtp_connection,
            options={'to': _recipient, 'subject': _subject})

        result = send(service, entry, _request_payload)
        response = result.response

        assert response == SMTP_Response

        email = stub.email
        assert email

        connection, to, subject, body = email.smtp.calls[0]

        assert connection == _smtp_connection
        assert to == _recipient
        assert subject == _subject
        assert body == _request_payload

# ################################################################################################################################

    def test_an_email_destination_with_no_recipient_is_refused(self) -> 'None':
        stub = _new_service()
        service = _as_service(stub)

        entry = new_entry(_smtp_connection, DestinationType.SMTP, _smtp_connection, options={'subject': _subject})

        with pytest.raises(DestinationException) as raised:
            _ = send(service, entry, _request_payload)

        assert 'has no recipient' in str(raised.value)

# ################################################################################################################################

    def test_an_email_destination_cannot_be_delivered_to_with_email_turned_off(self) -> 'None':
        stub = _new_service(has_email=False)
        service = _as_service(stub)

        entry = new_entry(_smtp_connection, DestinationType.SMTP, _smtp_connection, options={'to': _recipient})

        with pytest.raises(DestinationException) as raised:
            _ = send(service, entry, _request_payload)

        assert 'e-mail is not enabled' in str(raised.value)

# ################################################################################################################################
# ################################################################################################################################

class TestRejections:
    """ A destination that turned the message down answered, so every adapter reports that
    as part of its result.
    """

    def test_a_rest_endpoint_that_answered_with_an_error_status_turned_the_message_down(self) -> 'None':
        stub = _new_service()
        stub.rest.rejecting.append(_rest_connection)
        service = _as_service(stub)

        entry = new_entry(_rest_connection, DestinationType.REST, _rest_connection)

        result = send(service, entry, _request_payload)

        assert result.is_rejected is True
        assert result.response is REST_Rejected_Response
        assert result.response_text == REST_Rejected_Text

        # The status line alone is what the row is classified by, never the body.
        assert result.status == REST_Rejected_Status

# ################################################################################################################################

    def test_an_hl7_receiver_that_did_not_accept_the_message_turned_it_down(self) -> 'None':
        stub = _new_service()
        stub.mllp.rejecting.append(_mllp_connection)
        service = _as_service(stub)

        entry = new_entry(_mllp_connection, DestinationType.MLLP, _mllp_connection)

        result = send(service, entry, _request_payload)

        assert result.is_rejected is True
        assert result.status == MLLP_Rejected_Status

        # The acknowledgment is still what a channel replying from this destination answers with.
        assert result.response == MLLP_Rejected_Text

        # An AE or an AR is the receiving application saying no, so nothing here is guessed
        # from the wording of the error.
        assert result.classification == AuditClassification.Permanent

# ################################################################################################################################

    def test_a_message_the_transport_could_not_send_is_not_recorded_as_one_it_did(self) -> 'None':
        stub = _new_service()
        email = stub.email
        assert email

        email.smtp.rejecting.append(_smtp_connection)
        service = _as_service(stub)

        entry = new_entry(_smtp_connection, DestinationType.SMTP, _smtp_connection, options={'to': _recipient})

        result = send(service, entry, _request_payload)

        assert result.is_rejected is True
        assert result.response is False
        assert result.status

# ################################################################################################################################
# ################################################################################################################################

class TestQueuedDeliveries:
    """ A connection with the queue switch on hands the message over rather than sending it.
    """

    def test_a_queued_delivery_is_neither_rejected_nor_read_for_a_status(self) -> 'None':
        stub = _new_service()
        stub.rest.queued.append(_rest_connection)
        service = _as_service(stub)

        entry = new_entry(_rest_connection, DestinationType.REST, _rest_connection)

        result = send(service, entry, _request_payload)

        # A queue result has no `ok` to read, so nothing here reads it as a response.
        assert result.is_rejected is False
        assert result.status == ''
        assert result.response is REST_Queued_Response

        # There is no response body to keep either, the message not having been sent yet.
        assert result.response_text == ''

# ################################################################################################################################
# ################################################################################################################################

class TestUnknownTypes:

    def test_a_type_nothing_delivers_to_is_refused(self) -> 'None':
        stub = _new_service()
        service = _as_service(stub)

        entry = new_entry('carrier.pigeon', 'carrier-pigeon', 'carrier.pigeon')

        with pytest.raises(DestinationException) as raised:
            _ = send(service, entry, _request_payload)

        assert 'nothing delivers to' in str(raised.value)

# ################################################################################################################################
# ################################################################################################################################
