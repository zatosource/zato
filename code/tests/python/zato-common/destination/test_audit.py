# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import loads

# Zato
from zato.common.audit_log.api import AuditOutcome, AuditSource
from zato.common.destination.audit import get_hop_entry
from zato.common.destination.constants import DeliveryMode, DestinationOption, DestinationType, Respond_From_Service
from zato.common.destination.coordinator import deliver
from zato.common.destination.model import get_option, parse_config, DestinationException
from zato.common.destination.payload import new_overrides

from connection_recorder import get_attr_map, get_hop_rows, get_stored_list, new_test_context, Channel_Name, \
    ConnectionRecorder, FHIR_Connection, MLLP_Connection, Request_Payload, REST_Connection, Transient_Error

# ################################################################################################################################
# ################################################################################################################################

# The classification a failure another attempt can get past is recorded with
_transient_classification = 'transient'

# ################################################################################################################################
# ################################################################################################################################

class TestAuditTrail:

    def test_every_destination_is_recorded_under_the_message_that_came_in(self) -> 'None':
        recorder = ConnectionRecorder()
        context = new_test_context(recorder)
        config = parse_config(Channel_Name, get_stored_list(), Respond_From_Service, DeliveryMode.In_Order)

        _ = deliver(context, config, new_overrides(), Request_Payload)

        rows = get_hop_rows()

        assert len(rows) == 3

        # Each type is recorded under the source that type belongs to ..
        assert rows[0]['source'] == AuditSource.MLLP_Outgoing
        assert rows[1]['source'] == AuditSource.REST_Outgoing
        assert rows[2]['source'] == AuditSource.FHIR

        # .. against the connection it was delivered through ..
        assert rows[0]['object_name'] == MLLP_Connection
        assert rows[1]['object_name'] == REST_Connection
        assert rows[2]['object_name'] == FHIR_Connection

        # .. and all of them went through.
        for row in rows:
            assert row['outcome'] == AuditOutcome.OK
            assert row['status'] == ''

# ################################################################################################################################

    def test_a_recorded_delivery_carries_what_it_takes_to_repeat_it(self) -> 'None':
        recorder = ConnectionRecorder()
        context = new_test_context(recorder)
        config = parse_config(Channel_Name, get_stored_list(), Respond_From_Service, DeliveryMode.In_Order)

        _ = deliver(context, config, new_overrides(), Request_Payload)

        rows = get_hop_rows()

        # An MLLP delivery is the message and the destination it went to ..
        mllp_details = loads(rows[0]['data'])

        assert mllp_details == {'payload': Request_Payload, 'destination_name': MLLP_Connection}

        # .. whereas an HTTP one also carries the call that was made.
        fhir_details = loads(rows[2]['data'])

        assert fhir_details['payload'] == Request_Payload
        assert fhir_details['destination_name'] == FHIR_Connection
        assert fhir_details['method'] == 'POST'
        assert fhir_details['path'] == '/Patient'

# ################################################################################################################################

    def test_a_recorded_delivery_rebuilds_the_destination_it_went_to(self) -> 'None':
        recorder = ConnectionRecorder()
        context = new_test_context(recorder)
        config = parse_config(Channel_Name, get_stored_list(), Respond_From_Service, DeliveryMode.In_Order)

        _ = deliver(context, config, new_overrides(), Request_Payload)

        rows = get_hop_rows()

        # The REST row says everything a repeat of that one delivery needs, the method included ..
        rest_row = rows[1]
        rest_entry = get_hop_entry(rest_row['source'], rest_row['object_name'], loads(rest_row['data']))

        assert rest_entry.name == REST_Connection
        assert rest_entry.type == DestinationType.REST
        assert rest_entry.connection == REST_Connection
        assert get_option(rest_entry, DestinationOption.Method, '') == 'PUT'

        # .. and so does the FHIR one, with the path it was called at as well ..
        fhir_row = rows[2]
        fhir_entry = get_hop_entry(fhir_row['source'], fhir_row['object_name'], loads(fhir_row['data']))

        assert fhir_entry.type == DestinationType.FHIR
        assert get_option(fhir_entry, DestinationOption.Path, '') == '/Patient'

        # .. while a source that fans out to nothing has no delivery to repeat.
        try:
            _ = get_hop_entry(AuditSource.AS2, 'partner', {})
        except DestinationException as e:
            assert AuditSource.AS2 in str(e)
        else:
            raise Exception('A source with no destinations was expected to be rejected')

