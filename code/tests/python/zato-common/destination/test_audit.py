# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import loads

# Zato
from zato.common.audit_log.api import AuditOutcome, AuditSource
from zato.common.destination.constants import DeliveryMode, DestinationType, Respond_From_Service
from zato.common.destination.coordinator import deliver
from zato.common.destination.model import parse_config
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
        assert rows[0]['source'] == AuditSource.HL7
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

        # An MLLP delivery is the message and nothing else ..
        mllp_details = loads(rows[0]['data'])

        assert mllp_details == {'payload': Request_Payload}

        # .. whereas an HTTP one also carries the call that was made.
        fhir_details = loads(rows[2]['data'])

        assert fhir_details['payload'] == Request_Payload
        assert fhir_details['method'] == 'POST'
        assert fhir_details['path'] == '/Patient'

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
