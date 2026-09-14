# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# An outgoing MLLP connection carries the failures and the latency an outgoing FHIR connection does minus everything
# HTTP, plus the negative acknowledgments it alerts on - the codes, their threshold and window - and no silence, stored,
# defaulted, validated and listed under the mllp_outgoing type through the generic connection services.

# pytest
import pytest

# Zato
from zato.common.alerting.object_config import alert_type_fhir, alert_type_mllp_channel, alert_type_mllp_outgoing, \
    get_defaults, get_field_names, storage_name
from zato.common.exception import BadRequest
from zato.server.service.internal.generic.connection import Create, Edit

# Test support
from generic_stub import count_connections as _count_connections, create_mllp_outgoing as _create, get_list as _get_list, \
    mllp_outgoing_input as _mllp_input, new_service as _new_service, stored_opaque as _stored_opaque, \
    MLLP_Outgoing_Address as _mllp_address, MLLP_Outgoing_Name as _mllp_name, MLLP_Outgoing_Type as _mllp_type

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

# The names an outgoing MLLP connection stores its settings under, in the order of the tab
_storage_names = [storage_name(name) for name in get_field_names(alert_type_mllp_outgoing)]

# The names an outgoing FHIR connection stores that an outgoing MLLP one never does - everything that reads an HTTP status
_http_only_names = [storage_name(name) for name in get_field_names(alert_type_fhir)
    if name not in get_field_names(alert_type_mllp_outgoing)]

# The names an MLLP channel stores that an outgoing connection never does - the silence
_channel_only_names = [storage_name(name) for name in get_field_names(alert_type_mllp_channel)
    if name not in get_field_names(alert_type_mllp_outgoing)]

# ################################################################################################################################
# ################################################################################################################################

class TestCreate:

    def test_an_outgoing_mllp_connection_stores_the_settings_it_was_sent(self, session_factory:'any_') -> 'None':
        item_id = _create(session_factory,
            alert_ack_codes='AR, CR',
            alert_ack_threshold=2,
            alert_acks_window=600,
            alert_connection_failures=5,
            alert_connection_failures_window=900,
            alert_consecutive_failures=2,
            alert_email_connection='smtp:ops.smtp',
        )

        opaque = _stored_opaque(session_factory, item_id)

        assert opaque['alert_ack_codes'] == 'AR, CR'
        assert opaque['alert_ack_threshold'] == 2
        assert opaque['alert_acks_window'] == 600
        assert opaque['alert_connection_failures'] == 5
        assert opaque['alert_connection_failures_window'] == 900
        assert opaque['alert_consecutive_failures'] == 2
        assert opaque['alert_email_connection'] == 'smtp:ops.smtp'

        # The connection's details stay what they were sent as
        assert opaque['is_audit_log_active'] is True

    def test_an_ack_codes_text_of_one_code_stays_text(self, session_factory:'any_') -> 'None':
        item_id = _create(session_factory, alert_ack_codes='AR')

        opaque = _stored_opaque(session_factory, item_id)
        assert opaque['alert_ack_codes'] == 'AR'

    def test_an_outgoing_mllp_connection_fills_in_the_defaults_for_what_it_was_not_sent(self, session_factory:'any_') -> 'None':
        item_id = _create(session_factory, alert_max_latency=2500)

        opaque = _stored_opaque(session_factory, item_id)
        defaults = get_defaults(alert_type_mllp_outgoing)

        for name in _storage_names:
            assert name in opaque

        assert opaque['alert_max_latency'] == 2500
        assert opaque['alert_ack_codes'] == defaults['ack_codes']
        assert opaque['alert_ack_codes'] == 'AE, AR, CE, CR'
        assert opaque['alert_ack_threshold'] == defaults['ack_threshold']
        assert opaque['alert_acks_window'] == defaults['acks_window']
        assert opaque['alert_connection_failures'] == defaults['connection_failures']
        assert opaque['alert_connection_failures_window'] == defaults['connection_failures_window']
        assert opaque['alert_is_active'] is True
        assert opaque['alert_use_llm'] is True

    def test_nothing_http_and_no_silence_lands_on_an_outgoing_mllp_connection(self, session_factory:'any_') -> 'None':
        item_id = _create(session_factory)

        opaque = _stored_opaque(session_factory, item_id)

        assert _http_only_names
        for name in _http_only_names:
            assert name not in opaque

        assert _channel_only_names == ['alert_traffic_expected', 'alert_silence_window', 'alert_silence_slots']
        for name in _channel_only_names:
            assert name not in opaque

    def test_bad_ack_codes_are_refused_before_anything_is_written(self, session_factory:'any_') -> 'None':

        # A positive acknowledgment is never alerted on
        with pytest.raises(BadRequest) as ctx:
            _ = _create(session_factory, alert_ack_codes='AA')

        assert 'AA' in str(ctx.value)
        assert _count_connections(session_factory) == 0

    def test_the_settings_ride_in_the_config_message(self, session_factory:'any_') -> 'None':
        service = _new_service(Create, session_factory, _mllp_input(alert_ack_codes='CR', alert_connection_failures=7))
        service.handle()

        message = service.config_dispatcher.publish.call_args[0][0]

        assert message['alert_ack_codes'] == 'CR'
        assert message['alert_connection_failures'] == 7
        assert message['alert_ack_threshold'] == 3

