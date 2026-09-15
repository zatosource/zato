# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# An MCP gateway carries the core failure settings plus what is the gateway's own - the invalid calls, the rejections, the
# callers rejected, throttled and repeating themselves, the two latencies in seconds, the truncations, the volume budget as
# a byte count, the silence switch and the tool count - stored, defaulted, validated and listed under the mcp type through
# the generic connection services, with a negative threshold refused before anything is written.

# pytest
import pytest

# Zato
from zato.common.alerting.object_config import alert_type_llm, alert_type_mcp, get_defaults, get_field_names, storage_name
from zato.common.exception import BadRequest
from zato.server.service.internal.generic.connection import Create, Edit

# Test support
from generic_stub import count_connections as _count_connections, create_mcp as _create, get_list as _get_list, \
    mcp_input as _mcp_input, new_service as _new_service, stored_opaque as _stored_opaque, MCP_Name as _mcp_name, \
    MCP_Services as _mcp_services, MCP_Type as _mcp_type, MCP_URL_Path as _mcp_url_path

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

# The names an MCP gateway stores its settings under, in the order of the popup
_storage_names = [storage_name(name) for name in get_field_names(alert_type_mcp)]

# The names a gateway alone stores - what never lands on an LLM connection
_mcp_only_names = [storage_name(name) for name in get_field_names(alert_type_mcp)
    if name not in get_field_names(alert_type_llm)]

# ################################################################################################################################
# ################################################################################################################################

class TestCreate:

    def test_an_mcp_gateway_stores_the_settings_it_was_sent(self, session_factory:'any_') -> 'None':
        item_id = _create(session_factory,
            alert_invalid_calls=2,
            alert_invalid_calls_window=600,
            alert_rejections=4,
            alert_throttled_calls=20,
            alert_repeat_calls=30,
            alert_warning_latency=7.5,
            alert_error_latency=12,
            alert_volume_budget=2000000000,
            alert_volume_budget_window=3600,
            alert_traffic_expected=True,
            alert_max_tools=30,
            alert_email_connection='smtp:ops.smtp',
        )

        opaque = _stored_opaque(session_factory, item_id)

        assert opaque['alert_invalid_calls'] == 2
        assert opaque['alert_invalid_calls_window'] == 600
        assert opaque['alert_rejections'] == 4
        assert opaque['alert_throttled_calls'] == 20
        assert opaque['alert_repeat_calls'] == 30
        assert opaque['alert_warning_latency'] == 7.5
        assert opaque['alert_error_latency'] == 12
        assert opaque['alert_volume_budget'] == 2000000000
        assert opaque['alert_volume_budget_window'] == 3600
        assert opaque['alert_traffic_expected'] is True
        assert opaque['alert_max_tools'] == 30
        assert opaque['alert_email_connection'] == 'smtp:ops.smtp'

        # The gateway's own details stay what they were sent as
        assert opaque['url_path'] == _mcp_url_path
        assert opaque['services'] == _mcp_services
        assert opaque['validate_input'] is True

    def test_a_latency_of_seven_and_a_half_is_kept_as_a_fraction_and_the_budget_as_an_integer(self,
        session_factory:'any_') -> 'None':
        item_id = _create(session_factory, alert_warning_latency=7.5, alert_volume_budget=500000000)

        opaque = _stored_opaque(session_factory, item_id)

        assert opaque['alert_warning_latency'] == 7.5
        assert isinstance(opaque['alert_warning_latency'], float)

        assert opaque['alert_volume_budget'] == 500000000
        assert isinstance(opaque['alert_volume_budget'], int)

    def test_an_mcp_gateway_fills_in_the_defaults_for_what_it_was_not_sent(self, session_factory:'any_') -> 'None':
        item_id = _create(session_factory, alert_repeat_calls=30)

        opaque = _stored_opaque(session_factory, item_id)
        defaults = get_defaults(alert_type_mcp)

        for name in _storage_names:
            assert name in opaque

        assert opaque['alert_repeat_calls'] == 30
        assert opaque['alert_repeat_calls_window'] == defaults['repeat_calls_window']
        assert opaque['alert_repeat_calls_window'] == 300
        assert opaque['alert_invalid_calls'] == defaults['invalid_calls']
        assert opaque['alert_invalid_calls'] == 5
        assert opaque['alert_rejections'] == 3
        assert opaque['alert_auth_failures'] == 10
        assert opaque['alert_throttled_calls'] == 10
        assert opaque['alert_warning_latency'] == 5
        assert opaque['alert_error_latency'] == 15
        assert opaque['alert_truncations'] == 5
        assert opaque['alert_volume_budget'] == 100000000
        assert opaque['alert_volume_budget_window'] == 86400
        assert opaque['alert_traffic_expected'] is False
        assert opaque['alert_silence_window'] == 3600
        assert opaque['alert_max_tools'] == 25
        assert opaque['alert_is_active'] is True
        assert opaque['alert_use_llm'] is True

    def test_the_mcp_settings_are_the_gateways_own(self) -> 'None':

        # No status codes, no connection failures and no token budget - those are an outgoing connection's
        assert 'alert_status_codes' not in _storage_names
        assert 'alert_connection_failures' not in _storage_names
        assert 'alert_token_budget' not in _storage_names
        assert 'alert_max_latency' not in _storage_names

        # What the gateway alone stores, next to the two latencies and the truncations it shares with the LLM type
        assert _mcp_only_names == [
            'alert_invalid_calls', 'alert_invalid_calls_window',
            'alert_rejections', 'alert_rejections_window',
            'alert_auth_failures', 'alert_auth_failures_window',
            'alert_throttled_calls', 'alert_throttled_calls_window',
            'alert_repeat_calls', 'alert_repeat_calls_window',
            'alert_volume_budget', 'alert_volume_budget_window',
            'alert_traffic_expected', 'alert_silence_window', 'alert_silence_slots',
            'alert_max_tools',
        ]

    def test_a_negative_max_tools_is_refused_before_anything_is_written(self, session_factory:'any_') -> 'None':

        with pytest.raises(BadRequest) as ctx:
            _ = _create(session_factory, alert_max_tools=-1)

        assert 'max_tools' in str(ctx.value)
        assert _count_connections(session_factory) == 0

    def test_a_budget_that_is_not_a_number_is_refused(self, session_factory:'any_') -> 'None':

        with pytest.raises(BadRequest) as ctx:
            _ = _create(session_factory, alert_volume_budget='lots')

        assert 'volume_budget' in str(ctx.value)
        assert _count_connections(session_factory) == 0

    def test_the_settings_ride_in_the_config_message(self, session_factory:'any_') -> 'None':
        service = _new_service(Create, session_factory, _mcp_input(alert_repeat_calls=30, alert_max_tools=40))
        service.handle()

        message = service.config_dispatcher.publish.call_args[0][0]

        assert message['alert_repeat_calls'] == 30
        assert message['alert_max_tools'] == 40
        assert message['alert_invalid_calls'] == 5
        assert message['alert_warning_latency'] == 5

