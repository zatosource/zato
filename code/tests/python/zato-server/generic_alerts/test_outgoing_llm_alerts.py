# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# An outgoing LLM connection carries the failure settings an outgoing REST one does plus what is the LLM's own - the two
# latencies in seconds, the truncations, the refusals and the token budget with their windows - stored, defaulted, validated
# and listed under the llm type through the generic connection services, with no silence and no health check field on it.

# pytest
import pytest

# Zato
from zato.common.alerting.object_config import alert_type_llm, alert_type_rest, get_defaults, get_field_names, storage_name
from zato.common.exception import BadRequest
from zato.server.service.internal.generic.connection import Create, Edit

# Test support
from generic_stub import count_connections as _count_connections, create_llm as _create, get_list as _get_list, \
    llm_input as _llm_input, new_service as _new_service, stored_opaque as _stored_opaque, LLM_Address as _llm_address, \
    LLM_Model as _llm_model, LLM_Name as _llm_name, LLM_Type as _llm_type

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

# The names an outgoing LLM connection stores its settings under, in the order of the tab
_storage_names = [storage_name(name) for name in get_field_names(alert_type_llm)]

# The names an LLM connection alone stores - what never lands on a REST one
_llm_only_names = [storage_name(name) for name in get_field_names(alert_type_llm)
    if name not in get_field_names(alert_type_rest)]

# ################################################################################################################################
# ################################################################################################################################

class TestCreate:

    def test_an_outgoing_llm_connection_stores_the_settings_it_was_sent(self, session_factory:'any_') -> 'None':
        item_id = _create(session_factory,
            alert_status_codes='429, 5xx',
            alert_status_code_threshold=5,
            alert_truncations=2,
            alert_truncations_window=600,
            alert_refusals=4,
            alert_warning_latency=7.5,
            alert_error_latency=12,
            alert_token_budget=2000000,
            alert_token_budget_window=3600,
            alert_email_connection='smtp:ops.smtp',
        )

        opaque = _stored_opaque(session_factory, item_id)

        assert opaque['alert_status_codes'] == '429, 5xx'
        assert opaque['alert_status_code_threshold'] == 5
        assert opaque['alert_truncations'] == 2
        assert opaque['alert_truncations_window'] == 600
        assert opaque['alert_refusals'] == 4
        assert opaque['alert_warning_latency'] == 7.5
        assert opaque['alert_error_latency'] == 12
        assert opaque['alert_token_budget'] == 2000000
        assert opaque['alert_token_budget_window'] == 3600
        assert opaque['alert_email_connection'] == 'smtp:ops.smtp'

        # The LLM details stay what they were sent as
        assert opaque['model'] == _llm_model
        assert opaque['max_tokens'] == 4096

    def test_a_status_codes_text_of_one_code_stays_text(self, session_factory:'any_') -> 'None':
        item_id = _create(session_factory, alert_status_codes='429')

        opaque = _stored_opaque(session_factory, item_id)
        assert opaque['alert_status_codes'] == '429'

    def test_an_outgoing_llm_connection_fills_in_the_defaults_for_what_it_was_not_sent(self,
        session_factory:'any_') -> 'None':
        item_id = _create(session_factory, alert_token_budget=500000)

        opaque = _stored_opaque(session_factory, item_id)
        defaults = get_defaults(alert_type_llm)

        for name in _storage_names:
            assert name in opaque

        assert opaque['alert_token_budget'] == 500000
        assert opaque['alert_token_budget_window'] == defaults['token_budget_window']
        assert opaque['alert_token_budget_window'] == 86400
        assert opaque['alert_status_codes'] == defaults['status_codes']
        assert opaque['alert_status_codes'] == '429, 401, 403, 5xx'
        assert opaque['alert_truncations'] == defaults['truncations']
        assert opaque['alert_refusals'] == defaults['refusals']
        assert opaque['alert_warning_latency'] == 10
        assert opaque['alert_error_latency'] == 15
        assert opaque['alert_connection_failures'] == defaults['connection_failures']
        assert opaque['alert_is_active'] is True
        assert opaque['alert_use_llm'] is True

    def test_the_llm_settings_are_the_connections_own_and_there_is_no_silence_on_it(self) -> 'None':

        # The REST latency gives way to the LLM's two ..
        assert 'alert_max_latency' not in _storage_names

        # .. and what the LLM alone stores is its two latencies, its completions and its budget
        assert _llm_only_names == [
            'alert_truncations', 'alert_truncations_window',
            'alert_refusals', 'alert_refusals_window',
            'alert_warning_latency', 'alert_error_latency',
            'alert_token_budget', 'alert_token_budget_window',
        ]

        # An outgoing connection expects no traffic, so nothing about silence lands on it
        for name in _storage_names:
            assert 'silence' not in name, name

        # And there is no health check either
        for name in _storage_names:
            assert 'health' not in name, name

    def test_bad_status_codes_are_refused_before_anything_is_written(self, session_factory:'any_') -> 'None':

        with pytest.raises(BadRequest) as ctx:
            _ = _create(session_factory, alert_status_codes='6xx')

        assert '6xx' in str(ctx.value)
        assert _count_connections(session_factory) == 0

    def test_a_soap_fault_code_is_not_a_status_code(self, session_factory:'any_') -> 'None':

        with pytest.raises(BadRequest) as ctx:
            _ = _create(session_factory, alert_status_codes='Receiver')

        assert 'Receiver' in str(ctx.value)
        assert _count_connections(session_factory) == 0

    def test_the_settings_ride_in_the_config_message(self, session_factory:'any_') -> 'None':
        service = _new_service(Create, session_factory, _llm_input(alert_token_budget=750000, alert_truncations=7))
        service.handle()

        message = service.config_dispatcher.publish.call_args[0][0]

        assert message['alert_token_budget'] == 750000
        assert message['alert_truncations'] == 7
        assert message['alert_status_codes'] == '429, 401, 403, 5xx'
        assert message['alert_warning_latency'] == 10