# ################################################################################################################################
# ################################################################################################################################

class TestEdit:

    def test_an_edit_without_the_settings_keeps_the_stored_ones(self, session_factory:'any_') -> 'None':
        item_id = _create(session_factory, alert_ack_codes='CR', alert_email_connection='smtp:ops.smtp')

        service = _new_service(Edit, session_factory, _mllp_input(id=item_id, is_audit_log_active=False))
        service.handle()

        opaque = _stored_opaque(session_factory, item_id)

        assert opaque['alert_ack_codes'] == 'CR'
        assert opaque['alert_email_connection'] == 'smtp:ops.smtp'
        assert opaque['is_audit_log_active'] is False

        for name in _storage_names:
            assert name in opaque

    def test_an_edit_with_the_settings_replaces_them(self, session_factory:'any_') -> 'None':
        item_id = _create(session_factory, alert_ack_codes='CR')

        service = _new_service(Edit, session_factory, _mllp_input(id=item_id, alert_ack_codes='AE', alert_is_active=False))
        service.handle()

        opaque = _stored_opaque(session_factory, item_id)

        assert opaque['alert_ack_codes'] == 'AE'
        assert opaque['alert_is_active'] is False

    def test_an_edit_refuses_bad_ack_codes_and_keeps_the_stored_ones(self, session_factory:'any_') -> 'None':
        item_id = _create(session_factory, alert_ack_codes='CR')

        service = _new_service(Edit, session_factory, _mllp_input(id=item_id, alert_ack_codes='500'))

        with pytest.raises(BadRequest):
            service.handle()

        opaque = _stored_opaque(session_factory, item_id)
        assert opaque['alert_ack_codes'] == 'CR'

# ################################################################################################################################
# ################################################################################################################################

class TestGetList:

    def test_an_outgoing_mllp_connection_lists_every_setting_with_the_defaults_filled_in(self, session_factory:'any_') -> 'None':
        _ = _create(session_factory, alert_ack_codes='CR')

        rows = _get_list(session_factory, _mllp_type)
        assert len(rows) == 1

        row = rows[0]
        defaults = get_defaults(alert_type_mllp_outgoing)

        for name in _storage_names:
            assert name in row

        assert row['name'] == _mllp_name
        assert row['address'] == _mllp_address
        assert row['alert_ack_codes'] == 'CR'
        assert row['alert_ack_threshold'] == defaults['ack_threshold']
        assert row['alert_connection_failures'] == defaults['connection_failures']

        for name in _http_only_names:
            assert name not in row

        for name in _channel_only_names:
            assert name not in row

# ################################################################################################################################
# ################################################################################################################################
