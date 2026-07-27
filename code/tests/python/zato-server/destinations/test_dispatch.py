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
from zato.common.destination.constants import DestinationType
from zato.common.destination.model import new_entry, DestinationException
from zato.common.typing_ import cast_
from zato.server.destination.dispatch import send

from service_stub import ServiceStub, FHIR_Response, MLLP_Response, REST_Response, SMTP_Response

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

        response = send(service, entry, _request_payload)

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

        response = send(service, entry, _request_payload)

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

        response = send(service, entry, resource)

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

        response = send(service, entry, _request_payload)

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