# ################################################################################################################################
# ################################################################################################################################

class TestEdit:

    def test_an_edit_without_the_settings_keeps_the_stored_ones(self, session_factory:'any_') -> 'None':
        item_id = _create(session_factory, alert_token_budget=750000, alert_email_connection='smtp:ops.smtp')

        service = _new_service(Edit, session_factory, _llm_input(id=item_id, max_tokens=1024))
        service.handle()

        opaque = _stored_opaque(session_factory, item_id)

        assert opaque['alert_token_budget'] == 750000
        assert opaque['alert_email_connection'] == 'smtp:ops.smtp'
        assert opaque['max_tokens'] == 1024

        for name in _storage_names:
            assert name in opaque

    def test_an_edit_with_the_settings_replaces_them(self, session_factory:'any_') -> 'None':
        item_id = _create(session_factory, alert_token_budget=750000)

        service = _new_service(Edit, session_factory,
            _llm_input(id=item_id, alert_token_budget=1500000, alert_warning_latency=2.5, alert_is_active=False))
        service.handle()

        opaque = _stored_opaque(session_factory, item_id)

        assert opaque['alert_token_budget'] == 1500000
        assert opaque['alert_warning_latency'] == 2.5
        assert opaque['alert_is_active'] is False

    def test_an_edit_refuses_bad_status_codes_and_keeps_the_stored_ones(self, session_factory:'any_') -> 'None':
        item_id = _create(session_factory, alert_status_codes='429')

        service = _new_service(Edit, session_factory, _llm_input(id=item_id, alert_status_codes='Receiver'))

        with pytest.raises(BadRequest):
            service.handle()

        opaque = _stored_opaque(session_factory, item_id)
        assert opaque['alert_status_codes'] == '429'

# ################################################################################################################################
# ################################################################################################################################

class TestGetList:

    def test_an_outgoing_llm_connection_lists_every_setting_with_the_defaults_filled_in(self,
        session_factory:'any_') -> 'None':
        _ = _create(session_factory, alert_token_budget=750000)

        rows = _get_list(session_factory, _llm_type)
        assert len(rows) == 1

        row = rows[0]
        defaults = get_defaults(alert_type_llm)

        for name in _storage_names:
            assert name in row

        assert row['name'] == _llm_name
        assert row['address'] == _llm_address
        assert row['model'] == _llm_model
        assert row['alert_token_budget'] == 750000
        assert row['alert_status_codes'] == defaults['status_codes']
        assert row['alert_truncations'] == defaults['truncations']
        assert row['alert_refusals'] == defaults['refusals']
        assert row['alert_warning_latency'] == defaults['warning_latency']
        assert row['alert_connection_failures'] == defaults['connection_failures']

        # The secret never leaves the server
        assert 'secret' not in row

# ################################################################################################################################
# ################################################################################################################################