# ################################################################################################################################
# ################################################################################################################################

class TestEdit:

    def test_an_edit_without_the_settings_keeps_the_stored_ones(self, session_factory:'any_') -> 'None':
        item_id = _create(session_factory, alert_repeat_calls=30, alert_email_connection='smtp:ops.smtp')

        service = _new_service(Edit, session_factory, _mcp_input(id=item_id, validate_input=False))
        service.handle()

        opaque = _stored_opaque(session_factory, item_id)

        assert opaque['alert_repeat_calls'] == 30
        assert opaque['alert_email_connection'] == 'smtp:ops.smtp'
        assert opaque['validate_input'] is False

        for name in _storage_names:
            assert name in opaque

    def test_an_edit_with_the_settings_replaces_them(self, session_factory:'any_') -> 'None':
        item_id = _create(session_factory, alert_repeat_calls=30)

        service = _new_service(Edit, session_factory,
            _mcp_input(id=item_id, alert_repeat_calls=50, alert_warning_latency=2.5, alert_is_active=False))
        service.handle()

        opaque = _stored_opaque(session_factory, item_id)

        assert opaque['alert_repeat_calls'] == 50
        assert opaque['alert_warning_latency'] == 2.5
        assert opaque['alert_is_active'] is False

    def test_an_edit_refuses_a_negative_threshold_and_keeps_the_stored_ones(self, session_factory:'any_') -> 'None':
        item_id = _create(session_factory, alert_max_tools=30)

        service = _new_service(Edit, session_factory, _mcp_input(id=item_id, alert_max_tools=-5))

        with pytest.raises(BadRequest):
            service.handle()

        opaque = _stored_opaque(session_factory, item_id)
        assert opaque['alert_max_tools'] == 30

# ################################################################################################################################
# ################################################################################################################################

class TestGetList:

    def test_an_mcp_gateway_lists_every_setting_with_the_defaults_filled_in(self, session_factory:'any_') -> 'None':
        _ = _create(session_factory, alert_repeat_calls=30)

        rows = _get_list(session_factory, _mcp_type)
        assert len(rows) == 1

        row = rows[0]
        defaults = get_defaults(alert_type_mcp)

        for name in _storage_names:
            assert name in row

        assert row['name'] == _mcp_name
        assert row['url_path'] == _mcp_url_path
        assert row['alert_repeat_calls'] == 30
        assert row['alert_invalid_calls'] == defaults['invalid_calls']
        assert row['alert_volume_budget'] == defaults['volume_budget']
        assert row['alert_warning_latency'] == defaults['warning_latency']
        assert row['alert_max_tools'] == defaults['max_tools']

# ################################################################################################################################
# ################################################################################################################################