# ################################################################################################################################

    def test_an_e_mail_delivery_rebuilds_the_message_it_went_out_as(self) -> 'None':
        details = {
            'payload': Request_Payload,
            'destination_name': 'Ward notifications',
            'to': 'ward@example.com',
            'subject': 'Admission',
        }

        entry = get_hop_entry(AuditSource.Email_SMTP, 'smtp.internal', details)

        assert entry.name == 'Ward notifications'
        assert entry.type == DestinationType.SMTP
        assert entry.connection == 'smtp.internal'
        assert get_option(entry, DestinationOption.To, '') == 'ward@example.com'
        assert get_option(entry, DestinationOption.Subject, '') == 'Admission'

# ################################################################################################################################

    def test_a_delivery_a_connection_recorded_itself_is_addressed_by_that_connection(self) -> 'None':

        # A row a FHIR outconn wrote on its own behalf, before any of this existed, names
        # no destination - the connection it went through is the destination it went to
        details = {'payload': Request_Payload, 'method': 'PUT', 'path': '/Patient/1'}

        entry = get_hop_entry(AuditSource.FHIR, FHIR_Connection, details)

        assert entry.name == FHIR_Connection
        assert entry.connection == FHIR_Connection
        assert get_option(entry, DestinationOption.Method, '') == 'PUT'

        # An MLLP delivery is the message alone, so a row of one needs nothing beyond its connection
        mllp_entry = get_hop_entry(AuditSource.MLLP_Outgoing, MLLP_Connection, {'payload': Request_Payload})

        assert mllp_entry.type == DestinationType.MLLP
        assert mllp_entry.connection == MLLP_Connection
        assert mllp_entry.options == {}

# ################################################################################################################################

    def test_a_recorded_delivery_says_which_destination_of_which_channel_it_was(self) -> 'None':
        recorder = ConnectionRecorder()
        context = new_test_context(recorder)
        config = parse_config(Channel_Name, get_stored_list(), Respond_From_Service, DeliveryMode.In_Order)

        _ = deliver(context, config, new_overrides(), Request_Payload)

        rows = get_hop_rows()
        attrs = get_attr_map(rows[1]['id'])

        assert attrs['channel_name'] == Channel_Name
        assert attrs['destination_name'] == REST_Connection
        assert attrs['destination_type'] == DestinationType.REST
        assert attrs['delivery_sequence'] == '1'
        assert attrs['attempt'] == '1'

# ################################################################################################################################

    def test_every_attempt_is_recorded_so_the_history_has_no_holes(self) -> 'None':
        recorder = ConnectionRecorder()
        recorder.failing_attempts[MLLP_Connection] = 1

        context = new_test_context(recorder, retry_count=1)
        stored = get_stored_list()[:1]
        config = parse_config(Channel_Name, stored)

        _ = deliver(context, config, new_overrides(), Request_Payload)

        rows = get_hop_rows()

        assert len(rows) == 2

        # The attempt that failed says what stopped it ..
        assert rows[0]['outcome'] == AuditOutcome.Error
        assert rows[0]['status'] == Transient_Error
        assert get_attr_map(rows[0]['id'])['attempt'] == '1'

        # .. and the one that went through says so.
        assert rows[1]['outcome'] == AuditOutcome.OK
        assert get_attr_map(rows[1]['id'])['attempt'] == '2'

# ################################################################################################################################

    def test_a_delivery_that_never_got_through_is_a_row_to_act_on(self) -> 'None':
        recorder = ConnectionRecorder()
        recorder.always_failing[REST_Connection] = Transient_Error

        context = new_test_context(recorder)
        stored = get_stored_list()[1:2]
        config = parse_config(Channel_Name, stored)

        _ = deliver(context, config, new_overrides(), Request_Payload)

        rows = get_hop_rows()

        assert len(rows) == 1
        assert rows[0]['outcome'] == AuditOutcome.Error
        assert rows[0]['status'] == Transient_Error

        # A failure another attempt can get past is what the browser offers a resend for
        assert rows[0]['classification'] == _transient_classification

# ################################################################################################################################
# ################################################################################################################################
